import json
import pronouncing
import os
import re
import nltk
import syllapy
from nltk.corpus import words
import shutil

# Sight words must be unioned outside of dictionaryParser !!!!

if os.path.exists('dictionary_parser\\edited_generated_story.txt'):
    os.remove('dictionary_parser\\edited_generated_story.txt')

    
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
      "dge": [], "y rule suffixes": [], "tion": [],
    # Column 5
    "au": [], "war": [], "ey as in monkey": [], "ey as in they": [], "ph": [],
    "ie as in pie": [], "ie as in thief": [], "-sion as in tension": [], "-sion as in vision" : [],
    "y as in gym": [], "wr": [], "eigh": [], "ue as in blue": [], "ough": [], "wor": [], "ei as in receive": [],
    "ei as in vein": [], "augh": [], "oe": [], "ui": [], "ch as in echo": [], "wa": [], "eu": [], "gh": [], "mb": [],
    "mn": [], "que": [], "gn": [], "stle": [],"rh": [], "gue": [], "alk": [], "alt": [], "qua": [], "sc": [], 
    # Uncategorized
    "fail": [],
    "sight words": ['a', 'any', 'many', 'and', 'on', 'is', 'are', 'the', 'was', 'were', 'it', 'am', 'be', 'go', 'to', 'been', 'come', 'some', 'do', 'does', 'done', 'what', 'who', 'you', 'your', 'both', 'buy', 'door', 'floor', 'four', 'none', 'once', 'one', 'only', 'pull', 'push', 'sure', 'talk', 'walk', 'their', 'there', "they're", 'very', 'want', 'again', 'against', 'always', 'among', 'busy', 'could', 'should', 'would', 'enough', 'rough', 'tough', 'friend', 'move', 'prove', 'ocean', 'people', 'she', 'other', 'above', 'father', 'usually', 'special', 'front', 'thought', 'he', 'we', 'they', 'nothing', 'learned', 'toward', 'put', 'hour', 'beautiful', 'whole', 'trouble', 'of', 'off', 'use', 'have', 'our', 'say', 'make', 'take', 'see', 'think', 'look', 'give', 'how', 'ask', 'boy', 'girl', 'us', 'him', 'his', 'her', 'by', 'where', 'were', 'wear', 'hers', "don't", 'which', 'just', 'know', 'into', 'good', 'other', 'than', 'then', 'now', 'even', 'also', 'after', 'know', 'because', 'most', 'day', 'these', 'two', 'already', 'through', 'though', 'like', 'said', 'too', 'has', 'in', 'brother', 'sister', 'that', 'them', 'from', 'for', 'with', 'doing', 'well', 'before', 'tonight', 'down', 'about', 'but', 'up', 'around', 'goes', 'gone', 'build', 'built', 'cough', 'lose', 'loose', 'truth', 'daughter', 'son']
}
vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"
begin_intermediate_prefixes = ["re", "de", "sub", "pre", "com", "con", "pro", "ex", "be", "dis"]
begin_intermediate_suffixes = ["ful", "est", "ish", "less", "ness", "ling", "dom", "ic", "et", "en"]
intermediate_advanced_affixes = ["inter", "multi", "anti", "contra", "pseudo", "ology", "tion", "phobia"]
roots = ["port", "ject", "tract", "mit", "miss", "ceit", "ceive", "struct", "fact", "form", "spect", 
         "dict", "duct", "script", "rupt", "flect", "flex", "vert", "vers", "pel", "puls", "vis", "vid", "cap", "cept"]
vowel_phonemes = {
    "AA", "AE", "AH", "AO", "AW", "AY", 
    "EH", "EY", "IH", "IY", 
    "OW", "OY", "UH", "UW"
}

def is_valid_presuf(wordbase):
    if len(wordbase) < 3:
        return False
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

