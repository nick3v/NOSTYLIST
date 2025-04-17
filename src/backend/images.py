import mongo_connection
from bson import Binary
import os
import base64

# The collection name "images" will store all image data into the NOSTYLIST database
collection = mongo_connection.db["images"]

# The collection name "users" will store all user data from the login page into the NOSTYLIST database
user_collection = mongo_connection.db["users"]

# The collection name "outfits" will store all outfit data into the NOSTYLIST database
outfit_collection = mongo_connection.db["outfits"]


# Convert image in codespace folder to binary, delete image in folder, returns image in binary format
def image_to_binary():
    #  Image is always in codebase folder w/ name of "image.png"
    filename = "image.png"

    # Open image file in binary mode
    with open(filename, "rb") as image_file:
        binary_data = Binary(image_file.read())

    # file path of "image.png"
    file_path = os.path.join((os.getenv("HOME") or os.getenv("USERPROFILE")), "PycharmProjects", "NOSTYLIST", "src",
                             filename)

    # Check if the file exists before deleting
    if os.path.exists(file_path):
        os.remove(file_path)  # Delete the file
        print(f"{file_path} has been deleted.")
    else:
        print(f"{file_path} does not exist.")

    return binary_data


# Inserts a entry containing a username, outfit number (should be unique, [ ] if not in an outfit),
# image_description (hat, shirt, etc) [NON plural], and image data into mongo
def save_image(username, image_description, binary_data, outfit_num=[]):
    # So all entries are lower, need to have a correction in frontend if they misspell
    image_description = image_description.lower()
    
    print(f"Starting save_image for user: {username}, category: {image_description}")
    
    try:
        # Find the number of clothing items the user has and update it in the user collection
        result = user_collection.find_one({"username": username})
        if not result:
            print(f"ERROR: User {username} not found in database")
            raise Exception(f"User {username} not found")
            
        # Fix for shorts category - use the correct field name
        if image_description == "shorts":
            field_name = "num_shorts"
        else:
            field_name = "num_" + image_description + "s"
            
        print(f"Looking for field: {field_name} in user document")
        
        if field_name not in result:
            print(f"ERROR: Field {field_name} not found in user document")
            print(f"Available fields: {list(result.keys())}")
            raise Exception(f"Field {field_name} not found in user document")
            
        num = int(result[field_name])
        num += 1
        string_num = str(num)
        print(f"Incrementing {field_name} from {result[field_name]} to {string_num}")
        
        user_collection.update_one(
            {"username": username},
            {"$set": {field_name: string_num}}
        )

        # Insert the image data and metadata into the database
        document = {"username": username, "outfit_numbers": outfit_num, "image_description": image_description,
                    "image_id": string_num, "image_data": binary_data}
        collection.insert_one(document)
        print(f"Successfully saved {image_description} with ID: {string_num}")
        
        return string_num
    except Exception as e:
        print(f"ERROR in save_image: {str(e)}")
        raise


# Example code using image_to_binary() and save_image(username, image_description, image_id, outfit_num=[]):
# binary_data = image_to_binary()
# save_image("Jordan_Carter29", hat, binary_data): - if no outfit_num list is passed it's not a part of outfit

# Only used to store the 4 stock images which will represent an "empty" clothing item a part of an outfit
def save_stock_image(username, image_description, binary_data):  # DO NOT USE
    image_description = image_description.lower()
    # The admin (alexjvd) user will only have 1 clothing item for each category (all placeholder images)
    # shown in the user counts
    user_collection.update_one(
        {"username": username},
        {"$set": {"num_" + image_description + "s": "1"}}
    )

    # Insert the image data and metadata into the database - the ID of a stock blank image is -1
    document = {"username": username, "outfit_numbers": [], "image_description": image_description,
                "image_id": "-1", "image_data": binary_data}
    collection.insert_one(document)


# Returns the image data in a binary format, outfit_num is [] if not attached to an outfit
# Needs image_id (str) but other retrieval methods can be made since we need a carousel feature
def get_image(username, image_description, image_id, outfit_num=[]):
    # Get the image in binary format from mongo and return it
    if image_id == "-1":
        result = collection.find_one(
            # admin (alexjvd) is the username that contains all stock images - can change to whatever
            {"username": "alexjvd", "outfit_numbers": [], "image_description": image_description,
             "image_id": image_id})
    else:
        result = collection.find_one(
            {"username": username, "outfit_numbers": outfit_num, "image_description": image_description,
             "image_id": image_id})
    binary_data = result["image_data"]
    return binary_data


