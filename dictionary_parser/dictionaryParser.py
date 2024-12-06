import json
import pronouncing
import os
import re
import nltk
from nltk.corpus import words
import traceback

# Get the directory where `dictionaryParser.py` is located 
script_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure the script checks locally for nltk_data
os.environ['NLTK_DATA'] = os.path.expanduser('~/nltk_data')
# Check if 'words' from nltk is already downloaded
try:
    valid_words = set(words.words())
except LookupError:
    nltk.download('words') # If it’s not available, attempt to download it

categories = {
    # Column 1 - Consonant Sounds
    's': [], 't': [], 'b': [], 'm': [], 'l': [], 'd': [], 'n': [], 'p': [], 'k': [], 'j': [], 'v': [],
    'z': [], 'f': [], 'hard c': [], 'hard g': [], 'r': [], 'h': [], 'w': [], 'x': [], 'y as in yes': [],
    # Column 2 - All VOWELS (short & long)
    'long a': [], 'short a': [], 'long i': [], 'short i': [], 'long o': [], 'short o': [],
    'long u': [], 'short u': [], 'long e': [], 'short e': [],
    # Column 3 
    'fszl': [], 'qu': [], 'sh': [], 'ay': [], 'ck': [], 'ee': [], 'ch': [], 'or': [], 's blends': [],
    'l blends': [], 'r blends': [], '-ing, -ong, -ang, -ung': [], 'all': [], 'th': [], 'oy': [],
    '-ink, -ank, -onk, -unk': [], '-ft, -nd, -st': [], '-sp, -nt, -mp': [], '-sk, -lt, -lk': [], '-ct, -pt': [],
    'y as in dry': [], 'ar': [], 'wh': [], 'oo as in school': [], 'oo as in book': [], 'vce': [],
    'er': [], 'ow as in plow': [], 'ow as in snow': [], 'vccv': [], 'Open syll.': [], 'Closed syll.': [], 'contractions': [], 
    # Column 4
    'ear as in hear': [], 'ear as in early': [], 'y as in bumpy': [], 'aw': [], 'ly': [], 'ea as in eat': [],
    'ea as in bread': [], '3-letter beg. blends': [], 'vcv, vcccv patterns': [], 'tch': [], 'soft c': [], 
    'soft g': [], 'ai': [], 'igh': [], 'ed': [], '-ble, -cle, -dle, -fle, -gle, -kle, -ple, -tle, -zle': [],
    'l syllables': [],'v syllables': [], 'r syllables': [], 'oa': [], 'ir': [], '-ild, -ind, -old, -ost': [], 'oi': [], 'double rule-suffixes': [],
    'ew as in few/blew': [], 'v/v pattern': [], 'kn': [], 'e rule-suffixes': [], 'ou as in south': [], 'ur': [],
      'dge': [], 'y rule suffixes': [], 'tion': [],
    # Column 5
    'au': [], 'war': [], 'ey as in monkey': [], 'ey as in they': [], 'ph': [],
    'ie as in pie': [], 'ie as in thief': [], '-sion as in tension': [], '-sion as in vision' : [],
    'y as in gym': [], 'wr': [], 'eigh': [], 'ue as in blue': [], 'ough': [], 'wor': [], 'ei as in receive': [],
    'ei as in vein': [], 'augh': [], 'oe': [], 'ui': [], 'ch as in echo': [], 'wa': [], 'eu': [], 'gh': [], 'mb': [],
    'mn': [], 'que': [], 'gn': [], 'stle': [],'rh': [], 'gue': [], 'alk': [], 'alt': [], 'qua': [], 'sc': [], 
    # Uncategorized
    'failed to categorize': [],
}
vv_sounds = {
    'ai': ['AY IY'], 'ia': ['IY EY', 'IY AH', 'IY AE', 'AY AH'], 'ie': ['AY AH', 'AY IH'],
    'io': ['AY AH', 'IY OW', 'IY AA'], 'ea': ['IY AH', 'IY EH'], 'iu': ['IY AH', 'IY IH', 'IY UW'],
    'eo': ['IY ER', 'IY OW', 'IY AA'], 'ue': ['UW AH', 'UW EH'], 'eu': ['IY AH'], 'ao': ['EY AA'], 'ei': ['IY AH'], 
    'ua': ['UW EH', 'UW EY', 'AH W AH', 'AH W EY', 'UW W AH', 'UW EY', 'UW AH', 'UW AE']}
