import openai  # Use the standard OpenAI library
import anthropic
from dotenv import load_dotenv, dotenv_values
import json
import os
import nltk
from nltk.corpus import words
from main import path

# ====================================
# 1. Environment Setup
# ====================================

# Get absolute path to the root directory and .env file
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, '.env')

# Force load from .env file
load_dotenv(env_path, override=True)  # override=True will force it to override existing env variables

# Get API keys from .env file
config = dotenv_values(env_path)
openai_api_key = config.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
anthropic_api_key = config.get('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_API_KEY')

# ====================================
# 2. Initialize API Clients
# ====================================

# Initialize OpenAI client
openai.api_key = openai_api_key  # Set the OpenAI API key

# Initialize Anthropic client
anthropic_client = anthropic.Client(
    api_key=anthropic_api_key  # Set the Anthropic API key
)

# ====================================
# 3. NLTK Setup
# ====================================

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

# ====================================
# 4. File Handling
# ====================================

# Define file paths
edited_story_path = os.path.join(path, 'edited_generated_story.txt')
generated_story_path = os.path.join(path, 'generated_story.txt')

# Clear existing story files if they exist
for file_path in [edited_story_path, generated_story_path]:
    if os.path.exists(file_path):
        open(file_path, 'w').close()

# ====================================
# 5. Load Data
# ====================================

story_length = 500
chapters = 1

good_words = []
bad_words = []

# # Uncomment if you need categorized words
# with open(os.path.join(path, 'categorized_words.json')) as json_file:
#     words = json.load(json_file)

# Opening JSON file for guidewords
with open(os.path.join(path, 'truncated_dictionary.json')) as json_file:
    guidewords = json.load(json_file)

# ====================================
# 6. Define the Query Function
# ====================================

def query(prompt, model="anthropic"):
    """
    Queries the specified AI model (OpenAI or Anthropic) with the given prompt.

    Args:
        prompt (str): The input prompt to send to the model.
        model (str): The model to use ('chatgpt' or 'anthropic').

    Returns:
        str: The generated completion from the model.
    """
    model = "chatgpt" #### Was getting issues with anthropic, setting to chatgpt for now so I can push to production
    if model == "chatgpt":
        messages = [
            {"role": "system", "content": prompt},
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=story_length,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return ""
    
    elif model == "anthropic":
        try:
            # Format the prompt according to Anthropic's requirements
            # Typically, Anthropic expects prompts to be prefixed with a HUMAN_PROMPT and suffixed with AI_PROMPT
            formatted_prompt = f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}"
            
            response = anthropic_client.completion(
                prompt=formatted_prompt,
                model="claude-v1",  # Replace with the desired Claude model
                max_tokens_to_sample=story_length,  # Adjust as needed
                temperature=0.7,  # Adjust as needed
                stop_sequences=[anthropic.HUMAN_PROMPT]
            )
            
            # Extract the completion text
            completion = response.get('completion', '').strip()
            return completion
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return ""
    
    else:
        print(f"Unknown model: {model}")
        return ""

# ====================================
# 7. User Input Functions
# ====================================

input_data_path = os.path.join(path, 'problemsounds.json')


def clear_json_file():
    """Clear the contents of the JSON file."""
    with open(input_data_path, 'w', encoding='utf-8') as file:
        file.write('{}')  # Write an empty JSON object


def get_input_and_save():
    """Get user input and save it to a JSON file."""
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
    """Get comprehensive user input."""
    global sight_words
    global readingLevel
    global maxsyllable
    story_length_input = int(input("Enter the length of the story: "))
    topic = input("Enter your story topic: ")
    problems = input("Enter the problem letters separated by /: ").split("/")
    name = input("What do you want the main character's name to be: ")
    readingLevel = input("Enter the grade level of the reader (Only the grade number): ")
    
    try:
        readingLevel_int = int(readingLevel)
    except ValueError:
        print("Invalid grade level. Defaulting to 3.")
        readingLevel_int = 3

    if readingLevel_int <= 1:
        maxsyllable = 2
    elif readingLevel_int <= 3:
        maxsyllable = 3
    elif readingLevel_int <= 5:
        maxsyllable = 4
    elif readingLevel_int <= 7:
        maxsyllable = 5
    elif readingLevel_int <= 9:
        maxsyllable = 6
    else:
        maxsyllable = 10

    problems = [problem.strip() for problem in problems]  # Clean up whitespace

    return story_length_input, topic, problems, name, readingLevel

