import openai
import os
from time import time, sleep
import re
from nltk import word_tokenize


def open_file(filepath):
    # Read the file as binary
    with open(filepath, 'rb') as infile:
        rawdata = infile.read()

    # Detect the encoding
    result = chardet.detect(rawdata)
    charenc = result['encoding']

    # Open the file with the detected encoding
    with open(filepath, 'r', encoding=charenc) as infile:
        return infile.read()


openai.api_key = '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'


def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def gpt3_completion(prompt, engine='text-davinci-003', temp=0.6, top_p=1.0, tokens=1000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def recursive_chunk(text, max_tokens=800, overlap_ratio=0.2):
    # Tokenize the text
    tokens = word_tokenize(text)

    if len(tokens) <= max_tokens:
        return [text]  # Base case: Return the text as a single chunk

    # Calculate the overlap size
    overlap_size = int(max_tokens * overlap_ratio)

    # Determine the start and end indices of the current chunk
    start_index = 0
    end_index = max_tokens

    # Find the end index of the previous chunk to account for overlap
    previous_end_index = end_index - overlap_size

    # Recursive call to chunk the remaining text
    remaining_chunks = recursive_chunk(' '.join(tokens[previous_end_index:]), max_tokens, overlap_ratio)

    # Join the current chunk with the remaining chunks
    chunks = [' '.join(tokens[start_index:end_index])] + remaining_chunks

    return chunks

if __name__ == '__main__':
    alltext = open_file('input.txt')
    chunks = recursive_chunk(alltext)
    result = list()
    count = 0
    for chunk in chunks:
        count = count + 1
        prompt = open_file('prompt.txt').replace('<<PASSAGE>>', chunk)
        prompt = prompt.encode(encoding='ASCII', errors='ignore').decode()
        summary = gpt3_completion(prompt)
        print('\n\n\n', count, 'of', len(chunks), ' - ', summary)
        result.append(summary)
    save_file('\n\n'.join(result), book_title+'_%s.txt' % time())
