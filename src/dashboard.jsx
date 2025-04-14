import React from 'react';
import { useNavigate } from 'react-router-dom'; // 👈 Import this
import Carousel from './Carousel';
import './dashboard.css';
import './carousel.css';

const Dashboard = () => {
  const navigate = useNavigate(); // 👈 Initialize navigation

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <div className="sidebar-logo">NOSTYLIST</div>
        <nav className="sidebar-menu">
          <button>Profile</button>
          <button>Upload Image</button>
          <button onClick={() => navigate('/all-items')}>Show All Items</button>
          <button>Previous Fits</button>
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