sight_words = {'a', 'any', 'many', 'and', 'on', 'is', 'are', 'the', 'was', 'were', 'it', 'am', 'be', 'go', 'to', 'been', 'come', 'some', 'do', 'does', 'done', 'what', 'who', 'you', 'your', 'both', 'buy', 'door', 'floor', 'four', 'none', 'once', 'one', 'only', 'pull', 'push', 'sure', 'talk', 'walk', 'their', 'there', "they're", 'very', 'want', 'again', 'against', 'always', 'among', 'busy', 'could', 'should', 'would', 'enough', 'rough', 'tough', 'friend', 'move', 'prove', 'ocean', 'people', 'she', 'other', 'above', 'father', 'usually', 'special', 'front', 'thought', 'he', 'we', 'they', 'nothing', 'learned', 'toward', 'put', 'hour', 'beautiful', 'whole', 'trouble', 'of', 'off', 'use', 'have', 'our', 'say', 'make', 'take', 'see', 'think', 'look', 'give', 'how', 'ask', 'boy', 'girl', 'us', 'him', 'his', 'her', 'by', 'where', 'were', 'wear', 'hers', "don't", 'which', 'just', 'know', 'into', 'good', 'other', 'than', 'then', 'now', 'even', 'also', 'after', 'know', 'because', 'most', 'day', 'these', 'two', 'already', 'through', 'though', 'like', 'said', 'too', 'has', 'in', 'brother', 'sister', 'that', 'them', 'from', 'for', 'with', 'doing', 'well', 'before', 'tonight', 'down', 'about', 'but', 'up', 'around', 'goes', 'gone', 'build', 'built', 'cough', 'lose', 'loose', 'truth', 'daughter', 'son'}
VOWELS = set('aeiou')
CONSONANTS = set('bcdfghjklmnpqrstvwxyz')
COMPOUND_SOUNDS = {
    'ai', 'au', 'ay', 'ae', 'ao', 'ar', 'ea', 'ee', 'ei', 'eo', 'eu', 'er',
    'ia', 'ie', 'io', 'iu', 'ir', 'oa', 'oe', 'oi', 'oo', 'ou', 'or', 'ua',
    'ue', 'ui', 'uo', 'ur', 'ough', 'augh', 'igh', 'eigh', 'tio', 'sio',
    'ey', 'oy', 'ew', 'ow', 'aw', 'ye', 'uie', 'oux', 'cally'
    }

### Checks if compound vowel is a vowel/vowel -> yes is True
def is_vv(compound: str, arp: str) -> bool:
    for vow, phonemes in vv_sounds.items():
        if vow == compound:
            for pho in phonemes:
                if pho in arp:
                    return True
    return False

