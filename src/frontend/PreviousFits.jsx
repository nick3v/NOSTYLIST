import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './PreviousFits.css';

const PreviousFits = () => {
  const [outfits, setOutfits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchOutfits();
  }, []);
  
  const fetchOutfits = async () => {
    setLoading(true);
    try {
      // Get user ID from localStorage
      const userId = localStorage.getItem('userId');
      
      if (!userId) {
        throw new Error('User not authenticated');
      }
      
      console.log('Fetching outfits for user ID:', userId);
      const response = await fetch(`/api/users/${userId}/outfits`);
      
      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('API response:', data);
      
      if (data.success && data.outfits && data.outfits.length > 0) {
        setOutfits(data.outfits);
        console.log(`Loaded ${data.outfits.length} outfits`);
      } else {
        console.log('No outfits found');
        setOutfits([]);
      }
    } catch (err) {
      console.error('Error fetching outfits:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteOutfit = async (outfitNumber) => {
    if (!confirm('Are you sure you want to delete this outfit? The individual items will still be available.')) {
      return;
    }
    
    setIsDeleting(true);
    try {
      const userId = localStorage.getItem('userId');
      
      if (!userId) {
        throw new Error('User not authenticated');
      }
      
      console.log(`Deleting outfit #${outfitNumber}`);
      const response = await fetch(`/api/users/${userId}/outfits/${outfitNumber}`, {
        method: 'DELETE',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || `Failed to delete outfit: ${response.status}`);
      }
      
      console.log('Delete response:', data);
      
      // Update the UI by removing the outfit locally for a faster UI response
      setOutfits(currentOutfits => 
        currentOutfits.filter(outfit => outfit.outfitNumber !== outfitNumber)
      );
      
      // Also refresh from server to ensure sync
      await fetchOutfits();
      
    } catch (err) {
      console.error('Error deleting outfit:', err);
      setError(`Failed to delete outfit: ${err.message}`);
      // Show error for 3 seconds then clear it
      setTimeout(() => setError(null), 3000);
    } finally {
      setIsDeleting(false);
    }
  };

  // Handle placeholder display for item types
  const renderPlaceholder = (type) => {
    const placeholders = {
      hat: '👒',
      shirt: '👕',
      jacket: '🧥',
      short: '🩳',
      pant: '👖',
      shoe: '👟'
    };
    
    return (
      <div className="placeholder-item">
        <span>{placeholders[type] || '👕'}</span>
      </div>
    );
  };

  return (
    <div className="previous-fits-container">
      <aside className="sidebar">
        <div className="sidebar-logo">NOSTYLIST</div>
        <nav className="sidebar-menu">
          <button onClick={() => navigate('/dashboard')}>Dashboard</button>
          <button onClick={() => navigate('/upload-image')}>Upload Image</button>
          <button onClick={() => navigate('/all-items')}>Show All Items</button>
          <button className="active">Previous Fits</button>
          <button>Logout</button>
        </nav>
      </aside>

      <div className="previous-fits-content">
        <header className="previous-fits-header">
          <h1>Your Previous Fits</h1>
          <p>All your saved outfits in one place</p>
        </header>
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={() => window.location.reload()} className="retry-button">
              Retry
            </button>
          </div>
        )}
        
        {loading ? (
          <div className="loading">
            <p>Loading your fits...</p>
            <div className="loading-spinner"></div>
          </div>
        ) : outfits.length === 0 ? (
          <div className="no-fits-message">
            <p>You haven't saved any fits yet!</p>
            <button onClick={() => navigate('/dashboard')}>Create Your First Fit</button>
          </div>
        ) : (
          <div className="outfits-grid">
            {outfits.map((outfit, index) => (
              <div key={index} className="outfit-card">
                <div className="outfit-header">
                  <h3>Fit #{outfit.outfitNumber || index + 1}</h3>
                </div>
                
                <div className="outfit-items">
                  {outfit.items && outfit.items.map((item, itemIndex) => (
                    <div key={itemIndex} className="outfit-item">
                      {item && item.base64 ? (
                        <img 
                          src={item.base64} 
                          alt={`${item.type} item`} 
                          title={`${item.type}`}
                        />
                      ) : (
                        item && renderPlaceholder(item.type)
                      )}
                    </div>
                  ))}
                </div>
                
                <div className="outfit-actions">
                  <button 
                    className="delete-outfit-button" 
                    onClick={() => handleDeleteOutfit(outfit.outfitNumber)}
                    disabled={isDeleting}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Debug information to help with API issues */} {/* Commented our debug option to hide sensitive data
        <div className="debug-info">
          <div className="debug-header" onClick={() => document.querySelector('.debug-content').classList.toggle('show')}>
            Debug Info (Click to toggle)
          </div>
          <div className="debug-content">
            <p>User ID: {localStorage.getItem('userId') || 'Not found'}</p>
            <p>Outfits count: {outfits.length}</p>
            <p>Loading: {loading.toString()}</p>
            <p>Error: {error || 'None'}</p>
            <p>First outfit data (if any):</p>
            <pre>{outfits.length > 0 ? JSON.stringify(outfits[0], null, 2) : 'No outfits'}</pre>
          </div>
        </div> */}
      </div>
    </div>
  );
};

export default PreviousFits;