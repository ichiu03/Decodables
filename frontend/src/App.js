import React, { useState, useEffect } from 'react';
import './App.css';
import ProblemLettersSection from './components/ProblemLettersSection';
import StoryInputSection from './components/StoryInputSection';
import StoryGenerationSection from './components/StoryGenerationSection';
import StoryChoiceSection from './components/StoryChoiceSection';
import CharacterNameInput from './components/CharacterNameInput';
import Login from './components/Login';
import { processStory, getDecodability } from './services/api';
import StoryDisplay from './components/StoryDisplay';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Check if user was previously authenticated
  useEffect(() => {
    const auth = localStorage.getItem('isAuthenticated');
    if (auth === 'true') {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
    localStorage.setItem('isAuthenticated', 'true');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('isAuthenticated');
  };

  const [formData, setFormData] = useState({
    unknownSightWords: '',
    storyChoice: 'i',
    problemLetters: new Set(),
    storyInput: '',
    storyTopic: '',
    storyLength: '',
    readingLevel: '',
    characterName: ''
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
      console.log('Response in handleSubmit:', response);
      
      if (formData.storyChoice === 'g' && response.generatedStory) {
        // For generated stories, get decodability after generation
        const decodabilityResult = await getDecodability(response.generatedStory, formData.problemLetters);
        console.log('Decodability Result in handleSubmit:', decodabilityResult);
        setResult({
          ...response,
          decodability: decodabilityResult.decodability,
          badWords: decodabilityResult.badWords || []
        });
      } else {
        // For input stories, decodability is already included in the response
        setResult(response);
      }
      console.log('Final Result State:', result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Decodables</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
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
              placeholder="e.g., 5"
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
                <StoryDisplay 
                  story={result.processedStory} 
                  badWords={result.badWords || []}
                />
              </div>
            )}
            {result.generatedStory && (
              <div className="generated-story">
                <h3>Generated Story:</h3>
                <StoryDisplay 
                  story={result.generatedStory}
                  badWords={result.badWords || []}
                />
              </div>
            )}
            {result.decodability !== undefined && (
              <div className="decodability">
                <h3>Decodability Score:</h3>
                <p>{(result.decodability * 100).toFixed(2)}%</p>
                {result.badWords && Object.keys(result.badWords).length > 0 && (
                  <div className="bad-words-list">
                    <h4>Words with Problem Letters:</h4>
                    <div className="bad-words-grid">
                      {Object.entries(result.badWords).map(([word, count], index) => (
                        <span key={index} className="bad-word">
                          {word} ({count})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
