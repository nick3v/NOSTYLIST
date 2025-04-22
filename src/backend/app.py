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
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS", "DELETE"], "allow_headers": ["Content-Type", "Authorization"]}})


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
            outline_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   "public", f'{category}.png')

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
            outline_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   "public", outline_filename)

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

                if category == 'pant':
                    # Fill from corners (outside area)
                    flood_fill(mask, 0, 0)
                    flood_fill(mask, outline.width - 1, 0)
                    flood_fill(mask, 0, outline.height - 1)
                    flood_fill(mask, outline.width - 1, outline.height - 1)

                    # Invert the mask
                    for y in range(mask.height):
                        for x in range(mask.width):
                            mask.putpixel((x, y), 255 - mask.getpixel((x, y)))

                    # Make pants 50% larger
                    larger_mask = Image.new("L", mask.size, 0)
                    scale_factor = 1.5  # 1/1.5 to make result 50% larger
                    smaller_width = int(mask.width * scale_factor)
                    smaller_height = int(mask.height * scale_factor)
                    smaller_mask = mask.resize((smaller_width, smaller_height), Image.LANCZOS)
                    offset_x = (mask.width - smaller_width) // 2
                    offset_y = (mask.height - smaller_height) // 2
                    larger_mask.paste(smaller_mask, (offset_x, offset_y))
                    mask = larger_mask
                elif category == 'jacket':
                    # Do the regular center flood fill first
                    center_x, center_y = outline.width // 2, outline.height // 2
                    flood_fill(mask, center_x, center_y)

                    # Add additional flood fill points inside each sleeve
                    # Left sleeve (approximate coordinates)
                    left_sleeve_x = outline.width * 0.2
                    left_sleeve_y = outline.height * 0.4
                    flood_fill(mask, int(left_sleeve_x), int(left_sleeve_y))

                    # Right sleeve (approximate coordinates)
                    right_sleeve_x = outline.width * 0.8
                    right_sleeve_y = outline.height * 0.4
                    flood_fill(mask, int(right_sleeve_x), int(right_sleeve_y))
                else:
                    # For all other items, use center fill as before
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


@app.route('/api/users/<user_id>/items/<path:item_id>', methods=['DELETE'])
def delete_image(user_id, item_id):
    print(f"Deleting image with item_id: {item_id}")
    try:
        # Get the username from the user ID
        user_result = users.get_user_by_id(user_id)
        if not user_result["success"]:
            return jsonify({"error": "User not found"}), 404

        username = user_result["user"]["username"]

        # Extract category and image_id from the item_id
        parts = item_id.split('/')
        if len(parts) != 2:
            return jsonify({"error": "Invalid item ID format"}), 400
            
        category = parts[0]
        image_id = parts[1]

        # Find the specific image
        image_doc = images.collection.find_one({
            "username": username, 
            "image_description": category, 
            "image_id": image_id
        })

        if not image_doc:
            return jsonify({"error": "Image not found"}), 404

        outfit_num = image_doc["outfit_numbers"]

        # Delete the image
        delete_result = images.delete_image(username, category, image_id, outfit_num)

        if not delete_result:
            return jsonify({"error": "Failed to delete image"}), 500

        return jsonify({"success": True, "message": "Image deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Error deleting image: {str(e)}"}), 500



@app.route('/api/test')
def test_api():
    return jsonify({"message": "API is working!", "status": "success"}), 200


@app.route('/api/save-outfit', methods=['POST'])
def save_outfit():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        outfit_items = data.get('outfitItems')

        if not user_id or not outfit_items or len(outfit_items) != 6:
            return jsonify({
                "success": False,
                "message": "Invalid request. User ID and 6 outfit items are required."
            }), 400

        # Get the username from the user_id
        user_result = users.get_user_by_id(user_id)
        if not user_result["success"]:
            return jsonify({"success": False, "message": "User not found"}), 404

        username = user_result["user"]["username"]

        # Extract image IDs from the outfit items
        # The outfit array should contain items in this order: hat, shirt, jacket, shorts, pants, shoes
        outfit_ids = []
        for item in outfit_items:
            # If the item is null/empty, use -1 (placeholder for empty item)
            if not item or "id" not in item:
                outfit_ids.append("-1")
            else:
                # Extract the numeric ID from the item
                item_id = item.get("id", "-1").split("-")[-1]
                # If it's not a valid ID, use -1
                outfit_ids.append(item_id if item_id.isdigit() else "-1")

        # Create the outfit in the database
        outfits.create_outfit(username, outfit_ids)

        return jsonify({
            "success": True,
            "message": "Outfit saved successfully!"
        }), 200

    except Exception as e:
        logger.error(f"Error saving outfit: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error saving outfit: {str(e)}"
        }), 500


