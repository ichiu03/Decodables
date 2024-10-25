import openai
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

words = {
    'sh': [
        "a", "an", "be", "can", "do", "go", "is", "it", "me", "my", "no", "of", "on", "or", "so", 
    "to", "up", "we", "and", "cat", "dog", "man", "sun", "sea", "day", "big", "run", "see", 
    "say", "play", "ride", "work", "jump", "red", "blue", "green", "long", "warm", "cool", 
    "happy", "sad", "sing", "song", "bird", "find", "call", "ask", "fast", "near", "far", 
    "all", "any", "one", "two", "old", "new", "use", "care", "kind", "hard", "soft", "make",
    "see", "like", "love", "give", "yes", "no", "good", "bad", "may", "fall", "say", "tell",
    "few", "many", "high", "low", "who", "whom", "why", "ask", "put", "take", "left", "right",
    "home", "life", "joy", "rain", "dry", "snow", "end", "goal", "hope", "king", "queen",
    "land", "sky", "star", "moon", "plan", "near", "row"
    ],
    'ch': [
        'bird', 'fox', 'lamp', 'stone', 'grape', 'mud', 'kite', 'rain', 'book', 'swim',
        'dark', 'fish', 'blue', 'gold', 'milk', 'fork', 'tap', 'pen', 'light', 'moon',
        'mask', 'farm', 'soap', 'mop', 'rod', 'bed', 'hat', 'lane', 'sail', 'pond',
        'goal', 'rim', 'dart', 'pint', 'flag', 'worm', 'mist', 'barn', 'golf', 'bond',
        'do', 'go', 'he', 'me', 'we', 'she', 'my', 'not', 'are', 'was', 'am', 'has'
    ],
    'th': [
        "a", "an", "be", "can", "do", "go", "is", "it", "me", "my", "no", "of", "on", "or", "so", 
    "to", "up", "we", "and", "cat", "dog", "man", "sun", "sea", "day", "big", "run", "see", 
    "say", "play", "ride", "work", "jump", "red", "blue", "green", "long", "warm", "cool", 
    "happy", "sad", "sing", "song", "bird", "fish", "call", "ask", "fast", "near", "far", 
    "all", "any", "one", "two", "old", "new", "use", "care", "kind", "hard", "soft", "make",
    "see", "like", "love", "give", "yes", "no", "good", "bad", "may", "find", "say", "tell",
    "few", "many", "high", "low", "who", "whom", "why", "ask", "put", "take", "left", "right",
    "home", "life", "joy", "rain", "dry", "snow", "fall", "cool", "cook", "near", "far", "king",
    "queen", "land", "sky", "star", "moon", "plan", "row", "end", "goal", "hope"
    ],
    'wh': [
        'lamp', 'kite', 'rope', 'blue', 'map', 'dog', 'bird', 'pen', 'mud', 'cage',
        'milk', 'fox', 'fish', 'tap', 'fork', 'gold', 'rain', 'mop', 'dark', 'pond',
        'bed', 'mask', 'rod', 'farm', 'bag', 'light', 'hat', 'sail', 'lap', 'dart',
        'rim', 'fog', 'jog', 'cup', 'golf', 'flag', 'corn', 'bond', 'bell', 'mist',
        'be', 'is', 'it', 'do', 'go', 'he', 'she', 'we', 'me', 'not', 'are', 'has'
    ],
    'ph': [
        'bird', 'lamp', 'map', 'kite', 'fox', 'gold', 'mud', 'rope', 'milk', 'pond',
        'blue', 'dark', 'rain', 'bag', 'cage', 'pen', 'tap', 'mop', 'bed', 'mask',
        'farm', 'hat', 'lane', 'fish', 'fork', 'lap', 'door', 'rod', 'sail', 'light',
        'bond', 'rim', 'goal', 'dart', 'cup', 'bell', 'flag', 'corn', 'mist', 'jog',
        'is', 'it', 'of', 'as', 'do', 'go', 'we', 'he', 'she', 'me', 'not', 'was'
    ],
    'gh': [
        'lamp', 'kite', 'map', 'rope', 'mud', 'gold', 'bird', 'fish', 'rain', 'fork',
        'tap', 'milk', 'pen', 'fox', 'bag', 'bed', 'pond', 'cage', 'blue', 'mask',
        'farm', 'hat', 'lane', 'sail', 'rod', 'light', 'mop', 'door', 'lap', 'dart',
        'rim', 'goal', 'cup', 'bond', 'bell', 'flag', 'corn', 'mist', 'jog', 'wing',
        'be', 'is', 'of', 'to', 'do', 'go', 'he', 'we', 'she', 'me', 'not', 'are'
    ],
    'kn': [
        'fox', 'lamp', 'mud', 'map', 'gold', 'kite', 'rope', 'milk', 'pond', 'rain',
        'cage', 'bed', 'hat', 'bag', 'rod', 'dark', 'fork', 'blue', 'tap', 'farm',
        'fish', 'mask', 'mop', 'bird', 'light', 'sail', 'door', 'pen', 'lane', 'lap',
        'dart', 'rim', 'cup', 'goal', 'bell', 'flag', 'corn', 'bond', 'mist', 'jog',
        'be', 'is', 'do', 'go', 'we', 'he', 'she', 'me', 'not', 'was', 'are', 'has'
    ],
    'wr': [
        'lamp', 'map', 'mud', 'kite', 'rope', 'gold', 'bird', 'rain', 'milk', 'fox',
        'bag', 'pond', 'tap', 'cage', 'bed', 'dark', 'mask', 'farm', 'hat', 'sail',
        'mop', 'fish', 'pen', 'fork', 'light', 'rod', 'blue', 'lane', 'lap', 'dart',
        'rim', 'cup', 'goal', 'bond', 'bell', 'flag', 'corn', 'mist', 'jog', 'wing',
        'is', 'of', 'as', 'to', 'do', 'go', 'he', 'we', 'she', 'me', 'not', 'are'
    ],
    's': [
        "a", "an", "be", "can", "do", "go", "it", "me", "my", "no", "of", "on", "or", "to", 
        "up", "we", "and", "cat", "dog", "man", "day", "big", "run", "play", "ride", "work", 
        "jump", "red", "blue", "green", "long", "warm", "cool", "happy", "bad", "find", "call", 
        "near", "far", "all", "any", "one", "two", "old", "new", "make", "like", "love", "give", 
        "good", "may", "tell", "few", "many", "high", "low", "who", "whom", "why", "put", "take", 
        "left", "right", "home", "life", "joy", "rain", "dry", "fall", "end", "goal", "hope", 
        "king", "queen", "land", "moon", "plan", "row"
    ]

}

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

def get_words(problems):
    words_list = set(words[problems[0]]) if problems else set()
    for problem in problems[1:]:
        words_list.intersection_update(words[problem])
    return list(words_list)

def main():
    topic, problems = get_input()
    dictionary = get_words(problems)
    prompt = f"""
    You are a creative author.

    This is your language:

    {dictionary}

    Create a 500 word children's story using only the words in your pre-defined language.

    ONLY THESE WORDS {dictionary} ARE ALLOWED IN YOUR STORY

    If you use any other words, you will be disqualified.

    DO NOT USE THE LETTERS {problems} IN YOUR STORY.
    
    DO NOT USE ANY OTHER WORDS.
    """
    story = query(prompt)
    print(story)

    return 0
main()
