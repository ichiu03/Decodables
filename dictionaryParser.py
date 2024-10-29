import json
import pronouncing

# Define your categories based on the Orton-Gillingham Reading Specialist Test
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
    "y as in dry": [], "ar": [], "wh": [], "oo as school": [], "oo as in book": [], "vce": [],
    "er": [], "ow as in plow": [], "ow as in snow": [], "vccv": [], "Open syll.": [], "Closed syll.": [], "contractions": [], 
    # Column 4
    "ear as in hear": [], "ear as in early": [], "y as in bumpy": [], "aw": [], "ly": [], "ea as in eat": [],
    "ea as in bread": [], "3-letter beg. blends": [], "vcv, vcccv patterns": [], "tch": [], "soft c": [], 
    "soft g": [], "ai": [], "igh": [], "ed": [], "-ble, -cle, -dle, -fle, -gle, -kle, -ple, -tle, -zle": [],
    "V/R/L syllables": [], "oa": [], "ir": [], "-ild, -ind, -old, -ost": [], "oi": [], "double rule-suffixes": [],
    "ew as in few/blew": [], "v/v pattern": [], "kn": [], "e rule-suffixes": [], "ou as in south": [], "ur": [],
      "dge": [], "y rule suffixes": [], "tion": [], "bein/interm affixes": [], "base/suffix, prefix/base patterns": [], 
    # Column 5
    "au": [], "war": [], "-ey as in monkey": [], "ey as in they": [],  "Interm./adv. affixes": [], "ph": [],
    "ie in pie": [], "ie in thief": [], "beginning roots": [], "-sion in tension": [], "-sion in vision" : [],
    "y in gym": [], "wr": [], "eigh": [], "ue in blue": [], "ough": [], "war": [], "ei in recieve": [],
    "ei in vein": [], "augh": [], "oe": [], "ui": [], "ch in echo": [], "wa": [], "eu": [], "gh": [], "mb": [],
    "mn": [], "que": [], "gn": [], "stle": [],"rh": [], "gue": [], "alk": [], "alt": [], "qua": [], "sc": [], "2 syllable dblg.": [],     
    # Uncategorized
    "fail": []
}
vowels = "aeiou"
consonants = "bcdfghjklmnpqrstvwxyz"
# Can organize in "if "x" in word vs edge cases"
def x_in_word_check(word):
    keys = ["s", "t", "b", "m", "l", "d", "n", "p", "k", "j", "v", "z", "f", "r", "h", "w", "x",
        "a", "e", "i", "o", "e", "qu", "sh", "ay", "ck", "ee", "ch", "or", "all", "th", "oy",
        "ar", "wh", "er", "aw", "ly", "tch", "ed", "ai", "igh", "oa", "ir", "oi", "kn", "ur",
        "dge", "tion", "au", "wor", "wr", "eigh", "war", "augh", "oe", "ui", "wa", "eu", "gh",
        "mb", "mn", "que", "gn", "stle", "rh", "gue", "alk", "alt", "qua", "sc"]

    if "ing" in word or "ang" in word or "ong" in word or "ung" in word:
        categories["-ing, -ong, -ang, -ung"].append(word)

    if "ink" in word or "ank" in word or "onk" in word or "unk" in word: 
        categories["-ink, -ank, -onk, -unk"].append(word)

    if "sp" in word or "nt" in word or "mp" in word:
        categories["-sp, -nt, -mp"].append(word)

    if "sk" in word or "lt" in word or "lk" in word:
        categories["-sk, -lt, -lk"].append(word)

    if "ct" in word or "pt" in word:
        categories["-ct, -pt"].append(word)
        
    if ("ble" in word or "cle" in word or "dle" in word or "fle" in word or "gle" in word 
          or "kle" in word or "ple" in word or "tle" in word or "zle" in word):
         categories["-ble, -cle, -dle, -fle, -gle, -kle, -ple, -tle, -zle"].append(word)
         
    if "ild" in word or "ind" in word or "old" in word or "ost" in word:
        categories["-ild, -ind, -old, -ost"].append(word)

    for key in keys:
        if key in word:
            categories[key].append(word)

