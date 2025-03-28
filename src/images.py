import mongo_connection
from bson import Binary
import os

# The collection name "images" will store all image data into the NOSTYLIST database
collection = mongo_connection.db["images"]

# The collection name "users" will store all user data from the login page into the NOSTYLIST database
user_collection = mongo_connection.db["users"]

# Convert image in codespace folder to binary, delete image in folder, returns image in binary format
def image_to_binary():
    #  Image is always in codebase folder w/ name of "image.png"
    filename = "image.png"

    # Open image file in binary mode
    with open(filename, "rb") as image_file:
        binary_data = Binary(image_file.read())

    # file path of "image.png"
    file_path = os.path.join(os.getenv("HOME"), filename)

    # Check if the file exists before deleting
    if os.path.exists(file_path):
        os.remove(file_path)  # Delete the file
        print(f"{file_path} has been deleted.")
    else:
        print(f"{file_path} does not exist.")

    return binary_data


# Inserts a entry containing a username, outfit number (should be unique, 0 if not in an outfit),
# image_description (hat, shirt, etc) [NON plural], and image data into mongo
def save_image(username, image_description, binary_data, outfit_num=0):
    # So all entries are lower, need to have a correction in frontend if they misspell
    image_description = image_description.lower()

    # Find the number of clothing items the user has and update it in the user collection
    result = user_collection.find_one({"username": username})
    num = int(result["num_"+image_description+"s"])
    num += 1
    string_num = str(num)
    user_collection.update_one(
        {"username": username},
        {"$set": {"num_"+image_description+"s": string_num}}
    )

    # Insert the image data and metadata into the database
    document = {"username": username, "outfit_number": outfit_num, "image_description": image_description,
                "image_id": string_num, "image_data": binary_data}
    collection.insert_one(document)

# Returns the image data in a binary format, outfit_num is 0 if not attached to an outfit
# Needs image_id but other retrieval methods can be made since we need a carousel feature
def get_image(username, image_description, image_id, outfit_num=0):
    # Get the image in binary format from mongo and return it
    result = collection.find_one(
        {"username": username, "outfit_number": outfit_num, "image_description": image_description, "image_id": image_id})
    binary_data = result["image_data"]
    return binary_data

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
