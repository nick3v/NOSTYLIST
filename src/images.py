import mongo_connection
from bson import Binary
import os

# The collection name "images" will store all user data from the login page into the NOSTYLIST database
collection = mongo_connection.db["images"]

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


# Inserts a entry containing a username, image_description (hat, shirt, etc), and image data into mongo
def save_image(username, image_description, binary_data):
    # So all entries are lower, need to have a correction in frontend if they misspell
    image_description = image_description.lower()

    # Insert the binary data into a document
    document = {"username": username, "image_description": image_description, "image_data": binary_data}
    collection.insert_one(document)

# Returns the image data in a binary format
def get_image(username, image_description):
    # Get the image in binary format from mongo and return it
    result = collection.find_one({"username": username, "image_description": image_description})
    binary_data = result["image_data"]
    return binary_data

