import re

def load_synonyms(synonyms_file):
    synonyms_dict = {}
    with open(synonyms_file, 'r', encoding='utf-8') as file:
        for line in file:
            original, synonym = line.strip().split(None, 1)
            synonyms_dict[original.lower()] = synonym.lower()
    return synonyms_dict

def read_story(story_file):
    with open(story_file, 'r', encoding='utf-8') as file:
        story = file.read()
    return story

def replace_words_in_story(story, synonyms_dict):
    # Tokenize with regex to catch words and punctuation separately
    tokens = re.findall(r'\b\w+\b|[^\w\s]', story, re.UNICODE)

    # Create a list to hold the updated tokens
    updated_tokens = []

    for token in tokens:
        # Strip punctuation from the word for synonym lookup, preserving original
        stripped_token = re.sub(r'[^\w\s]', '', token).lower()

        if stripped_token in synonyms_dict:
            # Replace with the synonym and preserve case
            synonym = synonyms_dict[stripped_token]
            if token[0].isupper():
                synonym = synonym.capitalize()
            updated_tokens.append(synonym)
        else:
            # Keep the original token if no replacement is needed
            updated_tokens.append(token)

    # Join tokens to form the final story
    updated_story = ''.join(
        (' ' if i > 0 and tokens[i - 1].isalnum() and token.isalnum() else '') + token
        for i, token in enumerate(updated_tokens)
    )
    return updated_story

def save_updated_story(updated_story, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(updated_story)
    print(f"Updated story has been saved to '{output_file}'.")

if __name__ == "__main__":
    synonyms_file = 'synonyms.txt'
    story_file = 'generated_story.txt'
    output_file = 'updated_story.txt'

    # Load synonyms
    synonyms_dict = load_synonyms(synonyms_file)

    # Read the original story
    story = read_story(story_file)

    # Replace problematic words with synonyms
    updated_story = replace_words_in_story(story, synonyms_dict)

    # Save the updated story
    save_updated_story(updated_story, output_file)
