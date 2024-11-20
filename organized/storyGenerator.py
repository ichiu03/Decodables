import openai
from openai import OpenAI
import json
import os
import re
import nltk
from nltk.corpus import words

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

if os.path.exists('dictionary_parser\\edited_generated_story.txt'):
    open('dictionary_parser\\edited_generated_story.txt', 'w').close()

if os.path.exists('dictionary_parser\\generated_story.txt'):
    open('dictionary_parser\\generated_story.txt', 'w').close()

client = OpenAI(
    api_key='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'
)

story_length = 500
chapters = 1

good_words = []
bad_words = []

# Opening JSON file
with open('dictionary_parser\\categorized_words.json') as json_file:
    words = json.load(json_file)

### Function to get all words
def get_all_words():
    with open("dictionary_parser\\WordDatav4.txt", "r") as f:
        words = f.read().split("\n")
    return words[:2000]

### Function to query GPT-3.5
def query(prompt): 
    messages = [
        {"role": "system", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response.choices[0].message.content

### Function to get user input

input_data_path = 'dictionary_parser/problemsounds.json'

def clear_json_file():
    # Clear the contents of the JSON file
    with open(input_data_path, 'w', encoding='utf-8') as file:
        file.write('{}')  # Write an empty JSON object

def get_input():
 
    topic = input("Enter your story topic: ")
    problems = input("Enter the problem letters separated by commas: ").split(",")
    problems = [problem.strip() for problem in problems]  # Clean up whitespace

    return topic, problems

### Function to get words
def get_words(problems):
    global bad_words
    global good_words

    words_list = set(words[problems[0]]) if problems else set()
    for problem in problems[1:]:
        words_list.update(words[problem])
    all_words = get_all_words()
    bad_words = [word for word in all_words if word not in words_list]
    good_words = [word for word in all_words if word not in bad_words]
    return bad_words

### Function to write the story to a file as a list of words
### Function to write the story to a file with each word on a new line
import re

# Function to write the original and stripped-down versions of the story to separate files
def write_story_to_file(story):
    # Write the original story to 'generated_story.txt'
    with open('dictionary_parser\\generated_story.txt', 'w', encoding='utf-8') as file:
        file.write(story)
    print("\nOriginal story written to 'generated_story.txt'.")

    # Tokenize the story using NLTK's word_tokenize
### Function to delete the file before generating a new one
### Function to delete the files before generating new ones
def delete_old_file():
    file_paths = ['generated_story.txt']
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)
            print(f"Previous file '{path}' deleted.")


def generate_chapter(outline, chapter_number, length, story):
    prompt = f"""
    You are a creative author tasked with writing chapter {chapter_number} of a children's story (age 10).

    Here is the outline:

    {outline}

    Here is the story so far:

    {story}

    Write a {length} word chapter.

    Please ensure that you use proper punctuation and include spaces after punctuation marks.

    Return only the new chapter.
    """
    story = query(prompt)
    return story

def generate_outline(topic):
    prompt = f"""
    You are a creative author.

    Create an outline for a children's story about {topic} (Age 10).

    The story should be about {story_length} words long.

    The story should have a clear beginning, middle, and end and have a lesson.

    The story should be {chapters}  chapters long.

    Return only the outline
    """
    outline = query(prompt)
    return outline

def sentence_check(story):
    sentences = story.split(".")
    new_story = ""
    prev_sentence = sentences[0]
    for sentence in sentences:
        next_sentence = sentences[sentences.index(sentence) + 1] if sentences.index(sentence) < len(sentences) - 1 else ""
        if "___" in sentence:
            prompt = f"""
                Give 5 words that would make sense in the following blank space:
                {prev_sentence}
                {sentence}
                {next_sentence}
                return only the 5 words separated by commas. Like this "word1,word2,word3,word4,word5"
            """
            response = query(prompt)
            words = response.split(",")
            for word in words:
                pass
                # Use dictionary parser to check if the word is good
                # if it is, then add it to the sentence
        prev_sentence = sentence
    return new_story

def word_check(story, dictionary, problems):
    new_story = ""
    sentences = story.split(".")
    
    for sentence in sentences:
        words = sentence.split(" ")
        bad_words = []
        for i in range(len(words)):
            check = False
            for problem in problems:
                for example in dictionary[problem]:
                    if example in words[i]:
                        check = True
                        bad_words.append(words[i])
            if check:
                
                # Verify that the following sentence only contains words from this language: {dictionary}

                prompt = f"""
                    Rewrite the following sentence and remove all instances of the following words: {bad_words}

                """
                response = query(prompt)
                #print(response)
                new_story += response
            else:
                new_story += words[i] + " "
    return new_story

### Function to edit the story
### This function takes the story (string) as input and returns the edited story (string)
def edit(story):
    prompt = f"""
    Edit the following story.

    Make minial changes, only correct blatant errors.

    Remove any Contractions and replace with the full word choice instead

    Make sure all sentences are coherent.

    Remove sentences that do not make sense or are irrelevant.

    Here is the story to edit: {story}

    Return only the story, no extra words.
    """
    response = query(prompt)
    return response

def fix_spacing(text):
    # Insert a space after punctuation marks if not followed by a space
    text = re.sub(r'([.!?])([^\s])', r'\1 \2', text)
    return text

### Main function
def generate_story(topic, problems):
    
    dictionary = get_words(problems)
    outline = generate_outline(topic)
    story = ""

    for chapter in range(chapters):
        print(f"Generating chapter {chapter + 1}")
        new_chapter = generate_chapter(outline, chapter + 1, story_length // chapters, story)
        # temp_chapter = new_chapter
        # temp_chapter = sentence_check(temp_chapter, dictionary, problems)
        temp_chapter = edit(new_chapter)
        story += temp_chapter + "\n"  # Add a space between chapters
    print(story)
    # Fix missing spaces after punctuation
    # story = fix_spacing(story)

    # story = sentence_check(story)


    # print("\nFinal story:")
    # print(story)
    return story


if __name__ == "__main__":
    generate_story()