### Maps chunks of word to its phoneme, separating by VOWELS. Accounts for compound VOWELS as well. 
def mapChunksToPhonemes(word: str) -> dict:
    def collectAndMapPhonemes(iterable, chunk, phoneme_list, chunk_to_phonemes):
        try:
            while True:
                phoneme = next(iterable)
                phoneme_list.append(phoneme)
                if phoneme[-1].isdigit():  # Vowel phoneme found
                    break
        except StopIteration:
            pass
        if chunk:
            chunk_to_phonemes[chunk] = ' '.join(phoneme_list)
            phoneme_list.clear()
    
    arpabet = pronouncing.phones_for_word(word)
    arp = re.sub(r'\d', '', arpabet[0])
    chunk_to_phonemes = {}
    current_chunk = ''
    current_phoneme_chunk = []
    phoneme_iter = iter(arpabet[0].split())
    i = 0
    while i < len(word):
        # Check if we're at a compound vowel 
        compound = None
        for comp in sorted(COMPOUND_SOUNDS, key=len, reverse=True):
            if word[i:i + len(comp)] == comp:
                compound = word[i:i + len(comp)]
                break
        # Case 1: Consonant
        if compound is None and word[i] not in 'aeiouy':
            current_chunk += word[i]
            i += 1
        # Case 2: Singular vowel encountered
        elif compound is None and word[i] in 'aeiouy':
            current_chunk += word[i]
            i += 1
            collectAndMapPhonemes(phoneme_iter, current_chunk, current_phoneme_chunk, chunk_to_phonemes)
            current_chunk = ''
        # Case 3: Compound is team vowel
        elif compound and not is_vv(compound, arp):
            current_chunk += compound
            i += len(compound)
            collectAndMapPhonemes(phoneme_iter, current_chunk, current_phoneme_chunk, chunk_to_phonemes)
            current_chunk = ''
        # Case 4: Compound is vowel/vowel
        elif compound and is_vv(compound, arp):
            current_chunk += word[i]
            i += 1
            collectAndMapPhonemes(phoneme_iter, current_chunk, current_phoneme_chunk, chunk_to_phonemes)
            current_chunk = ''
        else: # Case 5: Skip non-alphabetical characters
            i += 1
    while True: # Handle rest of word
            try:
                phoneme = next(phoneme_iter)
                current_phoneme_chunk.append(phoneme)
            except StopIteration:
                break
    if current_chunk:
        chunk_to_phonemes[current_chunk] = ' '.join(current_phoneme_chunk)
    return chunk_to_phonemes

### Confirms whether to add a word to a category, based on troublesome phonemes
def verificationToAdd(word: str, arpabet: str, letters: str, desired_pho: list, problem_pho: list) -> bool:
    # Check if BOTH a desired phoneme AND a problem phoneme are present
    if not (any(pho in arpabet for pho in desired_pho) or any(pho in arpabet for pho in problem_pho)): return True
    matches = False
    mapping = mapChunksToPhonemes(word)
    for chunk, phoneme in mapping.items():
        if letters in chunk:
            for pho in desired_pho:
                if pho in phoneme:
                    matches = True
    return matches

