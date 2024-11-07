import json
import os
import re
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import nltk

# Ensure necessary NLTK data packages are downloaded
nltk.download('wordnet')
nltk.download('omw-1.4')  # WordNet's extended data
nltk.download('stopwords')

# Load categorized words
with open('dictionary_parser\\categorized_words.json', 'r') as json_file:
    categorized_words = json.load(json_file)

stop_words = set(stopwords.words('english'))

def get_problem_sounds():
    problems = input("Enter the problem letters separated by commas: ").split(",")
    return [p.strip() for p in problems]

def is_appropriate_synonym(synonym, original_word, problems, all_problematic_words):
    # Exclude synonyms that contain problem sounds
    if any(problem in synonym for problem in problems):
        return False
    # Exclude synonyms that are the same as the original word
    if synonym.lower() == original_word.lower():
        return False
    # Exclude synonyms that are in the problematic words list
    if synonym.lower() in all_problematic_words:
        return False
    # Exclude multi-word synonyms (optional)
    if len(synonym.split()) > 2:  # Adjust as needed
        return False
    # Exclude stop words
    if synonym.lower() in stop_words:
        return False
    # Exclude words with non-alphabetic characters
    if not synonym.isalpha():
        return False
    return True

def find_and_record_synonyms(problems):
    all_problem_words = set()

    # Collect all words from the arrays related to the problem sounds
    for problem in problems:
        if problem in categorized_words:
            all_problem_words.update(categorized_words[problem])
        else:
            print(f"Problem sound '{problem}' not found in categorized_words.json")

    # Collect all words from all problematic arrays to avoid using their synonyms
    all_problematic_words = set()
    for problem_sound in categorized_words:
        if problem_sound in problems:
            all_problematic_words.update([w.lower() for w in categorized_words[problem_sound]])

    synonyms_dict = {}
    for word in all_problem_words:
        appropriate_synonyms = set()
        original_word = word.strip()
        word_lower = original_word.lower()

        # Get the POS tags for the original word
        word_synsets = wordnet.synsets(word_lower)
        if not word_synsets:
            continue  # Skip words not found in WordNet

        # Collect POS tags of the original word
        original_pos_list = set(syn.pos() for syn in word_synsets)

        for synset in word_synsets:
            # Ensure the synonym is the same POS as the original word
            syn_pos = synset.pos()
            if syn_pos not in original_pos_list:
                continue

            for lemma in synset.lemmas():
                synonym = lemma.name().replace('_', ' ').lower()
                # Check if the synonym is appropriate
                if is_appropriate_synonym(synonym, original_word, problems, all_problematic_words):
                    appropriate_synonyms.add(synonym)

        if appropriate_synonyms:
            # Save the first acceptable synonym
            synonyms_dict[original_word] = appropriate_synonyms

    # Write the results to synonyms.txt
    with open('synonyms.txt', 'w', encoding='utf-8') as file:
        for word, synonyms in synonyms_dict.items():
            # Get the first acceptable synonym
            synonym = next(iter(synonyms))
            file.write(f"{word} {synonym}\n")

    print("Synonyms have been written to 'synonyms.txt'.")

if __name__ == "__main__":
    problems = get_problem_sounds()
    find_and_record_synonyms(problems)
