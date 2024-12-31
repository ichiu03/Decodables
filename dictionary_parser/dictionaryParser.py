import json
import pronouncing
import os
import re
import nltk
from nltk.corpus import words
from nltk.corpus import wordnet
import traceback

# Get the directory where `dictionaryParser.py` is located
path = os.path.dirname(os.path.abspath(__file__))

# Ensure the script checks locally for nltk_data
os.environ['NLTK_DATA'] = os.path.expanduser('~/nltk_data')

# Check if 'words' from nltk is already downloaded
try:
    valid_words = set(words.words())
except LookupError:
    nltk.download('words')
    valid_words = set(words.words())

# Check if 'wordnet' is already downloaded
try:
    wordnet.synsets('test')
except LookupError:
    nltk.download('wordnet')

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
    'ea as in bread': [], '3-letter beg. blends': [], 'vcv': [], 'vcccv': [], 'tch': [], 'soft c': [],
    '-ble, -cle, -dle, -fle, -gle, -kle, -ple, -tle, -zle': [], 'soft g': [], 'ai': [], 'igh': [], 'ed': [],
    'cle ending': [], 'vowel_team': [], 'r-controlled': [], 'oa': [], 'ir': [], '-ild, -ind, -old, -ost': [],
    'oi': [], 'double rule-suffixes': [], 'ew as in few/blew': [], 'v/v pattern': [], 'kn': [], 'e rule-suffixes': [],
    'ou as in south': [], 'ur': [], 'dge': [], 'y rule suffixes': [], 'tion': [],
    # Column 5
    'au': [], 'war': [], 'ey as in monkey': [], 'ey as in they': [], 'ph': [],
    'ie as in pie': [], 'ie as in thief': [], '-sion as in tension': [], '-sion as in vision' : [],
    'y as in gym': [], 'wr': [], 'eigh': [], 'ue as in blue': [], 'ough': [], 'wor': [], 'ei as in receive': [],
    'ei as in vein': [], 'augh': [], 'oe': [], 'ui': [], 'ch as in echo': [], 'wa': [], 'eu': [], 'gh': [], 'mb': [],
    'mn': [], 'que': [], 'gn': [], 'stle': [],'rh': [], 'gue': [], 'alk': [], 'alt': [], 'qua': [], 'sc': [],
    # Uncategorized
    'failed to categorize': [], 'too many syllables': []
}
vv_sounds = { # To add more v/v sounds, add them here AND into COMPOUND_SOUNDS
    'ai': ['AY IY'], 'ia': ['IY EY', 'IY AH', 'IY AE', 'AY AH'], 'ie': ['AY AH', 'AY IH', 'IY AH'],
    'io': ['AY AH', 'IY OW', 'IY AA'], 'ea': ['IY AH', 'IY EH'], 'iu': ['IY AH', 'IY IH', 'IY UW'],
    'eo': ['IY ER', 'IY OW', 'IY AA'], 'ue': ['UW AH', 'UW EH'], 'eu': ['IY AH', 'IY UW'], 'ao': ['EY AA'], 'ei': ['IY AH', 'IY IH'],
    'ua': ['UW EH', 'UW EY', 'AH W AH', 'AH W EY', 'UW W AH', 'UW EY', 'UW AH', 'UW AE'], 'oa': ['OW AH', 'OW AE'],
    'oe': ['UW EH', 'OW AH', 'AA IH', 'OW IH', 'UW ER', 'OW ER'], 'ui': ['UW IH', 'UW AH', 'Y UW AH', 'Y UW AY'],
    'ior': ['IY ER'], 'oir': ['AY ER']
    }