### The "easier" categories are categorized here
def xInWordCheck(word: str, arpabet: str) -> None:
    tokens = arpabet.split()
    keys = ['m', 'l', 'p', 'v', 'z', 'f', 'sh', 'ay', 'ck', 'ee', 'th', 'oy', 
        'wh', 'er', 'aw', 'tch', 'ed', 'ai', 'oa', 'kn', 'ur',
        'dge', 'tion', 'au', 'ough', 'wor', 'wr', 'eigh', 'augh', 'oe', 'ui', 'wa', 'eu', 'gh',
        'mb', 'mn', 'que', 'gn', 'stle', 'rh', 'gue', 'alk', 'alt', 'qua', 'sc', 'ph']

    if 'k' in word and 'K' in arpabet: categories['k'].append(word)
    if 'j' in word and 'JH' in arpabet: categories['j'].append(word)
    if 'oi' in word and 'OY' in tokens: categories['oi'].append(word)
    if 'ir' in word and 'ER' in tokens: categories['ir'].append(word)
    if 's' in word and 'S' in tokens: categories['s'].append(word)
    if 't' in word and 'T' in tokens: categories['t'].append(word)
    if 'b' in word and 'B' in tokens: categories['b'].append(word)
    if 'd' in word and 'D' in tokens: categories['d'].append(word)
    if 'n' in word and 'N' in tokens: categories['n'].append(word)
    if 'p' in word and 'P' in tokens: categories['p'].append(word)
    if 'h' in word and 'HH' in tokens: categories['h'].append(word)
    if 'x' in word and 'K S' in arpabet and 'K SH' not in arpabet: categories['x'].append(word)
    if 'qu' in word and 'K W' in arpabet: categories['qu'].append(word)
    if 'ch' in word and 'CH' in tokens: categories['ch'].append(word)
    if 'or' in word and 'AO R' in arpabet: categories['or'].append(word)
    if 'ar' in word and 'AA R' in arpabet: categories['ar'].append(word)
    if word[-2:] == 'ly' and tokens[-1] == 'IY': categories['ly'].append(word)
    if 'r' in word and 'R' in tokens:
        if 'ar' in word or 'er' in word or 'ir' in word or 'or' in word or 'ur' in word:
            pass
        categories['r'].append(word)
    if 'a' in word:
        if 'EY' in tokens and verificationToAdd(word, arpabet, 'a', ['EY'], ['AA', 'AH', 'AE']):
            categories['long a'].append(word)
        if ('AA' in tokens or 'AH' in tokens or 'AE' in tokens):
            if verificationToAdd(word, arpabet, 'a', ['AA', 'AH', 'AE'], ['EY']):
                categories['short a'].append(word)
    if 'e' in word:
        if 'IH' in tokens and verificationToAdd(word, arpabet, 'e', ['IH'], ['EH', 'AH']):
            categories['long e'].append(word)
        if ('EH' in tokens or 'AH' in tokens):
            if verificationToAdd(word, arpabet, 'e', ['IH', 'AH'],['IH']):
                categories['short e'].append(word)
    if 'i' in word:
        if 'AY' in tokens and verificationToAdd(word, arpabet, 'i', ['AY'], ['IH']): 
            categories['long i'].append(word)
        if 'IH' in tokens and verificationToAdd(word, arpabet, 'i', ['IH'], ['AY']): 
            categories['short i'].append(word)
    if 'o' in word:
        if 'OW' in tokens and verificationToAdd(word, arpabet, 'o', ['OW'], ['AH', 'AA', 'AO']):
            categories['long o'].append(word)
        if 'AH' in tokens or 'AA' in tokens or 'AO' in tokens: 
            if verificationToAdd(word, arpabet, 'o', ['AH', 'AA', 'AO'], ['OW']):
                categories['short o'].append(word)
    if 'u' in word:
        if 'UW' in tokens and verificationToAdd(word, arpabet, 'u', ['UW'], ['AH']):
            categories['long u'].append(word)
        if 'AH' in tokens and verificationToAdd(word, arpabet, 'u', ['AH'], ['UW']):
            categories['short u'].append(word)
    if 'w' in word and 'W' in tokens:
        if 'wh' in word: # Check if there's 'w' and 'wh'
            w_index = word.index('wh')
            no_wh = word[: w_index] + word[w_index + 2:]
            if 'w' in no_wh: # still a 'w', after removing 'wh'
                categories['w'].append(word)
        else:
            categories['w'].append(word)
    if 'ink' in word or 'ank' in word or 'onk' in word or 'unk' in word: categories['-ink, -ank, -onk, -unk'].append(word)
    if word.endswith('ft') or word.endswith('st') or word.endswith('nd'): categories['-ft, -nd, -st'].append(word)
    if word.endswith('sp') or word.endswith('nt') or word.endswith('mp'): categories['-sp, -nt, -mp'].append(word)
    if word.endswith('sk') or word.endswith('lt') or word.endswith('lk'): categories['-sk, -lt, -lk'].append(word)
    if word.endswith('ct') or word.endswith('pt'): categories['-ct, -pt'].append(word)
    if (word.endswith('ble') or word.endswith('cle') or word.endswith('dle') or word.endswith('fle') or 
        word.endswith('gle') or word.endswith('ple') or word.endswith('tle') or word.endswith('zle') or word.endswith('kle')):
        categories['-ble, -cle, -dle, -fle, -gle, -kle, -ple, -tle, -zle'].append(word)
    if 'igh' in word:
        index = word.find('igh')
        if word[index-1] not in 'eia':
            categories['igh'].append(word)
    if 'ild' in word or 'ind' in word or 'old' in word or 'ost' in word: categories['-ild, -ind, -old, -ost'].append(word)
    for key in keys:
        if key in word: categories[key].append(word)

def warCheck(word: str) -> None:
    if 'war' in word and 'ware' not in word: categories['war'].append(word)

