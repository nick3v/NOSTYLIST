import React from 'react';
import Carousel from './Carousel';
import './dashboard.css';
import './carousel.css';

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <img src="/asterisk.jpg" alt="Logo" className="logo" />
      </header>

      <main className="carousel-wrapper">
        <Carousel />
      </main>
    </div>
  );
};

export default Dashboard;
