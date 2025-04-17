import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw
import tempfile

from flask import Flask, request, jsonify
from flask_cors import CORS

import images
import outfits
import users

import logging  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

app = Flask(__name__)
# Enable CORS with more specific configuration
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    result = users.authenticate_user(username, password)

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 401


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"success": False, "message": "All fields are required"}), 400

    result = users.create_user(username, email, password)

    if result["success"]:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    result = users.get_user_by_id(user_id)

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


# Discards outfit and deletes all images associated with the outfit
def delete_outfit(user_id, outfit_num):
    result = users.get_user_by_id(user_id)
    if not result["success"]:
        logger.error(f"User not found for ID: {user_id}")
        return {"success": False, "message": "User not found"}
        
    # Extract username from the user object in the result
    username = result["user"]["username"]
    logger.info(f"Deleting outfit {outfit_num} for user: {username}")
    result = outfits.discard_outfit(username, outfit_num)

    for j in range(0, 4):
        if j == 0:
            image_description = "hat"
            image_id = result["hat_id"]
        elif j == 1:
            image_description = "shirt"
            image_id = result["shirt_id"]
        elif j == 2:
            image_description = "pant"
            image_id = result["pant_id"]
        else:
            image_description = "shoe"
            image_id = result["shoe_id"]
        images.delete_image(username, image_description, image_id, outfit_num)


@app.route('/api/users/<user_id>/all-items', methods=['GET'])
def get_all_clothing_items(user_id):
    result = users.get_user_by_id(user_id)
    if not result["success"]:
        return jsonify({"success": False, "message": "User not found"}), 404

    # Extract username from the user object in the result
    username = result["user"]["username"]
    all_items = images.get_all_images(username)

    return jsonify({"success": True, "items": all_items}), 200


@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    try:
        # Get form data
        user_id = request.form.get('userId')
        category = request.form.get('category')
        image_file = request.files.get('image')

        if not user_id or not category or not image_file:
            return jsonify({"success": False, "message": "Missing required data"}), 400

        # Validate category
        valid_categories = ['hat', 'shirt', 'pant', 'shoe', 'jacket', 'shorts']

        # Map the category to what the database expects
        if category not in valid_categories:
            return jsonify({"success": False, "message": "Invalid category"}), 400

        # Map categories to our database format
        category_mapping = {
            'hat': 'hat',
            'shirt': 'shirt',
            'pant': 'pant',
            'jacket': 'jacket',  # Keep jacket as jacket
            'shorts': 'shorts',  # Map shorts to shorts
            'shoe': 'shoe'
        }

        db_category = category_mapping[category]

        # Get the username from the user_id
        user_result = users.get_user_by_id(user_id)
        if not user_result["success"]:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Extract username from the user object in user_result
        username = user_result["user"]["username"]
        logger.info(f"Found username: {username} for user ID: {user_id}")

        # Process the image with outline-based cropping
        # Save the uploaded image to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image_file.save(temp_file.name)
            temp_path = temp_file.name

        # Load the image and convert to RGBA
        try:
            img = Image.open(temp_path)
            # Ensure image is RGBA
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Load the appropriate outline image
            outline_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', f'{category}.png')

            # If outline exists, use it for masking
            if os.path.exists(outline_path):
                outline = Image.open(outline_path).convert('RGBA')

                # Create mask from outline
                mask = Image.new("L", outline.size, 0)

                # Process the outline to create a mask - keeping dark areas
                for y in range(outline.height):
                    for x in range(outline.width):
                        pixel = outline.getpixel((x, y))
                        # For all clothing types, keep the dark areas (the outline)
                        if pixel[3] > 128 and sum(pixel[:3]) / 3 < 128:
                            mask.putpixel((x, y), 255)  # White in mask = area to keep

                # Fill the inside of the outline using flood fill
                center_x, center_y = outline.width // 2, outline.height // 2
                flood_fill(mask, center_x, center_y)

                # Create a new blank image with transparency
                cropped = Image.new("RGBA", img.size, (0, 0, 0, 0))

                # Resize the mask to match the uploaded image
                mask_resized = mask.resize(img.size, Image.LANCZOS)

                # Apply the mask
                for y in range(img.height):
                    for x in range(img.width):
                        mask_pixel = mask_resized.getpixel((x, y))
                        if mask_pixel > 0:
                            cropped.putpixel((x, y), img.getpixel((x, y)))

                # Save the result to a BytesIO object
                output = BytesIO()
                cropped.save(output, format='PNG')
                output.seek(0)

                # Save image to the database
                binary_data = output.getvalue()
                logger.info(f"Attempting to save image with category: {category}, db_category: {db_category}")
                try:
                    image_id = images.save_image(username, db_category, binary_data)
                    logger.info(f"Successfully saved image with ID: {image_id}")
                except Exception as e:
                    logger.error(f"Error saving image to database: {str(e)}")
                    raise e  # Re-raise to be caught by outer exception handler

                # Clean up the temporary file
                os.unlink(temp_path)

                return jsonify({
                    "success": True,
                    "message": "Image uploaded and processed successfully"
                }), 200
            else:
                # If no outline exists, just use the original image
                output = BytesIO()
                img.save(output, format='PNG')
                output.seek(0)

                # Save image to the database
                binary_data = output.getvalue()
                images.save_image(username, db_category, binary_data)

                # Clean up the temporary file
                os.unlink(temp_path)

                return jsonify({
                    "success": True,
                    "message": "Image uploaded successfully (no outline applied)"
                }), 200

        except Exception as e:
            # Clean up in case of error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            return jsonify({"success": False, "message": f"Error processing image: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


