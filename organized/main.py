### Imports

from dictionaryParser import *
from storyGenerator import *
from replace_synonyms import *
from synonymparser import *

with open('dictionary_parser\\dictionary.txt', 'r', encoding='utf-8') as file:
    large_dictionary = set(word.strip().lower() for word in file.readlines())


def get_words(sentence, problems, word_dict, previous_sentence, next_sentence):
    words = sentence.split(" ")
    bad_words = []
    for word in words:
        for problem in problems:
            if word in word_dict[problem]: #or word not in large_dictionary:
                bad_words.append(word)
    if len(bad_words) == 0:
        return None
    synonyms_dict = {}
    print("sentence: " + sentence)
    words = []
    for word in bad_words:
        prompt = f"""
            Give 5 words that would make sense as replacements for the following word in the sentence:
            word: {word}
            
            sentence: {sentence}

            return only the 5 words separated by commas. Like this "word1,word2,word3,word4,word5"
            order the words so the best fit is first
        """
        response = query(prompt)
        temp_words = response.split(",")
        words.extend(temp_words)

    words_dict = parse_and_process_words(sentence)
    blanks = len(words)//5
    words_blanks = [words[i:i+blanks] for i in range(0, len(words), blanks)]
    for problem in problems:
        for i in range(len(words_blanks)):
            for word in words_blanks[i]:
                if word in words_dict[problem] or word not in large_dictionary:
                    words.remove(word)
    for i in range(len(words_blanks)):
        if len(words_blanks[i]) >0:
            synonyms_dict[bad_words[i]]= " " + words_blanks[i][0] + " "
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

            # #replace
            # updated_sentence = replace_words_in_story(response, synonyms_dict)
            # print('Updated Sentence: '+ updated_sentence)
            # if '___' in updated_sentence:
            #     updated_sentence = get_words(updated_sentence, problems, previous_sentence, next_sentence)
            # else:
            #     return updated_sentence

        #### change to return synonyms_dict only#####
        # print(f"synonyms dict: {synonyms_dict}")
        # updated_sentence = replace_words_in_story(sentence, synonyms_dict)
        # return updated_sentence
        return synonyms_dict

def get_synonyms_dict(story, word_dict, problems):
    sentences = story.split(".")
    prev_sentence = sentences[0]
    synonyms_dict = {}
    for sentence in sentences:
        next_sentence = sentences[sentences.index(sentence) + 1] if sentences.index(sentence) < len(sentences) - 1 else ""
        words = sentence.split(" ")
        for word in words:
            for problem in problems:
                if word in word_dict[problem] and word not in sight_words:
                    print(f"bad word: {word}")
                    prompt = f"""
                        Give 5 words that would make sense as replacements for the following word in the sentence:

                        word: {word}
                        previous sentence (for context): {prev_sentence}
                        sentence to fix: {sentence}
                        next sentence (for context): {next_sentence}

                        return only the 5 words separated by commas. Like this "word1,word2,word3,word4,word5"
                        order the words so the best fit is first
                        """
                    response = query(prompt)
                    temp_words = response.split(",")
                    temp_words_dict = parse_and_process_words(response)
                    for temp_word in temp_words:
                        for problem in problems:
                            if temp_word in temp_words_dict[problem]:# or word not in large_dictionary:
                                temp_words.remove(temp_word)
                                print(f"CAUGHT {temp_word}")
                                break
                    if len(temp_words) > 0:
                        print(f"good word: {temp_words[0]}")
                        synonyms_dict[word] = " " + temp_words[0]
                    else:
                        synonyms_dict[word] = " ___"
                    break
        prev_sentence = sentence
    return synonyms_dict
    # print(f"synonyms dict: {synonyms_dict}")
    # return synonyms_dict

def sentence_check(story, problems):
    sentences = story.split(".")
    new_story = ""
    prev_sentence = sentences[0]
    for sentence in sentences:
        next_sentence = sentences[sentences.index(sentence) + 1] if sentences.index(sentence) < len(sentences) - 1 else ""
        if "___" in sentence:
            synonyms_dict = get_words(sentence, problems, prev_sentence, next_sentence)
            updated_sentence = replace_words_in_story(sentence, synonyms_dict)
            print('Updated Sentence: '+ updated_sentence)
            if '___' in updated_sentence:
                updated_sentence = get_words(updated_sentence, problems, prev_sentence, next_sentence)
            else:
                return updated_sentence
            new_story += updated_sentence + ". "
        else:
            new_story += sentence + ". "

        prev_sentence = sentence
    return new_story



