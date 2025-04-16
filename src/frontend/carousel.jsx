import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './carousel.css';

// Keep as fallback if API fails
const initialImages = [
  { src: '/rick shorts.jpg', category: 'Shorts' },
  { src: '/rick pants.jpg', category: 'Pants' },
  { src: '/rick jacket.jpg', category: 'Long Sleeves' },
  { src: '/rick shorts.jpg', category: 'Shorts' },
  { src: '/shirt.jpg', category: 'Shirts' },
  { src: '/rick pants.jpg', category: 'Pants' },
  { src: '/long sleeve.jpg', category: 'Long Sleeves' },
  { src: '/carti hat.jpg', category: 'Hats' },
  { src: '/rick boots.jpg', category: 'Shoes' }
];

// Map database categories to UI categories
const categoryMapping = {
  'hat': 'Hats',
  'shirt': 'Shirts',
  'pant': 'Pants',
  'shoe': 'Shoes',
  'long sleeve': 'Long Sleeves',
  'shorts': 'Shorts'
};

// UI categories for filtering - match exactly with the categoryMapping values
const categories = ['Hats', 'Shirts', 'Pants', 'Shorts', 'Long Sleeves', 'Shoes'];

const Carousel = () => {
  const carouselRef = useRef(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [allImages, setAllImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeCategories, setActiveCategories] = useState([...categories]);
  const [outfit, setOutfit] = useState([]);
  const [zoomedImg, setZoomedImg] = useState(null);
  const intervalRef = useRef(null);
  const [carouselKey, setCarouselKey] = useState(0);

  // Fetch images from the backend when component mounts
  useEffect(() => {
    const fetchImages = async () => {
      setLoading(true);
      try {
        // Get user ID from localStorage
        const userId = localStorage.getItem('userId');
        
        if (!userId) {
          console.error('User not authenticated');
          setError('User not authenticated');
          setAllImages([...initialImages]);  // Use fallback images
          return;
        }
        
        // Fetch images from the API
        console.log('Attempting to fetch images for user:', userId);
        
        // Use relative URL that will work with the proxy setup
        const response = await fetch(`/api/users/${userId}/all-items`);
        
        console.log('API response status:', response.status);
        
        // Handle non-200 responses
        if (!response.ok) {
          console.error(`Server responded with status: ${response.status}`);
          
          // Use fallback images for any error
          setError(`Server error (${response.status})`);
          console.log('Using fallback images due to server error');
          setAllImages([...initialImages]);
          return;
        }
        
        try {
          const data = await response.json();
          console.log('API response data:', data);
          
          if (data.success && data.items && data.items.length > 0) {
            // Transform API data to match component's expected format
            const formattedImages = data.items.map(item => {
              // Image URL already includes data:image prefix from the API
              const imageUrl = item.base64;
              
              // Log raw category from backend for debugging
              console.log(`Item category from backend: "${item.category}"`);
                
              // Map category from database to UI category
              const mappedCategory = categoryMapping[item.category.toLowerCase()] || 'Other';
              console.log(`Mapped to UI category: "${mappedCategory}"`);
              
              return {
                src: imageUrl,
                category: mappedCategory,
                id: item.id || Math.random().toString()
              };
            });
            
            console.log('Formatted images:', formattedImages);
            
            if (formattedImages.length > 0) {
              setAllImages(formattedImages);
              console.log('Loaded images from database:', formattedImages.length);
            } else {
              console.log('No formatted images, using fallback images');
              setAllImages([...initialImages]);
            }
          } else {
            console.log('No images found or API returned error, using fallback images');
            setAllImages([...initialImages]);  // Use fallback images if no data
          }
        } catch (jsonError) {
          console.error('Error parsing JSON response:', jsonError);
          setError('Error parsing server response');
          setAllImages([...initialImages]);
        }
      } catch (err) {
        console.error('Error fetching images:', err);
        setError(err.message);
        setAllImages([...initialImages]);  // Use fallback images on error
      } finally {
        setLoading(false);
      }
    };
    
    fetchImages();
  }, []);

  const isAllActive = activeCategories.length === categories.length;
  const filteredImages = allImages.filter(img => activeCategories.includes(img.category));

  // Ensure proper filtering when active categories change
  useEffect(() => {
    if (activeCategories.length === 1) {
      console.log(`Ensuring only ${activeCategories[0]} items are showing`);
      // Force filtered images to be recalculated with latest state
      const currentFiltered = allImages.filter(img => activeCategories.includes(img.category));
      console.log(`Found ${currentFiltered.length} items matching category ${activeCategories[0]}`);
      
      // Force rebuild carousel to ensure filters are applied immediately
      setCarouselKey(prev => prev + 1);
    }
  }, [activeCategories, allImages]);

  // Log filtering for debugging
  useEffect(() => {
    console.log('Active categories:', activeCategories);
    console.log('Total images:', allImages.length);
    console.log('Filtered images:', filteredImages.length);
    
    // Log categories of all images for debugging
    const categoryCounts = {};
    allImages.forEach(img => {
      categoryCounts[img.category] = (categoryCounts[img.category] || 0) + 1;
    });
    console.log('Images by category:', categoryCounts);
  }, [activeCategories, allImages, filteredImages.length]);

  const toggleCategory = (category) => {
    if (category === 'All') {
      console.log('Setting all categories active');
      setActiveCategories([...categories]);
    } else {
      console.log(`Setting only category "${category}" active`);
      // Show only the clicked category
      setActiveCategories([category]);
    }
    // Reset to first slide when changing filters
    setCurrentIndex(0);
    // Force rebuild carousel when category changes
    setCarouselKey(prev => prev + 1);
  };

  const prevSlide = () => {
    setCurrentIndex(prevIndex => {
        // Recalculate filtered length inside the update function for accuracy
        const currentFilteredLength = allImages.filter(img => activeCategories.includes(img.category)).length;
        if (currentFilteredLength === 0) return 0; // Avoid NaN with modulo 0
        return (prevIndex - 1 + currentFilteredLength) % currentFilteredLength;
    });
  };

  const nextSlide = () => {
    setCurrentIndex(prevIndex => {
        // Recalculate filtered length inside the update function for accuracy
        const currentFilteredLength = allImages.filter(img => activeCategories.includes(img.category)).length;
        if (currentFilteredLength === 0) return 0; // Avoid NaN with modulo 0
        return (prevIndex + 1) % currentFilteredLength;
    });
  };

  // Simple function to handle image zoom
  const handleImageClick = (src, index) => {
    setCurrentIndex(index);
    setZoomedImg(src);
  };

  // Simple function to close the zoomed view
  const closeZoom = () => {
    setZoomedImg(null);
    clearInterval(intervalRef.current);
    // Ensure carousel resumes auto-rotation
    if (filteredImages.length > 0) {
        intervalRef.current = setInterval(nextSlide, 4000);
    }
  };

  // Auto-rotation and keyboard navigation control
  useEffect(() => {
    const currentFilteredImages = allImages.filter(img => activeCategories.includes(img.category));
    
    clearInterval(intervalRef.current);
    intervalRef.current = null;

    if (!zoomedImg && currentFilteredImages.length > 0) {
        intervalRef.current = setInterval(nextSlide, 4000);
    }

    const handleKey = (e) => {
        if (!zoomedImg) {
            if (e.key === 'ArrowLeft') prevSlide();
            if (e.key === 'ArrowRight') nextSlide();
        }
    };
    document.addEventListener('keydown', handleKey);

    return () => {
        document.removeEventListener('keydown', handleKey);
        clearInterval(intervalRef.current);
    };
}, [allImages, activeCategories, zoomedImg]); // Keep dependencies

// Update carousel item classes based on index and filtered list
useEffect(() => {
    const currentFilteredImages = allImages.filter(img => activeCategories.includes(img.category));
    const newLength = currentFilteredImages.length;

    if (!carouselRef.current) {
        return;
    }

    let effectiveIndex = currentIndex;
    if (newLength === 0) {
        if (currentIndex !== 0) setCurrentIndex(0); 
        effectiveIndex = 0;
    } else if (currentIndex >= newLength) {
        effectiveIndex = Math.max(0, newLength - 1);
        setCurrentIndex(effectiveIndex);
    }

    requestAnimationFrame(() => {
        if (!carouselRef.current) return;
        const items = carouselRef.current.children;
        
        if (items.length !== newLength) {
             // Enable this console log for debugging
             console.warn(`Positioning rAF: Mismatch! DOM items (${items.length}) vs Filtered (${newLength}).`);
             return; 
        }
        
        if (newLength === 0) { 
             return;
        }

        const total = newLength;
        for (let i = 0; i < total; i++) {
            const item = items[i];
            if (!item) continue;

            item.className = 'carousel-item';
            let pos = (i - effectiveIndex + total) % total;
            if (pos > Math.floor(total / 2)) pos -= total;

            if (pos === 0) item.classList.add('active');
            else if (pos === -1 || (total < 3 && pos === total - 1)) item.classList.add('prev');
            else if (pos === 1 || (total < 3 && pos === -(total - 1))) item.classList.add('next');
            else if (pos === -2) item.classList.add('prev-2');
            else if (pos === 2) item.classList.add('next-2');
            else if (pos <= -3) item.classList.add('prev-3');
            else if (pos >= 3) item.classList.add('next-3');
        }
    });
}, [currentIndex, allImages, activeCategories]); // Keep dependencies

  const handleDrop = (e) => {
    e.preventDefault();
    const src = e.dataTransfer.getData('src');
    
    if (src && !outfit.includes(src)) {
        // Add to outfit
        setOutfit(prev => [...prev, src]);
        
        // Remove from allImages
        setAllImages(prev => prev.filter(item => item.src !== src));
        
        // Force reset carousel position and re-render the entire carousel
        setCurrentIndex(0);
        setCarouselKey(prev => prev + 1);
    }
  };

  const handleDragStart = (e, src) => {
    e.dataTransfer.setData('src', src);
  };

  const removeFromOutfit = (src) => {
    let categoryGuess;
    // Attempt to find the *original* item data if it came from the fetched list
    const originalItem = allImages.find(img => img.src === src) || initialImages.find(img => img.src === src);

    if (originalItem) {
        categoryGuess = originalItem.category;
    } else {
        // Fallback category guessing for all 6 categories
        categoryGuess = src.includes('hat') ? 'Hats' :
                        src.includes('shoe') || src.includes('boots') ? 'Shoes' :
                        src.includes('shorts') ? 'Shorts' :
                        src.includes('sleeve') ? 'Long Sleeves' :
                        src.includes('shirt') ? 'Shirts' :
                        'Pants'; // Default to pants
    }
    
    console.log(`Removing from outfit: ${src.substring(0, 20)}..., Category: ${categoryGuess}`);
    
    // First ensure the category is active so item will be visible
    if (!activeCategories.includes(categoryGuess)) {
      console.log(`Activating category ${categoryGuess} to make item visible`);
      setActiveCategories(prev => [...prev, categoryGuess]);
    }

    // Remove from outfit
    setOutfit(prev => prev.filter(item => item !== src));
    
    // Add the item back to allImages and ensure it appears at the front
    const newItem = { 
      src, 
      category: categoryGuess, 
      id: `returned-${Date.now()}-${Math.random().toString(36).substring(2, 9)}` 
    };
    
    console.log(`Adding back to carousel with ID: ${newItem.id}`);
    
    // First add the new item, then reset state to ensure carousel rebuilds
    setAllImages(prev => [newItem, ...prev]);
    
    // Reset carousel to show the returned item (index 0)
    setTimeout(() => {
      setCurrentIndex(0);
      setCarouselKey(prev => prev + 1);
      console.log('Carousel reset to show returned item');
    }, 0);
  };

  // Loading and error states
  if (loading && allImages.length === 0) {
    return <div className="dashboard-container"><div className="loading">Loading images...</div></div>;
  }

  return (
    <div className="dashboard-container">
      {error && <div className="error-message">{error}</div>}
      
      <div className="dashboard-content">
        <div className="category-toggle">
          <button
            className={`filter-btn ${isAllActive ? 'active' : ''}`}
            onClick={() => toggleCategory('All')}
          >
            All Items
          </button>
          {categories.map(cat => {
            // Add emoji icons to make categories more visual
            let buttonIcon = '';
            switch(cat) {
              case 'Hats':
                buttonIcon = '👒 ';
                break;
              case 'Shirts':
                buttonIcon = '👕 ';
                break;
              case 'Pants':
                buttonIcon = '👖 ';
                break;
              case 'Shorts':
                buttonIcon = '🩳 ';
                break;
              case 'Long Sleeves':
                buttonIcon = '🧥 ';
                break;
              case 'Shoes':
                buttonIcon = '👟 ';
                break;
              default:
                buttonIcon = '';
            }
            
            return (
              <button
                key={cat}
                className={`filter-btn ${activeCategories.includes(cat) && activeCategories.length === 1 ? 'active' : ''}`}
                onClick={() => toggleCategory(cat)}
              >
                {buttonIcon}{cat}
              </button>
            );
          })}
        </div>

        {filteredImages.length === 0 ? (
          <div className="no-images-message">No images found for selected categories</div>
        ) : (
          <div className={`carousel-container ${zoomedImg ? 'zoomed-active' : ''}`} key={carouselKey}>
            {!zoomedImg && <button className="carousel-arrow left" onClick={prevSlide}>&larr;</button>}
            <div className="carousel" ref={carouselRef}>
              {filteredImages.map((img, i) => (
                <div className="carousel-item" key={`${img.id}-${carouselKey}`}>
                  <div className="carousel-item-content">
                    <div 
                      className="image-wrapper"
                      onDragStart={(e) => handleDragStart(e, img.src)}
                      draggable={!zoomedImg}
                    >
                      <img
                        src={img.src}
                        alt={`${img.category} item`}
                        onClick={() => handleImageClick(img.src, i)}
                        className="carousel-image"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {!zoomedImg && <button className="carousel-arrow right" onClick={nextSlide}>&rarr;</button>}
          </div>
        )}
      </div>

      <div
        className="right-sidebar"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <h2>Your Fit</h2>
        {outfit.map((src, idx) => (
          <div key={idx} className="fit-item">
            <img src={src} alt="fit" />
            <button className="remove-btn" onClick={() => removeFromOutfit(src)}>✖</button>
          </div>
        ))}
      </div>

      {zoomedImg && (
        <div className="zoomed-overlay" onClick={closeZoom}>
          <div className="zoomed-container" onClick={(e) => e.stopPropagation()}>
            <img src={zoomedImg} alt="Enlarged view" className="zoomed-image" />
          </div>
        </div>
      )}
    </div>
  );
};

export default Carousel;
