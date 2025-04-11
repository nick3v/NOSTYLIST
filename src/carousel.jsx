import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './carousel.css';

const allImages = [
  { src: '/rick shorts.jpg', category: 'Shorts' },
  { src: '/rick pants.jpg', category: 'Pants' },
  { src: '/rick jacket.jpg', category: 'Jackets' },
  { src: '/rick shorts.jpg', category: 'Shorts' },
  { src: '/rick pants.jpg', category: 'Pants' },
  { src: '/rick jacket.jpg', category: 'Jackets' }
];

const categories = ['Pants', 'Shorts', 'Jackets'];

const Carousel = () => {
  const carouselRef = useRef(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [activeCategories, setActiveCategories] = useState([...categories]);
  const [outfit, setOutfit] = useState([]);
  const [zoomedImg, setZoomedImg] = useState(null);
  const intervalRef = useRef(null);

  const isAllActive = activeCategories.length === categories.length;
  const filteredImages = allImages.filter(img => activeCategories.includes(img.category));

  const toggleCategory = (category) => {
    if (category === 'All') setActiveCategories([...categories]);
    else {
      setActiveCategories(prev =>
        prev.includes(category) ? prev.filter(c => c !== category) : [...prev, category]
      );
    }
  };

  const prevSlide = () => setCurrentIndex((prev) => (prev - 1 + filteredImages.length) % filteredImages.length);
  const nextSlide = () => setCurrentIndex((prev) => (prev + 1) % filteredImages.length);

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'ArrowLeft') prevSlide();
      if (e.key === 'ArrowRight') nextSlide();
    };
    document.addEventListener('keydown', handleKey);
    intervalRef.current = setInterval(nextSlide, 4000);
    return () => {
      document.removeEventListener('keydown', handleKey);
      clearInterval(intervalRef.current);
    };
  }, [filteredImages]);

  useEffect(() => {
    if (!carouselRef.current || filteredImages.length === 0) return;

    requestAnimationFrame(() => {
      const items = carouselRef.current?.children;
      if (!items || items.length !== filteredImages.length) return;

      const total = filteredImages.length;

      for (let i = 0; i < total; i++) {
        const item = items[i];
        if (!item) continue;

        item.className = 'carousel-item';
        let pos = (i - currentIndex + total) % total;
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
  }, [currentIndex, filteredImages]);

  const handleDrop = (e) => {
  e.preventDefault();
  const src = e.dataTransfer.getData('src');
  if (src && !outfit.includes(src)) {
    setOutfit(prev => [...prev, src]);
    // Remove from carousel by filtering it out of `allImages`
    allImages.splice(allImages.findIndex(item => item.src === src), 1);
    setCurrentIndex(0); // Reset index to re-render carousel layout
  }
};


  const handleDragStart = (e, src) => {
    e.dataTransfer.setData('src', src);
  };

  const removeFromOutfit = (src) => {
    setOutfit(prev => prev.filter(item => item !== src));
  };

  return (
    <div>
      <div className="category-toggle">
        <button
          className={`filter-btn ${isAllActive ? 'active' : ''}`}
          onClick={() => toggleCategory('All')}
        >
          All
        </button>
        {categories.map(cat => (
          <button
            key={cat}
            className={`filter-btn ${activeCategories.includes(cat) ? 'active' : ''}`}
            onClick={() => toggleCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="carousel-container">
        <button className="carousel-arrow left" onClick={prevSlide}>&larr;</button>
        <div className="carousel" ref={carouselRef}>
          <AnimatePresence mode="wait">
            {filteredImages.map((img, i) => (
              <motion.div
                className="carousel-item"
                key={i}
                drag="x"
                dragConstraints={{ left: 0, right: 0 }}
                onClick={() => setZoomedImg(img.src)}
              >
                <div
                  onDragStart={(e) => handleDragStart(e, img.src)}
                  draggable
                  style={{ width: '100%', height: '100%' }}
                >
                  <img
                    src={img.src}
                    alt={`img-${i}`}
                    style={{ width: '100%', height: '100%', pointerEvents: 'none' }}
                  />
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
        <button className="carousel-arrow right" onClick={nextSlide}>&rarr;</button>
      </div>

      <div
        className="drop-zone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
      >
        <h3>Your Fit</h3>
        {outfit.map((src, idx) => (
          <div key={idx} className="fit-item">
            <img src={src} alt="fit" />
            <button className="remove-btn" onClick={() => removeFromOutfit(src)}>✖</button>
          </div>
        ))}
      </div>

      {zoomedImg && (
        <div className="modal" onClick={() => setZoomedImg(null)}>
          <img src={zoomedImg} className="zoomed-img" alt="zoomed" />
        </div>
      )}
    </div>
  );
};

export default Carousel;
