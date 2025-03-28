import mongo_connection

# The collection name "outfits" will store all outfit data into the NOSTYLIST database
collection = mongo_connection.db["outfits"]

# The collection name "users" will store all user data from the login page into the NOSTYLIST database
user_collection = mongo_connection.db["users"]

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
# Deletes an outfit based on username and outfit number
def delete_outfit(username, outfit_num): ## DO NOT USE YET
    # Need to change all user info and image info after delete
    result = collection.delete_one({"username": username, "outfit_number": outfit_num})

# Return number of outfits user has (string)
def get_num_outfits(username):
    result = user_collection.find_one({"username": username})
    num = result["num_outfits"]
    return num


