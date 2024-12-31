import json
import os
import nltk
from nltk.corpus import words
from main import path
from query import *
input_data_path = os.path.join(path, 'problemsounds.json')


# ====================================
# 3. NLTK Setup
# ====================================

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

if os.path.exists(os.path.join(path, 'edited_generated_story.txt')):
    open(os.path.join(path, 'edited_generated_story.txt'), 'w').close()

if os.path.exists(os.path.join(path, 'generated_story.txt')):
    open(os.path.join(path, 'generated_story.txt'), 'w').close()

story_length = 500
chapters = 1


# Opening JSON file for guidewords
with open(os.path.join(path, 'truncated_dictionary.json')) as json_file:
    guidewords = json.load(json_file)


    
### Function to get user input and choose API
def get_api_choice():
    while True:
        choice = input("Choose API to use (openai/anthropic): ").strip().lower()
        if choice in ['openai', 'anthropic']:
            return choice
        else:
            print("Invalid choice. Please enter 'openai' or 'anthropic'.")

def get_input_and_save():
    clear_json_file()  # Clear the file before saving new data
    
    topic = input("Enter your story topic: ")
    problems = input("Enter the problem letters separated by /: ").split("/")
    problems = [problem.strip() for problem in problems]  # Clean up whitespace
    
    # Ensure "fail" is always included
    if "fail" not in problems:
        problems.append("fail")

    # Create a dictionary to store the input
    input_data = {
        "topic": topic,
        "problems": problems
    }

    api_choice = get_api_choice()
    # Save the data to a JSON file
    with open(input_data_path, 'w', encoding='utf-8') as file:
        json.dump(input_data, file, indent=4)

    # Ask user to choose API
    return topic, problems, api_choice

def get_input():
    global sight_words
    global readingLevel
    global maxsyllable
    story_length = int(input("Enter the length of the story: "))
    topic = input("Enter your story topic: ")
    problems = input("Enter the problem letters separated by /: ").split("/")
    name = input("What do you want the main character's name to be: ")
    readingLevel = input("Enter the grade level of the reader (Only the grade number): ")
    api = get_api_choice()
    if int(readingLevel) <= 1:
        maxsyllable = 2
    elif int(readingLevel) <= 3:
        maxsyllable = 3
    elif int(readingLevel) <= 5:
        maxsyllable = 4
    elif int(readingLevel) <= 7:
        maxsyllable = 5
    elif int(readingLevel) <= 9:
        maxsyllable = 6
    else:
        maxsyllable = 10
    # sight_words = input("Enter the sight words separated by commas: ")
    problems = [problem.strip() for problem in problems]  # Clean up whitespace

    return story_length, topic, problems, name, readingLevel,api

### Function to write the story to a file
def write_story_to_file(story):
    # Write the original story to 'generated_story.txt'
    with open(os.path.join(path, 'generated_story.txt'), 'w', encoding='utf-8') as file:
        file.write(story)
    print("\nOriginal story written to 'generated_story.txt'.")

### Function to delete the files before generating new ones
def delete_old_file():
    file_paths = [os.path.join(path, 'generated_story.txt')]
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Previous file '{file_path}' deleted.")

def generate_chapter(outline, chapter_number, length, story, problems, readingLevel, api):
    # Collect guidewords for all problem sounds
    problem_examples = {}
    for problem in problems:
        problem = problem.strip()
        if problem in guidewords:
            problem_examples[problem] = guidewords[problem][:5]  # Limit to 5 examples for brevity
        else:
            print(f"Warning: Problem '{problem}' not found in guidewords dictionary.")

    # Format the examples for the prompt
    examples_str_list = []
    for problem, examples in problem_examples.items():
        formatted_examples = ", ".join([f"'{word}'" for word in examples])
        examples_str = f"The '{problem}' sound in {formatted_examples}"
        examples_str_list.append(examples_str)
    examples_str = "; ".join(examples_str_list)

    # Now, create the prompt including the examples_str
    prompt = f"""
    You are a creative author tasked with writing chapter {chapter_number} of an american children's story for a child at a {readingLevel} grade reading level.

    Here is the outline:

    {outline}

    Here is the story so far:

    {story}

    Please avoid using words that contain these sounds: {', '.join(problems)}.

    Some examples of words to avoid are: {examples_str}.

    Write a {length} word chapter.

    Please ensure that you use proper punctuation and include spaces after punctuation marks.

    Return only the new chapter.
    """
    # Generate the chapter using the query function
    new_chapter = query(prompt, api=api)
    return new_chapter

def generate_outline(topic, name, readingLevel, story_length=500, api='openai'):
    prompt = f"""
    You are a creative author.

    Create an outline for a children's story about {topic} for an american child at a {readingLevel} grade reading level.

    The story should be about {story_length} words long.

    The story should be {chapters} chapter(s) long.

    The main character should be named {name}.

    Return only the outline.
    """
    outline = query(prompt, api=api)
    return outline

### Main function
def generate_story(topic, problems, name, readingLevel, api, story_length=500):
    outline = generate_outline(topic, name, readingLevel, story_length, api)
    story = ""
   
    chapter=0
    while len(story.split()) < story_length:
        print(f"Generating chapter {chapter + 1} using {api}...")
        new_chapter = generate_chapter(outline, chapter + 1, story_length // chapters, story, problems, readingLevel, api)
        story += new_chapter + "\n"  # Add a newline between chapters
        chapter+=1
    print(story)
    return story


def clear_json_file():
    # Clear the contents of the JSON file
    with open(input_data_path, 'w', encoding='utf-8') as file:
        file.write('{}')  # Write an empty JSON object

### Main function
def main():
    topic, problems, api_choice = get_input_and_save()
    name = input("What do you want the main character's name to be: ")
    readingLevel = input("Enter the grade level of the reader (Only the grade number): ")
    
    # Determine story length (default to 500 if not using get_input)
    story_length = 500
    
    story = generate_story(topic, problems, name, readingLevel, api_choice, story_length)

    # Delete any existing output files only after the entire story is generated
    delete_old_file()

    # Write the final story to the file
    write_story_to_file(story)

    print("\nFinal story:")
    print(story)

if __name__ == "__main__":
    main()