### Handles all words with 'y' and their categories
def yCheck(word: str, arpabet: str) -> None:
    if 'y' not in word: return
    if 'ye' in word or 'ya' in word or 'yo' in word:
        if 'Y EH' in arpabet or 'Y OW' in arpabet or 'Y AO' in arpabet or 'Y UH' in arpabet or 'Y AH' in arpabet:
            categories['y as in yes'].append(word)
    if 'AY' in arpabet: 
        if verificationToAdd(word, arpabet, 'y', ['AY'], ['IH']):
            categories['y as in dry'].append(word)
    elif 'IY' in arpabet: 
        if verificationToAdd(word, arpabet, 'y', ['IY'], ['IH']):
            categories['y as in bumpy'].append(word)
    if 'IH' in arpabet: 
        if verificationToAdd(word, arpabet, 'y', ['IH'], ['IH']):
            categories['y as in gym'].append(word) 
    if arpabet.endswith('IY') and word.endswith('ey'): 
        if verificationToAdd(word, arpabet, 'ey', ['IY'], ['EY']):
            categories['ey as in monkey'].append(word)
    if 'ey' in word:
        if verificationToAdd(word, arpabet, 'ey', ['EY'], ['IH']):
            categories['ey as in they'].append(word)

def ingongangungCheck(word: str) -> None:
    # For -ong, -ang, -ung endings
    if word.endswith(('ong', 'ang', 'ung')):
        categories['-ing, -ong, -ang, -ung'].append(word)
    # For -ing endings
    if word.endswith('ing'):
        if len(word) <= 5: 
            categories['-ing, -ong, -ang, -ung'].append(word)
            return
        root_word = word[:-3] # Remove -ing
        modified_root_word = None
        # Regular check without -ing
        if root_word in valid_words: return
        # Check for the case of doubled consonants
        if len(root_word) > 1 and root_word[-1] == root_word[-2]: # swimming -> swim
            modified_root_word = root_word[:-1]
        if modified_root_word in valid_words: return
        # Single consonant with dropped 'e'
        modified_root_word_e = root_word + 'e'
        if modified_root_word_e in valid_words: return
        # Double consonant with dropped 'e'
        if modified_root_word is not None:
            modified_root_word_e2 = modified_root_word + 'e'
            if modified_root_word_e2 in valid_words: return
        # If we get here, we should add the word
        categories['-ing, -ong, -ang, -ung'].append(word)

def allCheck(word: str) -> None:
    if word.endswith('ly'):
        root_word = word[:-2]
        if 'all' in root_word:
            categories['all'].append(word)
    else:
        categories['all'].append(word)

def hardVsSoftC(word: str, arpabet: str) -> None:
    if 'c' not in word: return
    tokens = arpabet.split()
    hard_verification = verificationToAdd(word, arpabet, 'c', ['K'], ['S'])
    soft_verification = verificationToAdd(word, arpabet, 'c', ['S'], ['K'])
    if 'exce' in word and 'S' in tokens: categories['soft c'].append(word)
    elif hard_verification and soft_verification: return
    elif 'K' in tokens and hard_verification: categories['hard c'].append(word)
    elif 'S' in tokens and soft_verification: categories['soft c'].append(word)

def hardVsSoftG(word: str, arpabet: str) -> None:
    if 'g' not in word: return
    tokens = arpabet.split()
    hard_verification = verificationToAdd(word, arpabet, 'g', ['G'], ['JH'])
    soft_verification = verificationToAdd(word, arpabet, 'g', ['JH'], ['G'])
    if hard_verification and soft_verification: return
    elif 'G' in tokens and hard_verification: categories['hard g'].append(word)
    elif 'JH' in arpabet and soft_verification: categories['soft g'].append(word)

def ooCheck(word: str, arpabet: str) -> None:
    if 'oo' not in word: return
    if 'UW' in arpabet: categories['oo as in school'].append(word)
    if 'UH' in arpabet: categories['oo as in book'].append(word)

def owCheck(word: str, arpabet: str) -> None:
    if 'ow' not in word: return
    if 'AW' in arpabet: categories['ow as in plow'].append(word)
    if 'OW' in arpabet: categories['ow as in snow'].append(word)

def earCheck(word: str, arpabet: str) -> None:
    if 'ear' not in word: return
    if 'IH R' in arpabet or 'IY R' in arpabet: categories['ear as in hear'].append(word)
    if 'ER' in arpabet: categories['ear as in early'].append(word)

