import React from 'react';

const StoryInputSection = ({ storyInput, onChange }) => (
  <div className="form-group">
    <label htmlFor="storyInput">Copy and paste your text here:</label>
    <textarea
      id="storyInput"
      name="storyInput"
      value={storyInput}
      onChange={onChange}
      rows="6"
    />
  </div>
);

export default StoryInputSection; 