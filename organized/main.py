### Imports

from dictionaryParser import *
from storyGenerator import *
from replace_synonyms import *
from synonymparser import *


def main():

    # Generate the intial story
    story = generate_story()

    # Sort the words with dictionary_parser to see whats good and whats bad
    word_dict = parse_and_process_words(story)

    #synonym

    #replace