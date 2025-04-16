import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginFeature from './loginfeature.jsx';
import SignupFeature from './signupfeature.jsx';
import Dashboard from './dashboard.jsx';
import UploadImage from './UploadImage.jsx';
import AllItemsPage from './AllItemsPage.jsx';
import { AudioProvider } from './AudioContext.jsx';
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