from query import query
import re

def expand_story_section(
    story: str, 
    start_idx: int, 
    end_idx: int, 
    expansion_prompt: str, 
    problems: list, 
    maxsyllable: int,
    process_story_func
) -> str:
    """
    Expands a section of a story based on user highlighting and prompt.
    
    Args:
        story: Original story text
        start_idx: Starting index of highlighted section
        end_idx: Ending index of highlighted section
        expansion_prompt: User's instructions for expansion
        problems: List of problem sounds to avoid
        maxsyllable: Maximum syllables allowed per word
        process_story_func: Function to process the story
    
    Returns:
        str: The expanded and processed story
    """
    # Get the story sections
    highlighted_text = story[start_idx:end_idx]
    before_text = story[:start_idx]
    after_text = story[end_idx:]
    
    # Find the sentence boundaries for better context
    before_sentences = re.findall(r'[^.!?]*[.!?]', before_text)
    after_sentences = re.findall(r'[^.!?]*[.!?]', after_text)
    
    # Get immediate context (last 2 sentences before and first 2 after)
    context_before = ' '.join(before_sentences[-2:]) if before_sentences else ''
    context_after = ' '.join(after_sentences[:2]) if after_sentences else ''
    
    prompt = f"""
    You are expanding a children's story. Here is the context:
    
    Previous context:
    {context_before}
    
    Section to expand upon:
    {highlighted_text}
    
    Following context:
    {context_after}
    
    Expansion request: {expansion_prompt}
    
    Rules:
    1. Write additional content that naturally flows with the story
    2. Avoid using words containing these sounds: {', '.join(problems)}
    3. Keep the original highlighted text but expand upon it
    4. Maintain the same style and tone as the surrounding text
    5. Ensure the expansion connects smoothly with both the previous and following context
    
    Return only the new expanded portion of the story that will replace the highlighted section.
    """
    
    # Get the expansion text
    expansion = query(prompt)
    
    # Combine the story parts with the expansion
    new_story = before_text + expansion + after_text
    
    # Process the expanded story to ensure decodability
    processed_story = process_story_func(
        new_story, 
        problems, 
        maxsyllable, 
        apply_correction=True, 
        spellcheck=True, 
        combined=False
    )
    
    return processed_story

def get_expansion_metrics(
    original_story: str,
    expanded_story: str,
    problems: list,
    maxsyllable: int,
    process_story_func
) -> dict:
    """
    Calculates metrics about the story expansion.
    
    Returns:
        dict: Contains metrics like word count difference, 
              decodability comparison, etc.
    """
    # Get word counts
    original_words = len(re.findall(r'\b\w+\b', original_story))
    expanded_words = len(re.findall(r'\b\w+\b', expanded_story))
    
    # Get decodability scores
    original_decodability, original_bad_words = process_story_func(
        original_story,
        problems,
        maxsyllable,
        decodabilityTest=True
    )
    
    expanded_decodability, expanded_bad_words = process_story_func(
        expanded_story,
        problems,
        maxsyllable,
        decodabilityTest=True
    )
    
    return {
        "originalWordCount": original_words,
        "expandedWordCount": expanded_words,
        "wordCountDifference": expanded_words - original_words,
        "originalDecodability": original_decodability,
        "expandedDecodability": expanded_decodability,
        "originalBadWords": original_bad_words,
        "expandedBadWords": expanded_bad_words
    } 