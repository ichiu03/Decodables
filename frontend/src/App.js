import React, { useState } from 'react';
import './App.css';
import ProblemLettersSection from './components/ProblemLettersSection';
import StoryInputSection from './components/StoryInputSection';
import StoryGenerationSection from './components/StoryGenerationSection';
import StoryChoiceSection from './components/StoryChoiceSection';
import { processStory, getDecodability } from './services/api';
import CharacterNameInput from './components/CharacterNameInput';

function App() {
  const [formData, setFormData] = useState({
    unknownSightWords: '',
    storyChoice: 'i',
    problemLetters: new Set(),
    storyInput: '',
    storyTopic: '',
    storyLength: '',
    readingLevel: '',
    characterName: 'Max'
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name === 'problemLetters') {
      const newProblemLetters = new Set(formData.problemLetters);
      if (e.target.checked) {
        newProblemLetters.add(value);
      } else {
        newProblemLetters.delete(value);
      }
      setFormData(prevState => ({
        ...prevState,
        problemLetters: newProblemLetters
      }));
    } else {
      setFormData(prevState => ({
        ...prevState,
        [name]: value
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await processStory(formData);
      
      if (formData.storyChoice === 'g' && response.generatedStory) {
        // For generated stories, get decodability after generation
        const decodabilityResult = await getDecodability(response.generatedStory, formData.problemLetters);
        setResult({
          ...response,
          decodability: decodabilityResult.decodability
        });
      } else {
        // For input stories, decodability is already included in the response
        setResult(response);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Story Decodability Tool</h1>
      </header>
      <main className="App-main">
        <form onSubmit={handleSubmit} className="story-form">
          <div className="form-group">
            <label htmlFor="unknownSightWords">
              What sight words does the student not know? (separate with commas)
            </label>
            <input
              type="text"
              id="unknownSightWords"
              name="unknownSightWords"
              value={formData.unknownSightWords}
              onChange={handleInputChange}
              placeholder="e.g., the, and, but"
            />
          </div>

          <StoryChoiceSection 
            storyChoice={formData.storyChoice}
            onChange={handleInputChange}
          />

          <ProblemLettersSection
            selectedProblems={formData.problemLetters}
            onChange={handleInputChange}
          />

          {formData.storyChoice === 'i' ? (
            <StoryInputSection
              storyInput={formData.storyInput}
              onChange={handleInputChange}
            />
          ) : (
            <>
              <StoryGenerationSection
                storyTopic={formData.storyTopic}
                storyLength={formData.storyLength}
                onChange={handleInputChange}
              />
              <CharacterNameInput
                characterName={formData.characterName}
                onChange={handleInputChange}
              />
            </>
          )}

          <div className="form-group">
            <label htmlFor="readingLevel">
              Enter the grade level of the reader (only the grade number):
            </label>
            <input
              type="number"
              id="readingLevel"
              name="readingLevel"
              value={formData.readingLevel}
              onChange={handleInputChange}
              min="1"
              max="12"
            />
          </div>

          <button 
            type="submit" 
            className="submit-button"
            disabled={loading}
          >
            {loading ? 'Processing...' : 'Process Story'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            Error: {error}
          </div>
        )}

        {result && (
          <div className="result-section">
            <h2>Results</h2>
            {result.processedStory && (
              <div className="processed-story">
                <h3>Processed Story:</h3>
                <p>{result.processedStory}</p>
              </div>
            )}
            {result.generatedStory && (
              <div className="generated-story">
                <h3>Generated Story:</h3>
                <p>{result.generatedStory}</p>
              </div>
            )}
            {result.decodability !== undefined && (
              <div className="decodability">
                <h3>Decodability Score:</h3>
                <p>{(result.decodability * 100).toFixed(2)}%</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
