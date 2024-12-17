import React, { useState, useEffect } from 'react';
import './StoryDisplay.css';

const StoryDisplay = ({ story, badWords, onFoundWords }) => {
  console.log('StoryDisplay Props:', { story, badWords });

  useEffect(() => {
    if (story && badWords) {
      const foundWords = {};
      const badWordsArray = Object.keys(badWords);
      
      badWordsArray.forEach(word => {
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        const matches = story.match(regex);
        if (matches) {
          foundWords[word] = matches.length;
        }
      });
      
      onFoundWords(foundWords);
    }
  }, [story, badWords, onFoundWords]);

  const highlightBadWords = (text) => {
    if (!text || !badWords) return text;
    
    const badWordsArray = Object.keys(badWords);
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