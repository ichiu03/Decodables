import { PROBLEM_CATEGORIES } from '../constants/problemCategories';

const API_BASE_URL = process.env.NODE_ENV === 'production' ? 'https://decodables.onrender.com/api' : 'http://localhost:5000/api';

export const processStory = async (formData) => {
  try {
    // Get all possible problems from PROBLEM_CATEGORIES
    const allProblems = Object.values(PROBLEM_CATEGORIES).flat();
    
    // Get the problems the user DOESN'T know (ones that weren't selected)
    const unknownProblems = allProblems.filter(problem => !formData.problemLetters.has(problem));

    const response = await fetch(`${API_BASE_URL}/process-story`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        unknownSightWords: formData.unknownSightWords ? 
          formData.unknownSightWords.split(',').map(word => word.trim()).filter(Boolean) : 
          [],
        storyChoice: formData.storyChoice,
        problemLetters: unknownProblems,  // Send unselected problems instead
        storyInput: formData.storyInput || null,
        storyTopic: formData.storyTopic || null,
        storyLength: formData.storyLength ? parseInt(formData.storyLength) : null,
        readingLevel: formData.readingLevel ? parseInt(formData.readingLevel) : null,
        characterName: formData.characterName || 'Max'
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('API Response:', data);
    
    // Get decodability for both generated and input stories if not provided
    if (!data.decodability) {
      const storyText = data.generatedStory || data.processedStory;
      const decodabilityResult = await getDecodability(storyText, formData.problemLetters);
      return {
        ...data,
        decodability: decodabilityResult.decodability,
        badWords: decodabilityResult.badWords
      };
    }
    
    return {
      ...data,
      decodability: data.decodability,
      badWords: data.badWords || {}
    };
  } catch (error) {
    console.error('Error processing story:', error);
    throw error;
  }
};

export const getDecodability = async (text, selectedProblems) => {
  try {
    // Get all possible problems from PROBLEM_CATEGORIES
    const allProblems = Object.values(PROBLEM_CATEGORIES).flat();
    
    // Get the problems the user DOESN'T know (ones that weren't selected)
    const unknownProblems = allProblems.filter(problem => !selectedProblems.has(problem));

    const response = await fetch(`${API_BASE_URL}/decodability`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text || '',
        problems: unknownProblems  // Send unselected problems instead
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting decodability:', error);
    throw error;
  }
};

export const getWordPronunciation = async (word) => {
  try {
    const response = await fetch(`${API_BASE_URL}/pronounce?word=${encodeURIComponent(word)}`, {
      method: 'POST'
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const audioBlob = await response.blob();
    return URL.createObjectURL(audioBlob);
  } catch (error) {
    console.error('Error getting pronunciation:', error);
    throw error;
  }
}; 