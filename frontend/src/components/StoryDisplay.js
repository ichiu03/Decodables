import React from 'react';
import './StoryDisplay.css';

const StoryDisplay = ({ story, badWords }) => {
  const highlightBadWords = (text) => {
    if (!text || !badWords) return text;

    // Create a regex pattern from bad words, escaping special characters
    const pattern = badWords.map(word => 
      word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    ).join('|');
    
    if (!pattern) return text;

    const regex = new RegExp(`\\b(${pattern})\\b`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, i) => {
      if (badWords.some(word => word.toLowerCase() === part.toLowerCase())) {
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