const API_BASE_URL = process.env.NODE_ENV === 'production' ? 'https://decodables-backend.onrender.com/api' : 'http://localhost:5000/api';

export const processStory = async (formData) => {
  try {
    // Convert empty strings to null for optional fields
    const storyLength = formData.storyLength ? parseInt(formData.storyLength) : null;
    const readingLevel = formData.readingLevel ? parseInt(formData.readingLevel) : null;

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
        problemLetters: Array.from(formData.problemLetters),
        storyInput: formData.storyInput || null,
        storyTopic: formData.storyTopic || null,
        storyLength: storyLength,
        readingLevel: formData.readingLevel ? parseInt(formData.readingLevel) : null,
        characterName: formData.characterName || 'Max'
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // If it's an input story, get decodability immediately
    if (formData.storyChoice === 'i' && formData.storyInput) {
      const decodabilityResult = await getDecodability(formData.storyInput, formData.problemLetters);
      return {
        ...data,
        decodability: decodabilityResult.decodability
      };
    }
    
    return data;
  } catch (error) {
    console.error('Error processing story:', error);
    throw error;
  }
};

export const getDecodability = async (text, problems) => {
  try {
    const response = await fetch(`${API_BASE_URL}/decodability`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text || '',
        problems: Array.from(problems)
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