### Imports
import os

if os.path.exists('dictionary_parser/'):
    path = "dictionary_parser/"
else:
    path = ""

from dictionaryParser import *
from storyGenerator import *
from replace_synonyms import *
from collections import Counter
from datetime import datetime
import language_tool_python

sight_words = ""

with open(path + 'Dictionary.txt', 'r', encoding='utf-8') as file:
    large_dictionary = set(word.strip().lower() for word in file.readlines())

with open(path + 'truncated_dictionary.json') as json_file:
    guidewords = json.load(json_file)

def get_synonyms_dict(story: str, word_dict: dict, problems: list, maxsyllable: int) -> dict:
    sentences = story.split(".")
    prev_sentence = ""
    synonyms_dict = {}
    
    # Create a mapping from problem sound to example words
    problem_examples = {}
    for problem in problems:
        problem = problem.strip()
        if problem in guidewords:
            problem_examples[problem] = guidewords[problem][:5]  # Limit to 5 examples for brevity
        else:
            print(f"Warning: Problem '{problem}' not found in guidewords dictionary.")
    
    # Format the examples for the prompt
    examples_str_list = []
    for problem, examples in problem_examples.items():
        formatted_examples = ", ".join([f"'{word}'" for word in examples])
        examples_str = f"The '{problem}' sound in {formatted_examples}"
        examples_str_list.append(examples_str)
    examples_str = "; ".join(examples_str_list)

    for idx, sentence in enumerate(sentences):
        sentence = sentence.strip()
        next_sentence = sentences[idx + 1].strip() if idx + 1 < len(sentences) else ""
        words = sentence.split(" ")
        for word in words:
            # Remove punctuation and make lowercase
            clean_word = "".join(re.findall("[a-zA-Z]", word)).lower()
            for problem in problems:
                problem = problem.strip()
                if problem in word_dict and clean_word in word_dict[problem] and clean_word not in sight_words:
                    # Prepare the prompt
                    prompt = f"""
                        Give 10 synonyms for the word '{word}' that would fit naturally in the following sentence, and **do not** include any words containing these sounds: {', '.join(problems)}.
                        A change in tense or form of the word is not acceptable. Maintain tense and form as these words are going to replace the original word in a story.

                        Some examples of words to **avoid** are: {examples_str}.

                        Previous sentence (for context): {prev_sentence}
                        Sentence to fix: {sentence}
                        Next sentence (for context): {next_sentence}

                        Return only the 10 words separated by commas, like this: "word1, word2, word3, word4, word5".
                        Order the words so the best fit is first.

                        **RETURN ONLY THE LIST OF WORDS**
                        """
                    response = query(prompt).strip()
                    temp_words = [w.strip() for w in response.split(",") if w.strip()]
                    temp_words_dict = parseAndProcessWords(response, maxsyllable, "categorized_words.json")
                    # Remove words containing problem sounds
                    filtered_temp_words = []
                    for temp_word in temp_words:
                        temp_word_lower = temp_word.lower()
                        contains_problem = False
                        for problem_check in problems:
                            problem_check = problem_check.strip()
                            if problem_check in temp_words_dict and temp_word_lower in temp_words_dict[problem_check]:
                                contains_problem = True
                                break
                        if not contains_problem:
                            filtered_temp_words.append(temp_word)
                    if filtered_temp_words:
                        synonyms_dict[clean_word] = " " + filtered_temp_words[0]
                    else:
                        synonyms_dict[clean_word] = " ____"
        prev_sentence = sentence
    return synonyms_dict


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

def count_words_in_text(text: str) -> int:
    words = text.split()
    return len(words)

def correct_text(text: str) -> str:
    try:
        tool = language_tool_python.LanguageTool('en-US')
        matches = tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        return corrected_text
    except Exception as e:
        print(f"Warning: Grammar correction failed ({str(e)}). Proceeding with original text.")
        return text

def rewrite_sentences(story):
    sentences = story.split(".")  # Split sentences by period
    finaltext = ""  # To store the revised story
    
    for i, sentence in enumerate(sentences):
        # Get previous and next sentence for context
        prev_sentence = sentences[i - 1] if i > 0 else ""
        next_sentence = sentences[i + 1] if i < len(sentences) - 1 else ""
        
        # Form the prompt
        prompt = f"""
            Rewrite this sentence so it is easier to read if necessary. Remember this is for a childrens book: {sentence}
            
            If no rewrite is needed, return the same sentence.
            If it makes sense to, trim down the sentence so it is not redundant.

            Here is the previous sentence and next sentence for context: Previous: {prev_sentence} Next: {next_sentence}

            *** RETURN ONLY THE NEW SENTENCE OR THE SAME SENTENCE IF NO CHANGE IS NEEDED ***
        """
        
        # Call the function to get the rewritten sentence (query function assumed)
        sentence_rev = query(prompt).strip()

        if "return" in sentence_rev and "sentence" in sentence_rev:
            sentence_rev = query(prompt).strip()
        
        # Add the revised sentence to the final text
        if sentence_rev and sentence != prev_sentence and sentence !=next_sentence:  # Avoid adding empty strings
            finaltext += sentence_rev + " "
    
    return finaltext.strip()  # Strip trailing whitespace
   