# ====================================
# 8. Story Generation Functions
# ====================================

def write_story_to_file(story):
    """Write the original story to 'generated_story.txt'."""
    with open(generated_story_path, 'w', encoding='utf-8') as file:
        file.write(story)
    print("\nOriginal story written to 'generated_story.txt'.")


def delete_old_file():
    """Delete old story files before generating new ones."""
    file_paths = [generated_story_path, edited_story_path]
    for file_path in file_paths:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Previous file '{file_path}' deleted.")


def generate_chapter(outline, chapter_number, length, story, problems, readingLevel, model="anthropic"):
    """
    Generate a single chapter of the story.

    Args:
        outline (str): The outline of the story.
        chapter_number (int): The current chapter number.
        length (int): The length of the chapter in words.
        story (str): The current state of the story.
        problems (list): List of problem letters to avoid.
        readingLevel (str): The grade level of the reader.
        model (str): The model to use ('chatgpt' or 'anthropic').

    Returns:
        str: The generated chapter text.
    """
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
    new_chapter = query(prompt, model=model)
    return new_chapter


def generate_outline(topic, name, readingLevel, story_length=500, model="anthropic"):
    """
    Generate an outline for the story.

    Args:
        topic (str): The topic of the story.
        name (str): The main character's name.
        readingLevel (str): The grade level of the reader.
        story_length (int): The total length of the story in words.
        model (str): The model to use ('chatgpt' or 'anthropic').

    Returns:
        str: The generated outline.
    """
    prompt = f"""
    You are a creative author.

    Create an outline for a children's story about {topic} for a child at a {readingLevel} grade reading level.

    The story should be about {story_length} words long.

    The story should have a clear beginning, middle, and end and have a lesson.

    The story should be {chapters} chapter(s) long.

    The main character should be named {name}.

    Return only the outline.
    """
    outline = query(prompt, model=model)
    return outline


def generate_story(topic, problems, name, readingLevel, story_length=500, model="anthropic"):
    """
    Generate the complete story based on user inputs.

    Args:
        topic (str): The topic of the story.
        problems (list): List of problem letters to avoid.
        name (str): The main character's name.
        readingLevel (str): The grade level of the reader.
        story_length (int): The total length of the story in words.
        model (str): The model to use ('chatgpt' or 'anthropic').

    Returns:
        str: The complete generated story.
    """
    outline = generate_outline(topic, name, readingLevel, story_length=story_length, model=model)
    story = ""
   
    for chapter in range(chapters):
        print(f"Generating chapter {chapter + 1} using {model}...")
        new_chapter = generate_chapter(
            outline=outline,
            chapter_number=chapter + 1,
            length=story_length // chapters,
            story=story,
            problems=problems,
            readingLevel=readingLevel,
            model=model
        )
        if new_chapter:
            story += new_chapter + "\n"  # Add a newline between chapters
        else:
            print(f"Failed to generate chapter {chapter + 1} using {model}.")
    print(story)
    return story

# ====================================
# 9. Main Function
# ====================================

def main():
    """Main function to execute the story generation process."""
    # Uncomment the desired input method
    # topic, problems = get_input_and_save()
    story_length, topic, problems, name, readingLevel = get_input()

    # Choose the model to use
    model_choice = ""
    while model_choice.lower() not in ["chatgpt", "anthropic"]:
        model_choice = input("Which model would you like to use? Enter 'chatgpt' or 'anthropic': ").strip().lower()
        if model_choice.lower() not in ["chatgpt", "anthropic"]:
            print("Invalid choice. Please enter 'chatgpt' or 'anthropic'.")

    # Generate the story
    story = generate_story(
        topic=topic,
        problems=problems,
        name=name,
        readingLevel=readingLevel,
        story_length=story_length,
        model=model_choice
    )

    # Delete any existing output files only after the entire story is generated
    delete_old_file()

    # Write the final story to the file
    write_story_to_file(story)

    print("\nFinal story:")
    print(story)

if __name__ == "__main__":
    main()
