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


# Inserts a entry containing a username, outfit number (should be unique, 0 if not in an outfit),
# image_description (hat, shirt, etc) [NON plural], and image data into mongo
def save_image(username, image_description, binary_data, outfit_num=0):
    # So all entries are lower, need to have a correction in frontend if they misspell
    image_description = image_description.lower()

    # Find the number of clothing items the user has and update it in the user collection
    result = user_collection.find_one({"username": username})
    num = int(result["num_" + image_description + "s"])
    num += 1
    string_num = str(num)
    user_collection.update_one(
        {"username": username},
        {"$set": {"num_" + image_description + "s": string_num}}
    )

    # Insert the image data and metadata into the database
    document = {"username": username, "outfit_number": outfit_num, "image_description": image_description,
                "image_id": string_num, "image_data": binary_data}
    collection.insert_one(document)


# Only used to store the 4 stock images which will represent an "empty" clothing item a part of an outfit
def save_stock_image(username, image_description, binary_data):  # DO NOT USE
    image_description = image_description.lower()
    # The admin user will only have 1 clothing item for each category (all blank images) shown in the user counts
    user_collection.update_one(
        {"username": username},
        {"$set": {"num_" + image_description + "s": "1"}}
    )

    # Insert the image data and metadata into the database - the ID of a stock blank image is -1
    document = {"username": username, "outfit_number": "0", "image_description": image_description,
                "image_id": "-1", "image_data": binary_data}
    collection.insert_one(document)


# Returns the image data in a binary format, outfit_num is 0 if not attached to an outfit
# Needs image_id but other retrieval methods can be made since we need a carousel feature
def get_image(username, image_description, image_id, outfit_num=0):
    # Get the image in binary format from mongo and return it
    if image_id == "-1":
        result = collection.find_one(  # admin is the username that contains all stock images - can change to whatever
            {"username": "admin", "outfit_number": "0", "image_description": image_description,
             "image_id": image_id})
    else:
        result = collection.find_one(
            {"username": username, "outfit_number": outfit_num, "image_description": image_description,
             "image_id": image_id})
    binary_data = result["image_data"]
    return binary_data


# Delete an image, update all other image ids and number of images
def delete_image(username, image_description, image_id, outfit_num=0):
    # Delete image entry
    collection.delete_one({"username": username, "outfit_number": outfit_num, "image_description": image_description,
                           "image_id": image_id})

    # If the image is a part of an outfit, the outfit will display a blank stock image
    if outfit_num > 0:
        # Update outfit collection
        outfit_collection.update_one({"username": username, "outfit_number": outfit_num},
                                     {"$set": {image_description + "_id": "-1"}})
        # -1 will represent an id of blank stock clothing item image already stored in mongo

    # Get previous number of image_descriptions e.g. number of hats, shirts, etc
    num_image = int(get_num_image(username, image_description))

    # Update all other image ids create after deleted image
    for i in range(image_id + 1, num_image + 1):
        num = i - 1
        string_num = str(num)
        collection.update_one({"username": username, "image_description": image_description, "image_id": str(i)},
                              {"$set": {"image_id": string_num}})

    # Decrement total number of image_descriptions e.g. number of hats, shirts, etc. in user collection
    num_image -= 1
    string_num = str(num_image)
    user_collection.update_one({"username": username}, {"$set": {"num" + image_description + "s": string_num}})


# Selection for which type of image count to get
def get_num_image(username, image_description):
    if image_description == "hat":
        return get_num_hats(username)
    elif image_description == "shirt":
        return get_num_shirts(username)
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
        encoded = base64.b64encode(img["image_data"]).decode("utf-8")
        result.append({
            "image_id": img["image_id"],
            "description": img["image_description"],
            "outfit_number": img["outfit_number"],
            "base64": f"data:image/png;base64,{encoded}"
        })

    return result