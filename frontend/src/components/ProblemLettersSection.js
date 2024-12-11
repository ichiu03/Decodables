import React from 'react';
import { PROBLEM_CATEGORIES } from '../constants/problemCategories';

const ProblemLettersSection = ({ selectedProblems, onChange }) => (
  <div className="form-group problem-letters-section">
    <label>Select Problem Letters/Sounds:</label>
    <div className="categories-container">
      {Object.entries(PROBLEM_CATEGORIES).map(([category, problems]) => (
        <div key={category} className="category-group">
          <h3>{category}</h3>
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

export default ProblemLettersSection; 