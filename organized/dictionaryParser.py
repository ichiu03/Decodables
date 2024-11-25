import json
import pronouncing
import os
import re
import nltk
import syllapy
from nltk.corpus import words
import shutil
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
    # Column 2 - All vowels (short & long)
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
sight_words = {'a', 'any', 'many', 'and', 'on', 'is', 'are', 'the', 'was', 'were', 'it', 'am', 'be', 'go', 'to', 'been', 'come', 'some', 'do', 'does', 'done', 'what', 'who', 'you', 'your', 'both', 'buy', 'door', 'floor', 'four', 'none', 'once', 'one', 'only', 'pull', 'push', 'sure', 'talk', 'walk', 'their', 'there', "they're", 'very', 'want', 'again', 'against', 'always', 'among', 'busy', 'could', 'should', 'would', 'enough', 'rough', 'tough', 'friend', 'move', 'prove', 'ocean', 'people', 'she', 'other', 'above', 'father', 'usually', 'special', 'front', 'thought', 'he', 'we', 'they', 'nothing', 'learned', 'toward', 'put', 'hour', 'beautiful', 'whole', 'trouble', 'of', 'off', 'use', 'have', 'our', 'say', 'make', 'take', 'see', 'think', 'look', 'give', 'how', 'ask', 'boy', 'girl', 'us', 'him', 'his', 'her', 'by', 'where', 'were', 'wear', 'hers', "don't", 'which', 'just', 'know', 'into', 'good', 'other', 'than', 'then', 'now', 'even', 'also', 'after', 'know', 'because', 'most', 'day', 'these', 'two', 'already', 'through', 'though', 'like', 'said', 'too', 'has', 'in', 'brother', 'sister', 'that', 'them', 'from', 'for', 'with', 'doing', 'well', 'before', 'tonight', 'down', 'about', 'but', 'up', 'around', 'goes', 'gone', 'build', 'built', 'cough', 'lose', 'loose', 'truth', 'daughter', 'son'}
vowels = set('aeiou')
consonants = set('bcdfghjklmnpqrstvwxyz')
compound_sounds = {
    'ai', 'au', 'ay', 'ae', 'ao', 'ar', 'ea', 'ee', 'ei', 'eo', 'eu', 'er',
    'ia', 'ie', 'io', 'iu', 'ir', 'oa', 'oe', 'oi', 'oo', 'ou', 'or', 'ua',
    'ue', 'ui', 'uo', 'ur', 'ough', 'augh', 'igh', 'eigh', 'tio', 'sio',
    'ey', 'oy', 'ew', 'ow', 'aw', 'ye', 'uie', 'oux', 'cally'
    }
vv_sounds = {
    'ai': ['AY IY'], 'ia': ['IY EY', 'IY AH', 'IY AE', 'AY AH'], 'ie': ['AY AH', 'AY IH'],
    'io': ['AY AH', 'IY OW', 'IY AA'], 'ea': ['IY AH', 'IY EH'], 'iu': ['IY AH', 'IY IH', 'IY UW'],
    'eo': ['IY ER', 'IY OW', 'IY AA'], 'ue': ['UW AH', 'UW EH'], 'eu': ['IY AH'], 'ao': ['EY AA'], 'ei': ['IY AH'], 
    'ua': ['UW EH', 'UW EY', 'AH W AH', 'AH W EY', 'UW W AH', 'UW EY', 'UW AH', 'UW AE']}

### Checks if compound vowel is a vowel/vowel -> yes is True
def is_vv(compound: str, arp: str) -> bool:
    for vow, phonemes in vv_sounds.items():
        if vow == compound:
            for pho in phonemes:
                if pho in arp:
                    return True
    return False

### Maps chunks of word to its phoneme, separating by vowels. Accounts for compound vowels as well. 
def map_chunks_to_phonemes(word: str) -> dict:
    def collect_and_map_phonemes(iterable, chunk, phoneme_list, chunk_to_phonemes):
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
        for comp in sorted(compound_sounds, key=len, reverse=True):
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
            collect_and_map_phonemes(phoneme_iter, current_chunk, current_phoneme_chunk, chunk_to_phonemes)
            current_chunk = ''
        # Case 3: Compound is team vowel
        elif compound and not is_vv(compound, arp):
            current_chunk += compound
            i += len(compound)
            collect_and_map_phonemes(phoneme_iter, current_chunk, current_phoneme_chunk, chunk_to_phonemes)
            current_chunk = ''
        # Case 4: Compound is vowel/vowel
        elif compound and is_vv(compound, arp):
            current_chunk += word[i]
            i += 1
            collect_and_map_phonemes(phoneme_iter, current_chunk, current_phoneme_chunk, chunk_to_phonemes)
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

