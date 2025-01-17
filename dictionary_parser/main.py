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
from query import *
import language_tool_python

original_decodability = None
sight_words = ""

with open(path + '/Resources/Dictionary.txt', 'r', encoding='utf-8') as file:
    large_dictionary = set(word.strip().lower() for word in file.readlines())


with open(path + '/truncated_dictionary.json') as json_file:
    guidewords = json.load(json_file)

def get_synonyms_dict(story: str, problems: list, maxsyllable: int) -> dict:
    word_dict = parseAndProcessWords(story, maxsyllable)
    sentences = story.split(".")
    prev_sentence = ""
    synonyms_dict = {}


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
                        Give the 5 best words to replace this word '{word}' that would fit naturally in context to the following sentence, and **do not** include any words containing these sounds: {', '.join(problems)}.
                        A change in tense or form of the word is not acceptable. Maintain tense and form as these words are going to replace the original word in a story.

                        Sentence to fix: {sentence}

                        Return only the 5 words separated by commas, like this: "word1,word2,word3,word4,word5".
                        Order the words so the best fit is first.


                        **RETURN ONLY THE LIST OF WORDS**
                        """
                    response = query(prompt).strip()
                    temp_words = [w.strip() for w in response.split(",") if w.strip()]
                    temp_words_dict = parseAndProcessWords(response, maxsyllable)
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
                        synonyms_dict[clean_word] = word
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

    text = re.sub(r'["""]', '"', text)

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


   
def find_proper_nouns(story, sight_words):
    prompt = f""" 
            Find all of the proper nouns (People, Places, Things) in this {story}.

            Return all the proper nouns seperated by commas between each word. E.g. word1,word2,word3...

            Return just the list of all the words
            """
    propernouns = query(prompt)
    sight_words += "," + propernouns
    return 

def find_commons(topic):
    prompt = f"""What are 15 common words that are not in this prompt that could be found in a story with this prompt: {topic}
                
                Return only the words in this format: word1,word2,word3,...
                 """
    words = query(prompt)
    wordlist = words.split(',')
    return wordlist

