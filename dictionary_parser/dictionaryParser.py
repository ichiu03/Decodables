import json
import pronouncing
import os
import re
import nltk
import syllapy
from nltk.corpus import words

# Get the directory where `dictionaryParser.py` is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure the script checks locally for nltk_data
os.environ['NLTK_DATA'] = os.path.expanduser('~/nltk_data')

# Check if 'words' is already downloaded
try:
    # Try to access the words corpus
    valid_words = set(words.words())
except LookupError:
    # If it’s not available, attempt to download it
    print("Downloading 'words' corpus...")
    nltk.download('words')

categories = {
    # Column 1 - Consonant Sounds
    "s": [], "t": [], "b": [], "m": [], "l": [], "d": [], "n": [], "p": [], "k": [], "j": [], "v": [],
    "z": [], "f": [], "hard c": [], "hard g": [], "r": [], "h": [], "w": [], "x": [], "y as in yes": [],
    # Column 2 - All vowels (short & long)
    "a": [], "i": [], "o": [], "u": [], "e": [],
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
    "sight words": ['a','an', 'any', 'many', 'and', 'on', 'is', 'are', 'the', 'was', 'were', 'it', 'am', 'be', 'go', 'to', 'been', 'come', 'some', 'do', 'does', 'done', 'what', 'who', 'you', 'your', 'both', 'buy', 'door', 'floor', 'four', 'none', 'once', 'one', 'only', 'pull', 'push', 'sure', 'talk', 'walk', 'their', 'there', "they're", 'very', 'want', 'again', 'against', 'always', 'among', 'busy', 'could', 'should', 'would', 'enough', 'rough', 'tough', 'friend', 'move', 'prove', 'ocean', 'people', 'she', 'other', 'above', 'father', 'usually', 'special', 'front', 'thought', 'he', 'we', 'they', 'nothing', 'learned', 'toward', 'put', 'hour', 'beautiful', 'whole', 'trouble', 'of', 'off', 'use', 'have', 'our', 'say', 'make', 'take', 'see', 'think', 'look', 'give', 'how', 'ask', 'boy', 'girl', 'us', 'him', 'his', 'her', 'by', 'where', 'were', 'wear', 'hers', "don't", 'which', 'just', 'know', 'into', 'good', 'other', 'than', 'then', 'now', 'even', 'also', 'after', 'know', 'because', 'most', 'day', 'these', 'two', 'already', 'through', 'though', 'like', 'said', 'too', 'has', 'in', 'brother', 'sister', 'that', 'them', 'from', 'for', 'with', 'doing', 'well', 'before', 'tonight', 'down', 'about', 'but', 'up', 'around', 'goes', 'gone', 'build', 'built', 'cough', 'lose', 'loose', 'truth', 'daughter', 'son']
}
vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"
begin_intermediate_prefixes = ["re", "de", "sub", "pre", "com", "con", "pro", "ex", "be", "dis"]
begin_intermediate_suffixes = ["ful", "est", "ish", "less", "ness", "ling", "dom", "ic", "et", "en"]
intermediate_advanced_affixes = ["inter", "multi", "anti", "contra", "pseudo", "ology", "tion", "phobia"]
roots = ["port", "ject", "tract", "mit", "miss", "ceit", "ceive", "struct", "fact", "form", "spect", 
         "dict", "duct", "script", "rupt", "flect", "flex", "vert", "vers", "pel", "puls", "vis", "vid", "cap", "cept"]

def is_valid_presuf(wordbase):
    
    if len(wordbase) < 3:
        return False
    vowels = "aeiou"
    if not any(char in vowels for char in wordbase.lower()):
        return False
    if wordbase.lower() in valid_words:
        return True

    # Handle 'i' to 'y' change (e.g., 'beauti' -> 'beauty')
    if wordbase.endswith('i'):
        modified_word = wordbase[:-1] + 'y'
        if modified_word.lower() in valid_words:
            return True

    # Handle silent 'e' addition (e.g., 'hop' -> 'hope')
    modified_word = wordbase + 'e'
    if modified_word.lower() in valid_words:
        return True

    # Handle doubling consonants (e.g., 'begin' -> 'beginning')
    if len(wordbase) >= 3 and wordbase[-1] == wordbase[-2]:
        modified_word = wordbase[:-1]
        if modified_word.lower() in valid_words:
            return True

    # Handle 'ie' to 'y' change (e.g., 'dy' -> 'die')
    if wordbase.endswith('y') and len(wordbase) >= 2:
        modified_word = wordbase[:-1] + 'ie'
        if modified_word.lower() in valid_words:
            return True

    # Try replacing the last vowel with other vowels
    if wordbase[-1] in vowels:
        for vowel in vowels:
            if vowel != wordbase[-1]:
                modified_word = wordbase[:-1] + vowel
                if modified_word.lower() in valid_words:
                    return True

    return False