sight_words = {'eye', 'everyone', 'approve', 'prove', "who's", 'whom', 'heart', 'abroad', 'beauty', 'bouquet', 'building', 'builds', 'rebuild', 'builder', "doesn't", 'shoe', 'shoelace', 'laughter', 'laugh', 'laughed', 'laughs', 'roughly', 'although', 'thoroughly', 'throughout', 'dough', 'doughnut', 'sovereighnty', 'a', 'any', 'many', 'and', 'on', 'is', 'are', 'the', 'was', 'were', 'it', 'am', 'be', 'go', 'to', 'been', 'come', 'some', 'do', 'does', 'done', 'what', 'whoever', 'who', 'you', 'your', 'both', 'buy', 'door', 'floor', 'four', 'none', 'once', 'one', 'only', 'pull', 'push', 'sure', 'talk', 'walk', 'their', 'there', "they're", 'very', 'want', 'again', 'against', 'always', 'among', 'busy', 'could', 'should', 'would', 'enough', 'rough', 'tough', 'friend', 'move', 'prove', 'ocean', 'people', 'she', 'other', 'above', 'father', 'usually', 'special', 'front', 'thought', 'he', 'we', 'they', 'nothing', 'learned', 'toward', 'put', 'hour', 'beautiful', 'whole', 'trouble', 'of', 'off', 'use', 'have', 'our', 'say', 'make', 'take', 'see', 'think', 'look', 'give', 'how', 'ask', 'boy', 'girl', 'us', 'him', 'his', 'her', 'by', 'where', 'were', 'wear', 'hers', "don't", 'which', 'just', 'into', 'good', 'other', 'than', 'then', 'now', 'even', 'also', 'after', 'know', 'because', 'most', 'day', 'these', 'two', 'already', 'through', 'though', 'like', 'said', 'too', 'has', 'in', 'brother', 'sister', 'that', 'them', 'from', 'for', 'with', 'doing', 'well', 'before', 'tonight', 'down', 'about', 'but', 'up', 'around', 'goes', 'gone', 'build', 'built', 'cough', 'lose', 'loose', 'truth', 'daughter', 'son'}
VOWELS = frozenset('aeiou')
CONSONANTS = frozenset('bcdfghjklmnpqrstvwxyz')
COMPOUND_SOUNDS = frozenset({
    'ai', 'au', 'ay', 'ae', 'ao', 'ar', 'ea', 'ee', 'ei', 'eo', 'eu', 'er',
    'ia', 'ie', 'io', 'iu', 'ir', 'oa', 'oe', 'oi', 'oo', 'ou', 'or', 'ua',
    'ue', 'ui', 'uo', 'ur', 'ough', 'augh', 'igh', 'eigh', 'tio', 'sio',
    'ey', 'oy', 'ew', 'ow', 'aw', 'ye', 'uie', 'oux', 'cally', 'ear', 'tch', 'ior', 'oir'
    })
# Vowel phonemes, without R controlled phonemes
VOWEL_PHONEMES = frozenset({'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW'})
# Precompile the regex patterns
yRulePatterns = re.compile(r'[^aeiou](ies|ied|ier|iest)$')
vowelYPattern = re.compile(r'[aeiou]y')

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
    # Check if BOTH a desired phoneme AND a problem phoneme are present. if not, then passes check to add
    if not (any(pho in arpabet for pho in desired_pho) or any(pho in arpabet for pho in problem_pho)): return True
    matches = False
    mapping = mapChunksToPhonemes(word)
    keys = list(mapping.keys())  # for vce edge case
    for i, (chunk, phoneme) in enumerate(mapping.items()):
        if letters in chunk:
            edge_cases = (
                (letters == 'c' and 'ch' in chunk and desired_pho == ['K']) or  # hard c edge cases
                (letters == 'a' and ('ai' in chunk or 'ay' in chunk) and desired_pho == ['EY']) or  # long a edge cases
                (letters == 'g' and 'dge' in chunk and desired_pho == ['JH']) or
                (letters == 'a' and ('ar' in chunk or 'wa' in chunk) and desired_pho == ['AA', 'AH', 'AE']) or  # short a edge cases
                (letters == 'o' and ('or' in chunk or 'tio' in chunk) and desired_pho == ['AH', 'AA', 'AO']) or  # short o edge case
                (letters == 'u' and 'ue' in chunk and desired_pho == ['UW']) or  # long u edge case
                (letters == 'u' and 'ur' in chunk and desired_pho == ['AH'])  # short u edge case
            )
            if edge_cases:
                continue
            phonemes = [re.sub(r'\d', '', p) for p in phoneme.split()]
            if any(pho in phonemes for pho in desired_pho):
                if not (  # prevent a vce from being flagged as long a
                    letters == 'a' and
                    desired_pho == ['EY'] and
                    (i <= len(keys) - 2) and
                    vceBool(chunk + keys[i + 1])
                ) and not (  # prevent an -ank from being flagged as short a
                    letters == 'a' and
                    desired_pho == ['AA', 'AH', 'AE'] and
                    (i <= len(keys) - 2) and
                    'ank' in chunk + keys[i + 1]
                ) and not (  # prevent a vce from being flagged as long i
                    letters == 'i' and
                    desired_pho == ['AY'] and
                    (i <= len(keys) - 2) and
                    vceBool(chunk + keys[i + 1])
                ) and not (
                    letters == 'o' and
                    desired_pho == ['OW'] and
                    longOEdgeCase(chunk + keys[i + 1] if i <= len(keys) - 2 else chunk)
                ) and not (  # prevent a vce from being flagged as long u
                    letters == 'u' and
                    desired_pho == ['UW'] and
                    (i <= len(keys) - 2) and
                    vceBool(chunk + keys[i + 1])
                ) and not (  # prevent a vce from being flagged as long o
                    letters == 'o' and
                    desired_pho == ['OW'] and
                    (i <= len(keys) - 2) and
                    vceBool(chunk + keys[i + 1])
                ):
                    matches = True

    return matches


