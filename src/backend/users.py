import datetime
import mongo_connection
from passlib.hash import pbkdf2_sha256
from bson.objectid import ObjectId

# The collection name "users" will store all user data from the login page into the NOSTYLIST database
collection = mongo_connection.db["users"]

def create_user(username, email, password):
    """
    Create a new user in the database
    
    Args:
        username (str): User's username
        email (str): User's email address
        password (str): User's password (will be hashed)
        
    Returns:
        dict: Result containing success status and message/user_id
    """
    # Validate input data
    if not username or not email or not password:
        return {"success": False, "message": "All fields are required"}
    
    # Check if username or email already exists
    if collection.find_one({"$or": [{"username": username}, {"email": email}]}):
        return {"success": False, "message": "Username or email already exists"}
    
    # Hash the password for security
    hashed_password = pbkdf2_sha256.hash(password)
    
    # Create user document
    new_user = {
        "username": username,
        "email": email,
        "password": hashed_password,
        "created_at": datetime.datetime.utcnow(),
        "num_outfits": "0",
        "num_hats": "0",
        "num_shirts": "0",
        "num_pants": "0",
        "num_shoes": "0" # need to come back here if we add more accessories
    }
    
    try:
        # Insert user into database
        result = collection.insert_one(new_user)
        return {
            "success": True, 
            "user_id": str(result.inserted_id),
            "message": "User created successfully"
        }
    except Exception as e:
        return {"success": False, "message": f"Error creating user: {str(e)}"}

# Insert data as a dictionary (map) into Mongo:

# user1 = {
#    "username": "JordanCarter29",
#    "email": "playboicarti@spotify.com"
#    "password": "I_AM_NOT_DROPPING"
# }

# Make sure that the internal data (username, password, etc.) cannot be changed or accessed (needs to be secure)

# Insert the data into the users collection and obtain an inserted ID

# inserted_id = collection.insert_one(user1).inserted_id

def authenticate_user(username, password):
    """
    Authenticate a user based on username and password. This function verifies if the provided
    username exists in the database and if the password matches the stored hashed password.
    
    It returns a user ID on successful authentication to allow the application to identify 
    the specific user for subsequent operations like session management.
    
    Args:
        username (str): User's username
        password (str): User's password to verify
        
    Returns:
        dict: Result containing:
            - success (bool): Whether authentication was successful
            - user_id (str): MongoDB document ID of the authenticated user (on success)
            - message (str): Error message (on failure)
    """
    # Example usage:
    # result = authenticate_user("JordanCarter29", "I_AM_NOT_DROPPING")
    
    # print(result)
    # Validate input data
    if not username or not password:
        return {"success": False, "message": "Username and password are required"}
    
    # Find user by username
    user = collection.find_one({"username": username})
    
    # Check if user exists and password is correct using secure hash verification
    if user and pbkdf2_sha256.verify(password, user["password"]):
        # Return the MongoDB document ID to identify this specific user
        # This ID can be used to look up user data or manage sessions
        return {"success": True, "user_id": str(user["_id"])}
    
    return {"success": False, "message": "Invalid username or password"}


def get_user_by_id(user_id):
    """
    Retrieve a user document from the database based on their MongoDB document ID.
    
    Args:
        user_id (str): MongoDB document ID of the user to retrieve
        
    Returns:
        dict: Result containing:
            - success (bool): Whether retrieval was successful
            - user (dict): User document if found
            - message (str): Error message (on failure)
    """
    try:
        # Find user by ID
        user = collection.find_one({"_id": ObjectId(user_id)})
        
        if user:
            return {"success": True, "user": user}
        else:
            return {"success": False, "message": "User not found"}
    except Exception as e:
        return {"success": False, "message": f"Error retrieving user: {str(e)}"} 

    # Example usage:
    # result = get_user_by_id("66d563e1e5b58d4a8b75a33d")
    # print(JordanCarter29)