def x_in_word_check(word):
    keys = ["s", "t", "b", "m", "l", "d", "n", "p", "k", "j", "v", "z", "f", "r", "h", "w", "x",
        "a", "e", "i", "o", "u", "qu", "sh", "ay", "ck", "ee", "ch", "or", "all", "th", "oy", "ar", 
        "wh", "er", "aw", "ly", "tch", "ed", "ai", "igh", "oa", "ir", "oi", "kn", "ur",
        "dge", "tion", "au", "ough", "wor", "wr", "eigh", "augh", "oe", "ui", "wa", "eu", "gh",
        "mb", "mn", "que", "gn", "stle", "rh", "gue", "alk", "alt", "qua", "sc", "ph"]

    if "ing" in word or "ang" in word or "ong" in word or "ung" in word:
        categories["-ing, -ong, -ang, -ung"].append(word)

    if "ink" in word or "ank" in word or "onk" in word or "unk" in word: 
        categories["-ink, -ank, -onk, -unk"].append(word)
    
    if word.endswith("ft") or word.endswith("st") or word.endswith("nd"):
        categories["-ft, -nd, -st"].append(word)
    
    if word.endswith("sp") or word.endswith("nt") or word.endswith("mp"):
        categories["-sp, -nt, -mp"].append(word)

    if word.endswith("sk") or word.endswith("lt") or word.endswith("lk"):
        categories["-sk, -lt, -lk"].append(word)

    if word.endswith("ct") or word.endswith("pt"):
        categories["-ct, -pt"].append(word)
        
    if ("ble" in word or "cle" in word or "dle" in word or "fle" in word or "gle" in word 
          or "kle" in word or "ple" in word or "tle" in word or "zle" in word):
         categories["-ble, -cle, -dle, -fle, -gle, -kle, -ple, -tle, -zle"].append(word)
         
    if "ild" in word or "ind" in word or "old" in word or "ost" in word:
        categories["-ild, -ind, -old, -ost"].append(word)

    for key in keys:
        if key in word:
            categories[key].append(word)

def warCheck(word):
    if "war" in word and "ware" not in word:
        categories["war"].append(word)

def yCheck(word, arpabet):    
    # "y as in yes" (initial /Y/ sound or /JH/ sound)
    if arpabet.startswith("Y") or arpabet.startswith("JH"):
        categories["y as in yes"].append(word)
    # "y as in dry" (long "i" sound, represented by "AY1" in ARPAbet)
    if "AY1" in arpabet:
        categories["y as in dry"].append(word)
    # "y as in bumpy" (unstressed "IY0" sound in ARPAbet)
    elif "IY0" in arpabet:
        categories["y as in bumpy"].append(word)
    # "y in gym" (short "i" sound, "IH1" in ARPAbet)
    if "IH1" in arpabet:
        categories["y as in gym"].append(word) 
    # "-ey as in monkey" (ending with unstressed "IY0")
    if arpabet.endswith("IY0") and word.endswith("ey"):
        categories["ey as in monkey"].append(word)
    # "ey as in they" (long "EY1" sound)
    elif "EY1" in arpabet:
        categories["ey as in they"].append(word)

def hard_vs_soft_C(word, arpabet):
    if "K" in arpabet: # Hard C
        categories["hard c"].append(word)

    elif "S" in arpabet: # Soft C
        categories["soft c"].append(word)

def hard_vs_soft_G(word, arpabet):
    if "G" in arpabet: # Hard C
        categories["hard g"].append(word)

        
    elif "JH" in arpabet: # Soft C
        categories["soft g"].append(word)

def oo_check(word, arpabet):
    if "UW" in arpabet:
        categories["oo as in school"].append(word)

    if "UH" in arpabet:
        categories["oo as in book"].append(word)

def ow_check(word, arpabet):
    if "AW" in arpabet:
        categories["ow as in plow"].append(word)

    if "OW" in arpabet:
        categories["ow as in snow"].append(word)