### Helper function for long o edge cases
def longOEdgeCase(word: str):
    return 'ost' in word or 'old' in word or 'ow' in word or 'oll' in word or 'oa' in word

### The "easier" categories are categorized here
def xInWordCheck(word: str, arpabet: str, tokens: list) -> None:
    keys = ['m', 'l', 'p', 'v', 'z', 'f', 'sh', 'ay', 'ck', 'ee', 'th',
        'wh', 'tch', 'ai', 'dge', 'tion',
        'ough', 'wr', 'augh', 'stle', 'alk', 'ph']
    if 'er' in word and 'ER' in tokens: categories['er'].append(word)
    if 'oy' in word and 'OY' in tokens: categories['oy'].append(word)
    if 'oa' in word and verificationToAdd(word, arpabet, 'oa', ['OW'], ['AO']): categories['oa'].append(word)
    if (word.endswith('ble') or word.endswith('cle') or word.endswith('dle') or word.endswith('fle') or
        word.endswith('gle') or word.endswith('ple') or word.endswith('tle') or word.endswith('zle') or word.endswith('kle')):
        categories['-ble, -cle, -dle, -fle, -gle, -kle, -ple, -tle, -zle'].append(word)
    if 'k' in word and 'K' in tokens: categories['k'].append(word)
    if 'j' in word and 'JH' in tokens: categories['j'].append(word)
    if 'oi' in word and 'OY' in tokens: categories['oi'].append(word)
    if 'ir' in word and 'ER' in tokens and 'irr' not in word and 'ire' not in word:
        if verificationToAdd(word, arpabet, 'ir', ['ER'], ['IR']): categories['ir'].append(word)
    if 's' in word:
        if 'S' in tokens or 'Z' in tokens:
            if verificationToAdd(word, arpabet, 's', ['S', 'Z'], ['SH']): categories['s'].append(word)
    if 't' in word and 'T' in tokens: categories['t'].append(word)
    if 'b' in word and 'B' in tokens: categories['b'].append(word)
    if 'd' in word and 'D' in tokens: categories['d'].append(word)
    if 'n' in word and 'N' in tokens: categories['n'].append(word)
    if 'p' in word and 'P' in tokens: categories['p'].append(word)
    if 'h' in word and 'HH' in tokens: categories['h'].append(word)
    if 'x' in word and 'K S' in arpabet and 'K SH' not in arpabet: categories['x'].append(word)
    if 'qu' in word and 'K W' in arpabet:
        index = word.find('qu')
        if not (word[index+1] == 'a'): categories['qu'].append(word)
    if 'ch' in word and 'CH' in tokens and verificationToAdd(word, arpabet, 'ch', ['CH'], ['K']): categories['ch'].append(word)
    if 'or' in word and 'AO R' in arpabet and 'warrior' not in word: categories['or'].append(word)
    if 'au' in word and 'AH' in arpabet:
        index = word.find('au')
        if len(word) > index+2:
            if word[index+2] != 'r':
                categories['au'].append(word)
    if 'eigh' in word and 'EY' in arpabet: categories['eigh'].append(word)
    if 'oe' in word and not (is_vv('oe', arpabet)) and 'OW' in arpabet: categories['oe'].append(word)
    if 'eu' in word and not (is_vv('eu', arpabet)) and 'UW' in arpabet: categories['eu'].append(word)
    if 'mb' in word and 'M B' not in arpabet: categories['mb'].append(word)
    if 'mn' in word and 'M N' not in arpabet: categories['mn'].append(word)
    if 'que' in word and 'K W' not in arpabet: categories['que'].append(word)
    if 'gn' in word and 'G N' not in arpabet: categories['gn'].append(word)
    if 'qua' in word and 'K W A' in arpabet: categories['qua'].append(word)
    if 'sc' in word and 'S K' not in arpabet and 'SH' not in arpabet: categories['sc'].append(word)
    if 'alt' in word:
        tokens = arpabet.split()
        for i in range(len(tokens)-2):  # Subtract 2 to avoid index out of range
            if tokens[i] == 'AA' or tokens[i] == 'AH' or tokens[i] == 'AO':
                if tokens[i+1] == 'L' and tokens[i+2] == 'T':
                    categories['alt'].append(word)
    if 'gue' in word:
        if 'G Y' not in arpabet and 'G EH' not in arpabet: categories['gue'].append(word)
    if 'rh' in word:
        tokens = arpabet.split()
        for token in tokens:
            if 'R' in token:
                if verificationToAdd(word, arpabet, 'rh', ['R'], ['HH']):
                    categories['rh'].append(word)
    if 'wa' in word:
        if 'AA' in arpabet or 'AO' in arpabet:
            index = word.find('wa')
            if word[index+2] != 'r' and word[index+2] != 'y': categories['wa'].append(word)
    if 'ui' in word and not (is_vv('ui', arpabet)):
        index = word.find('ui')
        if word[index-1] != 'q' and word[index-1] != 'g' and word[index-1] != 'c': categories['ui'].append(word)
    if 'wor' in word:
        index = word.find('wor')
        if word[index+3] != 'e' and 'ER' in arpabet:
            categories['wor'].append(word)
    if 'ur' in word and 'ER' in tokens:
        index = word.find('ur')
        if word[index-1] == 'o': pass
        elif index+1 == len(word): categories['ur'].append(word) # Are last two letters
        elif len(word) > index+2:
            if word[index+2] in CONSONANTS: categories['ur'].append(word) # Is followed by a consonant
    if 'ar' in word and 'AA R' in arpabet: categories['ar'].append(word)
    if word[-2:] == 'ly' and tokens[-1] == 'IY':
        root_word = word[:-2]
        if root_word in valid_words: categories['ly'].append(word)
    if 'r' in word and 'R' in tokens:
        if 'ar' in word or 'er' in word or 'ir' in word or 'or' in word or 'ur' in word:
            pass
        categories['r'].append(word)
    if 'w' in word and 'W' in tokens:
        if 'wh' in word: # Check if there's 'w' and 'wh'
            w_index = word.index('wh')
            no_wh = word[: w_index] + word[w_index + 2:]
            if 'w' in no_wh: # still a 'w', after removing 'wh'
                categories['w'].append(word)
        else:
            categories['w'].append(word)
    if 'ink' in word or 'ank' in word or 'onk' in word or 'unk' in word and 'unknown' not in word: categories['-ink, -ank, -onk, -unk'].append(word)
    if word.endswith('ft') or word.endswith('st') or word.endswith('nd'): categories['-ft, -nd, -st'].append(word)
    if word.endswith('sp') or word.endswith('nt') or word.endswith('mp'): categories['-sp, -nt, -mp'].append(word)
    if word.endswith('sk') or word.endswith('lt') or word.endswith('lk'): categories['-sk, -lt, -lk'].append(word)
    if word.endswith('ct') or word.endswith('pt'): categories['-ct, -pt'].append(word)
    if 'igh' in word:
        index = word.find('igh')
        if word[index-1] not in 'eia':
            categories['igh'].append(word)
    if 'ild' in word or 'ind' in word:
        if 'AY' in arpabet: categories['-ild, -ind, -old, -ost'].append(word)
    if 'old' in word or 'ost' in word:
        if 'OH' in arpabet:categories['-ild, -ind, -old, -ost'].append(word)
    if 'aw' in word:
        if 'AO' in arpabet or 'AH' in arpabet or 'AA' in arpabet:
            if 'AH W' not in arpabet:
                categories['aw'].append(word)
    for key in keys:
        if key in word: categories[key].append(word)

