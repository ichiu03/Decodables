import React from 'react';
import './StoryDisplay.css';

const StoryDisplay = ({ story, badWords }) => {
  console.log('StoryDisplay Props:', { story, badWords });

  const highlightBadWords = (text) => {
    if (!text || !badWords) return text;
    console.log('Processing text:', text);
    console.log('Bad words:', badWords);

    // Convert badWords object to array if it's an object
    const badWordsArray = Array.isArray(badWords) ? badWords : Object.keys(badWords);
    
    // Create a regex pattern from bad words, escaping special characters
    const pattern = badWordsArray.map(word => 
      word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    ).join('|');
    
    if (!pattern) return text;

    const regex = new RegExp(`\\b(${pattern})\\b`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, i) => {
      const isBadWord = badWordsArray.some(word => word.toLowerCase() === part.toLowerCase());
      if (isBadWord) {
        return <span key={i} className="bad-word" title="This word contains problem letters">{part}</span>;
      }
      return part;
    });
  };

  return (
    <div className="story-text">
      {highlightBadWords(story)}
    </div>
  );
};

export default StoryDisplay; 