def ear_check(word, arpabet):
    if "IH" in arpabet and "R" in arpabet or "IY" in arpabet and "R" in arpabet:
        categories["ear as in hear"].append(word)
    elif "ER" in arpabet:
        categories["ear as in early"].append(word)

def s_blends(word):
    if ("sn" in word or "sm" in word or "st" in word or "sw" in word or "sc" in word or "sp" in word):
        categories["s blends"].append(word)
    
def l_blends(word):
    if ("bl" in word or "cl" in word or "fl" in word or "pl" in word or "gl" in word or "sl" in word):
        categories["l blends"].append(word)

def r_blends(word):
    if ("br" in word or "cr" in word or "dr" in word or "fr" in word or "gr" in word or "pr" in word or "tr" in word):
        categories["r blends"].append(word)

def ea_check(word, arpabet):
    if "IY" in arpabet:
        categories["ea as in eat"].append(word)
    if "EH" in arpabet:
        categories["ea as in bread"].append(word)

def vce_check(word):
    for i in range(len(word) - 2):
        if (word[i].lower() in vowels and
            word[i + 1].lower() in consonants and
            word[i + 2].lower() == 'e'):
            categories["vce"].append(word)
        
def OCE_check(word, arpabet):
    phonemes = arpabet.split()
    # Open syllables (ends in hard vowel)
    if word[-1] in vowels and len(word) > 1:
        if not(word[-1] == "e" and "IY" not in phonemes[-1]):
            categories["Open syll."].append(word)
    # Closed syllables (eg cat, man)
    for i in range(len(word) - 1):
        if word[i] in vowels and word[i + 1].lower() not in vowels:
            categories["Closed syll."].append(word)
            return
        
def ew_check(word, arpabet):
    if "UW" in arpabet:
        categories["ew as in few/blew"].append(word)

def ou_check(word, arpabet):
    if "AW" in arpabet:
        categories["ou as in south"].append(word)

def ue_check(word, arpabet):
    if "UW" in arpabet:
        categories["ue as in blue"].append(word)

def ei_check(word, arpabet):
    if "IY" in arpabet:
        categories["ei as in receive"].append(word)
    elif "EY" in arpabet:
        categories["ei as in vein"].append(word)

def ch_check(word, arpabet):
    ch_index = word.find("ch")
    if ch_index != -1:
        phonemes = arpabet.split()
        try:
            if phonemes[ch_index] == "K":
                categories["ch as in echo"].append(word)
        except IndexError:
            pass

def augh_check(word, arpabet):
    if "AA" in arpabet or "AO" in arpabet or "AH" in arpabet:
        categories["augh"].append(word)

def ough_check(word, arpabet):
    if "AA" in arpabet or "AO" in arpabet or "AH" in arpabet:
        categories["ough"].append(word)

def ie_check(word, arpabet):
    if "AY" in arpabet:
        categories["ie as in pie"].append(word)

    elif "IY" in arpabet:
        categories["ie as in thief"].append(word)

def sion_check(word, arpabet):
    if "SH" in arpabet:
        categories["-sion as in tension"].append(word)

    elif "ZH" in arpabet:
        categories["-sion as in vision"].append(word)

def threel_blends(word):
    if (word.startswith("spr") or word.startswith("spl") or word.startswith("thr") or word.startswith("scr") or word.startswith("squ") or word.startswith("shr") or word.startswith("str")):
        categories["3-letter beg. blends"].append(word)

def vccv(word):
    for i in range(len(word) - 3):
        if (word[i] in vowels and word[i+1] in consonants and 
            word[i+2] in consonants and word[i+3] in vowels):
            categories["vccv"].append(word)

def vcv(word):
    for i in range(len(word) - 2):  # Iterate through the word for 3-letter patterns
        if (word[i] in vowels and word[i+1] in consonants and word[i+2] in vowels):
            categories["vcv, vcccv patterns"].append(word)

def vcccv(word):
    for i in range(len(word) - 4):  # Iterate through the word for 5-letter patterns
        if (word[i] in vowels and word[i+1] in consonants and 
            word[i+2] in consonants and word[i+3] in consonants and 
            word[i+4] in vowels):
            categories["vcv, vcccv patterns"].append(word)

def vrl_check(word):
    for r in ["ar", "er", "ir", "or", "ur"]:
        if r in word:
            categories["r syllables"].append(word)
            break 
    for l in ["ol", "al", "ul", "el", "il"]:
        if l in word:
            categories["l syllables"].append(word)
            break  
    for v in ["iv", "av", "ov", "uv", "ev"]:
        if v in word:
            categories["v syllables"].append(word)
            break  