def process_story(story, problems, maxsyllable, apply_correction=False, spellcheck=False, combined=False, decodabilityTest=False, topic=None):
    global sight_words
    if topic:
        topic_words = topic.split()
        for i in range(len(topic_words)):
            sight_words+=(","+topic_words[i])
    find_proper_nouns(story, sight_words)
    def categorize_and_validate_words(story, problems, maxsyllable):
        # Prepare sight words set
        sight_words_set = set(word.lower().strip() for word in sight_words.split(','))


        # Tokenize the story into words and count occurrences
        story_words = re.findall(r'\b\w+\b', story.lower())
        story_word_counts = Counter(story_words)


        # Parse and process words to categorize them
        word_dict = parseAndProcessWords(story, maxsyllable)


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

        # Return results
        return {
            "decodability": decodability,
            "bad_occurrences": bad_occurrences,
            "wordcount": wordcount,
            "all_bads": all_bads,
        }
    decodability_file = "decodability_measurements.txt"
    def rewrite_sentences(story):
        # Split story into sentences
        sentences = [s.strip() for s in story.split(".") if s.strip()]
        modified = True
        max_attempts = 10  # Prevent infinite loops
        
        for i, sentence in enumerate(sentences):
            # Check individual sentence decodability
            sentence_decodability = categorize_and_validate_words(sentence, problems, maxsyllable)["decodability"]
            attempts = 0
            
            # Keep trying to improve sentence until it meets threshold or max attempts reached
            while sentence_decodability < 0.9 and attempts < 5:
                new_sentence = sentence
                new_decodability = categorize_and_validate_words(new_sentence, problems, maxsyllable)["decodability"]
                
                # Only update if new version is better
                if new_decodability > sentence_decodability:
                    sentences[i] = new_sentence
                    sentence_decodability = new_decodability
                    modified = True
                    print(f"Sentence {i+1} improved - Decodability: {sentence_decodability:.2f}")
                
                attempts += 1
                
        # Reconstruct story with improved sentences
        return ". ".join(sentences) + "."
        
    def grade_story(story):
        global readability
        readabilgrade = 0
        sentences = [s.strip() for s in story.split(".") if s.strip()]
        grades = []
        
        numsentences = len(sentences)
        for sentence in sentences:
            prompt = f"""You are a English Teacher. Grade this sentence on a scale of 0-100 base on its readability: {sentence}.
                        A 100 would be a sentence without any awkward words. Every awkward word is -10 points.
                        Return only the number grade and nothing else."""
            grade = query(prompt)
            # Convert string grade to integer
            try:
                grade_int = int(grade.strip())  # Remove whitespace and convert to int
                grades.append(grade_int)
                readabilgrade += grade_int
            except ValueError:
                print(f"Warning: Could not convert grade '{grade}' to integer")
                numsentences-=1
                continue
    
        readability = (readabilgrade/numsentences)/100
        return "\n".join(str(g) for g in grades) 
    
    def grammar_fix(story):
        prompt = f"""You are an expert English teacher. Fix the following story by:
        1. Add missing articles (a, an, the) where needed
        2. Add appropriate conjunctions (and, but, or, so) where needed  
        3. Add pronouns (he, she, it, they) where needed for clarity
        4. Fix any syntax/grammar issues while preserving the original meaning
        5. Keep ALL existing quotation marks and punctuation
        6. Do not change any vocabulary or add complex words
        7. Remove any awkward adjectives
        8. Return ONLY the corrected story with no other text
        
        Story to fix:
        {story}"""

        try:
            fixed_story = query(prompt)
            # Clean up any formatting issues
            fixed_story = fixed_story.strip()
            # Remove any "Here's the corrected story:" type prefixes
            fixed_story = re.sub(r'^(Here\'s |The )?(corrected |fixed )?story:?\s*', '', fixed_story, flags=re.IGNORECASE)
            return fixed_story
        except Exception as e:
            print(f"Error in grammar correction: {e}")
            return story

    def save_decodability_metrics(decodability, wordcount, marker, combo, problems):
        global original_decodability
        # Ensure the directory exists
        # Prepare the data for the file
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if original_decodability is not None:
            original_decodability = original_decodability[0] if isinstance(original_decodability, tuple) else original_decodability
        else:
            original_decodability = 0
        decodability_entry = f"Original Decodability: {original_decodability * 100:.2f}% Processed Decodability: {decodability * 100:.2f}% {current_time} Word Count: {wordcount} {marker} {combo} Problems: {problems}\n"
        with open(decodability_file, "a") as file:
            file.write(decodability_entry)
            
    def display_bad_words(bad_occurrences):
        print("Bad Word Occurrences:")
        for word, count in sorted(bad_occurrences.items()):
            print(f"{word}: {count}")
    

    def save_problem_words_by_sound(word_dict, problems, story):
        problem_words_file = "problem_words_by_sound.txt"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Clear the file before writing
        with open(problem_words_file, 'w') as file:
            file.write("")
        
        # Get all unique words from the story
        story_words = set(re.findall(r'\b\w+\b', story.lower()))
        
        # Create a mapping of words to their categories
        word_categories = {}
        for word in story_words:
            categories = []
            for problem in problems:
                problem = problem.strip()
                if problem in word_dict and word in word_dict[problem]:
                    categories.append(problem)
            word_categories[word] = categories
        
        with open(problem_words_file, "a", encoding='utf-8') as file:
            file.write(f"\n--- Problem Words Analysis {current_time} ---\n")
            
            # Write all story words with their categories
            file.write("\nAll words in story and their sound categories:\n")
            for word in sorted(story_words):
                categories = word_categories[word]
                if categories:
                    file.write(f"{word}: [{', '.join(categories)}]\n")
                else:
                    file.write(f"{word}: [no problem sounds]\n")
            
            file.write("\nProblem words by sound:\n")
            # Then write problem words by sound
            for problem in problems:
                problem = problem.strip()
                if problem in word_dict:
                    problem_words = [word for word in word_dict[problem] 
                                   if word.lower() not in sight_words.split(',') and word.lower() in story_words]
                    if problem_words:
                        file.write(f"{problem}: {', '.join(sorted(set(problem_words)))}\n")


    if decodabilityTest:
        print("Decodability Test Mode: Analyzing text without making changes.")
        results = categorize_and_validate_words(story, problems, maxsyllable)
        # Get word_dict for problem words
        story = story.lower()
        word_dict = parseAndProcessWords(story, maxsyllable)
        save_problem_words_by_sound(word_dict, problems, story)
        # Display and save bad word occurrences
        #display_bad_words(results["bad_occurrences"])
        if original_decodability is not None:
            save_decodability_metrics(results["decodability"], results["wordcount"], "Decodability Test", "", problems)
        # save_bad_word_counts(results["all_bads"])
        bad_words = results["bad_occurrences"]
        print(f"This text is {results['decodability'] * 100:.2f}% decodable")
        return results["decodability"], results["bad_occurrences"]
    else:
        # Process and apply corrections if enabled
        if apply_correction:
            print("Applying grammar correction...")
            story = correct_text(story)
        if spellcheck:
            print("Applying Spellcheck...")
            prompt = f"You are a literary editor. Rewrite this story and make any necessary changes to the story to make it 100% readable and abide by proper English writing and reading standards: {story}. Return just the new fixed story."
            story = query(prompt)
       
        decodability = categorize_and_validate_words(story, problems, maxsyllable)["decodability"]
        iteration = 0
        
        while decodability < 0.92 and iteration < 4:
            print(f"Decodability: {decodability}")
            print("Checking and categorizing words...")
            results = categorize_and_validate_words(story, problems, maxsyllable)
            print("Replacing problematic words...")
            synonyms_dict = get_synonyms_dict(story, problems, maxsyllable)
            story = replace_words_in_story(story, synonyms_dict)
            print("Formatting the story...")
            story = ultraformatting(story)
            decodability = categorize_and_validate_words(story, problems, maxsyllable)["decodability"]
            iteration+=1
        story = rewrite_sentences(story)
        decodability = categorize_and_validate_words(story, problems, maxsyllable)["decodability"]
        print(f"Decodability: {decodability}")
        grades = grade_story(story)
        story = grammar_fix(story)
        with open("grades.txt", "w") as grades_file:
            grades_file.write(grades)
        return story

