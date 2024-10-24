import openai
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

def query(prompt):
    messages = [
    {"role": "system", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content
  
def get_input():
    topic = input("Enter your story topic: ")
    problems =  (input("Enter the problem letters separated by commas: ")).split(",")
    return topic, problems

def main():
    topic, problems = get_input()
    prompt = f"""
    You are a creative author.

    Create a 1500 word children's story about {topic}.
    The story should be engaging and fun to read.

    """


main()