def process_story(story, problems, maxsyllable, apply_correction=False, spellcheck=False, combined=False, decodabilityTest=False): 
    if decodabilityTest:
        print("Decodability Test Mode: Analyzing text without making changes.")
        
        # Prepare sight words set
        sight_words_set = set(word.lower().strip() for word in sight_words.split(','))

        # Tokenize the story into words and count occurrences
        story_words = re.findall(r'\b\w+\b', story.lower())
        story_word_counts = Counter(story_words)

        # Parse and process words to categorize them
        word_dict = parseAndProcessWords(story, maxsyllable, "categorized_words.json")

        # Combine all bad words into a single set
        all_bads = set()
        for problem in problems:
            problem = problem.strip()
            if problem in word_dict:
                problem_words = set(word.lower() for word in word_dict[problem] if word.lower() not in sight_words_set)
                all_bads.update(problem_words)
            else:
                print(f"Warning: Problem '{problem}' not found in word dictionary.")

        # Count occurrences of each unique bad word in the story
        problemcount = 0
        bad_occurrences = {}
        for bad_word in all_bads:
            count = story_word_counts.get(bad_word, 0)
            if count > 0:
                problemcount += count
                bad_occurrences[bad_word] = count

        # Calculate decodability
        wordcount = len(story_words)
        decodability = 1 - (problemcount / wordcount) if wordcount > 0 else 0

        # Print the results
        print("Bad Word Occurrences:")
        for word, count in bad_occurrences.items():
            print(f"{word}: {count}")

        print(f"This text is {decodability * 100:.2f}% decodable")

        # Prepare the data for the file
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        decodability_entry = f"{decodability * 100:.2f}% {current_time} Word Count: {wordcount} Decodability Test\n"

        # Append the data to the file
        decodability_file = "decodability_measurements.txt"
        with open(decodability_file, "a") as file:
            file.write(decodability_entry)

        # Return the original story without changes
        return decodability

    else:
        # Existing code for processing the story
        # Apply grammar correction and spellcheck if enabled
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
            prompt = f"You are a literary editor. Rewrite this story and make any necessary changes to the story to make it 100% readable and abide by proper English writing and reading standards: {story}. Return just the new fixed story."
            story = query(prompt)
            marker += " Spellcheck"
        else:         
            print("Skipping Spellcheck...")
            marker += " No Spellcheck"

        if combined:
            combo = "Combined Text"
        else: 
            combo = ""

        # Continue with processing
        print("Checking each word...")
        word_dict = parseAndProcessWords(story, maxsyllable, "categorized_words.json")

        # Find synonyms
        print("Finding synonyms...")
        synonyms_dict = get_synonyms_dict(story, word_dict, problems, maxsyllable)

        # Replace problematic words with synonyms
        print("Replacing synonyms...")
        story = replace_words_in_story(story, synonyms_dict)

        # Rewrite problematic sentences
        story = rewrite_sentences(story)

        # Prepare sight words set
        sight_words_set = set(word.lower().strip() for word in sight_words.split(','))

        # Tokenize the story into words and count occurrences
        story_words = re.findall(r'\b\w+\b', story.lower())
        story_word_counts = Counter(story_words)

        # Combine all bad words into a single set
        all_bads = set()
        for problem in problems:
            problem = problem.strip()
            if problem in word_dict:
                problem_words = set(word.lower() for word in word_dict[problem] if word.lower() not in sight_words_set)
                all_bads.update(problem_words)
            else:
                print(f"Warning: Problem '{problem}' not found in word dictionary.")

        # Load existing word counts from file if it exists
        word_counts = {}
        try:
            with open('non_decodable_words.txt', 'r') as f:
                for line in f:
                    word, count = line.strip().split(': ')
                    word_counts[word] = int(count)
        except FileNotFoundError:
            pass

        # Update counts with new bad words
        for word in all_bads:
            word_counts[word] = word_counts.get(word, 0) + 1

        # Write updated counts back to file
        with open('non_decodable_words.txt', 'w') as f:
            for word, count in sorted(word_counts.items()):
                f.write(f'{word}: {count}\n')

        # Count occurrences of each unique bad word in the story
        problemcount = 0
        bad_occurrences = {}
        for bad_word in all_bads:
            count = story_word_counts.get(bad_word, 0)
            if count > 0:
                problemcount += count
                bad_occurrences[bad_word] = count

        # Calculate decodability
        wordcount = len(story_words)
        decodability = 1 - (problemcount / wordcount) if wordcount > 0 else 0

        # Print the results for the final updated story
        print("Bad Word Occurrences:")
        for word, count in bad_occurrences.items():
            print(f"{word}: {count}")

        print(f"This text is {decodability * 100:.2f}% decodable")

        # Prepare the data for the file
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        decodability_entry = f"{decodability * 100:.2f}% {current_time} Word Count: {wordcount} {marker} {combo}\n"

        # Append the data to the file
        decodability_file = "decodability_measurements.txt"
        with open(decodability_file, "a") as file:
            file.write(decodability_entry)

        # Save the final story
        if apply_correction and spellcheck and combined:
            output_file = 'combined.txt'
        elif apply_correction and spellcheck:
            output_file = 'updated_story_transition.txt'
        elif apply_correction:
            output_file = 'updated_story_corrected.txt'
        else:
            output_file = 'updated_story.txt'
        story = ultraformatting(story)
        save_updated_story(story, output_file)
        print(f"Updated story has been saved to '{output_file}'.")
        return story