def vowelCheck(word: str, arpabet: str, tokens: list) -> None:
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
            if verificationToAdd(word, arpabet, 'e', ['EH', 'AH'], ['IH']):
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
        if 'AH' in tokens and verificationToAdd(word, arpabet, 'u', ['AH'], ['UW']) and word not in {'stimulate', 'population'}:
            # exceptions to short u... for some reason their arpabet say they have the short u (AH) sound,
            # but they should be in long u (UW) category
            categories['short u'].append(word)


def edCheck(word: str) -> None:
    if word.endswith('ed'):
        root_word = word[:-1]  # Remove last letter, for words that end with e
        root_word2 = word[:-2] # Remove last two letters, for words that end with ed
        root_word3 = word[:-3] # Remove last three letters, for words that end with a doubled last letter and ed
        if root_word in valid_words or root_word2 in valid_words or root_word3 in valid_words:
            categories['ed'].append(word)

def warCheck(word: str) -> None:
    if 'war' in word and 'ware' not in word: categories['war'].append(word)

def ghCheck(word: str, arpabet: str) -> None:
    if 'gh' not in word: return
    if 'G' in arpabet and verificationToAdd(word, arpabet, 'gh', ['G'], ['HH']): categories['gh'].append(word)

def knCheck(word: str, arpabet: str) -> None:
    if 'kn' not in word: return
    if word == 'acknowledge': categories['kn'].append(word)
    mapping = mapChunksToPhonemes(word)
    for chunk, phoneme in mapping.items():
        if 'kn' in chunk:
            if 'K' in phoneme and 'N' in phoneme:
                continue
            elif 'N' in phoneme:
                categories['kn'].append(word)
                return