def sBlends(word: str) -> None:
    if 's' not in word: return
    if word.startswith('sn') or word.startswith('sm') or word.startswith('st') or word.startswith('sw') or word.startswith('sc') or word.startswith('sp'):
        if word[2] in VOWELS:
            categories['s blends'].append(word)
    
def lBlends(word: str) -> None:
    if 'l' not in word: return
    if word.startswith('bl') or word.startswith('cl') or word.startswith('fl') or word.startswith('pl') or word.startswith('gl') or word.startswith('sl'):
        if word[2] in VOWELS:
            categories['l blends'].append(word)

def rBlends(word: str) -> None:
    if 'r' not in word: return
    if word.startswith('br') or word.startswith('cr') or word.startswith('dr') or word.startswith('fr') or word.startswith('gr') or word.startswith('pr') or word.startswith('tr'):
        if word[2] in VOWELS:
            categories['r blends'].append(word)

def eaCheck(word: str, arpabet: str) -> None:
    if 'ea' not in word: return
    if 'IY' in arpabet: categories['ea as in eat'].append(word)
    if 'EH' in arpabet and 'EH R' not in arpabet: categories['ea as in bread'].append(word)

def contractionsCheck(word: str) -> None:
    if "'" in word:
        if re.match(r"[a-zA-Z]+\'[a-zA-Z]*", word):
            categories['contractions'].append(word)

def ewCheck(word: str, arpabet: str) -> None:
    if 'ew' not in word: return
    if 'UW' in arpabet: categories['ew as in few/blew'].append(word)

def ouCheck(word: str, arpabet: str) -> None:
    if 'ou' not in word: return
    if 'AW' in arpabet: categories['ou as in south'].append(word)

def ueCheck(word: str, arpabet: str) -> None:
    if 'ue' not in word: return
    if 'UW' in arpabet: categories['ue as in blue'].append(word)

def eiCheck(word: str, arpabet: str) -> None:
    if 'ei' not in word: return
    if 'IY' in arpabet: categories['ei as in receive'].append(word)
    elif 'EY' in arpabet: categories['ei as in vein'].append(word)

def chCheck(word: str, arpabet: str) -> None:
    if 'ch' not in word: return
    tokens = arpabet.split()
    if "K" in tokens and verificationToAdd(word, arpabet, 'ch', ['K'], ['CH']): 
        categories['ch as in echo'].append(word)

def aughCheck(word: str, arpabet: str) -> None:
    if 'augh' not in word: return
    if 'AA' in arpabet or 'AO' in arpabet or 'AH' in arpabet:
        categories['augh'].append(word)

def oughCheck(word: str, arpabet: str) -> None:
    if 'ough' not in word: return
    if 'AA' in arpabet or 'AO' in arpabet or 'AH' in arpabet:
        categories['ough'].append(word)

def ieCheck(word: str, arpabet: str) -> None:
    if 'ie' not in word: return
    if 'AY' in arpabet:
        categories['ie as in pie'].append(word)

    elif 'IY' in arpabet:
        categories['ie as in thief'].append(word)

def sionCheck(word: str, arpabet: str) -> None:
    if 'sion' not in word: return
    if 'SH' in arpabet:
        categories['-sion as in tension'].append(word)

    elif 'ZH' in arpabet:
        categories['-sion as in vision'].append(word)

def threelBlends(word: str) -> None:
    if (word.startswith('spr') or word.startswith('spl') or word.startswith('thr') or word.startswith('scr') or word.startswith('shr') or word.startswith('str')):
        categories['3-letter beg. blends'].append(word)

def vccvCheck(word: str, arpabet: str) -> None:
    if len(word) < 4: return
    for i in range(len(word) - 3):  # Changed to -3 since we need 4 characters (VCCV)
        if (word[i] in VOWELS and 
            word[i+1] in CONSONANTS and 
            word[i+2] in CONSONANTS and 
            word[i+3] in VOWELS):
            if len(word) > i + 4:
                categories['vccv'].append(word)
                return

