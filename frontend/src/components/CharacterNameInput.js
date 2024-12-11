import React from 'react';

const CharacterNameInput = ({ characterName, onChange }) => (
  <div className="form-group">
    <label htmlFor="characterName">
      Enter the main character's name:
    </label>
    <input
      type="text"
      id="characterName"
      name="characterName"
      value={characterName}
      onChange={onChange}
      placeholder="e.g., Max"
    />
  </div>
);

export default CharacterNameInput; 