import openai
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

story_length = 250

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

### Function to get all words
### This function takes no input and returns a list of words
def get_all_words():
    f = open("WordDatav4.txt", "r")
    words = f.read().split("\n")
    return words[:2000]

### Function to query GPT-3.5
### This function takes a prompt (string) as input and returns the response from GPT-3.5
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
### This function takes no input and returns the topic and problem letters as a tuple
def get_input():
    topic = input("Enter your story topic: ")
    problems =  (input("Enter the problem letters separated by commas: ")).split(",")
    return topic, problems

### Function to get words
### This function takes a list of problem letters (list of strings) as input and returns a list of words
def get_words(problems):
    words_list = set(words[problems[0]]) if problems else set()
    for problem in problems[1:]:
        words_list.update(words[problem])
    all_words = get_all_words()
    final_words = [word for word in all_words if word not in words_list]
   
    return list(final_words)

### Function to generate a story
### This function takes the topic (string), problems (list of strings), and dictionary (list of strings) as input and returns a story (string)
def generate_story(topic, problems, dictionary):
    prompt = f"""
    You are a creative author.

    This is your language:

    {dictionary}

    Create a {story_length} word children's story about {topic} using only the words in your pre-defined language.

    ONLY THESE WORDS ARE ALLOWED IN YOUR STORY:
    {dictionary}

    If you use any other words, you will be disqualified.

    DO NOT USE THE LETTERS {problems} IN YOUR STORY.
    
    DO NOT USE ANY OTHER WORDS.
    """
    story = query(prompt)
    return story

### Function to check sentences
### This function takes the story (string) and dictionary (list of strings) as input and returns a new story (string)
def sentence_check(story, dictionary):
    new_story = ""
    sentences = story.split(".")
    for i in range(len(sentences)):
        previous_sentence = sentences[i-1] + "." if i >0 else sentences[0] + "."
        next_sentence = sentences[i+1] + "." if i < len(sentences)-1 else sentences[i] + "."
        sentence = sentences[i] + "."
        prompt = f"""
        Verify that the following sentence only contains words from this language: {dictionary}

        If the sentence contains any other words, please rewrite the sentence using only the words from the language and return only the new sentence.
        Otherwise, return only the original sentence

        Here is the sentence to rewrite: {sentence}

        Here is the previous sentence for context: {previous_sentence}

        Here is the next sentence for context: {next_sentence}


        You will be disqualified if you return any words other than the new sentence or the original sentence.
        """
        response = query(prompt)
        #print(response)
        new_story += response
    return new_story

### Function to edit the story
### This function takes the story (string) as input and returns the edited story (string)
def edit(story):
    prompt = f"""
    Edit the following story.

    Make minial changes, only correct blatant errors.

    Make sure all sentences are coherent.

    Remove sentences that do not make sense or are irrelevant.

    Here is the story to edit: {story}

    Return only the story, no extra words.
    """
    response = query(prompt)
    return response

### Main function
def main():
    topic, problems = get_input()
    dictionary = get_words(problems)
    story = generate_story(topic, problems, dictionary)
    new_story = sentence_check(story, dictionary)
    new_story = edit(new_story)
    print(new_story)
    return 0

if __name__ == "__main__":
    main()
