from openai import OpenAI
import anthropic
from dotenv import load_dotenv, dotenv_values
from storyGenerator import *
import os
import json
import tiktoken

global good_words
global bad_words
global encoding
good_words = set()
bad_words = set()
encoding = tiktoken.encoding_for_model("gpt-4o-mini")

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_PATH, '.env')
RESOURCES_PATH = os.path.join(BASE_PATH, 'Resources')

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

def get_bad_words(problems):
    """Get words that contain problem patterns from large_categorized_words.json"""
    bad_words = []
    total_words = 0
    category_counts = {}
    
    try:
        with open(os.path.join(RESOURCES_PATH, 'large.json'), 'r') as file:
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
    """Get words that contain dont problem patterns from categorized_words.json"""
    good_words = sight_words.split(',') if sight_words else []
    total_words = len(good_words)
    category_counts = {}
    
    try:
        with open(os.path.join(RESOURCES_PATH, 'categorized_words.json'), 'r') as file:
            categorized_words = json.load(file)
            
        # Gather all words from Good categories
        for category, words in categorized_words.items():
            if category not in problems:
                words_in_category = [word.lower() for word in words]
                good_words.extend(words_in_category)
                category_counts[category] = len(words_in_category)
                total_words += len(words_in_category)

        # Remove duplicates and filter out empty strings
        good_words = list(set(filter(None, good_words)))
        
        # Print statistics
        print(f"Total words processed: {total_words}")
        print(f"Unique Good words after deduplication: {len(good_words)}")
        print("\nWords per category:")
        for category, count in category_counts.items():
            print(f"{category}: {count}")
            
        return good_words
        
    except FileNotFoundError:
        print("Error: large_categorized_words.json not found")
        return []
    
def fine_tune(good_words, bad_words):
    print(good_words)
    print(bad_words)

def set_word_lists(problems,sight_words):
    """Set up good and bad word lists for token biasing"""
    global good_words, bad_words
    bad_words = get_bad_words(problems)
    good_words = get_good_words(problems,sight_words)
    fine_tune(good_words,bad_words)
    

def get_token_biases():
    token_biases = {}
    # Process bad words with strong negative bias
    for word in bad_words:
        tokens = encoding.encode(f" {word}")
        for token in tokens:
            token_biases[token] = -100
    
    # Process good words with positive bias
    for word in good_words:
        tokens = encoding.encode(f" {word}")
        for token in tokens:
            if token not in token_biases:
                token_biases[token] = 5
    return token_biases

def query_openai(prompt):
    messages = [
        {"role": "user", "content": prompt},
    ]
    # Get and apply token biases    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
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