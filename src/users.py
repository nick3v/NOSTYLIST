import mongo_connection

# The collection name "users" will store all user data from the login page into the NOSTYLIST database
collection = mongo_connection.db["users"]

# Insert data as a dictionary (map) into Mongo:

# user1 = {
#    "username": "JordanCarter29",
#    "email": "playboicarti@spotify.com"
#    "password": "I_AM_NOT_DROPPING"
# }

# Make sure that the internal data (username, password, etc.) cannot be changed or accessed (needs to be secure)

# Insert the data into the users collection

# inserted_id = collection.insert_one(user1).inserted_id
