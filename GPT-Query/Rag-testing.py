import openai
from openai import OpenAI
import os
import json

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

story_length = 1000
chapters = 3

good_words = []
bad_words = []

# Opening JSON file
with open('dictionary_parser\categorized_words.json') as json_file:
    words = json.load(json_file)

### Function to get all words
### This function takes no input and returns a list of words
def get_all_words():
    f = open("dictionary_parser\WordDatav4.txt", "r")
    words = f.read().split("\n")
    return words[:2000]

### Function to query GPT-3.5
### This function takes a prompt (string) as input and returns the response from GPT-3.5
def query(prompt): 
    messages = [
    {"role": "system", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
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
    global bad_words
    global good_words

    words_list = set(words[problems[0]]) if problems else set()
    for problem in problems[1:]:
        words_list.update(words[problem])
    all_words = get_all_words()
    bad_words = [word for word in all_words if word not in words_list]
    good_words = [word for word in all_words if word not in bad_words]
    return bad_words

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

### Function to generate a chapter
### This function takes the problems (string), outline (string), dictionary (list of strings), chapter_number (int), length (int), and story (string) as input and returns a chapter (string)
def generate_chapter(problems, outline, dictionary, chapter_number, length, story):
    prompt = f"""
    You are a creative author tasked with writing the {chapter_number} chapter of a children's story (age 10).

    Here is the outline:

    {outline}

    Here is the story so far:

    {story}


    Write a {length} word chapter.

    DO NOT USE WORDS WITH THESE SOUNDS: {problems}
    Here are examples of the bad words: {bad_words}
    

    If you use any words like this, you will be disqualified.

    DO NOT USE THE SOUNDS {problems} IN YOUR STORY.
    

    Return only the new chapter.
    """
    story = query(prompt)
    return story

### Function to check sentences
### This function takes the story (string) and dictionary (list of strings) as input and returns a new story (string)
def sentence_check(story, dictionary, problems):
    new_story = ""
    sentences = story.split(".")
    for i in range(len(sentences)):
        check = False
        remove_words = []
        for word in bad_words:
            if word in sentences[i]:
                check = True
                remove_words.append(word)
        for problem in problems:
            if problem in sentences[i]:
                check = True
        if check:
            previous_sentence = sentences[i-1] + "." if i >0 else sentences[0] + "."
            next_sentence = sentences[i+1] + "." if i < len(sentences)-1 else sentences[i] + "."
            sentence = sentences[i] + "."
            # Verify that the following sentence only contains words from this language: {dictionary}

            prompt = f"""
        
            Rewrite the following sentence and remove these words: {remove_words}

            Also remove any words with the following sounds: {problems}

            Rewrite the sentence without using these sounds: {problems} and return only the new sentence.

            Here is the sentence to rewrite: {sentence}

            Here is the previous sentence for context: {previous_sentence}

            Here is the next sentence for context: {next_sentence}

            REMOVE ALL WORDS WITH THESE SOUNDS: {problems}
            DO NOT USE THESE SOUNDS IN THE REWRITE

            You will be disqualified if you return any words other than the new sentence.
            """
            response = query(prompt)
            #print(response)
            new_story += response
        else:
            new_story += sentences[i] + "."
    return new_story

def word_check(story, dictionary, problems):
    new_story = ""
    sentences = story.split(".")
    
    for sentence in sentences:
        words = sentence.split(" ")
        bad_words = []
        for i in range(len(words)):
            check = False
            for problem in problems:
                for example in dictionary[problem]:
                    if example in words[i]:
                        check = True
                        bad_words.append(words[i])
            if check:
                
                # Verify that the following sentence only contains words from this language: {dictionary}

                prompt = f"""
                    Rewrite the following sentence and remove all instances of the following words: {bad_words}

                """
                response = query(prompt)
                #print(response)
                new_story += response
            else:
                new_story += words[i] + " "
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

### Function to generate an outline
### This function takes the topic (string) as input and returns an outline (string)
def generate_outline(topic):
    prompt = f"""
    You are a creative author.

    Create an outline for a children's story about {topic} (Age 10).

    The story should be about {story_length} words long.

    The story should have a clear beginning, middle, and end and have a lesson.

    The story should be {chapters}  chapters long.

    Return only the outline
    """
    outline = query(prompt)
    return outline

### Main function
def main():
    topic, problems = get_input()
    dictionary = get_words(problems)
    outline = generate_outline(topic)
    story =""
    for chapter in range(chapters):
        print(f"Generating chapter {chapter+1}")
        new_chapter = generate_chapter(problems, outline, dictionary, chapter+1, story_length//chapters, story)
        temp_chapter = new_chapter
        temp_chapter = sentence_check(new_chapter, dictionary, problems)
        temp_chapter = edit(temp_chapter)
        story += temp_chapter
    #story = generate_story(topic, problems, dictionary)
    print(story)
    return 0

if __name__ == "__main__":
    main()
