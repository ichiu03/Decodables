import React from 'react';
import './ProblemLettersSection.css';
import { PROBLEM_CATEGORIES } from '../constants/problemCategories';

const ProblemLettersSection = ({ selectedProblems, onChange }) => {
  const areAllProblemsSelected = (problems) => {
    return problems.every(problem => selectedProblems.has(problem));
  };

  const handleSelectAll = (category, problems) => {
    const allSelected = areAllProblemsSelected(problems);
    const newProblems = new Set(selectedProblems);
    
    problems.forEach(problem => {
      if (allSelected) {
        newProblems.delete(problem);
      } else {
        newProblems.add(problem);
      }
    });
    
    const event = {
      target: {
        type: 'checkbox',
        name: 'problemLetters',
        checked: !allSelected,
        value: newProblems
      }
    };
    onChange(event);
  };

  return (
    <div className="form-group problem-letters-section">
      <label>Select Problem Letters/Sounds:</label>
      <div className="categories-container">
        {Object.entries(PROBLEM_CATEGORIES).map(([category, problems]) => (
          <div key={category} className="category-group">
            <div className="category-header">
              <h3>{category}</h3>
              <button
                type="button"
                className={`select-all-button ${areAllProblemsSelected(problems) ? 'selected' : ''}`}
                onClick={() => handleSelectAll(category, problems)}
              >
                {areAllProblemsSelected(problems) ? 'Deselect All' : 'Select All'}
              </button>
            </div>
            <div className="problems-grid">
              {problems.map(problem => (
                <label key={problem} className="problem-checkbox">
                  <input
                    type="checkbox"
                    name="problemLetters"
                    value={problem}
                    checked={selectedProblems.has(problem)}
                    onChange={onChange}
                  />
                  <span>{problem}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProblemLettersSection; 