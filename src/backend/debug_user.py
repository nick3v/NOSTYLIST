import mongo_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get database connection
db = mongo_connection.db
user_collection = db["users"]

def debug_user_fields():
    """
    Debug function to print all users and their fields,
    specifically checking for the num_shorts field
    """
    logger.info("Starting user field debugging")
    
    # Get all users
    users = list(user_collection.find({}))
    logger.info(f"Found {len(users)} users in the database")
    
    for user in users:
        username = user.get('username', 'unknown')
        logger.info(f"User: {username}")
        logger.info(f"Fields: {list(user.keys())}")
        
        # Check for clothing count fields
        for field in ['num_hats', 'num_shirts', 'num_jackets', 'num_shorts', 'num_pants', 'num_shoes']:
            if field in user:
                logger.info(f"  {field}: {user[field]}")
            else:
                logger.error(f"  MISSING FIELD: {field}")

def fix_user_fields():
    """
    Add missing fields to user documents
    """
    logger.info("Starting user field fixes")
    
    # Fields that should be present in every user document with default values
    required_fields = {
        "num_outfits": "0",
        "num_hats": "0",
        "num_shirts": "0",
        "num_jackets": "0",
        "num_shorts": "0",
        "num_pants": "0",
        "num_shoes": "0"
    }
    
    # Get all users
    users = list(user_collection.find({}))
    logger.info(f"Found {len(users)} users in the database")
    
    update_count = 0
    for user in users:
        username = user.get('username', 'unknown')
        update_needed = False
        updates = {}
        
        # Check if each required field exists
        for field, default_value in required_fields.items():
            if field not in user:
                updates[field] = default_value
                update_needed = True
                logger.info(f"Will add missing field {field} to user {username}")
        
        # Update the user if needed
        if update_needed:
            user_collection.update_one(
                {"_id": user["_id"]},
                {"$set": updates}
            )
            update_count += 1
            logger.info(f"Updated user {username} with missing fields")
    
    logger.info(f"Updated {update_count} users with missing fields")
    return update_count

if __name__ == "__main__":
    logger.info("Running user database diagnostics")
    
    # First debug to see what's wrong
    debug_user_fields()
    
    # Then fix the issues
    fixed_count = fix_user_fields()
    
    # Debug again to verify fixes
    if fixed_count > 0:
        logger.info("After fixes:")
        debug_user_fields()
    else:
        logger.info("No fixes needed, all users have required fields") 