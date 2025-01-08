import React, { useState, useEffect, useCallback } from 'react';
import { getWordPronunciation } from '../services/api';
import './StoryDisplay.css';

const StoryDisplay = ({ story, badWords, onFoundWords }) => {
  const [audioUrls, setAudioUrls] = useState({});
  const [isPlaying, setIsPlaying] = useState({});
  const [hoveredWord, setHoveredWord] = useState(null);
  const [isPlayingStory, setIsPlayingStory] = useState(false);
  const [storyAudio] = useState(new Audio(`${process.env.PUBLIC_URL}/story.mp3`));

  // Add error handling for audio loading
  useEffect(() => {
    storyAudio.onerror = () => {
      console.error('Error loading story audio');
      setIsPlayingStory(false);
    };
  }, [storyAudio]);

  const handlePlayStory = useCallback(() => {
    if (isPlayingStory) {
      storyAudio.pause();
      storyAudio.currentTime = 0;
      setIsPlayingStory(false);
    } else {
      // Reload the audio source when playing
      storyAudio.src = `${process.env.PUBLIC_URL}/story.mp3?t=${Date.now()}`;
      storyAudio.play().catch(error => {
        console.error('Error playing story:', error);
        setIsPlayingStory(false);
      });
      setIsPlayingStory(true);
    }
  }, [storyAudio, isPlayingStory]);

  useEffect(() => {
    storyAudio.onended = () => setIsPlayingStory(false);
    return () => {
      storyAudio.pause();
      storyAudio.currentTime = 0;
    };
  }, [storyAudio]);

  // Pre-fetch audio for all bad words when story changes
  useEffect(() => {
    const fetchAudioForWords = async () => {
      if (!story || !badWords) return;
      
      const words = Object.keys(badWords);
      for (const word of words) {
        // Create a regex to match whole words only
        const wordRegex = new RegExp(`\\b${word}\\b`, 'i');
        if (wordRegex.test(story) && !audioUrls[word]) {
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
    <div className="story-container">
      <div className="story-header">
        <button 
          className="story-audio-button"
          onClick={handlePlayStory}
        >
          {isPlayingStory ? '🔊 Playing...' : '🔊'}
        </button>
      </div>
      <div className="story-text">
        {highlightBadWords(story)}
      </div>
    </div>
  );
};

export default StoryDisplay; 