def handle_sight_words(default_sight_words: str, problematic_words: str) -> str:
    sight_words_list = default_sight_words.split(",")
    probsight_words_list = problematic_words.split(",")
    for word in probsight_words_list:
        if word in sight_words_list:
            sight_words_list.remove(word)
    return ",".join(sight_words_list)

def capitalize_problematic_words(story: str, bad_words: dict) -> str:
    """Capitalize all problematic words in the story."""
    problemwords = []
    words = story.split()
    for i, word in enumerate(words):
        # Strip punctuation for comparison but keep it for replacement
        clean_word = re.sub(r'[^\w\s]', '', word.lower())
        if clean_word in bad_words:
            # Preserve punctuation while capitalizing the word part
            punctuation = ''.join(c for c in word if not c.isalnum())
            capitalized = word.upper()
            words[i] = capitalized
            problemwords.append(words[i])
    print(problemwords)
    return ' '.join(words)

def save_final_story(story, decodability, bad_words):
    """Save the final story and its decodability score to final.txt with problematic words capitalized."""
    capitalized_story = capitalize_problematic_words(story, bad_words)
    with open("final.txt", "w") as f:
        f.write(f"Final Story (Decodability: {decodability*100:.2f}%):\n\n")
        f.write(f"(Readability: {readability*100:.2f}%)\n\n")
        f.write(capitalized_story)

