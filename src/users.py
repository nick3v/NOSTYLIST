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
        "created_at": datetime.datetime.utcnow()
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