def verification_to_add(word: str, arpabet: str, letters: str, desired_pho: list, problem_pho: list) -> bool:
    if not any(pho in arpabet for pho in desired_pho) or any(pho in arpabet for pho in problem_pho): return
    matches = False
    mapping = map_chunks_to_phonemes(word)
    for chunk, phoneme in mapping.items():
        if letters in chunk:
            for pho in desired_pho:
                if pho in phoneme:
                    matches = True
    return matches

def is_valid_presuf(wordbase: str) -> bool:
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

def x_in_word_check(word: str, arpabet: str) -> None:
    tokens = arpabet.split()
    keys = ['m', 'l', 'p', 'v', 'z', 'f', 'sh', 'ay', 'ck', 'ee', 'all', 'th', 'oy', 
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
    if 'r' in word and 'R' in tokens:
        if 'ar' in word or 'er' in word or 'ir' in word or 'or' in word or 'ur' in word:
            pass
        categories['r'].append(word)
    if 'a' in word:
        if 'EY' in tokens and verification_to_add(word, arpabet, 'a', ['EY'], ['AA', 'AH', 'AE']):
            categories['long a'].append(word)
        if ('AA' in tokens or 'AH' in tokens or 'AE' in tokens):
            if verification_to_add(word, arpabet, 'a', ['AA', 'AH', 'AE'], ['EY']):
                categories['short a'].append(word)
    if 'e' in word:
        if 'IH' in tokens and verification_to_add(word, arpabet, 'e', ['IH'], ['EH', 'AH']):
            categories['long e'].append(word)
        if ('EH' in tokens or 'AH' in tokens):
            if verification_to_add(word, arpabet, 'e', ['IH', 'AH'],['IH']):
                categories['short e'].append(word)
    if 'i' in word:
        if 'AY' in tokens and verification_to_add(word, arpabet, 'i', ['AY'], ['IH']): 
            categories['long i'].append(word)
        if 'IH' in tokens and verification_to_add(word, arpabet, 'i', ['IH'], ['AY']): 
            categories['short i'].append(word)
    if 'o' in word:
        if 'OW' in tokens and verification_to_add(word, arpabet, 'o', ['OW'], ['AH', 'AA', 'AO']):
            categories['long o'].append(word)
        if 'AH' in tokens or 'AA' in tokens or 'AO' in tokens: 
            if verification_to_add(word, arpabet, 'o', ['AH', 'AA', 'AO'], ['OW']):
                categories['short o'].append(word)
    if 'u' in word:
        if 'UW' in tokens and verification_to_add(word, arpabet, 'u', ['UW'], ['AH']): categories['long u'].append(word)
        if 'AH' in tokens and verification_to_add(word, arpabet, 'u', ['AH'], ['UW']): categories['short u'].append(word)
    if 'w' in word and 'W' in tokens:
        if 'wh' in word: # Check if there's 'w' and 'wh'
            w_index = word.index('wh')
            no_wh = word[: w_index] + word[w_index + 2:]
            if 'w' in no_wh: # still a 'w', after removing 'wh'
                categories['w'].append(word)
        else:
            categories['w'].append(word)
    if 'qu' in word and 'K W' in arpabet: categories['qu'].append(word)
    if 'ch' in word and 'CH' in tokens: categories['ch'].append(word)
    if 'or' in word and 'AO R' in arpabet: categories['or'].append(word)
    if 'ar' in word and 'AA R' in arpabet: categories['ar'].append(word)
    if word[-2:] == 'ly' and tokens[-1] == 'IY': categories['ly'].append(word)
    if 'ing' in word or 'ang' in word or 'ong' in word or 'ung' in word: categories['-ing, -ong, -ang, -ung'].append(word)
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

def yCheck(word: str, arpabet: str) -> None:   
    # 'y as in yes' (initial /Y/ sound)
    if 'ye' in word or 'ya' in word or 'yo' in word:
        if 'Y EH' in arpabet or 'Y OW' in arpabet or 'Y AO' in arpabet or 'Y UH' in arpabet or 'Y AH' in arpabet:
            categories['y as in yes'].append(word)
    # 'y as in dry' (long 'i' sound, represented by 'AY1' in ARPAbet)
    if 'AY' in arpabet: categories['y as in dry'].append(word)
    # 'y as in bumpy' (unstressed 'IY0' sound in ARPAbet)
    elif 'IY' in arpabet: categories['y as in bumpy'].append(word)
    # 'y in gym' (short 'i' sound, 'IH1' in ARPAbet)
    if 'IH' in arpabet: categories['y as in gym'].append(word) 
    # '-ey as in monkey' (ending with unstressed 'IY0')
    if arpabet.endswith('IY') and word.endswith('ey'): categories['ey as in monkey'].append(word)
    # 'ey as in they' (long 'EY1' sound)
    elif 'ey' in word and 'EY' in arpabet: categories['ey as in they'].append(word)

def hard_vs_soft_C(word: str, arpabet: str) -> None:
    tokens = arpabet.split()
    hard_verification = verification_to_add(word, arpabet, 'c', ['K'], ['S'])
    soft_verification = verification_to_add(word, arpabet, 'c', ['S'], ['K'])
    if 'exce' in word and 'S' in tokens: categories['soft c'].append(word)
    elif hard_verification and soft_verification: return
    elif 'K' in tokens and hard_verification: categories['hard c'].append(word)
    elif 'S' in tokens and soft_verification: categories['soft c'].append(word)

def hard_vs_soft_G(word: str, arpabet: str) -> None:
    tokens = arpabet.split()
    hard_verification = verification_to_add(word, arpabet, 'g', ['G'], ['JH'])
    soft_verification = verification_to_add(word, arpabet, 'g', ['JH'], ['G'])
    if hard_verification and soft_verification: return
    elif 'G' in tokens and hard_verification: categories['hard g'].append(word)
    elif 'JH' in arpabet and soft_verification: categories['soft g'].append(word)

def oo_check(word: str, arpabet: str) -> None:
    if 'UW' in arpabet:
        categories['oo as in school'].append(word)

    if 'UH' in arpabet:
        categories['oo as in book'].append(word)

def ow_check(word: str, arpabet: str) -> None:
    if 'AW' in arpabet:
        categories['ow as in plow'].append(word)

    if 'OW' in arpabet:
        categories['ow as in snow'].append(word)

def ear_check(word: str, arpabet: str) -> None:
    if 'IH R' in arpabet or 'IY R' in arpabet:
        categories['ear as in hear'].append(word)
    elif 'ER' in arpabet:
        categories['ear as in early'].append(word)

def s_blends(word: str) -> None:
    if word.startswith('sn') or word.startswith('sm') or word.startswith('st') or word.startswith('sw') or word.startswith('sc') or word.startswith('sp'):
        if word[2] in vowels:
            categories['s blends'].append(word)
    
def l_blends(word: str) -> None:
    if word.startswith('bl') or word.startswith('cl') or word.startswith('fl') or word.startswith('pl') or word.startswith('gl') or word.startswith('sl'):
        if word[2] in vowels:
            categories['l blends'].append(word)

def r_blends(word: str) -> None:
    if word.startswith('br') or word.startswith('cr') or word.startswith('dr') or word.startswith('fr') or word.startswith('gr') or word.startswith('pr') or word.startswith('tr'):
        if word[2] in vowels:
            categories['r blends'].append(word)

def ea_check(word: str, arpabet: str) -> None:
    if 'IY' in arpabet:
        categories['ea as in eat'].append(word)
    if 'EH' in arpabet and 'EH R' not in arpabet:
        categories['ea as in bread'].append(word)

def vce_check(word: str) -> None:
    for i in range(len(word) - 2):
        if (word[i].lower() in vowels and
            word[i + 1].lower() in consonants and
            word[i + 2].lower() == 'e'):
            categories['vce'].append(word)
        
def OCE_check(word: str, arpabet: str) -> None:
    tokens = arpabet.split()
    # Open syllables (ends in hard vowel)
    if word[-1] in vowels and len(word) > 1:
        if not(word[-1] == 'e' and 'IY' not in tokens[-1]):
            categories['Open syll.'].append(word)
    # Closed syllables (eg cat, man)
    for i in range(len(word) - 1):
        if word[i] in vowels and word[i + 1].lower() not in vowels:
            categories['Closed syll.'].append(word)
            return
        
def ew_check(word: str, arpabet: str) -> None:
    if 'UW' in arpabet:
        categories['ew as in few/blew'].append(word)

def ou_check(word: str, arpabet: str) -> None:
    if 'AW' in arpabet:
        categories['ou as in south'].append(word)

def ue_check(word: str, arpabet: str) -> None:
    if 'UW' in arpabet:
        categories['ue as in blue'].append(word)

def ei_check(word: str, arpabet: str) -> None:
    if 'IY' in arpabet:
        categories['ei as in receive'].append(word)
    elif 'EY' in arpabet:
        categories['ei as in vein'].append(word)

def ch_check(word: str, arpabet: str) -> None:
    ch_index = word.find('ch')
    if ch_index != -1:
        tokens = arpabet.split()
        try:
            if tokens[ch_index] == 'K':
                categories['ch as in echo'].append(word)
        except IndexError:
            pass

def augh_check(word: str, arpabet: str) -> None:
    if 'AA' in arpabet or 'AO' in arpabet or 'AH' in arpabet:
        categories['augh'].append(word)

def ough_check(word: str, arpabet: str) -> None:
    if 'AA' in arpabet or 'AO' in arpabet or 'AH' in arpabet:
        categories['ough'].append(word)

def ie_check(word: str, arpabet: str) -> None:
    if 'AY' in arpabet:
        categories['ie as in pie'].append(word)

    elif 'IY' in arpabet:
        categories['ie as in thief'].append(word)

def sion_check(word: str, arpabet: str) -> None:
    if 'SH' in arpabet:
        categories['-sion as in tension'].append(word)

    elif 'ZH' in arpabet:
        categories['-sion as in vision'].append(word)

def threel_blends(word: str) -> None:
    if (word.startswith('spr') or word.startswith('spl') or word.startswith('thr') or word.startswith('scr') or word.startswith('shr') or word.startswith('str')):
        categories['3-letter beg. blends'].append(word)

def vccv(word: str) -> None:
    for i in range(len(word) - 3):
        if (word[i] in vowels and word[i+1] in consonants and 
            word[i+2] in consonants and word[i+3] in vowels):
            categories['vccv'].append(word)

def vcv(word: str) -> None:
    for i in range(len(word) - 2):  # Iterate through the word for 3-letter patterns
        if (word[i] in vowels and word[i+1] in consonants and word[i+2] in vowels):
            categories['vcv, vcccv patterns'].append(word)

def vcccv(word: str) -> None:
    for i in range(len(word) - 4):  # Iterate through the word for 5-letter patterns
        if (word[i] in vowels and word[i+1] in consonants and 
            word[i+2] in consonants and word[i+3] in consonants and 
            word[i+4] in vowels):
            categories['vcv, vcccv patterns'].append(word)

def vrl_check(word: str) -> None:
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

def vv_check(word: str, arpabet: str) -> None:
    i = 0
    while i < len(word):
        for comp in vv_sounds:
            if word[i:i + len(comp)] == comp:
                compound = word[i: i+len(comp)]
                if is_vv(compound, arpabet):
                    categories['v/v pattern'].append(word)
        i += 1

def should_double_consonant(word: str, arpabet: str) -> None:
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
            if syllable_count == 1 or (stress_pattern and stress_pattern[-1] == '1'):
                categories['double rule-suffixes'].append(word)

def fszl_check(word: str, arpabet: str) -> None:
    if pronouncing.syllable_count(arpabet) == 1:
        tokens = arpabet.split()
        for vowel in ['IH', 'EH', 'AH', 'UH', 'AA', 'AE']:
            if vowel in tokens[-2]:
                categories['fszl'].append(word)
    
# Precompile the regex patterns
y_rule_patterns = re.compile(r'[^aeiou](ies|ied|ier|iest)$')
vowel_y_pattern = re.compile(r'[aeiou]y')

def is_y_rule_suffix(word: str) -> bool:
    EXCEPTIONS = {'frontier', 'glacier', 'soldier', 'barrier', 'carrier', 'pier', 'priest', 'series', 'species'}
    if word in EXCEPTIONS:
        return False

    if y_rule_patterns.search(word): # Check for patterns where Y changes to I
        return True
    if word.endswith('ying'): # Check for "ying" suffix
        return True

    # Disallow words with Vowel + Y patterns
    if vowel_y_pattern.search(word):
        return False

    # Final check for "ies" pattern without vowels before "y"
    if word.endswith('ies') and not 'y' in word[:word.rfind('ies')]:
        return True

    return False

def get_words(story: str) -> list:
    words = re.findall(r'\b\w+\b', story)
    return words

def parse_and_process_words(story: str, output_path = "output.json") -> dict:
    try:
        words = get_words(story)
        unique_words = set(words)
        print('-=-=-= Parsing through words =-=-=-\n')
        for word in unique_words:
            word.lower()
            if word in sight_words:
                continue
            phones = pronouncing.phones_for_word(word)
            if not phones:
                print(f"\t'{word}' not found in the pronouncing library's dictionary.")
                categories['failed to categorize'].append(word)
                continue
            
            arpabet = re.sub(r'\d', '', phones[0])
            
            if 'c' in word:
                hard_vs_soft_C(word, arpabet)
            if 'g' in word:
                hard_vs_soft_G(word, arpabet)
            if 'y' in word:
                yCheck(word, arpabet)
            if "'" in word:
                categories['contractions'].append(word)
            if 'oo' in word:
                oo_check(word, arpabet)
            if 'ow' in word:
                ow_check(word, arpabet)
            if 'ear' in word:
                ear_check(word, arpabet)
            if 'ea' in word:
                ea_check(word, arpabet)
            if 's' in word:
                s_blends(word)
            if 'l' in word:
                l_blends(word)
            if 'r' in word:
                r_blends(word)
            if 'ew' in word:
                ew_check(word, arpabet)
            if 'ou' in word:
                ou_check(word, arpabet)
            if 'ue' in word:
                ue_check(word, arpabet)
            if 'ei' in word:
                ei_check(word, arpabet)
            if 'ie' in word:
                ie_check(word, arpabet)
            if 'ch' in word:
                ch_check(word, arpabet)
            if 'sion' in word:
                sion_check(word, arpabet)
            if 'augh' in word:
                augh_check(word, arpabet)
            if 'ough' in word:
                ough_check(word, arpabet)
            if 'r' or 'l' in word:
                threel_blends(word)
            if 'war' in word:
                warCheck(word)
            if len(word) > 3 and word[-1] in 'fszl' and word[-2] in 'fszl' and word[-1] == word[-2]:
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
                categories['y rule suffixes'].append(word)
            #if is_e_rule_suffix(word):
                #categories['e rule-suffixes'].append(word)
            if 'v' in word or 'l' in word or 'r' in word:
                vrl_check(word)
            
            vce_check(word)
            OCE_check(word, arpabet)
            x_in_word_check(word, arpabet)

        if os.path.exists(output_path):
            os.remove(output_path)
        with open(output_path, 'w') as file:
            json.dump(categories, file, indent=4)

        print("\n-=-=-= Finished categorzing! Saved to 'categorized_words.json' =-=-=-")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Detailed traceback:")
        traceback.print_exc()
    return categories

def getTopWords(num: int, input_path: str, output_path: str) -> None:
    with open(input_path, 'r') as f:
        data_dict = json.load(f)
    truncated_dict = {key: values[:num] for key, values in categories.items()}
    with open(output_path, 'w') as f:
        json.dump(truncated_dict, f, indent=4)
    
    print(f"Data successfully written to truncated_dictionary.json")

def main():
    filename = 'Dictionary.txt' 
    input_path = os.path.join(script_dir, filename)
    output_path = os.path.join(script_dir, 'dictionary_categorized.json')
    with open(input_path, 'r') as f:
        story = f.read()
    parse_and_process_words(story, output_path)

main()

### Takes in a list of all the problem categories and makes sure every categories doesn't have words from 
### any of the categories. 
def ridOverlap(problemCategories: list) -> None:
    badWords = []
    for category in problemCategories:
        badWords.extend(categories[category])
    badWords = set(badWords)  # Deduplicate

    for key, value in categories.items():
        categories[key] = [word for word in value if word not in badWords]