def main():
    global sight_words
    global maxsyllable
    global original_decodability
    global topic
    maxsyllable = 2
    default_sight_words = "back,beauty,bouquet,builder,rebuild,doesn't,shoe,shoelace,laughter,laugh,laughed,laughs,roughly,although,thoroughly,throughout,dough,doughnut,sovereighnty,a,at,any,many,and,on,is,are,the,was,were,it,am,be,go,to,out,been,this,come,some,do,does,done,what,who,you,your,both,buy,door,floor,four,none,once,one,only,pull,push,sure,talk,walk,their,there,they're,very,want,again,against,always,among,busy,could,should,would,enough,rough,tough,friend,move,prove,ocean,people,she,other,above,father,usually,special,front,thought,he,we,they,nothing,learned,toward,put,hour,beautiful,beautifully,whole,trouble,of,off,use,have,our,say,make,take,see,think,look,give,how,ask,boy,girl,us,him,his,her,by,where,were,wear,hers,don't,which,just,know,into,good,other,than,then,now,even,also,after,know,because,most,day,these,two,already,through,though,like,said,too,has,in,brother,sister,that,them,from,for,with,doing,well,before,tonight,down,about,but,up,around,goes,gone,build,built,cough,lose,loose,truth,daughter,son"
    probsight_words = input("What sight words does the student not know (use only words and commas): ")
   
    sight_words = handle_sight_words(default_sight_words, probsight_words)
   
    gendec = input("Would you like to generate a story (g) or input a story (i): ")
    if gendec.lower() == "g":
        # Use get_input_and_save to retrieve api_choice
        story_length, topic, problems, name, readingLevel, api_choice = get_input()
        topic_words = topic.split()
        for i in range(len(topic_words)):
            sight_words+=(","+topic_words[i])
        
        # Adjust maxsyllable based on readingLevel
        if int(readingLevel) <= 1:
            maxsyllable = 2
        elif int(readingLevel) <= 3:
            maxsyllable = 3
        elif int(readingLevel) <= 7:
            maxsyllable = 4
        elif int(readingLevel) <= 9:
            maxsyllable = 5
        else:
            maxsyllable = 10
        
        problems.append("too many syllables")
        sight_words += name
        get_bad_words(problems)
        get_good_words(problems,sight_words)
        story = generate_story(topic, problems, name, readingLevel, api_choice, story_length)
        original_decodability, _ = process_story(story, problems, maxsyllable, apply_correction=False, spellcheck=False, combined=False, decodabilityTest=True)
        if original_decodability > 0.97:
            print("Decodability is already high enough, no need to process further.")
            print(f'\n\nFinal Story: {story}')
            print(f"Decodability: {original_decodability* 100:.2f}%")
            save_final_story(story, original_decodability, bad_words)  
            return original_decodability
        print("Generating story...")
    elif gendec.lower() == "i":
        topic = input("What is the text about: ")
        readingLevel = input("Enter the grade level of the reader (Only the grade number): ")
        if int(readingLevel) <= 1:
            maxsyllable = 2
        elif int(readingLevel) <= 3:
            maxsyllable = 3
        elif int(readingLevel) <= 7:
            maxsyllable = 4
        elif int(readingLevel) <= 9:
            maxsyllable = 5
        else:
            maxsyllable = 10
        problems = input("Enter the problem letters separated by /: ").split("/")
        problems.append("too many syllables")
        file = input("Copy and Paste your text here: ")
        story = file
        original_decodability, _ = process_story(story, problems, maxsyllable, apply_correction=False, spellcheck=False, combined=False, decodabilityTest=True)
        if original_decodability > 0.95:
            print("Decodability is already high enough, no need to process further.")
            print(f'\n\nFinal Story: {story}')
            print(f"Decodability: {original_decodability* 100:.2f}%")
            return original_decodability
    print(story)

    #TODO: Implement a sort of check that adds common words for the topic to see if the student knows them and check overlap with problem sounds emphasizes these words arent allowed.

    # Process the combined story
    story4 = process_story(story, problems, maxsyllable, apply_correction=True, spellcheck=True, combined=False)


    decodability, bad_words = process_story(story4, problems, maxsyllable, apply_correction=True, spellcheck=True, combined=True, decodabilityTest=True)
    print(f'\n\nFinal Story:')
    capitalized_story = capitalize_problematic_words(story4, bad_words)
    print(capitalized_story)
    print(f"Decodability: {decodability}")
    save_final_story(story4, decodability, bad_words)
    return decodability

if __name__ == "__main__":
    main()




