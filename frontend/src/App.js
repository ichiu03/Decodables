import React, { useState, useEffect } from 'react';
import './App.css';
import ProblemLettersSection from './components/ProblemLettersSection';
import StoryInputSection from './components/StoryInputSection';
import StoryGenerationSection from './components/StoryGenerationSection';
import StoryChoiceSection from './components/StoryChoiceSection';
import CharacterNameInput from './components/CharacterNameInput';
import Login from './components/Login';
import { processStory} from './services/api';
import StoryDisplay from './components/StoryDisplay';
import { Document, Packer, Paragraph } from 'docx';
import { jsPDF } from 'jspdf';


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
  const [foundBadWords, setFoundBadWords] = useState({});


  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name === 'problemLetters') {
      if (value instanceof Set) {
        // Handle "Select All" case
        setFormData(prevState => ({
          ...prevState,
          problemLetters: value
        }));
      } else {
        // Handle individual checkbox case
        setFormData(prevState => {
          const newProblemLetters = new Set(prevState.problemLetters);
          if (e.target.checked) {
            newProblemLetters.add(value);
          } else {
            newProblemLetters.delete(value);
          }
          return {
            ...prevState,
            problemLetters: newProblemLetters
          };
        });
      }
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
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };


  const handleFoundWords = (words) => {
    setFoundBadWords(words);
  };


  const handleDownload = async (format) => {
    try {
      const content = result.processedStory || result.generatedStory;
      if (!content) return;

      if (format === 'docx') {
        // Create DOCX document
        const doc = new Document({
          sections: [{
            properties: {},
            children: [
              new Paragraph({
                text: content
              })
            ],
          }],
        });

        // Generate and download the DOCX file
        const blob = await Packer.toBlob(doc);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'story.docx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } 
      else if (format === 'pdf') {
        // Create PDF document
        const pdf = new jsPDF();
        
        // Split content into lines that fit the page width
        const lines = pdf.splitTextToSize(content, 180);
        
        // Add text to PDF
        pdf.setFontSize(12);
        let yPosition = 20;
        
        // Add lines page by page
        for (let i = 0; i < lines.length; i++) {
          if (yPosition > 280) {
            pdf.addPage();
            yPosition = 20;
          }
          pdf.text(lines[i], 15, yPosition);
          yPosition += 7;
        }
        
        // Download the PDF
        pdf.save('story.pdf');
      }
    } catch (err) {
      setError(`Error downloading ${format} file: ${err.message}`);
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
                  badWords={result.badWords || {}}
                  onFoundWords={handleFoundWords}
                />
              </div>
            )}
            {result.generatedStory && (
              <div className="generated-story">
                <h3>Generated Story:</h3>
                <StoryDisplay
                  story={result.generatedStory}
                  badWords={result.badWords || {}}
                  onFoundWords={handleFoundWords}
                />
              </div>
            )}
            {result && result.decodability !== undefined && (
              <div className="decodability">
                <h3>Decodability Score:</h3>
                <p>{(result.decodability * 100).toFixed(2)}%</p>
                {Object.keys(foundBadWords).length > 0 && (
                  <div className="bad-words-list">
                    <h4>Words with Problem Letters:</h4>
                    <div className="bad-words-grid">
                      {Object.entries(foundBadWords).map(([word, data], index) => (
                        <span
                          key={index}
                          className="bad-word"
                          title={`Problem categories: ${data.categories.join(', ')}`}
                        >
                          {word} ({data.count})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            {(result.processedStory || result.generatedStory) && (
              <div className="download-buttons">
                <button
                  className="download-button docx"
                  onClick={() => handleDownload('docx')}
                >
                  Download as DOCX
                </button>
                <button
                  className="download-button pdf"
                  onClick={() => handleDownload('pdf')}
                >
                  Download as PDF
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}


export default App;