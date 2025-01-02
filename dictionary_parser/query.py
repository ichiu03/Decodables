from openai import OpenAI
import anthropic
from dotenv import load_dotenv, dotenv_values
from storyGenerator import *
import os


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


def query_openai(prompt):
    messages = [
        {"role": "system", "content": prompt},
    ]
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=messages,
    )
    return response.choices[0].message.content

def query_openaiplus(prompt):
    messages = [
        {"role": "user", "content": prompt},
    ]
    response = openai_client.chat.completions.create(
        model="o1-mini-2024-09-12",
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