def combine(story1, story2, problems):
    prompt = f"""
    Take the two versions of the story provided below and combine their sentences into one improved version. 
    Retain the original plot and key details.
    Keep the creative language from both versions.
    Try to avoid run-on sentences.
    Ensure the final story maintains the same narrative structure but uses the best phrases from each version. 
    Do not invent new plot elements or diverge from the original stories.
    **Most Importantly** Try to avoid including these sounds: {problems}.

    Version 1: {story1}

    Version 2: {story2}
    """
    ultstory = query(prompt)
    return ultstory

def handle_sight_words(default_sight_words: str, problematic_words: str) -> str:
    sight_words_list = default_sight_words.split(",")
    probsight_words_list = problematic_words.split(",")
    for word in probsight_words_list:
        if word in sight_words_list:
            sight_words_list.remove(word)
    return ",".join(sight_words_list)

def main():
    global sight_words
    global maxsyllable
    default_sight_words = "a,at,any,many,and,on,is,are,the,was,were,it,am,be,go,to,out,been,this,come,some,do,does,done,what,who,you,your,both,buy,door,floor,four,none,once,one,only,pull,push,sure,talk,walk,their,there,they're,very,want,again,against,always,among,busy,could,should,would,enough,rough,tough,friend,move,prove,ocean,people,she,other,above,father,usually,special,front,thought,he,we,they,nothing,learned,toward,put,hour,beautiful,whole,trouble,of,off,use,have,our,say,make,take,see,think,look,give,how,ask,boy,girl,us,him,his,her,by,where,were,wear,hers,don't,which,just,know,into,good,other,than,then,now,even,also,after,know,because,most,day,these,two,already,through,though,like,said,too,has,in,brother,sister,that,them,from,for,with,doing,well,before,tonight,down,about,but,up,around,goes,gone,build,built,cough,lose,loose,truth,daughter,son"
    probsight_words = input("What sight words does the student not know (use only words and commas): ")
    
    sight_words = handle_sight_words(default_sight_words, probsight_words)
    
    gendec = input("Would you like to generate a story (g) or input a story (i): ")
    if gendec == "g":
        story_length, topic, problems,name,readingLevel = get_input()
        problems.append("too many syllables")
        story= generate_story(topic, problems, name, readingLevel, story_length)
        print("Generating story...")
    elif gendec == "i":
        problems = input("Enter the problem letters separated by /: ").split("/")
        problems.append("too many syllables")
        file = input("Copy and Paste your text here: ")
        story =  file
        decodabuilityog = process_story(story, problems, 10, apply_correction=False, spellcheck=False, combined=False, decodabilityTest=True)
    print(story)

    # First Run: Without Grammar Correction
    print("\n--- Processing Without Grammar Correction ---")
    story1 = process_story(story, problems, 10, apply_correction=False, spellcheck=False, combined=False)

    print("\n--- Processing With Grammar Correction and Spell Check ---")
    story2 = process_story(story, problems, 10,apply_correction=True, spellcheck=True, combined=False)

    # Now, combine the two stories
    story3 = combine(story1, story2, problems)

    # Process the combined story
    story4 = process_story(story3, problems, apply_correction=True, spellcheck=True, combined=True)

    print(f'\n\nFinal Story: {story4}')



if __name__ == "__main__":
    main()


#b/l/p/j/ck/wh/aw/tch/igh/ir/oi  
#wh/aw/tch/igh/ir/oi/kn/ur/dge/tion/war/ph/eigh/wor/ough  
#s/l/r/b/sh/ar/ai/-ing, -ong, -ang, -ung/ea as in eat  
#t/p/n/m/th/ch/oo as in school/ow as in plow/y as in dry  
#d/w/z/h/ck/s blends/l blends/er/ea as in bread/igh  
#r/v/l/qu/th/ay/ow as in snow/ear as in hear/y as in bumpy  

#New idea if word appears 2+ times prompt the bot to find alternative words that could work in the context but may be different in their meaning
#Could reduce decodability

