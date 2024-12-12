from openai import OpenAI
from dotenv import load_dotenv
import json
import os
import nltk
from nltk.corpus import words

load_dotenv()

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

if os.path.exists('dictionary_parser/edited_generated_story.txt'):
    open('dictionary_parser/edited_generated_story.txt', 'w').close()

if os.path.exists('dictionary_parser/generated_story.txt'):
    open('dictionary_parser/generated_story.txt', 'w').close()

client = OpenAI(
    api_key= os.getenv('OPENAI_API_KEY')
)

story_length = 500
chapters = 1

good_words = []
bad_words = []

# Opening JSON file for words categorized by problems
with open('dictionary_parser/categorized_words.json') as json_file:
    words = json.load(json_file)

# Opening JSON file for guidewords
with open('dictionary_parser/truncated_dictionary.json') as json_file:
    guidewords = json.load(json_file)

### Function to get all words
def get_all_words():
    with open("dictionary_parser/WordDatav4.txt", "r") as f:
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

    # Save the data to a JSON file
    with open(input_data_path, 'w', encoding='utf-8') as file:
        json.dump(input_data, file, indent=4)

    return topic, problems

def get_input():
    global sight_words
    global readingLevel
    global maxsyllable
    story_length = int(input("Enter the length of the story: "))
    topic = input("Enter your story topic: ")
    problems = input("Enter the problem letters separated by /: ").split("/")
    name = input("What do you want the main character's name to be: ")
    readingLevel = input("Enter the grade level of the reader (Only the grade number): ")
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

    return story_length, topic, problems, name, readingLevel, maxsyllable

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

### Function to write the story to a file
def write_story_to_file(story):
    # Write the original story to 'generated_story.txt'
    with open('dictionary_parser/generated_story.txt', 'w', encoding='utf-8') as file:
        file.write(story)
    print("\nOriginal story written to 'generated_story.txt'.")

### Function to delete the files before generating new ones
def delete_old_file():
    file_paths = ['generated_story.txt']
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)
            print(f"Previous file '{path}' deleted.")

def generate_chapter(outline, chapter_number, length, story, problems, readingLevel):
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
    You are a creative author tasked with writing chapter {chapter_number} of a children's story for a child at a {readingLevel} grade reading level.

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
    new_chapter = query(prompt)
    return new_chapter

def generate_outline(topic, name, readingLevel, story_length = 500):
    prompt = f"""
    You are a creative author.

    Create an outline for a children's story about {topic} for a child at a {readingLevel} grade reading level.

    The story should be about {story_length} words long.

    The story should have a clear beginning, middle, and end and have a lesson.

    The story should be {chapters} chapter(s) long.

    The main character should be named {name}.

    Return only the outline.
    """
    outline = query(prompt)
    return outline

### Main function
def generate_story(topic, problems, name, readingLevel, story_length=500):
    dictionary = get_words(problems)
    outline = generate_outline(topic, name, readingLevel)
    story = ""
    
    for chapter in range(chapters):
        print(f"Generating chapter {chapter + 1}")
        new_chapter = generate_chapter(outline, chapter + 1, story_length // chapters, story, problems, readingLevel)
        story += new_chapter + "\n"  # Add a newline between chapters
    print(story)
    return story

### Main function
def main():
    topic, problems = get_input_and_save()
    story = generate_story(topic, problems)

    # Delete any existing output files only after the entire story is generated
    delete_old_file()

    # Write the final story to the file
    write_story_to_file(story)

    print("\nFinal story:")
    print(story)

if __name__ == "__main__":
    main()
