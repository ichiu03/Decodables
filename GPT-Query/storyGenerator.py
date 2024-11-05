import openai
from openai import OpenAI
import json
import os
import re
import nltk
from nltk.corpus import words

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

client = OpenAI(
    api_key='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'
)

story_length = 200
chapters = 3

good_words = []
bad_words = []

# Opening JSON file
with open('dictionary_parser\\categorized_words.json') as json_file:
    words = json.load(json_file)

### Function to get all words
def get_all_words():
    with open("dictionary_parser\\WordDatav4.txt", "r") as f:
        words = f.read().split("\n")
    return words[:2000]

### Function to query GPT-3.5
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
def get_input():
    topic = input("Enter your story topic: ")
    problems = (input("Enter the problem letters separated by commas: ")).split(",")
    return topic, problems

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

### Function to write the story to a file as a list of words
### Function to write the story to a file with each word on a new line
import re

# Function to write the original and stripped-down versions of the story to separate files
def write_story_to_file(story):
    # Write the original story to 'generated_story.txt'
    with open('generated_story.txt', 'w', encoding='utf-8') as file:
        file.write(story)
    print("\nOriginal story written to 'generated_story.txt'.")

    # Tokenize the story using NLTK's word_tokenize
    words_list = nltk.word_tokenize(story)
    with open('output_words_list.txt', 'w', encoding='utf-8') as file:
        for word in words_list:
            # Remove punctuation and hidden characters from each word
            cleaned_word = re.sub(r'[^\w\s]', '', word).strip()
            if cleaned_word:
                file.write(f"{cleaned_word}\n")
    print("\nStripped-down story written to 'output_words_list.txt'.")
### Function to delete the file before generating a new one
### Function to delete the files before generating new ones
def delete_old_file():
    file_paths = ['output_words_list.txt', 'generated_story.txt']
    for path in file_paths:
        if os.path.exists(path):
            os.remove(path)
            print(f"Previous file '{path}' deleted.")


def generate_chapter(problems, outline, dictionary, chapter_number, length, story):
    prompt = f"""
    You are a creative author tasked with writing chapter {chapter_number} of a children's story (age 10).

    Here is the outline:

    {outline}

    Here is the story so far:

    {story}

    Write a {length} word chapter.

    Please ensure that you use proper punctuation and include spaces after punctuation marks.

    Return only the new chapter.
    """
    story = query(prompt)
    return story

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

def fix_spacing(text):
    # Insert a space after punctuation marks if not followed by a space
    text = re.sub(r'([.!?])([^\s])', r'\1 \2', text)
    return text

### Main function
def main():
    topic, problems = get_input()
    dictionary = get_words(problems)
    outline = generate_outline(topic)
    story = ""

    for chapter in range(chapters):
        print(f"Generating chapter {chapter + 1}")
        new_chapter = generate_chapter(problems, outline, dictionary, chapter + 1, story_length // chapters, story)
        temp_chapter = new_chapter
        temp_chapter = sentence_check(temp_chapter, dictionary, problems)
        temp_chapter = edit(temp_chapter)
        story += temp_chapter + " "  # Add a space between chapters

    # Fix missing spaces after punctuation
    story = fix_spacing(story)

    # Delete any existing output files only after the entire story is generated
    delete_old_file()

    # Write the final story to the file
    write_story_to_file(story)

    print("\nFinal story:")
    print(story)
    return 0


if __name__ == "__main__":
    main()
