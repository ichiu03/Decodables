import React from 'react';

const StoryGenerationSection = ({ storyTopic, storyLength, onChange }) => (
  <>
    <div className="form-group">
      <label htmlFor="storyTopic">Enter your story topic:</label>
      <input
        type="text"
        id="storyTopic"
        name="storyTopic"
        value={storyTopic}
        onChange={onChange}
        placeholder="e.g., A day at the beach"
      />
    </div>

    <div className="form-group">
      <label htmlFor="storyLength">
        Enter the length of the story (in words):
      </label>
      <input
        type="number"
        id="storyLength"
        name="storyLength"
        value={storyLength}
        onChange={onChange}
        min="1"
      />
    </div>
  </>
);

export default StoryGenerationSection; 