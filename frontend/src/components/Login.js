import React, { useState } from 'react';
import { GoogleLogin } from 'react-google-login';
import './Login.css';

const Login = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (credentials.username === 'DecodablesTest' && credentials.password === 'DecodablesTest1') {
      onLogin();
    } else {
      setError('Invalid username or password');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleGoogleLoginSuccess = (response) => {
    console.log('Google login success:', response);
    onLogin();
  };

  const handleGoogleLoginFailure = (response) => {
    console.log('Google login failure:', response);
    setError('Google login failed. Please try again.');
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>Login to Decodables</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username:</label>
            <input
              type="text"
              id="username"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">Password:</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              required
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="login-button">Login</button>
        </form>
        <GoogleLogin
          clientId={process.env.REACT_APP_GOOGLE_CLIENT_ID}
          buttonText="Log in with Google"
          onSuccess={handleGoogleLoginSuccess}
          onFailure={handleGoogleLoginFailure}
          cookiePolicy={'single_host_origin'}
        />
      </div>
    </div>
  );
};

export default Login;