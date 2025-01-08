import React, { useState, useEffect, useCallback } from 'react';
import { getWordPronunciation } from '../services/api';
import './StoryDisplay.css';

const StoryDisplay = ({ story, badWords, onFoundWords }) => {
  const [audioUrls, setAudioUrls] = useState({});
  const [isPlaying, setIsPlaying] = useState({});
  const [hoveredWord, setHoveredWord] = useState(null);

  // Pre-fetch audio for all bad words when story changes
  useEffect(() => {
    const fetchAudioForWords = async () => {
      if (!story || !badWords) return;
      
      const words = Object.keys(badWords);
      for (const word of words) {
        if (story.toLowerCase().includes(word) && !audioUrls[word]) {
          try {
            const audioUrl = await getWordPronunciation(word);
            setAudioUrls(prev => ({ ...prev, [word]: audioUrl }));
          } catch (error) {
            console.error(`Error fetching audio for ${word}:`, error);
          }
        }
      }
    };
    
    fetchAudioForWords();
  }, [story, badWords]); // Remove audioUrls from dependency array

  const handlePlayPronunciation = useCallback((word) => {
    try {
      const audio = new Audio(audioUrls[word]);
      setIsPlaying(prev => ({ ...prev, [word]: true }));
      
      audio.onended = () => {
        setIsPlaying(prev => ({ ...prev, [word]: false }));
      };
      
      audio.play();
    } catch (error) {
      console.error('Error playing pronunciation:', error);
    }
  }, [audioUrls]);

  const highlightBadWords = useCallback((text) => {
    if (!text || !badWords) return text;
    
    const badWordsArray = Object.keys(badWords);
    const pattern = badWordsArray.map(word => 
      word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    ).join('|');
    
    if (!pattern) return text;

    const regex = new RegExp(`\\b(${pattern})\\b`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, i) => {
      const lowerPart = part.toLowerCase();
      if (badWords[lowerPart]) {
        const uniqueCategories = [...new Set(badWords[lowerPart].categories)];
        const tooltip = `Problem categories: ${uniqueCategories.join(', ')}`;
        const isHovered = hoveredWord === lowerPart;
        
        return (
          <span 
            key={i} 
            className="bad-word-container"
            onMouseEnter={() => setHoveredWord(lowerPart)}
            onMouseLeave={() => setHoveredWord(null)}
          >
            <span className="bad-word" title={tooltip}>
              {part}
            </span>
            {isHovered && audioUrls[lowerPart] && (
              <button 
                className="pronunciation-button"
                onClick={(e) => {
                  e.preventDefault();
                  handlePlayPronunciation(lowerPart);
                }}
                disabled={isPlaying[lowerPart]}
              >
                {isPlaying[lowerPart] ? '🔊' : '🔈'}
              </button>
            )}
          </span>
        );
      }
      return part;
    });
  }, [badWords, hoveredWord, audioUrls, isPlaying, handlePlayPronunciation]);

  return (
    <div className="story-text">
      {highlightBadWords(story)}
    </div>
  );
};

export default StoryDisplay; 