def yCheck(word, arpabet):    
    # "y as in yes" (initial /Y/ sound or /JH/ sound)
    if arpabet.startswith("Y") or arpabet.startswith("JH"):
        categories["y as in yes"].append(word)
    # "y as in dry" (long "i" sound, represented by "AY1" in ARPAbet)
    elif "AY1" in arpabet:
        categories["y as in dry"].append(word)
    # "y as in bumpy" (unstressed "IY0" sound in ARPAbet)
    elif "IY0" in arpabet:
        categories["y as in bumpy"].append(word)
    # "y in gym" (short "i" sound, "IH1" in ARPAbet)
    elif "IH1" in arpabet:
        categories["y in gym"].append(word) 
    # "-ey as in monkey" (ending with unstressed "IY0")
    elif arpabet.endswith("IY0"):
        categories["-ey as in monkey"].append(word)
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
    if "ER" in arpabet:
        categories["ear as in early"].append(word)

def s_blends(word):
    if ("sn" in word or "sm" in word or "st" in word or "sw" in word):
        categories["s blends"].append(word)
    
def l_blends(word):
    if ("bl" in word or "cl" in word or "fl" in word):
        categories["l blends"].append(word)

def r_blends(word):
    if ("br" in word or "cr" in word or "dr" in word or "fr" in word or "gr" in word or "pr" in word or "tr" in word):
        categories["s blends"].append(word)

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
        
def OCE_check(word):
    # Open syllables (ends in hard vowel)
    if word[-1].lower() in vowels and len(word) > 1:
        categories["Open syll."].append(word)
    # Closed syllables (eg cat, man)
    for i in range(len(word) - 1):
        if word[i].lower() in vowels and word[i + 1].lower() not in vowels:
            categories["Closed syll."].append(word)
            return
        
def ew_check(word, arpabet):
    if "Y UW" in arpabet:
        categories["ew as in few"].append(word)
    elif "UW" in arpabet and "Y UW" not in arpabet:
        categories["ew as in blew"].append(word)

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
    if "K" in arpabet:
        categories["ch as in echo"].append(word)

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
    if ("thr" in word or "scr" in word or "spr" in word or "shr" in word or "spl" in word or "str" in word):
        categories["3-letter beg. blends"].append(word)

def vccv(word):
    for i in range(len(word) - 3):
        if (word[i] in vowels and word[i+1] in consonants and 
            word[i+2] in consonants and word[i+3] in vowels):
            categories["vccv"].append(word)

def vcv(word):
    for i in range(len(word) - 2):  # Iterate through the word for 3-letter patterns
        if (word[i] in vowels and word[i+1] in consonants and 
            word[i+2] in vowels):
            categories["vcv"].append(word)

def vcccv(word):
    for i in range(len(word) - 4):  # Iterate through the word for 5-letter patterns
        if (word[i] in vowels and word[i+1] in consonants and 
            word[i+2] in consonants and word[i+3] in consonants and 
            word[i+4] in vowels):
            categories["vcccv"].append(word)

def syllable_type_check(word, arpabet):
    # Check for R-Controlled Syllable: presence of "ER", "AR", or "OR" in ARPAbet
    if any(r_controlled in arpabet for r_controlled in ["ER", "AR", "OR"]):
        categories["V/R/L syllables"].append(word)
    # Check for L-Controlled Syllable: Vowel followed by "L" in word spelling
    if any(l_controlled in arpabet for l_controlled in ["OL", "AL", "UL"]):
        categories["V/R/L syllables"].append(word)
    # Check for V-Controlled Syllable: Vowel followed by "V" in word spelling
    if any(v_controlled in arpabet for v_controlled in ["IV", "AV", "OV", "UV"]):
        categories["V/R/L syllables"].append(word)

def parse_and_process_words(file_path):
    try:
        with open(file_path, 'r') as file:
            words = file.read().splitlines()

        unique_words = set(words)
        for word in unique_words:
            word.lower()
            phones = pronouncing.phones_for_word(word)
            if not phones:
                print(f"Word '{word}' not found in dictionary.")
                categories["fail"].append(word)
                pass

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
            if "s" in word and word[1] in consonants:
                ear_check(word)
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
            if "ch" in word:
                ch_check(word, arpabet)
            if "sion" in word:
                sion_check(word, arpabet)
            if "r" or "l" in word:
                threel_blends(word)
            if len(word) >= 3:
                vcv(word)
            if len(word) >= 4:
                vccv(word)
            if len(word) >= 5:
                vcccv(word)
            vce_check(word)
            OCE_check(word)
            x_in_word_check(word)

        # Write the categorized words to a JSON file
        with open('categorized_words.json', 'w') as json_file:
            json.dump(categories, json_file, indent=4)

        print("Processing complete. Categorized words saved to 'categorized_words.json'.")
    
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parse_and_process_words('WordDatav4.txt')

main()