### Handles all words with 'y' and their categories
def yCheck(word: str, arpabet: str) -> None:
    if 'y' not in word: return
    if 'ye' in word or 'ya' in word or 'yo' in word:
        if 'Y EH' in arpabet or 'Y OW' in arpabet or 'Y AO' in arpabet or 'Y UH' in arpabet or 'Y AH' in arpabet:
            categories['y as in yes'].append(word)
    if 'AY' in arpabet:
        if verificationToAdd(word, arpabet, 'y', ['AY'], ['IH']) and 'yike' not in word:
            categories['y as in dry'].append(word)
    elif 'IY' in arpabet:
        if verificationToAdd(word, arpabet, 'y', ['IY'], ['IH']):
            categories['y as in bumpy'].append(word)
    if 'IH' in arpabet:
        if verificationToAdd(word, arpabet, 'y', ['IH'], ['IY']):
            if word != 'everything' and 'year' not in word:
                categories['y as in gym'].append(word)
    if arpabet.endswith('IY') and word.endswith('ey'):
        if verificationToAdd(word, arpabet, 'ey', ['IY'], ['EY']):
            categories['ey as in monkey'].append(word)
    if 'ey' in word and 'EY' in arpabet:
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

def allCheck(word: str, arpabet: str) -> None:
    if 'AO L' not in arpabet: return
    if word.endswith('ly'):
        if len(word) > 5:
            root_word = word[:-2]
            if 'all' in root_word:  
                categories['all'].append(word)
    elif 'all' in word:
        categories['all'].append(word)

def hardVsSoftC(word: str, arpabet: str, tokens: list) -> None:
    if 'c' not in word: return
    hard_verification = verificationToAdd(word, arpabet, 'c', ['K'], ['S'])
    soft_verification = verificationToAdd(word, arpabet, 'c', ['S'], ['K'])
    if 'exce' in word and 'S' in tokens: categories['soft c'].append(word)
    elif hard_verification and soft_verification: return
    elif 'K' in tokens and hard_verification: categories['hard c'].append(word)
    elif 'S' in tokens and soft_verification: categories['soft c'].append(word)

def hardVsSoftG(word: str, arpabet: str, tokens: list) -> None:
    if 'g' not in word: return
    hard_verification = verificationToAdd(word, arpabet, 'g', ['G'], ['JH'])
    soft_verification = verificationToAdd(word, arpabet, 'g', ['JH'], ['G'])
    if hard_verification and soft_verification: return
    elif 'G' in tokens and hard_verification: categories['hard g'].append(word)
    elif 'JH' in arpabet and soft_verification: categories['soft g'].append(word)


def ooCheck(word: str, arpabet: str) -> None:
    if 'oo' not in word: return
    if 'UW' in arpabet:
        index = word.find('oo')
        if index+2 < len(word) and word[index+2] != 'r': categories['oo as in school'].append(word)
    if 'UH' in arpabet: categories['oo as in book'].append(word)


def owCheck(word: str, arpabet: str) -> None:
    if 'ow' not in word: return
    if 'AW' in arpabet: categories['ow as in plow'].append(word)
    if 'OW' in arpabet: categories['ow as in snow'].append(word)


def earCheck(word: str, arpabet: str) -> None:
    if 'ear' not in word: return
    if 'IH R' in arpabet or 'IY R' in arpabet: categories['ear as in hear'].append(word)
    if 'ER' in arpabet: categories['ear as in early'].append(word)


def sBlends(word: str, tokens: list) -> None:
    if 's' not in word: return
    if word.startswith('sn') or word.startswith('sm') or word.startswith('st') or word.startswith('sw') or word.startswith('sc') or word.startswith('sp'):
        if word[2] in VOWELS and tokens[1] not in VOWEL_PHONEMES:
            categories['s blends'].append(word)
   

