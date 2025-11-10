import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBHandler:
    def __init__(self):
        """
        Initialize the MongoDB handler with connection configuration.
        """
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.database_name = os.getenv("MONGODB_DATABASE", "aijukebox")
        self.collection_name = os.getenv("MONGODB_COLLECTION", "songs")
        self.client = None
        self.db = None
        self.collection = None
        
        if not self.mongodb_uri:
            raise ValueError("MONGODB_URI not found in environment variables")
        
        self.connect()
    
    def connect(self):
        """
        Establish connection to MongoDB.
        """
        try:
            self.client = MongoClient(self.mongodb_uri)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise
    
    def insert_song_data(self, song_data: Dict[str, Any]) -> bool:
        """
        Insert song data into MongoDB collection.
        
        Args:
            song_data (dict): Dictionary containing song information
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add timestamp to the data
            song_data_with_timestamp = song_data.copy()
            song_data_with_timestamp["timestamp"] = datetime.now(timezone.utc)
            
            # Insert the data
            result = self.collection.insert_one(song_data_with_timestamp)
            
            if result.inserted_id:
                logger.info(f"Successfully inserted song data with ID: {result.inserted_id}")
                return True
            else:
                logger.warning("Failed to insert song data")
                return False
                
        except Exception as e:
            logger.error(f"Error inserting song data: {e}")
            return False
    
    def close_connection(self):
        """
        Close the MongoDB connection.
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Example usage
if __name__ == "__main__":
    try:
        # Initialize the MongoDB handler
        mongo_handler = MongoDBHandler()
        
        # Example song data
        example_song_data = {
            "song_name": "Example Song",
            "genre": "Pop",
            "styles": "Upbeat, Catchy",
            "lyrics_description": "About love and relationships",
            "acceptable": True,
            "roast": "Not bad, but could use more cowbell."
        }
        
        # Insert the data
        success = mongo_handler.insert_song_data(example_song_data)
        print(f"Insertion successful: {success}")
        
        # Close the connection
        mongo_handler.close_connection()
        print("MongoDB connection closed.")
        
    except Exception as e:
        print(f"Error: {e}")
        # Try to close connection if it exists
        try:
            mongo_handler.close_connection()
        except:
            pass
