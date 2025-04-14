import React, { useEffect, useState } from 'react';
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
  const userId = 'your-user-id'; // Replace this with actual dynamic user ID

  useEffect(() => {
    fetch(`http://localhost:5001/api/users/${userId}/all-items`)
      .then(res => res.json())
      .then(data => {
        if (data.success && data.items.length > 0) {
          setItems(data.items);
        } else {
          setItems(fallbackItems.map(src => ({ base64: src, description: 'Fallback' })));
        }
      })
      .catch(err => {
        console.error('Error fetching images:', err);
        setItems(fallbackItems.map(src => ({ base64: src, description: 'Fallback' })));
      });
  }, []);

  return (
    <div className="all-items">
      <header className="all-items-header">
        All Items
      </header>
      <section className="items-gallery">
        {items.map((item, index) => (
          <div key={index} className="gallery-item-wrapper">
            <img
              src={item.base64}
              alt={item.description || `Clothing ${index}`}
              className="gallery-item"
            />
          </div>
        ))}
      </section>
    </div>
  );
};

export default AllItemsPage;
