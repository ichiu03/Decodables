import React, { useState, useEffect } from 'react';
import { getWordPronunciation } from '../services/api';
import './StoryDisplay.css';

const StoryDisplay = ({ story, badWords, onFoundWords }) => {
//   console.log('StoryDisplay Props:', { story, badWords });

  const [audioUrls, setAudioUrls] = useState({});
  const [isPlaying, setIsPlaying] = useState({});

  const handlePlayPronunciation = async (word) => {
    try {
      if (!audioUrls[word]) {
        const audioUrl = await getWordPronunciation(word);
        setAudioUrls(prev => ({ ...prev, [word]: audioUrl }));
      }

      const audio = new Audio(audioUrls[word]);
      setIsPlaying(prev => ({ ...prev, [word]: true }));
      
      audio.onended = () => {
        setIsPlaying(prev => ({ ...prev, [word]: false }));
      };
      
      audio.play();
    } catch (error) {
      console.error('Error playing pronunciation:', error);
    }
  };

  useEffect(() => {
    if (story && badWords) {
      const foundWords = {};
      const badWordsArray = Object.keys(badWords);
      
      badWordsArray.forEach(word => {
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        const matches = story.match(regex);
        if (matches) {
          const uniqueCategories = [...new Set(badWords[word].categories)];
          foundWords[word] = {
            count: matches.length,
            categories: uniqueCategories
          };
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
      if (badWords[part.toLowerCase()]) {
        const uniqueCategories = [...new Set(badWords[part.toLowerCase()].categories)];
        const tooltip = `Problem categories: ${uniqueCategories.join(', ')}`;
        return (
          <span 
            key={i} 
            className="bad-word-container"
          >
            <span className="bad-word" title={tooltip}>
              {part}
            </span>
            <button 
              className="pronunciation-button"
              onClick={() => handlePlayPronunciation(part.toLowerCase())}
              disabled={isPlaying[part.toLowerCase()]}
            >
              {isPlaying[part.toLowerCase()] ? '🔊' : '🔈'}
            </button>
          </span>
        );
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