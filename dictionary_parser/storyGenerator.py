import json
import os
import nltk
from nltk.corpus import words
from main import path
from query import *
input_data_path = os.path.join(path, 'problemsounds.json')
from dictionaryParser import parseAndProcessWords
from main import sight_words


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

global good_words
global bad_words
good_words = set()
bad_words = set()

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

def get_bad_words(problems):
    """Get words that contain problem patterns from large_categorized_words.json"""
    bad_words = []
    total_words = 0
    category_counts = {}
    
    try:
        with open('dictionary_parser/Resources/large_categorized_words.json', 'r') as file:
            categorized_words = json.load(file)
            
        # Gather all words from problem categories
        for problem in problems:
            problem = problem.strip()
            if problem in categorized_words:
                words_in_category = [word.lower() for word in categorized_words[problem]]
                bad_words.extend(words_in_category)
                category_counts[problem] = len(words_in_category)
                total_words += len(words_in_category)
            else:
                print(f"Warning: Problem '{problem}' not found in word dictionary.")
                category_counts[problem] = 0
        
        # Remove duplicates and filter out empty strings
        bad_words = list(set(filter(None, bad_words)))
        
        # Print statistics
        print(f"Total words processed: {total_words}")
        print(f"Unique bad words after deduplication: {len(bad_words)}")
        print("\nWords per category:")
        for category, count in category_counts.items():
            print(f"{category}: {count}")
            
        return bad_words
        
    except FileNotFoundError:
        print("Error: large_categorized_words.json not found")
        return []
    
def get_good_words(problems,sight_words):
    good_words = sight_words
 
    num = 0
    with open(os.path.join(path, 'Resources/ChildDiction.txt'), 'r') as file:
        words = file.read()
    categorized_words = parseAndProcessWords(words, 100)
    for category in categorized_words:
        if category not in problems:
            for word in categorized_words[category]:
                if word not in good_words:
                    good_words += word + ", "
                    num += 1
    
    print(f"Number of good words: {num}")
    return good_words

    
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


#fucntion to get dictionary of good words from resources/ChildDiction.txt


def generate_chapter(outline, chapter_number, length, story, problems, readingLevel, api, good_words):
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
    Avoid using words that contain these sounds: {', '.join(problems)}.
    You are only allowed to use the following words: 
    START OF DICTIONARY
    {good_words}
    END OF DICTIONARY

    The above dictionary is all of the words that are allowed to be used in the story, they are the only words you know.
    ONLY USE WORDS FROM THE DICTIONARY OR ELSE YOU WILL BE FIRED. YOU ARE WRITING FOR KIDS IF YOU FAIL THIS TASK THEY WILL NEVER GET TO LEARN TO READ.
    You are not allowed to use any words that contain the sounds in the problems list.
    
    Here is the outline:

    {outline}

    Here is the story so far:

    {story}

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
    good_words = get_good_words(problems,sight_words)
    chapter=0
    while len(story.split()) < story_length:
        print(f"Generating chapter {chapter + 1} using {api}...")
        new_chapter = generate_chapter(outline, chapter + 1, story_length // chapters, story, problems, readingLevel, api, good_words)
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