@app.route('/api/users/<user_id>/outfits', methods=['GET'])
def get_user_outfits(user_id):
    try:
        # Get the username from the user_id
        user_result = users.get_user_by_id(user_id)
        if not user_result["success"]:
            return jsonify({"success": False, "message": "User not found"}), 404

        username = user_result["user"]["username"]

        # Use the collections from imported modules rather than direct mongo_connection
        # Get all outfits for the user from MongoDB
        user_outfits = []
        outfit_docs = outfits.collection.find({"username": username})

        for outfit in outfit_docs:
            outfit_data = {
                "outfitNumber": outfit["outfit_number"],
                "items": []
            }

            # Get each item in the outfit
            item_types = [
                {"type": "hat", "id": outfit["hat_id"]},
                {"type": "shirt", "id": outfit["shirt_id"]},
                {"type": "jacket", "id": outfit["jacket_id"]},
                {"type": "short", "id": outfit["short_id"]},
                {"type": "pant", "id": outfit["pant_id"]},
                {"type": "shoe", "id": outfit["shoe_id"]}
            ]

            # Fetch the actual image data for each item
            for item in item_types:
                # Skip placeholder items
                if item["id"] == "-1":
                    outfit_data["items"].append({
                        "type": item["type"],
                        "id": "-1",
                        "base64": None
                    })
                    continue

                if item["type"] == "short":
                    image_doc = images.collection.find_one({
                        "username": username,
                        "image_description": "shorts",
                        "image_id": item["id"]
                    })
                else:
                    image_doc = images.collection.find_one({
                        "username": username,
                        "image_description": item["type"],
                        "image_id": item["id"]
                    })

                if image_doc:
                    import base64
                    # Convert binary image data to base64 string
                    base64_data = base64.b64encode(image_doc["image_data"]).decode('utf-8')
                    img_src = f"data:image/png;base64,{base64_data}"

                    outfit_data["items"].append({
                        "type": item["type"],
                        "id": item["id"],
                        "base64": img_src
                    })
                else:
                    # Item not found, use placeholder
                    outfit_data["items"].append({
                        "type": item["type"],
                        "id": "-1",
                        "base64": None
                    })

            user_outfits.append(outfit_data)

        # Sort outfits by outfit number (newest first)
        user_outfits.sort(key=lambda x: int(x["outfitNumber"]), reverse=True)

        return jsonify({
            "success": True,
            "outfits": user_outfits
        }), 200

    except Exception as e:
        logger.error(f"Error getting user outfits: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error getting outfits: {str(e)}"
        }), 500
    return jsonify({'message': 'API is working!'})


@app.route('/api/users/<user_id>/outfits/<outfit_num>', methods=['DELETE'])
def delete_user_outfit(user_id, outfit_num):
    try:
        # Get the username from the user_id
        user_result = users.get_user_by_id(user_id)
        if not user_result["success"]:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Extract username from the user object in the result
        username = user_result["user"]["username"]
        
        # Check if the outfit exists first
        outfit_exists = outfits.collection.find_one({"username": username, "outfit_number": outfit_num})
        if not outfit_exists:
            return jsonify({"success": False, "message": "Outfit not found"}), 404
        
        try:
            # Delete the outfit but keep the items
            result = outfits.discard_outfit(username, outfit_num)
            
            return jsonify({
                "success": True,
                "message": "Outfit deleted successfully"
            }), 200
        except Exception as e:
            logger.error(f"Error in discard_outfit function: {str(e)}")
            # Alternative approach: manually delete the outfit record if the discard_outfit function fails
            try:
                outfits.collection.delete_one({"username": username, "outfit_number": outfit_num})
                return jsonify({
                    "success": True,
                    "message": "Outfit deleted (simple method)"
                }), 200
            except Exception as inner_e:
                logger.error(f"Error in fallback delete: {str(inner_e)}")
                return jsonify({"success": False, "message": f"Failed to delete outfit: {str(inner_e)}"}), 500
        
    except Exception as e:
        logger.error(f"Error deleting outfit: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Error deleting outfit: {str(e)}"
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)