# Example code using get_image(username, image_description, image_id, outfit_num=[]):
#   binary_data = get_image("KenyattaCarson", "hat", "1") - if no outfit_num list is passed it's not a part of outfit
#   file_path = "image.png"
#   with open(file_path, "wb") as file:
#       file.write(binary_data)

# Image id (string)
# Delete an image, update all other image ids and number of images
def delete_image(username, image_description, image_id, outfit_num=[]):
    # Delete image entry
    collection.delete_one({"username": username, "image_description": image_description, "image_id": image_id})

    # If the image is a part of an outfit, the outfit will display a blank stock image
    if len(outfit_num) > 0:
        for i in range(len(outfit_num)):
            # Update outfit collection
            outfit_collection.update_one({"username": username, "outfit_number": outfit_num[i]},
                                         {"$set": {image_description + "_id": "-1"}})
            # -1 will represent an id of blank stock clothing item image already stored in mongo

    # Get previous number of image_descriptions e.g. number of hats, shirts, etc
    num_image = int(get_num_image(username, image_description))

    # Update all other image ids create after deleted image
    for i in range(int(image_id) + 1, num_image + 1):
        num = i - 1
        string_num = str(num)
        collection.update_one({"username": username, "image_description": image_description, "image_id": str(i)},
                              {"$set": {"image_id": string_num}})

    # Decrement total number of image_descriptions e.g. number of hats, shirts, etc. in user collection
    num_image -= 1
    string_num = str(num_image)
    user_collection.update_one({"username": username}, {"$set": {"num_" + image_description + "s": string_num}})


# Example code using delete_image(username, image_description, image_id, outfit_num=[]):
# delete_image("BobbySandimandie","hat", "1") - if no outfit_num list is passed it's not a part of outfit


# Selection for which type of image count to get
def get_num_image(username, image_description):
    if image_description == "hat":
        return get_num_hats(username)
    elif image_description == "shirt":
        return get_num_shirts(username)
    elif image_description == "jacket":
        return get_num_jackets(username)
    elif image_description == "shorts":
        return get_num_shorts(username)
    elif image_description == "pant":
        return get_num_pants(username)
    else:
        return get_num_shoes(username)


# Return number of hats user has (string)
def get_num_hats(username):
    result = user_collection.find_one({"username": username})
    num = result["num_hats"]
    return num


# Return number of shirts user has (string)
def get_num_shirts(username):
    result = user_collection.find_one({"username": username})
    num = result["num_shirts"]
    return num


# Return number of jackets / long sleeves / hoodies user has (string)
def get_num_jackets(username):
    result = user_collection.find_one({"username": username})
    num = result["num_jackets"]
    return num


# Return number of shorts user has (string)
def get_num_shorts(username):
    result = user_collection.find_one({"username": username})
    num = result["num_shorts"]
    return num


# Return number of pants user has (string)
def get_num_pants(username):
    result = user_collection.find_one({"username": username})
    num = result["num_pants"]
    return num


# Return number of shoes user has (string)
def get_num_shoes(username):
    result = user_collection.find_one({"username": username})
    num = result["num_shoes"]
    return num

# for show all items - marco
def get_all_images(username):
    # Find all images not part of stock (-1) and not attached to outfits (outfit_number = "0")
    user_images = collection.find({
        "username": username,
        "image_id": {"$ne": "-1"}
    })

    result = []
    for img in user_images:
        # Check if image_data exists
        if "image_data" in img:
            try:
                encoded = base64.b64encode(img["image_data"]).decode("utf-8")
                result.append({
                    "id": img["image_id"],
                    "category": img["image_description"],
                    "outfit_numbers": img.get("outfit_numbers", []),
                    "base64": f"data:image/png;base64,{encoded}"
                })
            except Exception as e:
                print(f"Error processing image: {e}")
        else:
            print(f"Image data not found for record: {img.get('image_id', 'unknown')}")

    return result