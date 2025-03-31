import mongo_connection

# The collection name "outfits" will store all outfit data into the NOSTYLIST database
collection = mongo_connection.db["outfits"]

# The collection name "users" will store all user data from the login page into the NOSTYLIST database
user_collection = mongo_connection.db["users"]

# The collection name "images" will store all image data into the NOSTYLIST database
image_collection = mongo_connection.db["images"]


# The first outfit number is #1, if an image has an outfit #0 then it does not belong to an outfit
# Same for all clothing / image ids

# outfit is a list of strings which contain all the image ids in this order:
# Hat, Shirt, Pants, Shoes -- We can add more if needed
def create_outfit(username, outfit):
    # Find the number of outfits the user has and update it in the user collection
    result = user_collection.find_one({"username": username})
    num = int(result["num_outfits"])
    num += 1
    string_num = str(num)
    user_collection.update_one(
        {"username": username},
        {"$set": {"num_outfits": string_num}}
    )

    # Insert the outfit metadata into the database
    document = {"username": username, "outfit_number": string_num, "hat_id": outfit[0], "shirt_id": outfit[1],
                "pant_id": outfit[2], "shoe_id": outfit[3]}
    collection.insert_one(document)


# Returns list of image descriptions and their respective image ids Ex: Hat, 1, Shirt, 2 etc.
# Needs outfit_num but other retrieval methods can be made since we need a carousel feature
def get_outfit(username, outfit_num):
    result = collection.find_one({"username": username, "outfit_number": outfit_num})
    outfit = ["hat"]
    outfit.append(result["hat_id"]), outfit.append("shirt"), outfit.append(result["shirt_id"]), outfit.append("pant")
    outfit.append(result["pant_id"]), outfit.append("shoe"), outfit.append(result["shoe_id"])
    return outfit


# Updates all other outfit ids and clothing counts
# Discards an outfit based on username and outfit number (all images are still saved in db but are now unlinked and have
# an outfit number of 0
# Returns all image ids (and previous outfit ID) so that if they want to delete the images they can
def discard_outfit(username, outfit_num):
    # Get all image and outfit ids
    result = collection.find_one({"username": username, "outfit_number": outfit_num})

    # Update deleted outfit numbers in image collection
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
        image_collection.update_one({"username": username, "image_description": image_description,
                                     "image_id": image_id}, {"$set": {"outfit_number": "0"}})

    # Delete outfit entry
    collection.delete_one({"username": username, "outfit_number": outfit_num})

    # Get number of outfits
    num_outfits = int(get_num_outfits(username))

    # Update all other outfit Ids created after
    for i in range(outfit_num + 1, num_outfits + 1):
        string_num2 = str(i)
        result2 = collection.find_one({"username": username, "outfit_number": string_num2})
        num = i-1
        string_num = str(num)
        collection.update_one({"username": username, "outfit_number": string_num2},
                              {"$set": {"outfit_number": string_num}})

        # Decrement outfit numbers in image collection
        for j in range(0, 4):
            if j == 0:
                image_description = "hat"
                image_id = result2["hat_id"]
            elif j == 1:
                image_description = "shirt"
                image_id = result2["shirt_id"]
            elif j == 2:
                image_description = "pant"
                image_id = result2["pant_id"]
            else:
                image_description = "shoe"
                image_id = result2["shoe_id"]
            image_collection.update_one({"username": username, "outfit_number": string_num2,
                                         "image_description": image_description,"image_id": image_id},
                                        {"$set": {"outfit_number": string_num}})

    # Decrement number of outfits in user collection
    num_outfits -= 1
    string_num = str(num_outfits)
    user_collection.update_one({"username": username}, {"$set": {"num_outfits": string_num}})

    return result


# Return number of outfits user has (string)
def get_num_outfits(username):
    result = user_collection.find_one({"username": username})
    num = result["num_outfits"]
    return num
