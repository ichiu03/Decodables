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
    "er": [], "ow as in plow": [], "ow as in snow": [], "vccv": [], "O/C/E syllables": [], "contractions": [], 
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
    "Uncategorized": []
}
vowels = {"a", "e", "i", "o", "u"}
# Can organize in "if "x" in word vs edge cases"
def x_in_word_check(word):
    categorized = False
    keys = ["s", "t", "b", "m", "l", "d", "n", "p", "k", "j", "v", "z", "f", "r", "h", "w", "x",
        "a", "e", "i", "o", "e", "qu", "sh", "ay", "ck", "ee", "ch", "or", "all", "th", "oy",
        "ar", "wh", "er", "aw", "ly", "tch", "ed", "ai", "igh", "oa", "ir", "oi", "kn", "ur",
        "dge", "tion", "au", "wor", "wr", "eigh", "war", "augh", "oe", "ui", "wa", "eu", "gh",
        "mb", "mn", "que", "gn", "stle", "rh", "gue", "alk", "alt", "qua", "sc"]

    if "ing" in word or "ang" in word or "ong" in word or "ung" in word:
        categories["-ing, -ong, -ang, -ung"].append(word)
        categorized = True

    if "ink" in word or "ank" in word or "onk" in word or "unk" in word: 
        categories["-ink, -ank, -onk, -unk"].append(word)
        categorized = True

    if "sp" in word or "nt" in word or "mp" in word:
        categories["-sp, -nt, -mp"].append(word)
        categorized = True

    if "sk" in word or "lt" in word or "lk" in word:
        categories["-sk, -lt, -lk"].append(word)
        categorized = True

    if "ct" in word or "pt" in word:
        categories["-ct, -pt"].append(word)
        categorized = True
        
    if ("ble" in word or "cle" in word or "dle" in word or "fle" in word or "gle" in word 
          or "kle" in word or "ple" in word or "tle" in word or "zle" in word):
         categories["-ble, -cle, -dle, -fle, -gle, -kle, -ple, -tle, -zle"].append(word)
         categorized = True
         
    if "ild" in word or "ind" in word or "old" in word or "ost" in word:
        categories["-ild, -ind, -old, -ost"].append(word)
        categorized = True

    for key in keys:
        if key in word:
            categories[key].append(word)
            categorized = True

    return categorized

def yCheck(word):
    categorized = False
    
    # Get the ARPAbet phoneme list for the word
    phones = pronouncing.phones_for_word(word)
    if not phones:
        print(f"Word '{word}' not found in dictionary.")
        return None
    
    # Use the first pronunciation in the list
    arpabet = phones[0]
    
    # "y as in yes" (initial /Y/ sound or /JH/ sound)
    if arpabet.startswith("Y") or arpabet.startswith("JH"):
        categories["y as in yes"].append(word)
        categorized = True
    
    # "y as in dry" (long "i" sound, represented by "AY1" in ARPAbet)
    elif "AY1" in arpabet:
        categories["y as in dry"].append(word)
        categorized = True
    
    # "y as in bumpy" (unstressed "IY0" sound in ARPAbet)
    elif "IY0" in arpabet:
        categories["y as in bumpy"].append(word)
        categorized = True
    
    # "y in gym" (short "i" sound, "IH1" in ARPAbet)
    elif "IH1" in arpabet:
        categories["y in gym"].append(word)
        categorized = True
    
    # "-ey as in monkey" (ending with unstressed "IY0")
    elif arpabet.endswith("IY0"):
        categories["-ey as in monkey"].append(word)
        categorized = True
    
    # "ey as in they" (long "EY1" sound)
    elif "EY1" in arpabet:
        categories["ey as in they"].append(word)
        categorized = True

    return categorized

def hard_vs_soft_C(word):
    categorized = False
    phones = pronouncing.phones_for_word(word)
    if not phones:
        print(f"Word '{word}' not found in dictionary.")
        return None
    arpabet = phones[0]
    if "K" in arpabet: # Hard C
        categories["hard c"].append(word)
        categorized = True

    elif "S" in arpabet: # Soft C
        categories["soft c"].append(word)
        categorized = True

def hard_vs_soft_G(word):
    categorized = False
    phones = pronouncing.phones_for_word(word)
    if not phones:
        print(f"Word '{word}' not found in dictionary.")
        return None
    
    arpabet = phones[0]
    
    if "G" in arpabet: # Hard C
        categories["hard g"].append(word)
        categorized = True
        
    elif "JH" in arpabet: # Soft C
        categories["soft g"].append(word)
        categorized = True
    
    return categorized

def oo_check(word):
    categorized = False
    phones = pronouncing.phones_for_word(word)
    if not phones:
        print(f"Word '{word}' not found in dictionary.")
        return None
    arpabet = phones[0]

    if "UW" in arpabet:
        categories["oo as in school"].append(word)
        categorized = True
    if "UH" in arpabet:
        categories["oo as in book"].append(word)
        categorized = True

    return categorized

def parse_and_process_words(file_path):
    try:
        # Read words from the file
        with open(file_path, 'r') as file:
            words = file.read().splitlines()

        # Remove duplicates by converting to a set
        unique_words = set(words)

        # Categorize words
        for word in unique_words:
            word.lower()
            categorized = x_in_word_check(word)
            if "c" in word:
                categorized = hard_vs_soft_C(word)
            if "g" in word:
                categorized = hard_vs_soft_G(word)
            if "y" in word:
                yCheck(word)
            # elif . . . 
            if not categorized:
                print(f"Was not able to categorize: {word}. ")

        # Write the categorized words to a JSON file
        with open('categorized_words.json', 'w') as json_file:
            json.dump(categories, json_file, indent=4)

        print("Processing complete. Categorized words saved to 'categorized_words.json'.")
    
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function with the path to your text file
def main():
    #parse_and_process_words('parsed_words.txt')
    word = "bumpy"
    phones = pronouncing.phones_for_word(word)
    print(phones[0])

main()
