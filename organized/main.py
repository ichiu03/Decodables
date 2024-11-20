### Imports

from dictionaryParser import *
from storyGenerator import *
from replace_synonyms import *
from synonymparser import *


def sentence_check(story, problems):
    sentences = story.split(".")
    new_story = ""
    prev_sentence = sentences[0]
    synonyms_dict = {}
    for sentence in sentences:
        next_sentence = sentences[sentences.index(sentence) + 1] if sentences.index(sentence) < len(sentences) - 1 else ""
        if "___" in sentence:
            prompt = f"""
                Give 5 words that would make sense in the following blank space:
                prevoius sentence: {prev_sentence}
                sentence to change: {sentence}
                next sentence: {next_sentence}
                return only the 5 words separated by commas. Like this "word1,word2,word3,word4,word5"
                order the words so the best fit is first
            """
            response = query(prompt)
            words = response.split(",")
            words_dict = parse_and_process_words(story)
            for problem in problems:
                for word in words:
                    if word in words_dict[problem]:
                        words.remove(word)
            if len(words) >0:
                synonyms_dict['___']= words[0]
            else:
                synonyms_dict['___'] = "___"
            updated_sentence = replace_words_in_story(sentence, synonyms_dict)
            new_story += updated_sentence
        else:
            new_story += sentence

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
    print(updated_story)
    output_file = 'dictionary_parser\\updated_story.txt'
    save_updated_story(updated_story, output_file)

if __name__ == "__main__":
    main()