def vceCheck(word: str) -> None:
    if len(word) < 3: return
    if (word[-3].lower() in VOWELS and
        word[-2].lower() in CONSONANTS and
        word[-1].lower() == 'e'):
        categories['vce'].append(word)
        
def OCECheck(word: str, arpabet: str) -> None:
    if len(word) < 2: return
    tokens = arpabet.split()
    # Open syllables: Check if the last sound is a long vowel sound
    if tokens[-1] in ['AY', 'EY', 'IY', 'OW', 'UW'] and word[-1] in VOWELS:
        categories['Open syll.'].append(word)
        return
    # Closed syllables: Check if it has a short vowel sound followed by a consonant sound
    if word[-1] in CONSONANTS and word[-2] in VOWELS:
        for i in range(len(tokens) - 1):
            if (tokens[i] in ['AE', 'EH', 'IH', 'AA', 'AH', 'UH'] and 
            tokens[i + 1] not in ['AY', 'EY', 'IY', 'OW', 'UW', 'AE', 'EH', 'IH', 'AA', 'AH', 'UH']):
                if word[-1] == 's':
                    root_word = word[:-1]
                    if root_word in valid_words or root_word[-1] in VOWELS:
                        return
                elif word.endswith('ed'):
                    root_word = word[:-1] # Remove 'd'
                    if root_word in valid_words or root_word[-1] in VOWELS:
                        return
                    root_word = word[:-2] # Remove 'ed'
                    if root_word in valid_words or root_word[-1] in VOWELS:
                        return  
                categories['Closed syll.'].append(word)
                return

def vcvCheck(word: str) -> None:
    if len(word) < 3: return
    for i in range(len(word) - 2):  # Iterate through the word for 3-letter patterns
        if (word[i] in VOWELS and word[i+1] in CONSONANTS and word[i+2] in VOWELS):
            categories['vcv, vcccv patterns'].append(word)

def vcccvCheck(word: str) -> None:
    if len(word) < 5: return
    for i in range(len(word) - 4):  # Iterate through the word for 5-letter patterns
        if (word[i] in VOWELS and word[i+1] in CONSONANTS and 
            word[i+2] in CONSONANTS and word[i+3] in CONSONANTS and 
            word[i+4] in VOWELS):
            categories['vcv, vcccv patterns'].append(word)

def vrlCheck(word: str) -> None:
    if len(word) < 3: return
    for r in ['ar', 'er', 'ir', 'or', 'ur']:
        if r in word:
            categories['r syllables'].append(word)
            break 
    for l in ['ol', 'al', 'ul', 'el', 'il']:
        if l in word:
            categories['l syllables'].append(word)
            break  
    for v in ['iv', 'av', 'ov', 'uv', 'ev']:
        if v in word:
            categories['v syllables'].append(word)
            break  

def vvCheck(word: str, arpabet: str) -> None:
    if len(word) < 3: return
    i = 0
    while i < len(word):
        for comp in vv_sounds:
            if word[i:i + len(comp)] == comp:
                compound = word[i: i+len(comp)]
                if is_vv(compound, arpabet):
                    categories['v/v pattern'].append(word)
        i += 1

def shouldDoubleConsonant(word: str, arpabet: str) -> None:
    if len(word) < 2: return
    last_char = word[-1]
    second_last_char = word[-2]
    # Step 1: Check if the word ends with a single consonant preceded by a vowel
    if last_char not in VOWELS and second_last_char in VOWELS:
        # Check syllable count and stress pattern using pronouncing library
        if arpabet:
            # Use the first ARPAbet pronunciation available
            syllable_count = pronouncing.syllable_count(arpabet)
            stress_pattern = pronouncing.stresses(arpabet)
            # Apply the Doubling Rule based on syllable count and stress
            if syllable_count == 1 or (stress_pattern and stress_pattern[-1] == '1'):
                categories['double rule-suffixes'].append(word)

def fszlCheck(word: str, arpabet: str) -> None:
    if len(word) < 3 or word[-1] not in 'fszl' or word[-2] not in 'fszl' or word[-1] != word[-2]: return
    tokens = arpabet.split()
    for vowel in ['IH', 'EH', 'AH', 'UH', 'AA', 'AE']:
        if vowel in tokens[-2]:
            categories['fszl'].append(word)
    
