### Imports

from dictionaryParser import *
from storyGenerator import *
from replace_synonyms import *
from synonymparser import *

def get_words(sentence, problems, previous_sentence, next_sentence):
    synonyms_dict = {}
    prompt = f"""
        Give 10 words that would make sense in the following blank space:
        
        {sentence}

        return only the 10 words separated by commas. Like this "word1,word2,word3,word4,word5"
        order the words so the best fit is first
    """
    response = query(prompt)
    words = response.split(",")
    words_dict = parse_and_process_words(sentence)
    print(words_dict)
    for problem in problems:
        for word in words:
            if word in words_dict[problem]:
                words.remove(word)
    if len(words) >0:
        synonyms_dict['___']= " " + words[0]
        updated_sentence = replace_words_in_story(sentence, synonyms_dict)
        return updated_sentence
    else:
        prompt = f"""
            Rewrite the following sentence to preserve the meaning and remove the blank space:

            here is the previous sentence for context: {previous_sentence}
            here is the sentence with the blank space: {sentence}
            here is the next sentence for context: {next_sentence}

            return only the new sentence or you will be DISQUALIFIED
        """
        response = query(prompt)
        word_dict = parse_and_process_words(response)

        #synonym
        synonyms_dict = synonymparser(word_dict, problems)

        #replace
        updated_sentence = replace_words_in_story(response, synonyms_dict)
        if '___' in updated_sentence:
            updated_sentence = get_words(updated_sentence, problems, previous_sentence, next_sentence)
        else:
            return updated_sentence




def sentence_check(story, problems):
    sentences = story.split(".")
    new_story = ""
    prev_sentence = sentences[0]
    for sentence in sentences:
        next_sentence = sentences[sentences.index(sentence) + 1] if sentences.index(sentence) < len(sentences) - 1 else ""
        if "___" in sentence:
            updated_sentence = get_words(sentence, problems, prev_sentence, next_sentence)
            new_story += updated_sentence + ". "
        else:
            new_story += sentence + ". "

        prev_sentence = sentence
    return new_story

def main():
    topic, problems = get_input()
    # Generate the intial story
    print("Generating story...")
    story = generate_story(topic, problems)
    print(story)
    # Sort the words with dictionary_parser to see whats good and whats bad
    print("Checking each word...")
    word_dict = parse_and_process_words(story)

    #synonym
    print("Finding synonyms...")
    synonyms_dict = synonymparser(word_dict, problems)

    #replace
    print("Replacing synonyms...")
    updated_story = replace_words_in_story(story, synonyms_dict)

    story = sentence_check(updated_story, problems)

    print("Saving updated story...")
    print(story)
    output_file = 'dictionary_parser\\updated_story.txt'
    save_updated_story(story, output_file)

if __name__ == "__main__":
    main()