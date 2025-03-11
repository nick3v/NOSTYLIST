import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginFeature from './loginfeature';
import SignupFeature from './signupfeature';
import './loginfeature.css';

document.addEventListener('DOMContentLoaded', () => {
    const rootElement = document.getElementById('root');
    if (rootElement) {
        ReactDOM.render(
            <React.StrictMode>
                <BrowserRouter>
                    <Routes>
                        <Route path="/" element={<LoginFeature />} />
                        <Route path="/signup" element={<SignupFeature />} />
                    </Routes>
                </BrowserRouter>
            </React.StrictMode>,
            rootElement
        );
    } else {
        console.error('Root element not found!');
    }
});