# Precompile the regex patterns
yRulePatterns = re.compile(r'[^aeiou](ies|ied|ier|iest)$')
vowelYPattern = re.compile(r'[aeiou]y')

def isYRuleSuffix(word: str) -> bool:
    EXCEPTIONS = {'frontier', 'glacier', 'soldier', 'barrier', 'carrier', 'pier', 'priest', 'series', 'species'}
    if word in EXCEPTIONS:
        return

    if yRulePatterns.search(word): # Check for patterns where Y changes to I
        categories['y rule suffixes'].append(word)
    if word.endswith('ying'): # Check for "ying" suffix
        categories['y rule suffixes'].append(word)
    # Disallow words with Vowel + Y patterns
    if vowelYPattern.search(word):
        return 
    # Final check for "ies" pattern without VOWELS before "y"
    if word.endswith('ies') and not 'y' in word[:word.rfind('ies')]:
        categories['y rule suffixes'].append(word)
    return 

def getWords(text: str) -> set:
    words = re.findall(r'\b[A-Za-z]+\'?[A-Za-z]*\b', text.lower())
    return set(words)

def callCategorizationFunctions(word: str, arpabet: str, syllable_count: int) -> None:
    hardVsSoftC(word, arpabet)
    hardVsSoftG(word, arpabet)
    yCheck(word, arpabet)
    ooCheck(word, arpabet)
    owCheck(word, arpabet)
    earCheck(word, arpabet)
    eaCheck(word, arpabet)
    sBlends(word)
    lBlends(word)
    rBlends(word)
    ewCheck(word, arpabet)
    ouCheck(word, arpabet)
    ueCheck(word, arpabet)
    eiCheck(word, arpabet)
    ieCheck(word, arpabet)
    chCheck(word, arpabet)
    sionCheck(word, arpabet)
    aughCheck(word, arpabet)
    oughCheck(word, arpabet)
    threelBlends(word)
    warCheck(word)
    allCheck(word)
    shouldDoubleConsonant(word, arpabet)
    vcvCheck(word)
    vvCheck(word, arpabet)
    vcccvCheck(word)
    isYRuleSuffix(word)
    vrlCheck(word)
    vceCheck(word)
    xInWordCheck(word, arpabet)
    ingongangungCheck(word)
    contractionsCheck(word)
    if syllable_count == 2:
        vccvCheck(word, arpabet)
    if syllable_count == 1:
        OCECheck(word, arpabet)
        fszlCheck(word, arpabet)

def parseAndProcessWords(story: str, output_path = "output.json") -> dict:
    try:
        words = getWords(story)
        unique_words = set(words)
        print('parsing through words. . .\n')
        for word in unique_words:
            word.lower()
            if word in sight_words:
                continue
            phones = pronouncing.phones_for_word(word)
            if not phones:
                print(f"\t'{word}' not found in the pronouncing library's dictionary.")
                categories['failed to categorize'].append(word)
                continue
            syllable_count = pronouncing.syllable_count(phones[0])
            arpabet = re.sub(r'\d', '', phones[0])
            callCategorizationFunctions(word, arpabet, syllable_count)
            
        if os.path.exists(output_path):
            os.remove(output_path)
        with open(output_path, 'w') as file:
            json.dump(categories, file, indent=4)

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Detailed traceback:")
        traceback.print_exc()
    return categories

def getTopWords(num: int, output_path: str) -> None:
    truncated_dict = {key: values[:num] for key, values in categories.items()}
    with open(output_path, 'w') as f:
        json.dump(truncated_dict, f, indent=4)
    print(f"Data successfully written to truncated_dictionary.json")

def main():
    input_path = os.path.join(script_dir, 'Dictionary.txt')
    output_path = os.path.join(script_dir, 'dictionary_categorized.json')
    output_path2 = os.path.join(script_dir, 'truncated_dictionary.json')
    with open(input_path, 'r') as f:
        story = f.read()
    parseAndProcessWords(story, output_path)
    getTopWords(20, output_path2)
if __name__ == "__main__":
    main()
