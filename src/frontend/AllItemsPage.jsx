import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AllItemsPage.css';

const fallbackItems = [
  '/rick pants.jpg',
  '/rick shorts.jpg',
  '/rick jacket.jpg',
  '/rick pants.jpg',
  '/rick shorts.jpg',
  '/rick jacket.jpg'
];

const AllItemsPage = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchItems = async () => {
      setLoading(true);
      try {
        // Get user ID from localStorage
        const userId = localStorage.getItem('userId');
        
        if (!userId) {
          throw new Error('User not authenticated');
        }
        
        console.log('Attempting to fetch all items for user:', userId);
        // Use relative URL that will work with the proxy setup
        const response = await fetch(`/api/users/${userId}/all-items`);
        
        console.log('API response status:', response.status);
        
        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success && data.items && data.items.length > 0) {
          // Process the image data
          const processedItems = data.items.map(item => {
            // Convert base64 string to proper URL format if needed
            const imageUrl = item.base64.startsWith('data:image') 
              ? item.base64 
              : `data:image/png;base64,${item.base64}`;
              
            return {
              ...item,
              base64: imageUrl,
              description: item.category || 'Item'
            };
          });
          
          setItems(processedItems);
          console.log(`Loaded ${processedItems.length} items from database`);
        } else {
          console.log('No items found, using fallback images');
          setItems(fallbackItems.map(src => ({ base64: src, description: 'Fallback' })));
        }
      } catch (err) {
        console.error('Error fetching images:', err);
        setError(err.message);
        // Use fallback items if there's an error
        setItems(fallbackItems.map(src => ({ base64: src, description: 'Fallback' })));
      } finally {
        setLoading(false);
      }
    };
    
    fetchItems();
  }, []);

  const handleBackToDashboard = () => {
    navigate('/dashboard');
  };

  return (
    <div className="all-items">
      <header className="all-items-header">
        <button className="back-button" onClick={handleBackToDashboard}>Back to Dashboard</button>
        <h1>All Items</h1>
      </header>
      
      {error && <div className="error-message">{error}</div>}
      
      {loading ? (
        <div className="loading-message">Loading your items...</div>
      ) : items.length === 0 ? (
        <div className="empty-message">
          <p>You don't have any items yet.</p>
          <button className="upload-button" onClick={() => navigate('/upload-image')}>
            Upload your first item
          </button>
        </div>
      ) : (
        <section className="items-gallery">
          {items.map((item, index) => (
            <div key={index} className="gallery-item-wrapper">
              <div className="gallery-item-image-container">
                <img
                  src={item.base64}
                  alt={item.description || `Clothing ${index}`}
                  className="gallery-item"
                />
              </div>
              <div className="item-category">{item.category || item.description}</div>
            </div>
          ))}
        </section>
      )}
    </div>
  );
};

export default AllItemsPage;
