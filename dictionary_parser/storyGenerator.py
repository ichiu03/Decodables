from openai import OpenAI
import anthropic
from dotenv import load_dotenv, dotenv_values
import json
import os
import nltk
from nltk.corpus import words
from main import path

input_data_path = os.path.join(path, 'problemsounds.json')

# Get absolute path to the root directory and .env file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, '.env')

# Force load from .env file
load_dotenv(env_path, override=True)  # override=True will force it to override existing env variables

# Get API keys from .env file
config = dotenv_values(env_path)
openai_api_key = config.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
anthropic_api_key = config.get('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY')

# Initialize OpenAI client
openai_client = OpenAI(
    api_key=openai_api_key  # Use the explicitly loaded OpenAI key
)

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(
    api_key=anthropic_api_key  # Ensure you have set ANTHROPIC_API_KEY in your .env
)
openai_client = OpenAI(
    api_key=openai_api_key
)
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

good_words = []
bad_words = []

# Opening JSON file for guidewords
with open(os.path.join(path, 'truncated_dictionary.json')) as json_file:
    guidewords = json.load(json_file)


def query_openai(prompt):
    messages = [
        {"role": "system", "content": prompt},
    ]
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response.choices[0].message.content

def query_anthropic(prompt):
    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0,
        system="You are a creative author tasked with generating children's stories.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    ) # Extract and join the text content from the response
    response = "".join(block.text for block in message.content if hasattr(block, "text"))
    print(message.content)
    print(response)
    return response

### Function to query the selected API
def query(prompt, api='openai'):
    if api == 'openai':
        try:
            return query_openai(prompt)
        except Exception as e:
            print(f"Error querying OpenAI: {e}\nTrying Anthropic...")
            return query_anthropic(prompt)
            return None
    elif api == 'anthropic':
        try:
            return query_anthropic(prompt)
        except Exception as e:
            print(f"Error querying Anthropic: {e}\nTrying OpenAI...")
            return query_openai(prompt)
    
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
    new_chapter = query(prompt, api=api)
    return new_chapter

def generate_outline(topic, name, readingLevel, story_length=500, api='openai'):
    prompt = f"""
    You are a creative author.

    Create an outline for a children's story about {topic} for a child at a {readingLevel} grade reading level.

    The story should be about {story_length} words long.

    The story should have a clear beginning, middle, and end and have a lesson.

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
   
    for chapter in range(chapters):
        print(f"Generating chapter {chapter + 1} using {api}...")
        new_chapter = generate_chapter(outline, chapter + 1, story_length // chapters, story, problems, readingLevel, api)
        story += new_chapter + "\n"  # Add a newline between chapters
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