def x_in_word_check(word, arpabet):
    keys = ["m", "l", "p", "k", "j", "v", "z", "f", "x",
        "sh", "ay", "ck", "ee", "all", "th", "oy", 
        "wh", "er", "aw", "tch", "ed", "ai", "oa", "kn", "ur",
        "dge", "tion", "au", "ough", "wor", "wr", "eigh", "augh", "oe", "ui", "wa", "eu", "gh",
        "mb", "mn", "que", "gn", "stle", "rh", "gue", "alk", "alt", "qua", "sc", "ph"]

    tokens = arpabet.split()
    if 'oi' in word and 'OY' in tokens:
        categories['oi'].append(word)
    if 'ir' in word and "ER" in tokens:
        categories['ir'].append(word)
    if "s" in word and "S" in tokens:
        categories["s"].append(word)
    if "t" in word and "T" in tokens:
        categories["t"].append(word)
    if "b" in word and "B" in tokens:
        categories["b"].append(word)
    if "d" in word and "D" in tokens:
        categories["d"].append(word)
    if "n" in word and "N" in tokens:
        categories["n"].append(word)
    if "p" in word and "P" in tokens:
        categories["p"].append(word)
    if "r" in word and "R" in tokens:
        categories["r"].append(word)
    if "h" in word and "HH" in tokens:
        categories["h"].append(word)
    if "x" in word and "K S" in arpabet:
        categories["x"].append(word)
    if "a" in word:
        if "EY" in tokens:
            categories["long a"].append(word)
        if "AA" in tokens or "AH" in tokens or "AE" in tokens:
            categories["short a"].append(word)
    if "e" in word:
        if "IH" in tokens:
            categories["long e"].append(word)
        if "EH" in tokens or "AH" in tokens:
            categories["short e"].append(word)
    if "i" in word:
        if "AY" in tokens:
            categories["long i"].append(word)
        if "IH" in tokens:
            categories["short i"].append(word)
    if "o" in word:
        if "OW" in tokens:
            categories["long o"].append(word)
        if "AH" in tokens or "AA" in tokens or "AO" in tokens:
            categories["short o"].append(word)
    if "u" in word:
        if "UW" in tokens:
            categories["long u"].append(word)
        if "AH" in tokens:
            categories["short u"].append(word)
    if "w" in word and "W" in tokens:
        if "wh" in word: # Check if there's 'w' and 'wh'
            w_index = word.index('wh')
            no_wh = word[: w_index] + word[w_index + 2:]
            if "w" in no_wh: # still a 'w', after removing 'wh'
                categories['w'].append(word)
        else:
            categories['w'].append(word)
    if "qu" in word:
        if "K W" in arpabet:
            categories["qu"].append(word)
    if "ch" in word:
        if "CH" in tokens:
            categories["ch"].append(word)
    if "or" in word:
        if "AO R" in arpabet:
            categories["or"].append(word)
    if "ar" in word:
        if "AA R" in arpabet:
            categories["ar"].append(word)
    if word[-2:] == "ly" and tokens[-1] == "IY":
        categories["ly"].append(word)
    if "igh" in word:
        index = word.find("igh")
        if word[index-1] not in 'eia':
            categories['igh'].append(word)
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
    if (word.endswith('ble') or word.endswith('cle') or word.endswith('dle') or word.endswith('fle') or 
        word.endswith('gle') or word.endswith('ple') or word.endswith('tle') or word.endswith('zle') or word.endswith('kle')):
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
    # "y as in yes" (initial /Y/ sound)
    if "ye" in word or "ya" in word or "yo" in word:
        if "Y EH" in arpabet or "Y OW" in arpabet or "Y AO" in arpabet or "Y UH" in arpabet or "Y AH" in arpabet:
            categories["y as in yes"].append(word)
    # "y as in dry" (long "i" sound, represented by "AY1" in ARPAbet)
    if "AY" in arpabet:
        categories["y as in dry"].append(word)
    # "y as in bumpy" (unstressed "IY0" sound in ARPAbet)
    elif "IY" in arpabet:
        categories["y as in bumpy"].append(word)
    # "y in gym" (short "i" sound, "IH1" in ARPAbet)
    if "IH" in arpabet:
        categories["y as in gym"].append(word) 
    # "-ey as in monkey" (ending with unstressed "IY0")
    if arpabet.endswith("IY") and word.endswith("ey"):
        categories["ey as in monkey"].append(word)
    # "ey as in they" (long "EY1" sound)
    elif "ey" in word and "EY" in arpabet:
        categories["ey as in they"].append(word)

def hard_vs_soft_C(word, arpabet):
    for i, (letter, phone) in enumerate(zip(word, arpabet.split())):
        if letter == 'c' and phone == 'K':  # Ensure 'C' specifically makes the 'K' sound
            categories["hard c"].append(word)
            return  # Exit once categorized as hard 'C'
    categories["soft c"].append(word)

def hard_vs_soft_G(word, arpabet):
    tokens = arpabet.split()
    if "G" in tokens: # Hard C
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
    if "IH R" in arpabet or "IY R" in arpabet:
        categories["ear as in hear"].append(word)
    elif "ER" in arpabet:
        categories["ear as in early"].append(word)

def s_blends(word):
    if word.startswith("sn") or word.startswith("sm") or word.startswith("st") or word.startswith("sw") or word.startswith("sc") or word.startswith("sp"):
        if word[2] in vowels:
            categories["s blends"].append(word)
    
def l_blends(word):
    if word.startswith("bl") or word.startswith("cl") or word.startswith("fl") or word.startswith("pl") or word.startswith("gl") or word.startswith("sl"):
        if word[2] in vowels:
            categories["l blends"].append(word)

def r_blends(word):
    if word.startswith("br") or word.startswith("cr") or word.startswith("dr") or word.startswith("fr") or word.startswith("gr") or word.startswith("pr") or word.startswith("tr"):
        if word[2] in vowels:
            categories["r blends"].append(word)

def ea_check(word, arpabet):
    if "IY" in arpabet:
        categories["ea as in eat"].append(word)
    if "EH" in arpabet and "EH R" not in arpabet:
        categories["ea as in bread"].append(word)