def vv_check(word, arpabet):
    arpabet_tokens = arpabet.split()
    consecutive_vowels = any(word[i] in vowels and word[i + 1] in vowels for i in range(len(word) - 1))
    distinct_vowel_sounds = sum(1 for phoneme in arpabet_tokens if phoneme[0] in vowels.upper()) >= 2
    if consecutive_vowels and distinct_vowel_sounds:
        categories["v/v pattern"].append(word)

def should_double_consonant(word, arpabet):
    last_char = word[-1]
    second_last_char = word[-2]
    # Step 1: Check if the word ends with a single consonant preceded by a vowel
    if last_char not in vowels and second_last_char in vowels:
        # Check syllable count and stress pattern using pronouncing library
        if arpabet:
            # Use the first ARPAbet pronunciation available
            syllable_count = pronouncing.syllable_count(arpabet)
            stress_pattern = pronouncing.stresses(arpabet)
            # Apply the Doubling Rule based on syllable count and stress
            if syllable_count == 1 or (stress_pattern and stress_pattern[-1] == "1"):
                categories["double rule-suffixes"].append(word)

def begin_interm_affixes(word):
    exceptions = ["e-mail", "e-book", "e-commerce", "eject", "emit", "emigrate", "amorphous", "asymmetry", "adrift", "along", "alike", "queen", "dozen", "raven", "heaven", "rotten", "burden", "kitten", "Lauren", "broken", "budget", "target", "honest", "arrest", "protest", "contest", "request", "decline", "demonstrate", "democratic", "determine", "external", "extra"]

    if word in exceptions:
        if word not in categories["begin/interm affixes"]:
            categories["begin/interm affixes"].append(word)
        return  # Exit early if the word is an exception

    # Check for prefixes
    for prefix in begin_intermediate_prefixes:
        if word.startswith(prefix):
            wordbase = word[len(prefix):]  # Correctly remove the prefix
            if is_valid_presuf(wordbase):
                if word not in categories["begin/interm affixes"]:
                    categories["begin/interm affixes"].append(word)
                break  # Exit the loop once a match is found

    # Check for suffixes
    for suffix in begin_intermediate_suffixes:
        if word.endswith(suffix):
            wordbase = word[:-len(suffix)]  # Correctly remove the suffix
            if is_valid_presuf(wordbase):
                if word not in categories["begin/interm affixes"]:
                    categories["begin/interm affixes"].append(word)
                break  
            # Exit the loop once a match is found

# Function to categorize words with base/suffix or prefix/base patterns
def base_suffix_prefix_base(word):
    for prefix in begin_intermediate_prefixes:
        if word.startswith(prefix):
            base = word[len(prefix):]  # Base ?
            if base:  # If there's remaining base
                categories["base/suffix, prefix/base patterns"].append(word)
                break

    for suffix in begin_intermediate_suffixes:
        if word.endswith(suffix):
            base = word[:-len(suffix)]  # Remove suffix to identify base
            if base:  # If there's remaining base
                categories["base/suffix, prefix/base patterns"].append(word)
                break

# Function to categorize words with intermediate/advanced affixes
def interm_adv_affixes(word):
    for affix in intermediate_advanced_affixes:
        if word.startswith(affix) or word.endswith(affix):
            categories["interm./adv. affixes"].append(word)
            break

# Function to categorize words with beginning roots
def beginning_roots(word):
    for root in roots:
        if word.startswith(root):
            categories["beginning roots"].append(word)
            break

def fszl_check(word, arpabet):
    if pronouncing.syllable_count(arpabet) == 1:
        phonemes = arpabet.split()
        for vowel in ["IH", "EH", "AH", "UH", "AA", "AE"]:
            if vowel in phonemes[-2]:
                categories["fszl"].append(word)
    
def is_y_rule_suffix(word):
    #Maybe temporary Solution
    exceptions = ["frontier", "glacier", "soldier", "barrier", "carrier", "pier", "priest", "series", "species"]
    
    if word in exceptions:
        return False

    if re.search(r'[^aeiou]ies$', word) or re.search(r'[^aeiou]ied$', word) or re.search(r'[^aeiou]ier$', word) or re.search(r'[^aeiou]iest$', word):
        return True

    if re.search(r'.*ying$', word):
        return True

    if re.search(r'[aeiou]y.*$', word):
        return False  

    if re.search(r'.*ies$', word) and not re.search(r'[aeiou]y', word):
        return True

    return False

