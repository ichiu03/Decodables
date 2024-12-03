### Imports

from dictionaryParser import *
from storyGenerator import *
from replace_synonyms import *
from collections import Counter
from datetime import datetime
import language_tool_python

sight_words = ""

with open('dictionary_parser\\dictionary.txt', 'r', encoding='utf-8') as file:
    large_dictionary = set(word.strip().lower() for word in file.readlines())

def get_synonyms_dict(story, word_dict, problems):
    sentences = story.split(".")
    prev_sentence = sentences[0]
    synonyms_dict = {}
    for sentence in sentences:
        next_sentence = sentences[sentences.index(sentence) + 1] if sentences.index(sentence) < len(sentences) - 1 else ""
        words = sentence.split(" ")
        for word in words:
            word = "".join(re.findall("[a-zA-Z]", word)).lower()
            for problem in problems:
                if word in word_dict[problem] and word not in sight_words:
                    #HARD CODE
                    prompt = f"""
                        Give 10 words that would make sense as replacements for the following word in the sentence and don't include these sounds: {problems}:

                        word: {word}.
                        previous sentence (for context): {prev_sentence}.
                        sentence to fix: {sentence}.
                        next sentence (for context): {next_sentence}.

                        return only the 10 words separated by commas. Like this: "word1,word2,word3,word4,word5"
                        order the words so the best fit is first

                        RETURN ONLY THE LIST OF WORDS
                        """
                    response = query(prompt)
                    temp_words = response.split(",")
                    temp_words_dict = parseAndProcessWords(response)
                    for temp_word in temp_words:
                        for problem in problems:
                            if temp_word in temp_words_dict[problem]:
                                temp_words.remove(temp_word)
                                break
                    if len(temp_words) > 0:
                        synonyms_dict[word] = " " + temp_words[0]
                    else:
                        synonyms_dict[word] = " ___"
        prev_sentence = sentence
    return synonyms_dict

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

def ultraformatting(text):
    # Normalize multiple underscores to '____'
    text = re.sub(r'_{2,}', '____', text)
    
    # Ensure spaces around '____', treating it as a word
    # Add a space before '____' if it's attached to a word character
    text = re.sub(r'(?<=\w)(____)', r' \1', text)
    # Add a space after '____' if it's followed by a word character
    text = re.sub(r'(____)(?=\w)', r'\1 ', text)
    # Handle cases where multiple '____' are adjacent
    text = re.sub(r'(____)(____)', r'\1 \2', text)
    
    # Remove unnecessary spaces before punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    
    # Ensure there's a space after punctuation marks if not present, unless followed by punctuation or quotes
    text = re.sub(r'([,.!?;:])([^\s"\'().,!?:;])', r'\1 \2', text)
    
    # Handle quotation marks with a state machine
    chars = list(text)
    new_chars = []
    in_quotes = False
    i = 0
    while i < len(chars):
        c = chars[i]
        if c == '"':
            if in_quotes:
                # Closing quote
                # Remove space before closing quote
                if new_chars and new_chars[-1] == ' ':
                    new_chars.pop()
                new_chars.append(c)
                in_quotes = False
                # Add space after closing quote if needed
                if i + 1 < len(chars) and chars[i + 1] not in ' ,.!?;:\'"':
                    new_chars.append(' ')
            else:
                # Opening quote
                # Add space before opening quote if necessary
                if new_chars and new_chars[-1] not in ' \n':
                    new_chars.append(' ')
                new_chars.append(c)
                in_quotes = True
                # Skip any spaces immediately after the opening quote
                i += 1
                while i < len(chars) and chars[i] == ' ':
                    i += 1
                continue
        else:
            new_chars.append(c)
        i += 1
    text = ''.join(new_chars)
    
    # Normalize multiple spaces to a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Trim leading and trailing spaces
    text = text.strip()
    
    return text

def count_words_in_text(text):
    words = text.split()
    return len(words)

