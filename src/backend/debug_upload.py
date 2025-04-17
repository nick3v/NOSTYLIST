import logging
import os
import tempfile
from io import BytesIO
from PIL import Image
import base64

import mongo_connection
import images
import users

# Configure detailed logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connections
db = mongo_connection.db
user_collection = db["users"]
image_collection = db["images"]

def test_shorts_upload(username, test_image_path):
    """
    Test uploading a shorts image for the specified user
    
    Args:
        username: The username to test with
        test_image_path: Path to a test image file
    """
    logger.info(f"Testing shorts upload for user: {username}")
    
    # Verify user exists
    user = user_collection.find_one({"username": username})
    if not user:
        logger.error(f"User {username} not found")
        return False
    
    logger.info(f"User found with fields: {list(user.keys())}")
    logger.info(f"Current num_shorts value: {user.get('num_shorts', 'NOT FOUND')}")
    
    # Load the test image
    try:
        logger.info(f"Loading test image from: {test_image_path}")
        with open(test_image_path, "rb") as f:
            image_data = f.read()
        
        # Convert to PIL Image for verification
        img = Image.open(BytesIO(image_data))
        logger.info(f"Image loaded successfully: {img.format}, {img.size}, {img.mode}")
        
        # Convert back to binary for storage
        output = BytesIO()
        img.save(output, format='PNG')
        binary_data = output.getvalue()
        
        # Directly test the save_image function
        logger.info("Attempting to save shorts image directly...")
        try:
            image_id = images.save_image(username, "shorts", binary_data)
            logger.info(f"Successfully saved shorts with ID: {image_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving shorts image: {str(e)}")
            
            # Check if the field exists exactly as expected
            if "Field num_shorts not found in user document" in str(e):
                logger.error(f"Field verification failed. Available fields: {list(user.keys())}")
                
                # Try to fix the field
                logger.info("Attempting to fix user document...")
                user_collection.update_one(
                    {"username": username},
                    {"$set": {"num_shorts": "0"}}
                )
                logger.info("User document updated with num_shorts field")
                
                # Try again
                try:
                    image_id = images.save_image(username, "shorts", binary_data)
                    logger.info(f"Second attempt successful! Saved shorts with ID: {image_id}")
                    return True
                except Exception as e2:
                    logger.error(f"Second attempt also failed: {str(e2)}")
            
            # If we get here, both attempts failed
            return False
            
    except Exception as e:
        logger.error(f"Error processing test image: {str(e)}")
        return False

def find_test_image():
    """Find an appropriate test image in the project"""
    # Look in common image directories
    search_paths = [
        "./public",
        "./src/frontend/assets",
        "./src/assets",
        "./assets",
        "."
    ]
    
    for path in search_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                # Look for any image file
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    return os.path.join(path, file)
    
    return None

if __name__ == "__main__":
    logger.info("Starting shorts upload test")
    
    # Find a test user
    users_list = list(user_collection.find({}, {"username": 1}))
    if not users_list:
        logger.error("No users found in database")
    else:
        # Use the first user we find
        test_user = users_list[0]["username"]
        logger.info(f"Using test user: {test_user}")
        
        # Find a test image
        test_image = find_test_image()
        if not test_image:
            logger.error("No test image found")
        else:
            logger.info(f"Found test image: {test_image}")
            result = test_shorts_upload(test_user, test_image)
            
            if result:
                logger.info("Test SUCCESSFUL")
            else:
                logger.error("Test FAILED") 