import React from 'react';
import { useNavigate } from 'react-router-dom';

const TestPage = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{ 
      backgroundColor: 'red', 
      color: 'white', 
      padding: '40px', 
      textAlign: 'center',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      fontSize: '24px'
    }}>
      <h1 style={{ marginBottom: '20px' }}>TEST PAGE</h1>
      <p style={{ marginBottom: '20px' }}>If you can see this, React is working!</p>
      <button 
        onClick={() => navigate('/dashboard')}
        style={{
          padding: '10px 20px',
          backgroundColor: 'white',
          color: 'red',
          border: 'none',
          borderRadius: '5px',
          fontSize: '18px',
          cursor: 'pointer'
        }}
      >
        Back to Dashboard
      </button>
    </div>
  );
};

export default TestPage; 