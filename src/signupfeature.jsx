import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './loginfeature.css';
import { useAudio } from './AudioContext';

const SignupFeature = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { isMuted, toggleMute } = useAudio();

  useEffect(() => {
    const resizeBackground = () => {
      document.body.style.backgroundSize = 'cover';
      document.body.style.backgroundPosition = 'center';
      document.body.style.backgroundAttachment = 'fixed';
    };

    resizeBackground();
    window.addEventListener('resize', resizeBackground);

    return () => {
      window.removeEventListener('resize', resizeBackground);
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('userId', data.user_id);
        window.location.href = '/dashboard';
      } else {
        setError(data.message || 'Signup failed. Please try again.');
      }
    } catch (err) {
      setError('An error occurred. Please try again later.');
      console.error('Signup error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
      <div className="show-login" style={{ width: '100vw', height: '100vh', overflow: 'hidden' }}>
        <button 
          className="mute-button" 
          onClick={toggleMute}
          title={isMuted ? "Unmute" : "Mute"}
        >
          {isMuted ? (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <line x1="23" y1="9" x2="17" y2="15"></line>
              <line x1="17" y1="9" x2="23" y2="15"></line>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
          )}
        </button>
        <div className="login-container" style={{ display: 'flex', opacity: 1, transform: 'translateX(0)', width: '100%' }}>
          <div className="login-card">
            <div className="login-header">
              <h1>NOSTYLIST</h1>
              <p>Create your account</p>
            </div>

            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                    type="text"
                    id="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    autoComplete="username"
                    placeholder="Choose a username"
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                    placeholder="Enter your email"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                    placeholder="Create a password"
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                    type="password"
                    id="confirmPassword"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    autoComplete="new-password"
                    placeholder="Confirm your password"
                />
              </div>

              <button
                  type="submit"
                  className="login-button"
                  disabled={loading}
              >
                {loading ? 'Creating account...' : 'Sign Up'}
              </button>
            </form>

            <div className="login-footer">
              <p>Already have an account? <Link to="/">Log in</Link></p>
            </div>
          </div>
        </div>
      </div>
  );
};

export default SignupFeature;