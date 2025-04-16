import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginFeature from './loginfeature';
import SignupFeature from './signupfeature';
import Dashboard from './dashboard';
import UploadImage from './UploadImage';
import AllItemsPage from './AllItemsPage';
import { AudioProvider } from './AudioContext';
import './loginfeature.css';

document.addEventListener('DOMContentLoaded', () => {
    const rootElement = document.getElementById('root');
    if (rootElement) {
        ReactDOM.render(
            <React.StrictMode>
                <AudioProvider>
                    <BrowserRouter>
                        <Routes>
                            <Route path="/" element={<LoginFeature />} />
                            <Route path="/signup" element={<SignupFeature />} />
                            <Route path="/dashboard" element={<Dashboard />} />
                            <Route path="/upload-image" element={<UploadImage />} />
                            <Route path="/all-items" element={<AllItemsPage />} />
                        </Routes>
                    </BrowserRouter>
                </AudioProvider>
            </React.StrictMode>,
            rootElement
        );
    } else {
        console.error('Root element not found!');
    }
});