def lBlends(word: str) -> None:
    if 'l' not in word: return
    if word.startswith('bl') or word.startswith('cl') or word.startswith('fl') or word.startswith('pl') or word.startswith('gl') or word.startswith('sl'):
        categories['l blends'].append(word)


def rBlends(word: str) -> None:
    if 'r' not in word: return
    if word.startswith('br') or word.startswith('cr') or word.startswith('dr') or word.startswith('fr') or word.startswith('gr') or word.startswith('pr') or word.startswith('tr'):
        categories['r blends'].append(word)


def eaCheck(word: str, arpabet: str) -> None:
    if 'ea' not in word or not is_vv('ea', arpabet): return
    if 'IY' in arpabet and verificationToAdd(word, arpabet, 'ea', ['IY'], ['EH', 'EY']):
        index = arpabet.find('IY')
        if index+3 < len(arpabet) and arpabet[index+3] != 'R': categories['ea as in eat'].append(word)
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
    if 'AW' in arpabet and verificationToAdd(word, arpabet, 'ou', ['AW'], ['AH']):
        categories['ou as in south'].append(word)


def ueCheck(word: str, arpabet: str) -> None:
    if 'ue' not in word or is_vv('ue', arpabet): return
    if 'UW' in arpabet and verificationToAdd(word, arpabet, 'ue', ['UW'], ['EH', 'AH']):
        categories['ue as in blue'].append(word)


def eiCheck(word: str, arpabet: str) -> None:
    if 'ei' not in word or is_vv('ei', arpabet): return
    if 'IY' in arpabet and verificationToAdd(word, arpabet, 'ei', ['IY'], ['EY']): categories['ei as in receive'].append(word)
    elif 'EY' in arpabet: categories['ei as in vein'].append(word)


def chCheck(word: str, arpabet: str, tokens: list) -> None:
    if 'ch' not in word or 'xch' in word: return
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
    if 'ie' not in word or 'ier' in word: return
    if 'AY' in arpabet and not (is_vv('ie', arpabet)):
        categories['ie as in pie'].append(word)
    elif 'IY' in arpabet and not (is_vv('ie', arpabet)) and verificationToAdd(word, arpabet, 'ie', ['IY'], ['UW']):
        categories['ie as in thief'].append(word)


def sionCheck(word: str, arpabet: str) -> None:
    if 'sion' not in word: return
    if 'SH' in arpabet:
        categories['-sion as in tension'].append(word)
    elif 'ZH' in arpabet:
        categories['-sion as in vision'].append(word)


def threelBlends(word: str) -> None:
    if (word.startswith('spr') or word.startswith('spl') or word.startswith('scr') or word.startswith('str')):
        categories['3-letter beg. blends'].append(word)


def vccvCheck(word: str, syllable_count: int, tokens: list) -> None:
    if (not (6 <= len(word) <= 7) or syllable_count != 2 or word.endswith('e') or 
        any(sound in word for sound in COMPOUND_SOUNDS) or word.endswith('ed') or word.endswith('ing')): return
    if len(tokens) != 6: return
    if (tokens[0] not in VOWEL_PHONEMES and
        tokens[1] in VOWEL_PHONEMES and
        tokens[2] not in VOWEL_PHONEMES and
        tokens[3] not in VOWEL_PHONEMES and
        tokens[4] in VOWEL_PHONEMES and
        tokens[5] not in VOWEL_PHONEMES):
        categories['vccv'].append(word)


def vceCheck(word: str) -> None:
    if len(word) < 3: return
    VCE_SUFFIXES = ['ive', 'age', 'ture']
    if (word[-3].lower() in VOWELS and
        word[-2].lower() in CONSONANTS and
        word[-1].lower() == 'e'):
        categories['vce'].append(word)

def vceBool(word: str) -> bool:  # helper function, returns true if a vce word
    if len(word) < 3:
        return False
    return (word[-3].lower() in VOWELS and
        word[-2].lower() in CONSONANTS and
        word[-1].lower() == 'e')
       

def OCECheck(word: str, syllable_count: int, tokens: list) -> None:
    if syllable_count != 1 or len(word) < 2: return
    for i in range(len(word)-1): # No team vowels
        if word[i] in VOWELS and word[i+1] in VOWELS:
            return
    for i, letter in enumerate(word): # No r-controlled syllables
        if letter in VOWELS:
            if i+1 < len(word) and word[i+1] == 'r':
                return
    # Open syllables: Check if the last sound is a long vowel sound
    if tokens[-1] in ['AY', 'EY', 'IY', 'OW', 'UW'] and word[-1] in VOWELS:
        # Check for vowel combinations
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


