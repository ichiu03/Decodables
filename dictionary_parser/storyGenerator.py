import openai
from openai import OpenAI
import json
import os
import re
import nltk
from nltk.corpus import words
from dictionaryParser import parseAndProcessWords
import random

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

if os.path.exists('dictionary_parser\\edited_generated_story.txt'):
    open('dictionary_parser\\edited_generated_story.txt', 'w').close()

if os.path.exists('dictionary_parser\\generated_story.txt'):
    open('dictionary_parser\\generated_story.txt', 'w').close()

client = OpenAI(
    api_key= os.environ.get('OPENAI_API_KEY')
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

def get_input_and_save():
    clear_json_file()  # Clear the file before saving new data
    
    topic = input("Enter your story topic: ")
    problems = input("Enter the problem letters separated by commas: ").split(",")
    problems = [problem.strip() for problem in problems]  # Clean up whitespace
    
    # Ensure "fail" is always included
    if "fail" not in problems:
        problems.append("fail")

    # Create a dictionary to store the input
    input_data = {
        "topic": topic,
        "problems": problems
    }

    # Save the data to a JSON file
    with open(input_data_path, 'w', encoding='utf-8') as file:
        json.dump(input_data, file, indent=4)

    return topic, problems

def get_input():
    global story_length
    global sight_words
    global readingLevel
    story_length = int(input("Enter the length of the story: "))
    topic = input("Enter your story topic: ")
    readingLevel = input("Enter the grade level of the reader (Only the grade number): ")
    problems = input("Enter the problem letters separated by commas: ").split(",")
    # sight_words = input("Enter the sight words separated by commas: ")
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
    You are a creative author tasked with writing chapter {chapter_number} of a children's story for a child at a {readingLevel} grade reading level.

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

def generate_outline(topic,name):
    
    prompt = f"""
    You are a creative author.

    Create an outline for a children's story about {topic} of a children's story for a child at a {readingLevel} grade reading level.

    The story should be about {story_length} words long.

    The story should have a clear beginning, middle, and end and have a lesson.

    The story should be {chapters}  chapters long.

    The main character should be named {name}.

    Return only the outline
    """
    outline = query(prompt)
    return outline


### Main function
def generate_story(topic, problems):
    
    dictionary = get_words(problems)
    name = input("What do you want the main charachter's name to be: ")
    outline = generate_outline(topic, name)
    story = ""
    
    for chapter in range(chapters):
        print(f"Generating chapter {chapter + 1}")
        new_chapter = generate_chapter(outline, chapter + 1, story_length // chapters, story)
        # temp_chapter = new_chapter
        # temp_chapter = sentence_check(temp_chapter, dictionary, problems)
        # temp_chapter = edit(new_chapter)
        story += new_chapter + "\n"  # Add a space between chapters
    print(story)
    # Fix missing spaces after punctuation
    # story = fix_spacing(story)

    # story = sentence_check(story)


    # print("\nFinal story:")
    # print(story)
    return story


### Main function
def main():
    topic, problems = get_input_and_save()
    dictionary = get_words(problems)
    outline = generate_outline(topic)
    story = ""


    for chapter in range(chapters):
        print(f"Generating chapter {chapter + 1}")
        new_chapter = generate_chapter(outline, chapter + 1, story_length // chapters, story)
        temp_chapter = new_chapter
        #temp_chapter = sentence_check(temp_chapter, dictionary, problems)
        #temp_chapter = edit(temp_chapter)
        story += temp_chapter + " "  # Add a space between chapters

    # Fix missing spaces after punctuation
    #story = fix_spacing(story)

    #story = sentence_check(story)

    # Delete any existing output files only after the entire story is generated
    delete_old_file()

    # Write the final story to the file
    write_story_to_file(story)

    print("\nFinal story:")
    print(story)
    return 0


if __name__ == "__main__":
    main()
