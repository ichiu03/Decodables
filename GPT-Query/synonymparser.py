import json
import os
from nltk.corpus import wordnet
import openai
from openai import OpenAI

client = OpenAI(
    api_key='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'
)


# Load categorized words
with open('dictionary_parser\\categorized_words.json', 'r', encoding='utf-8') as json_file:
    categorized_words = json.load(json_file)

# Load problem sounds (categories) to gather words from
with open('dictionary_parser\\problemsounds.json', 'r') as json_file:
    categories = json.load(json_file)

# Function to gather words from specified categories
def gather_words_from_categories(categorized_words, categories):
    gathered_words = []

    for category in categories.get('problems', []):  # Ensure we access the 'problems' key in the JSON
        if category in categorized_words:
            gathered_words.extend(categorized_words[category])

    # Remove duplicates and filter out any empty strings if needed
    gathered_words = list(set(filter(None, gathered_words)))

    return gathered_words


# Function to find a synonym for a word
def find_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            # Exclude the original word from the synonyms list
            if lemma.name().lower() != word.lower():
                synonyms.add(lemma.name().lower())
    return synonyms if synonyms else None  # Return all synonyms if available


def query(prompt): 
    messages = [
        {"role": "system", "content": prompt},
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    return response.choices[0].message.content

# Function to write words and their synonyms to a text file
# Function to write words and their synonyms to a text file
def write_words_with_synonyms(gathered_words, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        for word in gathered_words:
            synonyms = find_synonyms(word)
            if synonyms:
                # Convert the set to a list for JSON serialization
                synonyms_list = list(synonyms)
                message = f"Which one of these synonyms is most similar to '{word}': {synonyms_list}. Respond with just the word."
                synonym = query(message)
                if synonym:
                    file.write(f"{word} {synonym}\n")
                else:
                    file.write(f"{word} ____\n")
            else:
                file.write(f"{word} ____\n")

    print(f"Words and their synonyms have been saved to '{output_path}'")

# Main function to execute the entire process
def main():
    # Gather words from specified categories
    gathered_words = gather_words_from_categories(categorized_words, categories)
    
    # Path for the output file
    output_path = 'dictionary_parser\\word_synonyms.txt'
    
    # Write words and their synonyms to the text file
    write_words_with_synonyms(gathered_words, output_path)

# Run the main function
if __name__ == "__main__":
    main()

