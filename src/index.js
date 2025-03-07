import React from 'react';
import ReactDOM from 'react-dom';
import LoginFeature from './loginfeature';
import './loginfeature.css';

// Make sure the DOM is loaded before rendering
document.addEventListener('DOMContentLoaded', () => {
  const rootElement = document.getElementById('root');
  if (rootElement) {
    ReactDOM.render(
      <React.StrictMode>
        <LoginFeature />
      </React.StrictMode>,
      rootElement
    );
  } else {
    console.error('Root element not found!');
  }
});