def vce_check(word):
    for i in range(len(word) - 2):
        if (word[i].lower() in vowels and
            word[i + 1].lower() in consonants and
            word[i + 2].lower() == 'e'):
            categories["vce"].append(word)
        
def OCE_check(word, arpabet):
    tokens = arpabet.split()
    # Open syllables (ends in hard vowel)
    if word[-1] in vowels and len(word) > 1:
        if not(word[-1] == "e" and "IY" not in tokens[-1]):
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
        tokens = arpabet.split()
        try:
            if tokens[ch_index] == "K":
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
    if (word.startswith("spr") or word.startswith("spl") or word.startswith("thr") or word.startswith("scr") or word.startswith("shr") or word.startswith("str")):
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
    consecutive = False
    for i in range(len(word) - 1):
        if word[i] in vowels and word[i + 1] in vowels:
            consecutive = True
    if not consecutive: return 

    tokens = arpabet.split()
    count = 0
    while count + 1 < len(tokens):
        first = tokens[count]
        second = tokens[count + 1]
        if first in vowel_phonemes and second in vowel_phonemes:
            categories["v/v pattern"].append(word)
            return
        count += 1

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

def fszl_check(word, arpabet):
    if pronouncing.syllable_count(arpabet) == 1:
        tokens = arpabet.split()
        for vowel in ["IH", "EH", "AH", "UH", "AA", "AE"]:
            if vowel in tokens[-2]:
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

def map_chunks_to_phonemes(word):
    arpabet = pronouncing.phones_for_word(word)
    phonemes = arpabet[0].split()  # Use the first phonetic transcription
    chunk_to_phonemes = {}
    current_chunk = []
    current_phoneme_chunk = []
    phoneme_iter = iter(phonemes)
    for letter in word:
        current_chunk.append(letter)
        if letter in vowels:  # Finalize chunk at vowel
            try:
                # Collect phonemes until a vowel phoneme is encountered
                while True:
                    phoneme = next(phoneme_iter)
                    current_phoneme_chunk.append(phoneme)
                    if phoneme[-1].isdigit():  # Vowel phoneme found
                        break
            except StopIteration:
                pass
            # Map the current chunk to its phonemes
            chunk_to_phonemes[''.join(current_chunk)] = ' '.join(current_phoneme_chunk)
            current_chunk = []
            current_phoneme_chunk = []

    # Handle any leftover chunk or phoneme
    if current_chunk:
        chunk_to_phonemes[''.join(current_chunk)] = ' '.join(current_phoneme_chunk)
        
    return chunk_to_phonemes

def parse_and_process_words(input_path, output_path):
    try:
        with open(input_path, 'r') as file:
            words = file.read().splitlines()
        unique_words = set(words)
        print("-=-=-= Parsing through words =-=-=-\n")
        for word in unique_words:
            word.lower()
            if word in categories["sight words"]:
                continue
            phones = pronouncing.phones_for_word(word)
            if not phones:
                print(f"\t'{word}' not found in the pronouncing library's dictionary.")
                categories["fail"].append(word)
                continue

            arp = phones[0]
            arpabet = re.sub(r'\d', '', arp)
            
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
            x_in_word_check(word, arpabet)

        # Delete the file if it already exists
        if os.path.exists(output_path):
            os.remove(output_path)

        with open(output_path, 'w') as json_file:
            json.dump(categories, json_file, indent=4)

        print("\n-=-=-= Finished categorzing! Saved to 'categorized_words.json' =-=-=-")
    
    except FileNotFoundError:
        print(f"The file {input_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def getTopWords(num, input_path, output_path):
    with open(input_path, 'r') as f:
        data_dict = json.load(f)
    truncated_dict = {key: values[:num] for key, values in categories.items()}
    with open(output_path, 'w') as f:
        json.dump(truncated_dict, f, indent=4)
    
    print(f"Data successfully written to truncated_dictionary.json")

### Takes in a list of all the problem categories and makes sure every categories doesn't have words from 
### any of the categories. 
def ridOverlap(problemCategories: list) -> None:
    badWords = []
    for category in problemCategories:
        badWords.extend(categories[category])
    badWords = set(badWords)  # Deduplicate

    for key, value in categories.items():
        categories[key] = [word for word in value if word not in badWords]


def main():
    filename = 'generated_story.txt' 
    input_path = os.path.join(script_dir, filename)
    output_path = os.path.join(script_dir, "categorized_words.json")
    parse_and_process_words(input_path, output_path)

def run(inFile: str, outFile: str, full_or_truncated: bool):
    input_path = os.path.join(script_dir, inFile)
    output_path = os.path.join(script_dir, outFile)
    if full_or_truncated:
        parse_and_process_words(input_path, output_path)
    else:
        getTopWords(20, 'categorized_words.json', 'truncated_dictionary.json')

main()

#print(map_chunks_to_phonemes("builder"))