# Helper function for flood fill algorithm (used in image processing)
# Add this to your app.py if it's not already there

def flood_fill(mask_img, x, y, target_value=0, replacement_value=255):
    """Simple flood fill algorithm to fill the inside of the outline"""
    if mask_img is None:
        return

    width, height = mask_img.size

    # If pixel is already the replacement value, return
    try:
        if mask_img.getpixel((x, y)) == replacement_value:
            return
    except Exception as e:
        print(f"Error checking pixel value: {str(e)}")
        return

    # Queue for flood fill
    queue = [(x, y)]
    visited = set()

    while queue:
        x, y = queue.pop(0)
        if (x, y) in visited:
            continue

        visited.add((x, y))

        # If pixel is the target value, replace it
        try:
            if mask_img.getpixel((x, y)) == target_value:
                mask_img.putpixel((x, y), replacement_value)

                # Add adjacent pixels to queue
                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                        queue.append((nx, ny))
        except Exception as e:
            # Skip problematic pixels
            print(f"Error in flood fill: {str(e)}")
            continue


# Add this to your app.py

# Add this to your app.py

@app.route('/api/crop-image', methods=['POST'])
def crop_image():
    logger.info("Crop image endpoint called")

    # Debug request info
    logger.info("Request content type: %s", request.content_type)
    logger.info("Request form keys: %s", list(request.form.keys()) if request.form else "None")
    logger.info("Request files keys: %s", list(request.files.keys()) if request.files else "None")

    try:
        # Get form data
        user_id = request.form.get('userId')
        category = request.form.get('category')
        image_file = request.files.get('image')
        
        logger.info(f"Received request with userId: {user_id}, category: {category}, image: {'Yes' if image_file else 'No'}")

        # Get scale and position data
        scale = float(request.form.get('scale', 1.0))
        offset_x = int(request.form.get('offsetX', 0))
        offset_y = int(request.form.get('offsetY', 0))
        
        logger.info(f"Scale: {scale}, offsets: ({offset_x}, {offset_y})")

        if not user_id or not category or not image_file:
            missing = []
            if not user_id: missing.append("userId")
            if not category: missing.append("category")
            if not image_file: missing.append("image")
            error_msg = f"Missing required data: {', '.join(missing)}"
            logger.error(error_msg)
            return jsonify({"success": False, "message": error_msg}), 400

        # Validate category
        valid_categories = ['hat', 'shirt', 'pant', 'shoe', 'jacket', 'shorts']

        # Map the category to what the database expects
        if category not in valid_categories:
            error_msg = f"Invalid category: {category}. Valid options are: {', '.join(valid_categories)}"
            logger.error(error_msg)
            return jsonify({"success": False, "message": error_msg}), 400

        # Map categories to our database format
        category_mapping = {
            'hat': 'hat',
            'shirt': 'shirt',
            'pant': 'pant',
            'jacket': 'jacket',  # Keep jacket as jacket
            'shorts': 'shorts',  # Map shorts to shorts
            'shoe': 'shoe'
        }

        db_category = category_mapping[category]

        # Get the username from the user_id
        user_result = users.get_user_by_id(user_id)
        if not user_result["success"]:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Extract username from the user object in user_result
        username = user_result["user"]["username"]
        logger.info(f"Found username: {username} for user ID: {user_id}")

        # Save the uploaded image to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            image_file.save(temp_file.name)
            temp_path = temp_file.name

        try:
            # SPECIAL CASE FOR SHORTS: Skip cropping and directly save the original image
            if category == 'shorts':
                logger.info("Processing shorts: bypassing cropping process")
                
                # Just load and convert the image to RGBA
                img = Image.open(temp_path)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Save image to memory
                output = BytesIO()
                img.save(output, format='PNG')
                output.seek(0)
                
                # Save to database
                binary_data = output.getvalue()
                logger.info(f"Saving shorts image directly without cropping")
                try:
                    image_id = images.save_image(username, db_category, binary_data)
                    logger.info(f"Successfully saved shorts with ID: {image_id}")
                except Exception as e:
                    logger.error(f"Error saving shorts to database: {str(e)}")
                    raise e
                
                # Clean up
                os.unlink(temp_path)
                
                # Return success
                response = jsonify({
                    "success": True,
                    "message": "Shorts image saved successfully (no cropping applied)",
                    "imageId": image_id
                })
                response.headers.add('Content-Type', 'application/json')
                return response, 200
            
            # For all other categories, continue with normal cropping process
            # Load the image and convert to RGBA
            img = Image.open(temp_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Resize the image based on scale
            if scale != 1.0:
                img = img.resize(
                    (int(img.width * scale), int(img.height * scale)),
                    Image.LANCZOS
                )

            # Create a blank canvas with a standard size
            canvas_width = 400
            canvas_height = 400
            composite = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

            # Calculate position to paste the image
            x = (canvas_width - img.width) // 2 + offset_x
            y = (canvas_height - img.height) // 2 + offset_y

            # Paste the image onto the canvas
            composite.paste(img, (x, y), img)

            # Get the appropriate outline file
            outline_filename = ''
            if category == 'hat':
                outline_filename = 'hatOutline.png'
            elif category == 'jacket':
                outline_filename = 'longOutline.png'
            elif category == 'pant':
                outline_filename = 'pantsOutline.png'
            elif category == 'shirt':
                outline_filename = 'shirtOutline.png'
            elif category == 'shoe':
                outline_filename = 'shoesOutline.png'
            elif category == 'shorts':
                outline_filename = 'shortsOutline.png'

            # Use the correct path to the public directory
            outline_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', outline_filename)

            if os.path.exists(outline_path):
                # Load the outline image
                outline = Image.open(outline_path).convert('RGBA')

                # Create mask from outline
                mask = Image.new("L", outline.size, 0)

                # Process the outline to create a mask (keep dark areas)
                for y in range(outline.height):
                    for x in range(outline.width):
                        pixel = outline.getpixel((x, y))
                        if pixel[3] > 128 and sum(pixel[:3]) / 3 < 128:
                            mask.putpixel((x, y), 255)  # White in mask = area to keep

                # Fill the inside of the outline using flood fill
                center_x, center_y = outline.width // 2, outline.height // 2
                flood_fill(mask, center_x, center_y)

                # Calculate scaling to fit within canvas
                max_width = canvas_width * 0.8
                max_height = canvas_height * 0.8

                # Calculate scale while maintaining aspect ratio
                scaling_factor = 1
                if outline.width > max_width or outline.height > max_height:
                    width_ratio = max_width / outline.width
                    height_ratio = max_height / outline.height
                    scaling_factor = min(width_ratio, height_ratio)

                # Resize the mask and place in the center of the canvas
                resized_mask = mask.resize(
                    (int(mask.width * scaling_factor), int(mask.height * scaling_factor)),
                    Image.LANCZOS
                )

                # Create a full-sized canvas mask
                canvas_mask = Image.new("L", (canvas_width, canvas_height), 0)
                offset_x = (canvas_width - resized_mask.width) // 2
                offset_y = (canvas_height - resized_mask.height) // 2
                canvas_mask.paste(resized_mask, (offset_x, offset_y))

                # Apply the mask to create the final cropped image
                cropped = Image.composite(composite, Image.new("RGBA", composite.size, (0, 0, 0, 0)), canvas_mask)
            else:
                # If no outline exists, use a basic shape as fallback
                canvas_mask = Image.new("L", (canvas_width, canvas_height), 0)
                draw = ImageDraw.Draw(canvas_mask)

                if category == 'hat':
                    draw.pieslice([125, 50, 275, 125], start=0, end=180, fill=255)
                elif category in ['pant', 'shorts']:
                    draw.rectangle([100, 200, 300, 375], fill=255)
                elif category in ['shirt', 'jacket']:
                    draw.ellipse([100, 100, 300, 250], fill=255)
                elif category == 'shoe':
                    draw.ellipse([125, 300, 275, 375], fill=255)

                # Apply the mask to create the final cropped image
                cropped = Image.composite(composite, Image.new("RGBA", composite.size, (0, 0, 0, 0)), canvas_mask)

            # Save the cropped image to memory
            output = BytesIO()
            cropped.save(output, format='PNG')
            output.seek(0)

            # Save image to the database
            binary_data = output.getvalue()
            logger.info(f"Attempting to save image with category: {category}, db_category: {db_category}")
            try:
                image_id = images.save_image(username, db_category, binary_data)
                logger.info(f"Successfully saved image with ID: {image_id}")
            except Exception as e:
                logger.error(f"Error saving image to database: {str(e)}")
                raise e  # Re-raise to be caught by outer exception handler

            # Clean up the temporary file
            os.unlink(temp_path)

            # Ensure proper JSON response with Content-Type header
            response = jsonify({
                "success": True,
                "message": "Image cropped and saved successfully",
                "imageId": image_id
            })
            response.headers.add('Content-Type', 'application/json')
            return response, 200

        except Exception as e:
            # Clean up in case of error
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            logger.error(f"Error processing image: {str(e)}")
            return jsonify({"success": False, "message": f"Error processing image: {str(e)}"}), 500

    except Exception as e:
        logger.error(f"Error in crop_image endpoint: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/test')
def test_api():
    return jsonify({'message': 'API is working!'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)