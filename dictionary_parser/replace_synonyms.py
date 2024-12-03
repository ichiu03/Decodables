import re
import openai
from openai import OpenAI
import json
import os

client = OpenAI(
    api_key= os.environ.get('OPENAI_API_KEY')
)


def load_synonyms(synonyms_file):
    synonyms_dict = {}
    with open(synonyms_file, 'r', encoding='utf-8') as file:
        for line in file:
            original, synonym = line.strip().split(None, 1)
            synonyms_dict[original.lower()] = synonym.lower()
    print(synonyms_dict)
    return synonyms_dict

def read_story(story_file):
    with open(story_file, 'r', encoding='utf-8') as file:
        story = file.read()
    return story

def replace_words_in_story(story, synonyms_dict):
    # Tokenize with regex to catch words and punctuation separately
    tokens = re.findall(r'\b\w+\b|[^\w\s]', story, re.UNICODE)

    # Create a list to hold the updated tokens
    updated_tokens = []

    for token in tokens:
        # Check if the token is a word (not punctuation)
        if re.match(r'\w+', token):
            # Lookup without punctuation and replace if found
            stripped_token = token.lower()

            if stripped_token in synonyms_dict:
                # Replace with the synonym and preserve case
                synonym = synonyms_dict[stripped_token]
                if token[0].isupper():
                    synonym = synonym.capitalize()
                updated_tokens.append(synonym)
            else:
                # Keep the original token if no replacement is needed
                updated_tokens.append(token)
        else:
            # Append punctuation directly
            updated_tokens.append(token)

    # Join tokens to form the final story
    updated_story = ''.join(
        (' ' if i > 0 and tokens[i - 1].isalnum() and token.isalnum() else '') + token
        for i, token in enumerate(updated_tokens)
    )
    return updated_story

def save_updated_story(updated_story, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(updated_story)
    print(f"Updated story has been saved to '{output_file}'.")

def query(prompt): 
    messages = [
        {"role": "system", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response.choices[0].message.content


import re

import re

def format_punctuation_with_quotes(text):
    # Normalize multiple underscores to '____'
    text = re.sub(r'_{2,}', '____', text)
    
    # Ensure spaces around '____', treating it as a word
    # Add a space before '____' if it's attached to a word character
    text = re.sub(r'(?<=\w)(____)', r' \1', text)
    # Add a space after '____' if it's followed by a word character
    text = re.sub(r'(____)(?=\w)', r'\1 ', text)
    # Handle cases where multiple '____' are adjacent
    text = re.sub(r'(____)(____)', r'\1 \2', text)
    
    # Remove unnecessary spaces before punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    
    # Ensure there's a space after punctuation marks if not present, unless followed by punctuation or quotes
    text = re.sub(r'([,.!?;:])([^\s"\'().,!?:;])', r'\1 \2', text)
    
    # Handle quotation marks with a state machine
    chars = list(text)
    new_chars = []
    in_quotes = False
    i = 0
    while i < len(chars):
        c = chars[i]
        if c == '"':
            if in_quotes:
                # Closing quote
                # Remove space before closing quote
                if new_chars and new_chars[-1] == ' ':
                    new_chars.pop()
                new_chars.append(c)
                in_quotes = False
                # Add space after closing quote if needed
                if i + 1 < len(chars) and chars[i + 1] not in ' ,.!?;:\'"':
                    new_chars.append(' ')
            else:
                # Opening quote
                # Add space before opening quote if necessary
                if new_chars and new_chars[-1] not in ' \n':
                    new_chars.append(' ')
                new_chars.append(c)
                in_quotes = True
                # Skip any spaces immediately after the opening quote
                i += 1
                while i < len(chars) and chars[i] == ' ':
                    i += 1
                continue
        else:
            new_chars.append(c)
        i += 1
    text = ''.join(new_chars)
    
    # Normalize multiple spaces to a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Trim leading and trailing spaces
    text = text.strip()
    
    return text

if __name__ == "__main__":
    synonyms_file = 'dictionary_parser\\word_synonyms.txt'
    story_file = 'dictionary_parser\\generated_story.txt'
    output_file = 'dictionary_parser\\updated_story.txt'
    
    # Load synonyms
    synonyms_dict = load_synonyms(synonyms_file)
    
    # Read the original story
    story = read_story(story_file)
    
    # Replace problematic words with synonyms
    updated_story = replace_words_in_story(story, synonyms_dict)
    
    updated_story = format_punctuation_with_quotes(updated_story)
    # Save the updated story
    save_updated_story(updated_story, output_file)

