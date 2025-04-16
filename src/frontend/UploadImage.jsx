import React, { useState, useRef, useEffect } from 'react';
import './UploadImage.css';
import { useNavigate } from 'react-router-dom';

const UploadImage = () => {
    const navigate = useNavigate();
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [category, setCategory] = useState('shirt');
    const [isCropping, setIsCropping] = useState(false);
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const [imagePosition, setImagePosition] = useState({ x: 0, y: 0 });
    const [scale, setScale] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const canvasRef = useRef(null);
    const outlineImgRef = useRef(null);

    const categories = ['hat', 'shirt', 'pant', 'shoe', 'long sleeve', 'shorts'];

    // Handle file selection
    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setSelectedFile(file);
        setPreviewUrl(URL.createObjectURL(file));
        setIsCropping(true);
        setImagePosition({ x: 0, y: 0 });
        setScale(1);
    };

    // Mouse event handlers for dragging the image
    const startDrag = (e) => {
        if (!previewUrl) return;
        setIsDragging(true);
        setDragStart({
            x: e.clientX,
            y: e.clientY
        });
    };

    const onDrag = (e) => {
        if (!isDragging) return;

        const deltaX = e.clientX - dragStart.x;
        const deltaY = e.clientY - dragStart.y;

        setImagePosition(prev => ({
            x: prev.x + deltaX,
            y: prev.y + deltaY
        }));

        setDragStart({
            x: e.clientX,
            y: e.clientY
        });
    };

    const endDrag = () => {
        setIsDragging(false);
    };

    // Handle zoom slider change
    const handleZoomChange = (e) => {
        setScale(parseFloat(e.target.value));
    };

    // Initial rendering and updates to the canvas
    useEffect(() => {
        if (!canvasRef.current || !previewUrl) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');

        // Load the user's image
        const userImage = new Image();
        userImage.crossOrigin = "Anonymous";

        userImage.onload = () => {
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw user image with position and scale
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;

            ctx.save();
            ctx.translate(centerX + imagePosition.x, centerY + imagePosition.y);
            ctx.scale(scale, scale);
            ctx.drawImage(
                userImage,
                -userImage.width / 2,
                -userImage.height / 2,
                userImage.width,
                userImage.height
            );
            ctx.restore();

            // Direct mapping to the outline images with correct filenames
            const outlineImage = new Image();

            // Map category to correct filename
            let outlineFile = '';
            if (category === 'hat') outlineFile = 'hatOutline.png';
            else if (category === 'long sleeve') outlineFile = 'longOutline.png';
            else if (category === 'pant') outlineFile = 'pantsOutline.png';
            else if (category === 'shirt') outlineFile = 'shirtOutline.png';
            else if (category === 'shoe') outlineFile = 'shoesOutline.png';
            else if (category === 'shorts') outlineFile = 'shortsOutline.png';

            outlineImage.src = `/${outlineFile}`;
            console.log('Loading outline:', outlineImage.src);

            outlineImage.onload = () => {
                // Calculate scaling to fit within canvas
                const maxWidth = canvas.width * 0.8;
                const maxHeight = canvas.height * 0.8;

                // Calculate scale while maintaining aspect ratio
                let scaleFactor = 1;
                if (outlineImage.width > maxWidth || outlineImage.height > maxHeight) {
                    const widthRatio = maxWidth / outlineImage.width;
                    const heightRatio = maxHeight / outlineImage.height;
                    scaleFactor = Math.min(widthRatio, heightRatio);
                }

                // Calculate centered position
                const scaledWidth = outlineImage.width * scaleFactor;
                const scaledHeight = outlineImage.height * scaleFactor;
                const posX = (canvas.width - scaledWidth) / 2;
                const posY = (canvas.height - scaledHeight) / 2;

                // Draw the scaled outline
                ctx.drawImage(
                    outlineImage,
                    posX,
                    posY,
                    scaledWidth,
                    scaledHeight
                );
            };

            outlineImage.onerror = (err) => {
                console.error(`Failed to load outline for ${category}:`, err);
            };
        };

        userImage.src = previewUrl;
    }, [previewUrl, category, imagePosition, scale]);

    // Test the API connection
    const testApiConnection = async () => {
        try {
            // Use absolute URL to match the crop-image endpoint
            const response = await fetch('http://localhost:5001/api/test');
            const data = await response.json();
            console.log('API test response:', data);
            return true;
        } catch (err) {
            console.error('API test failed:', err);
            return false;
        }
    };

    // Process and save the cropped image using the Flask backend
    const handleCrop = async () => {
        if (!selectedFile) {
            setError('Please select an image first');
            return;
        }

        setIsLoading(true);
        setError('');

        // Test API connection first
        const isApiWorking = await testApiConnection();
        if (!isApiWorking) {
            setError('Cannot connect to server API. Please check if the server is running.');
            setIsLoading(false);
            return;
        }

        try {
            // Get user ID from localStorage or your auth system
            const userId = localStorage.getItem('userId'); // Adjust as needed

            if (!userId) {
                setError('User not authenticated');
                setIsLoading(false);
                return;
            }

            // Create form data to send to the server
            const formData = new FormData();
            formData.append('image', selectedFile);
            formData.append('category', category);
            formData.append('userId', userId);
            formData.append('scale', scale);
            formData.append('offsetX', imagePosition.x);
            formData.append('offsetY', imagePosition.y);

            // Send the request to the Flask backend
            const response = await fetch('http://localhost:5001/api/crop-image', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });

            // Check if response is OK and has JSON content
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const textResponse = await response.text();
                console.error('Non-JSON response:', textResponse);
                throw new Error('Server did not return JSON. Response: ' + textResponse.substring(0, 100));
            }

            const data = await response.json();

            if (data.success) {
                setSuccess('Image cropped and saved successfully!');
                setTimeout(() => {
                    // Clear form and redirect to show all items
                    setSelectedFile(null);
                    setPreviewUrl(null);
                    setIsCropping(false);
                    navigate('/all-items');
                }, 2000);
            } else {
                setError(data.message || 'Failed to crop image');
            }
        } catch (err) {
            console.error('Error cropping image:', err);
            setError('An error occurred while processing your image');
        } finally {
            setIsLoading(false);
        }
    };

    const handleCancel = () => {
        setSelectedFile(null);
        setPreviewUrl(null);
        setIsCropping(false);
        setError('');
        setSuccess('');
    };

    return (
        <div className="upload-container">
            <div className="sidebar">
                <div className="sidebar-logo">NOSTYLIST</div>
                <nav className="sidebar-menu">
                    <button onClick={() => navigate('/dashboard')}>Dashboard</button>
                    <button className="active">Upload Image</button>
                    <button onClick={() => navigate('/all-items')}>Show All Items</button>
                    <button>Previous Fits</button>
                    <button>Logout</button>
                </nav>
            </div>

            <div className="upload-content">
                <h1 className="upload-title">Upload Clothing Item</h1>

                {!isCropping ? (
                    <div className="upload-form">
                        <div className="upload-input">
                            <label htmlFor="file-upload" className="custom-file-upload">
                                Choose Image
                            </label>
                            <input
                                id="file-upload"
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                            />
                            {selectedFile && <span className="file-name">{selectedFile.name}</span>}
                        </div>

                        <div className="category-selector">
                            <label>Select Category:</label>
                            <div className="category-buttons">
                                {categories.map(cat => (
                                    <button
                                        key={cat}
                                        className={category === cat ? 'active-category' : ''}
                                        onClick={() => setCategory(cat)}
                                    >
                                        {cat}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="crop-container">
                        <div className="crop-tools">
                            <div className="zoom-control">
                                <label>Zoom:</label>
                                <input
                                    type="range"
                                    min="0.1"
                                    max="3"
                                    step="0.1"
                                    value={scale}
                                    onChange={handleZoomChange}
                                />
                            </div>

                            <div className="category-selector smaller">
                                <label>Category:</label>
                                <div className="category-buttons">
                                    {categories.map(cat => (
                                        <button
                                            key={cat}
                                            className={category === cat ? 'active-category' : ''}
                                            onClick={() => setCategory(cat)}
                                        >
                                            {cat}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div
                            className="canvas-container"
                            onMouseDown={startDrag}
                            onMouseMove={onDrag}
                            onMouseUp={endDrag}
                            onMouseLeave={endDrag}
                        >
                            <canvas
                                ref={canvasRef}
                                width={400}
                                height={400}
                                className="crop-canvas"
                            />

                            <div className="drag-instructions">
                                Drag to position • Zoom to resize • Outline shows crop area
                            </div>
                        </div>

                        <div className="crop-actions">
                            <button
                                className="cancel-button"
                                onClick={handleCancel}
                            >
                                Cancel
                            </button>
                            <button
                                className="crop-button"
                                onClick={handleCrop}
                                disabled={isLoading}
                            >
                                {isLoading ? 'Processing...' : 'Save Cropped Image'}
                            </button>
                        </div>
                    </div>
                )}

                {error && <div className="error-message">{error}</div>}
                {success && <div className="success-message">{success}</div>}
            </div>
        </div>
    );
};

export default UploadImage;