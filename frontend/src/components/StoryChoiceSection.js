import React from 'react';

const StoryChoiceSection = ({ storyChoice, onChange }) => (
  <div className="form-group">
    <label>Would you like to generate a story or input one?</label>
    <div className="radio-group">
      <label>
        <input
          type="radio"
          name="storyChoice"
          value="g"
          checked={storyChoice === 'g'}
          onChange={onChange}
        />
        Generate Story
      </label>
      <label>
        <input
          type="radio"
          name="storyChoice"
          value="i"
          checked={storyChoice === 'i'}
          onChange={onChange}
        />
        Input Story
      </label>
    </div>
  </div>
);

export default StoryChoiceSection; 