#def is_e_rule_suffix(word):
 #   for suffix in begin_intermediate_suffixes:
  #      if word.endswith(suffix) and len(word) > 6:
   #         if is_valid_word(word) or is_valid_word(word+'e'):
    #            return True

    #return False

def parse_and_process_words(file_path):
    try:
        with open(file_path, 'r') as file:
            words = file.read().splitlines()

        unique_words = set(words)
        print("-=-=-= Parsing through words =-=-=-\n")
        for word in unique_words:
            word.lower()
            phones = pronouncing.phones_for_word(word)
            if not phones:
                print(f"\t'{word}' not found in the pronounce library's dictionary.")
                categories["fail"].append(word)
                continue 
            else: 
                print("\n", word)

            arpabet = phones[0]
            
            if "c" in word:
                hard_vs_soft_C(word, arpabet)
            if "g" in word:
                hard_vs_soft_G(word, arpabet)
            if "y" in word:
                yCheck(word, arpabet)
            if "'" in word:
                categories["contractions"].append(word)
            if "oo" in word:
                oo_check(word, arpabet)
            if "ow" in word:
                ow_check(word, arpabet)
            if "ear" in word:
                ear_check(word, arpabet)
            if "ea" in word:
                ea_check(word, arpabet)
            if "s" in word:
                s_blends(word)
            if "l" in word:
                l_blends(word)
            if "r" in word:
                r_blends(word)
            if "ew" in word:
                ew_check(word, arpabet)
            if "ou" in word:
                ou_check(word, arpabet)
            if "ue" in word:
                ue_check(word, arpabet)
            if "ei" in word:
                ei_check(word, arpabet)
            if 'ie' in word:
                ie_check(word, arpabet)
            if "ch" in word:
                ch_check(word, arpabet)
            if "sion" in word:
                sion_check(word, arpabet)
            if "augh" in word:
                augh_check(word, arpabet)
            if "ough" in word:
                ough_check(word, arpabet)
            if "r" or "l" in word:
                threel_blends(word)
            if "war" in word:
                warCheck(word)
            if word[-1] in "fszl" and word[-2] in "fszl" and word[-1] == word[-2]:
                fszl_check(word, arpabet)
            if len(word) >= 3:
                should_double_consonant(word, arpabet)
                vcv(word)
                vv_check(word, arpabet)
            if len(word) >= 4:
                vccv(word)
            if len(word) >= 5:
                vcccv(word)
            if is_y_rule_suffix(word):
                categories["y rule suffixes"].append(word)
            #if is_e_rule_suffix(word):
                #categories["e rule-suffixes"].append(word)
            if "v" in word or "l" in word or "r" in word:
                vrl_check(word)
            
            vce_check(word)
            OCE_check(word, arpabet)
            x_in_word_check(word)
            beginning_roots(word)
            begin_interm_affixes(word)
            base_suffix_prefix_base(word)
            interm_adv_affixes(word)

        output_path = os.path.join(script_dir, "categorized_words.json")
        
        # Delete the file if it already exists
        if os.path.exists(output_path):
            os.remove(output_path)

        with open(output_path, 'w') as json_file:
            json.dump(categories, json_file, indent=4)

        print("\n-=-=-= Finished categorzing! Saved to 'categorized_words.json' =-=-=-")
    
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def getTopWords(num, inFile, outFile):
    input_path = os.path.join(script_dir, inFile)
    output_path = os.path.join(script_dir, outFile)
    with open(input_path, 'r') as f:
        data_dict = json.load(f)

    truncated_dict = {key: values[:num] for key, values in categories.items()}

    with open(output_path, 'w') as f:
        json.dump(truncated_dict, f, indent=4)
    
    print(f"Data successfully written to truncated_dictionary.json")

def main():
    input_path = os.path.join(script_dir, 'output_words_list.txt') #WordDatav4.txt
    parse_and_process_words(input_path)
    #getTopWords(20, 'categorized_words.json', 'truncated_dictionary.json')
    phones1 = pronouncing.phones_for_word("fizz")
    #phones2 = pronouncing.phones_for_word("early")
    #print(phones1)
    #ear_check("year", phones1[0])
    #ear_check("early", phones2[0])
    #print(phones1)
    #print(phones1[0])
    #fszl_check("fizz", phones1[0])
    #print(categories["fszl"])

main()