def correct_text(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    return corrected_text

def process_story(story, problems, apply_correction=False, spellcheck=False):
    if apply_correction:
        print("Applying grammar correction...")
        story = correct_text(story)
        print("Corrected Story:")
        print(story)
        marker = "grammar corrected"
    else:
        print("Skipping grammar correction...")
        marker = "grammar not corrected"
    
    if spellcheck:
        print("Applying Spellcheck...")
        prompt = f" You are a literary editor. Rewrite this story and make any necessary changes to the story to make it 100% readable and abide by proper english writing and reading standards: {story}. Return just the new fixed story."
        story = query(prompt)
        marker += " Spellcheck"
        
    else:         
        print("Skipping Spellcheck...")
        marker += " No Spellcheck"
        
    promptgrade =f"What is the quality of this story ranked on a grading scale of A-F: {story}. Return only the letter grade (A,B,C,D,F) and nothing else."
    graded = query(promptgrade)
    



    # Continue with your processing
    print("Checking each word...")
    word_dict = parseAndProcessWords(story)

    # Find synonyms
    print("Finding synonyms...")
    synonyms_dict = get_synonyms_dict(story, word_dict, problems)

    # Replace problematic words with synonyms
    print("Replacing synonyms...")
    story = replace_words_in_story(story, synonyms_dict)

    # Prepare sight words set
    sight_words_set = set(word.lower().strip() for word in sight_words.split(','))

    # Tokenize the story into words and count occurrences
    story_words = re.findall(r'\b\w+\b', story.lower())
    story_word_counts = Counter(story_words)

    # Combine all bads into a single set
    all_bads = set()
    for problem in problems:
        problem_words = set(word.lower() for word in word_dict[problem] if word.lower() not in sight_words_set)
        all_bads.update(problem_words)

    # Count occurrences of each unique bad word in the story
    problemcount = 0
    bad_occurrences = {}
    for bad_word in all_bads:
        count = story_word_counts.get(bad_word, 0)
        if count > 0:
            problemcount += count
            bad_occurrences[bad_word] = count

    # Print the results for the final updated story
    print("Bad Word Occurrences:")
    for word, count in bad_occurrences.items():
        print(f"{word}: {count}")

    # Calculate decodability
    wordcount = count_words_in_text(story)
    decodability = 1 - problemcount / wordcount

    # Print decodability to the console
    print(f"This text is {decodability * 100:.2f}% decodable")

    # Prepare the data for the file
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    decodability_entry = f"{decodability * 100:.2f}% {current_time} Word Count: {len(story.split())} Grade: {graded} {marker}\n"

    # Append the data to the file
    decodability_file = "dictionary_parser\\decodability_measurements.txt"
    with open(decodability_file, "a") as file:
        file.write(decodability_entry)

    # Save the final story
    if apply_correction and spellcheck:
        output_file = 'dictionary_parser\\updated_story_transition.txt'
    elif apply_correction:
        output_file = 'dictionary_parser\\updated_story_corrected.txt'
    else:
        output_file = 'dictionary_parser\\updated_story.txt'
    story = ultraformatting(story)
    save_updated_story(story, output_file)
    print(f"Updated story has been saved to '{output_file}'.")



def main():
    topic, problems = get_input()
    global sight_words
    sight_words = "a,any,many,and,on,is,are,the,was,were,it,am,be,go,to,been,come,some,do,does,done,what,who,you,your,both,buy,door,floor,four,none,once,one,only,pull,push,sure,talk,walk,their,there,they're,very,want,again,against,always,among,busy,could,should,would,enough,rough,tough,friend,move,prove,ocean,people,she,other,above,father,usually,special,front,thought,he,we,they,nothing,learned,toward,put,hour,beautiful,whole,trouble,of,off,use,have,our,say,make,take,see,think,look,give,how,ask,boy,girl,us,him,his,her,by,where,were,wear,hers,don't,which,just,know,into,good,other,than,then,now,even,also,after,know,because,most,day,these,two,already,through,though,like,said,too,has,in,brother,sister,that,them,from,for,with,doing,well,before,tonight,down,about,but,up,around,goes,gone,build,built,cough,lose,loose,truth,daughter,son"
    
    print("Generating story...")
    story = generate_story(topic, problems)
    print(story)

    # First Run: Without Grammar Correction
    print("\n--- Processing Without Grammar Correction ---")
    process_story(story, problems, apply_correction=False, spellcheck=False)
    
    print("\n--- Processing With Grammar Correction and Spell Check words---")
    process_story(story, problems, apply_correction=True, spellcheck=True)



if __name__ == "__main__":
    main()


#b,l,p,j,ck,wh,aw,tch,igh,ir,oi

#wh,aw,tch,igh,ir,oi,kn,ur,dge,tion,war,ph,eigh,wor,ough