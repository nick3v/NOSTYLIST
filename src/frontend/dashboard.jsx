import React from 'react';
import { useNavigate } from 'react-router-dom';
import Carousel from './Carousel';
import './dashboard.css';
import './carousel.css';

const Dashboard = () => {
    const navigate = useNavigate();

    return (
        <div className="dashboard-container">
            <aside className="sidebar">
                <div className="sidebar-logo">NOSTYLIST</div>
                <nav className="sidebar-menu">
                    <button>Profile</button>
                    <button onClick={() => navigate('/upload-image')}>Upload Image</button>
                    <button onClick={() => navigate('/all-items')}>Show All Items</button>
                    <button onClick={() => navigate('/previous-fits')}>Previous Fits</button>
                    <button>Logout</button>
                </nav>
            </aside>

            <div className="dashboard-content">
                <header className="dashboard-header">
                    <img src="/asterisk.jpg" alt="Logo" className="logo" />
                </header>

                <main className="carousel-wrapper">
                    <Carousel />
                </main>
            </div>
        </div>
    );
};

export default Dashboard;