def vcvCheck(word: str, syllable_count: int, tokens: list) -> None:
    if (not (5 <= len(word) <= 8) or syllable_count != 2 or word.endswith('e') or 
        any(sound in word for sound in COMPOUND_SOUNDS) or word.endswith('ed') or word.endswith('ing')): return
    # Check for double letters
    for i in range(1, len(word) - 2):
        first = word[i]
        second = word[i+1]
        if first == second or first in VOWELS and second in VOWELS:
            return
    if len(tokens) != 5: return
    if (tokens[0] not in VOWEL_PHONEMES and
        tokens[1] in VOWEL_PHONEMES and
        tokens[2] not in VOWEL_PHONEMES and
        tokens[3] in VOWEL_PHONEMES and
        tokens[4] not in VOWEL_PHONEMES):
        categories['vcv'].append(word)


def vcccvCheck(word: str, syllable_count: int, tokens: list) -> None:
    if (not (7 <= len(word) <= 9) or syllable_count != 2 or word.endswith('e') or 
        any(sound in word for sound in COMPOUND_SOUNDS) or word.endswith('ed') or word.endswith('ing')) : return
    if len(tokens) != 7: return
    # Check for consecutive letters in the consonant cluster
    for i in range(1, len(word)-2   ):
        first = word[i]
        second = word[i+1]
        if first == second or first in VOWELS and second in VOWELS:
            return
    # VCCCV check
    if (tokens[0] not in VOWEL_PHONEMES and
        tokens[1] in VOWEL_PHONEMES and
        tokens[2] not in VOWEL_PHONEMES and
        tokens[3] not in VOWEL_PHONEMES and
        tokens[4] not in VOWEL_PHONEMES and
        tokens[5] in VOWEL_PHONEMES and
        tokens[6] not in VOWEL_PHONEMES):
        categories['vcccv'].append(word)


def vrlCheck(word: str, syllable_count: int) -> None:
    if len(word) < 3 or syllable_count != 1: return
    if word.endswith('le'):
        index = word.rfind('le')
        if index > 0 and word[index-1] not in VOWELS:
            categories['cle ending'].append(word)
    for i in range(len(word)-2): # Team Vowels. Only 1 syllable, V/V doesn't apply
        if word[i] in VOWELS and word[i+1] in VOWELS and word[i+2] != 'r':
            categories['vowel_team'].append(word)
            return
    for r_sound in ['ar', 'er', 'ir', 'or', 'ur']: # R-controlled
        if r_sound in word:
            categories['r-controlled'].append(word)
            return  


def vvCheck(word: str, arpabet: str) -> None:
    if len(word) < 3 or word == 'theatre': return
    i = 0
    while i < len(word):
        for comp in vv_sounds:
            if word[i:i + len(comp)] == comp:
                compound = word[i: i+len(comp)]
                if is_vv(compound, arpabet):
                    categories['v/v pattern'].append(word)
        i += 1


def doubleConsonant(word: str) -> None:
    index = None
    for suffix in ['ed', 'es', 'ing']:
        if word.endswith(suffix):
            index = word.rfind(suffix)
            if word[index-1] == word[index-2]:
                categories['double rule-suffixes'].append(word)


def fszlCheck(word: str, syllable_count: int, tokens: list) -> None:
    if len(word) < 3 or word[-1] not in 'fszl' or word[-2] not in 'fszl' or word[-1] != word[-2] or syllable_count != 1: return
    for vowel in ['IH', 'EH', 'AH', 'UH', 'AA', 'AE']:
        if vowel in tokens[-2]:
            categories['fszl'].append(word)

### Chris did this one. May want to redo one day
def yRuleSuffix(word: str) -> bool:
    EXCEPTIONS = {'frontier', 'glacier', 'soldier', 'barrier', 'carrier', 'pier', 'priest', 'series', 'species', 'lies'}
    if word in EXCEPTIONS:
        return
    if yRulePatterns.search(word): # Check for patterns where Y changes to I
        categories['y rule suffixes'].append(word)
    elif word.endswith('ying'): # Check for "ying" suffix
        categories['y rule suffixes'].append(word)
    # Disallow words with Vowel + Y patterns
    elif vowelYPattern.search(word):
        return
    # Final check for "ies" pattern without VOWELS before "y"
    elif word.endswith('ies') and not 'y' in word[:word.rfind('ies')]:
        categories['y rule suffixes'].append(word)