def main():
    topic, problems = get_input()
    global sight_words
    sight_words = "his,she,the,they,that,is,was,to,their,has,them,then,than,with,and,of,for,as,at,by,an,or,if,be,are,not,from,have,when,where,what,how,why,who,which,will,can,do,does,done,doing"
    # Generate the intial story
    print("Generating story...")
    story = generate_story(topic, problems)
    print(story)
    # Sort the words with dictionary_parser to see whats good and whats bad
    print("Checking each word...")
    word_dict = parse_and_process_words(story)
    print(word_dict)
    #synonym
    print("Finding synonyms...")
    # synonyms_dict = synonymparser(word_dict, problems)
    synonyms_dict = get_synonyms_dict(story, word_dict, problems)

    #replace
    print("Replacing synonyms...")
    story = replace_words_in_story(story, synonyms_dict)

    # story = sentence_check(updated_story, problems)

    print("Saving updated story...")
    print(story)

    global categories
    categories = {
        # Column 1 - Consonant Sounds
        "s": [], "t": [], "b": [], "m": [], "l": [], "d": [], "n": [], "p": [], "k": [], "j": [], "v": [],
        "z": [], "f": [], "hard c": [], "hard g": [], "r": [], "h": [], "w": [], "x": [], "y as in yes": [],
        # Column 2 - All vowels (short & long)
        "long a": [], "short a": [], "long i": [], "short i": [], "long o": [], "short o": [],
        "long u": [], "short u": [], "long e": [], "short e": [],
        # Column 3 
        "fszl": [], "qu": [], "sh": [], "ay": [], "ck": [], "ee": [], "ch": [], "or": [], "s blends": [],
        "l blends": [], "r blends": [], "-ing, -ong, -ang, -ung": [], "all": [], "th": [], "oy": [],
        "-ink, -ank, -onk, -unk": [], "-ft, -nd, -st": [], "-sp, -nt, -mp": [], "-sk, -lt, -lk": [], "-ct, -pt": [],
        "y as in dry": [], "ar": [], "wh": [], "oo as in school": [], "oo as in book": [], "vce": [],
        "er": [], "ow as in plow": [], "ow as in snow": [], "vccv": [], "Open syll.": [], "Closed syll.": [], "contractions": [], 
        # Column 4
        "ear as in hear": [], "ear as in early": [], "y as in bumpy": [], "aw": [], "ly": [], "ea as in eat": [],
        "ea as in bread": [], "3-letter beg. blends": [], "vcv, vcccv patterns": [], "tch": [], "soft c": [], 
        "soft g": [], "ai": [], "igh": [], "ed": [], "-ble, -cle, -dle, -fle, -gle, -kle, -ple, -tle, -zle": [],
        "l syllables": [],"v syllables": [], "r syllables": [], "oa": [], "ir": [], "-ild, -ind, -old, -ost": [], "oi": [], "double rule-suffixes": [],
        "ew as in few/blew": [], "v/v pattern": [], "kn": [], "e rule-suffixes": [], "ou as in south": [], "ur": [],
        "dge": [], "y rule suffixes": [], "tion": [], "begin/interm affixes": [], "base/suffix, prefix/base patterns": [], 
        # Column 5
        "au": [], "war": [], "ey as in monkey": [], "ey as in they": [],  "interm./adv. affixes": [], "ph": [],
        "ie as in pie": [], "ie as in thief": [], "beginning roots": [], "-sion as in tension": [], "-sion as in vision" : [],
        "y as in gym": [], "wr": [], "eigh": [], "ue as in blue": [], "ough": [], "wor": [], "ei as in receive": [],
        "ei as in vein": [], "augh": [], "oe": [], "ui": [], "ch as in echo": [], "wa": [], "eu": [], "gh": [], "mb": [],
        "mn": [], "que": [], "gn": [], "stle": [],"rh": [], "gue": [], "alk": [], "alt": [], "qua": [], "sc": [], "2 syllable dblg.": [],     
        # Uncategorized
        "fail": [],
        "sight words": ['a', 'any', 'many', 'and', 'on', 'is', 'are', 'the', 'was', 'were', 'it', 'am', 'be', 'go', 'to', 'been', 'come', 'some', 'do', 'does', 'done', 'what', 'who', 'you', 'your', 'both', 'buy', 'door', 'floor', 'four', 'none', 'once', 'one', 'only', 'pull', 'push', 'sure', 'talk', 'walk', 'their', 'there', "they're", 'very', 'want', 'again', 'against', 'always', 'among', 'busy', 'could', 'should', 'would', 'enough', 'rough', 'tough', 'friend', 'move', 'prove', 'ocean', 'people', 'she', 'other', 'above', 'father', 'usually', 'special', 'front', 'thought', 'he', 'we', 'they', 'nothing', 'learned', 'toward', 'put', 'hour', 'beautiful', 'whole', 'trouble', 'of', 'off', 'use', 'have', 'our', 'say', 'make', 'take', 'see', 'think', 'look', 'give', 'how', 'ask', 'boy', 'girl', 'us', 'him', 'his', 'her', 'by', 'where', 'were', 'wear', 'hers', "don't", 'which', 'just', 'know', 'into', 'good', 'other', 'than', 'then', 'now', 'even', 'also', 'after', 'know', 'because', 'most', 'day', 'these', 'two', 'already', 'through', 'though', 'like', 'said', 'too', 'has', 'in', 'brother', 'sister', 'that', 'them', 'from', 'for', 'with', 'doing', 'well', 'before', 'tonight', 'down', 'about', 'but', 'up', 'around', 'goes', 'gone', 'build', 'built', 'cough', 'lose', 'loose', 'truth', 'daughter', 'son']
    }
    word_dict = parse_and_process_words(story)
    for problem in problems:
        print(f"problem: {problem}")
        bads = [i for i in word_dict[problem] if i not in sight_words and i in story]
        print(f"bads: {bads}")
    
    output_file = 'dictionary_parser\\updated_story.txt'
    save_updated_story(story, output_file)

if __name__ == "__main__":
    main()


#b,l,p,j,ck,wh,aw,tch,igh,ir,oi

#wh,aw,tch,igh,ir,oi,kn,ur,dge,tion,war,ph,eigh,wor,ough