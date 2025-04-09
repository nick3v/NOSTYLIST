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
    document = {"username": username, "outfit_number": string_num, "hat_id": str(outfit[0]), "shirt_id": str(outfit[1]),
                "pant_id": str(outfit[2]), "shoe_id": str(outfit[3])}
    collection.insert_one(document)

    # Update image collection respective outfit_numbers
    for j in range(0, 4):
        if j == 0:
            image_description = "hat"
            image_id = str(outfit[0])
        elif j == 1:
            image_description = "shirt"
            image_id = str(outfit[1])
        elif j == 2:
            image_description = "pant"
            image_id = str(outfit[2])
        else:
            image_description = "shoe"
            image_id = str(outfit[3])
        result3 = image_collection.find_one({"username": username, "image_description": image_description,
                                             "image_id": image_id})
        outfit_nums = result3["outfit_numbers"]
        outfit_nums.append(string_num)
        image_collection.update_one({"username": username, "image_description": image_description, "image_id": image_id}
                                    , {"$set": {"outfit_numbers": outfit_nums}})


# Example code using create_outfit():
# create_outfit("CartiManIanGoLie", [29 29 29 29])


# Returns list of image Ids in this order: hat, shirt, pant, shoe as strings
# Needs outfit_num (str) but other retrieval methods can be made since we need a carousel feature
def get_outfit(username, outfit_num):
    result = collection.find_one({"username": username, "outfit_number": outfit_num})
    outfit = []
    outfit.append(str(result["hat_id"])), outfit.append(str(result["shirt_id"])), outfit.append(str(result["pant_id"]))
    outfit.append(str(result["shoe_id"]))
    return outfit


# Example code using get_outfit():
# outfit = get_outfit("Kenyatta", "29") - returns all image ids of outfit from top to bottom


# Updates all other outfit ids (str) and clothing counts
# Discards an outfit based on username and outfit number (str) (all images are still saved in db but are now unlinked
# and have an outfit number of 0
# Returns all image ids so that if they want to delete the images they can
def discard_outfit(username, outfit_num):
    # Get all image and outfit ids
    result = collection.find_one({"username": username, "outfit_number": outfit_num})

    # Update deleted outfit numbers in image collection
    for j in range(0, 4):
        if j == 0:
            image_description = "hat"
            image_id = str(result["hat_id"])
        elif j == 1:
            image_description = "shirt"
            image_id = str(result["shirt_id"])
        elif j == 2:
            image_description = "pant"
            image_id = str(result["pant_id"])
        else:
            image_description = "shoe"
            image_id = str(result["shoe_id"])
        result3 = image_collection.find_one({"username": username, "image_description": image_description,
                                             "image_id": image_id})
        outfit_nums = result3["outfit_numbers"]
        outfit_nums.remove(outfit_num)  # Take out the discarded outfit number
        image_collection.update_one({"username": username, "image_description": image_description,
                                     "image_id": image_id}, {"$set": {"outfit_numbers": outfit_nums}})

    # Delete outfit entry
    collection.delete_one({"username": username, "outfit_number": outfit_num})

    # Get number of outfits
    num_outfits = int(get_num_outfits(username))

    # Update all other outfit Ids created after
    for i in range(int(outfit_num) + 1, num_outfits + 1):
        string_num2 = str(i)
        result2 = collection.find_one({"username": username, "outfit_number": string_num2})
        num = i - 1
        string_num = str(num)
        collection.update_one({"username": username, "outfit_number": string_num2},
                              {"$set": {"outfit_number": string_num}})

        # Decrement outfit numbers in image collection
        for j in range(0, 4):
            if j == 0:
                image_description = "hat"
                image_id = str(result2["hat_id"])
            elif j == 1:
                image_description = "shirt"
                image_id = str(result2["shirt_id"])
            elif j == 2:
                image_description = "pant"
                image_id = str(result2["pant_id"])
            else:
                image_description = "shoe"
                image_id = str(result2["shoe_id"])
            result3 = image_collection.find_one({"username": username, "image_description": image_description,
                                                 "image_id": image_id})
            outfit_nums = result3["outfit_numbers"]
            index = outfit_nums.index(string_num2)
            outfit_nums[index] = string_num
            image_collection.update_one({"username": username, "image_description": image_description,
                                         "image_id": image_id}, {"$set": {"outfit_numbers": outfit_nums}})

    # Decrement number of outfits in user collection
    num_outfits -= 1
    string_num = str(num_outfits)
    user_collection.update_one({"username": username}, {"$set": {"num_outfits": string_num}})

    # Return the list of all image ids so that deleting images is possible if needed
    outfit_list = []
    outfit_list.append(str(result["hat_id"])), outfit_list.append(str(result["shirt_id"])), \
        outfit_list.append(str(result["pant_id"])), outfit_list.append(str(result["shoe_id"]))
    return outfit_list

# Example code using discard_outfit()
# outfit_list = discard_outfit("IfLooksCouldKill", "29")


# Return number of outfits user has (string)
def get_num_outfits(username):
    result = user_collection.find_one({"username": username})
    num = result["num_outfits"]
    return num