def areWordsRelated(root: str, suffixed: str) -> bool:
   root_synsets = wordnet.synsets(root) # Sets of Synonyms (synset)
   suffixed_synsets = wordnet.synsets(suffixed)
   if not root_synsets or not suffixed_synsets:
       return False
   # Check if any of the definitions or lemmas contain the root word
   for synset in suffixed_synsets:
       definition = synset.definition().lower()
       lemmas = [lemma.name().lower() for lemma in synset.lemmas()]
       if root in definition or root in lemmas:
           return True
   return False


def eRuleSuffix(word: str) -> None:
    # Suffixes that require dropping 'e'
    drop_e_suffixes = ['ing', 'er']
    # Check for suffixes that drop 'e'
    for suffix in drop_e_suffixes:
        if word.endswith(suffix):
            root_without_e = word[:-len(suffix)]
            root_with_e = root_without_e + 'e'
            if (len(root_without_e) <= 2 or  
                not any(c in 'aeiou' for c in root_without_e)):
                continue
            if (pronouncing.phones_for_word(root_with_e) and
               not pronouncing.phones_for_word(root_without_e) and
               areWordsRelated(root_with_e, word)):
               categories['e rule-suffixes'].append(word)
               return
    # Suffixes that keep 'e'
    keep_e_suffixes = ['able', 'ible', 'ous', 'est']
    # Check for suffixes that keep 'e'
    for suffix in keep_e_suffixes:
        if word.endswith(suffix):
            root = word[:-len(suffix)]  # First get the root by removing suffix
            if (len(root) <= 2 or
                not any(c in 'aeiou' for c in root)):
                continue
            if (pronouncing.phones_for_word(root + 'e') and
               areWordsRelated(root + 'e', word)):
               categories['e rule-suffixes'].append(word)
               return


def getWords(text: str) -> set:
    words = re.findall(r'\b[A-Za-z]+\'?[A-Za-z]*\b', text.lower())
    return set(words)

def callCategorizationFunctions(word: str, arpabet: str, syllable_count: int, tokens: list) -> None:
    vceCheck(word)  # placing vceCheck before vowel check for a 'long a' edge case
    vowelCheck(word, arpabet, tokens)
    knCheck(word, arpabet)
    hardVsSoftC(word, arpabet, tokens)
    hardVsSoftG(word, arpabet, tokens)
    yCheck(word, arpabet)
    ooCheck(word, arpabet)
    owCheck(word, arpabet)
    earCheck(word, arpabet)
    eaCheck(word, arpabet)
    sBlends(word, tokens)
    lBlends(word)
    rBlends(word)
    ghCheck(word, arpabet)
    ewCheck(word, arpabet)
    ouCheck(word, arpabet)
    ueCheck(word, arpabet)
    eiCheck(word, arpabet)
    ieCheck(word, arpabet)
    chCheck(word, arpabet, tokens)
    edCheck(word)
    sionCheck(word, arpabet)
    aughCheck(word, arpabet)
    oughCheck(word, arpabet)
    threelBlends(word)
    warCheck(word)
    allCheck(word, arpabet)
    doubleConsonant(word)
    vcvCheck(word, syllable_count, tokens)
    vvCheck(word, arpabet)
    vcccvCheck(word, syllable_count, tokens)
    yRuleSuffix(word)
    eRuleSuffix(word)
    vrlCheck(word, syllable_count)
    xInWordCheck(word, arpabet, tokens)
    ingongangungCheck(word)
    contractionsCheck(word) 
    vccvCheck(word, syllable_count, tokens)
    OCECheck(word, syllable_count, tokens)
    fszlCheck(word, syllable_count, tokens)


def parseAndProcessWords(story: str, syllable_limit:str) -> dict:
    try:
        words = getWords(story)
        unique_words = set(words)
        # print('parsing through words. . .\n')
        for word in unique_words:
            word.lower()
            if word in sight_words:
                continue
            phones = pronouncing.phones_for_word(word)
            if not phones:
                categories['failed to categorize'].append(word)
                continue
            syllable_count = pronouncing.syllable_count(phones[0])
            if syllable_count > syllable_limit:
                categories['too many syllables'].append(word)
                continue
            arpabet = re.sub(r'\d', '', phones[0])
            tokens = arpabet.split()
            callCategorizationFunctions(word, arpabet, syllable_count, tokens)

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
    input_path = os.path.join(path, 'Resources/Dictionary.txt')
    output_path = os.path.join(path, 'Resources/categorized_words.json')
    with open(input_path, 'r') as f:
        story = f.read()
    dictionary = parseAndProcessWords(story, syllable_limit=1000)
    print("done parsing")
    with open(output_path, 'w') as f:
        json.dump(dictionary, f, indent=4)
    
if __name__ == "__main__":
    main()