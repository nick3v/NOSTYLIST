import React, { useState, useEffect, useRef } from 'react';
import './loginfeature.css';

const LoginFeature = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const audioRef = useRef(null);

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

  const handleEnterClick = () => {
    setShowLogin(true);
    if (audioRef.current) {
      audioRef.current.play().catch(error => console.error('Playback failed', error));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('userId', data.user_id);
        window.location.href = '/dashboard';
      } else {
        setError(data.message || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      setError('An error occurred. Please try again later.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
      <div className={showLogin ? 'show-login' : ''}>
        <audio ref={audioRef} src="/In The Air.mp3" style={{ display: 'none' }}></audio>
        {!showLogin && (
            <div className="landing-container">
              <h1 className="landing-title" onClick={handleEnterClick}>NOSTYLIST</h1>
            </div>
        )}

        {showLogin && (
            <div className="login-container">
              <div className="login-card">
                <div className="login-header">
                  <h1>NOSTYLIST</h1>
                  <p>Sign in to continue</p>
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
                        placeholder="Enter your username"
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
                        autoComplete="current-password"
                        placeholder="Enter your password"
                    />
                  </div>

                  <button
                      type="submit"
                      className="login-button"
                      disabled={loading}
                  >
                    {loading ? 'Signing in...' : 'Sign In'}
                  </button>
                </form>

                <div className="login-footer">
                  <p>Don't have an account? <a href="/signup">Sign up</a></p>
                </div>
              </div>
            </div>
        )}
      </div>
  );
};

export default LoginFeature;
