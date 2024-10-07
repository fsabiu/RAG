import json
import os
from typing import Dict, List, Optional
import logging
from src.rag_app.core.interfaces.storage_interface import StorageInterface

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileStorage(StorageInterface):
    def __init__(self, base_path: str):
        self.base_path = base_path
        
        # Check if the base folder exists
        if not os.path.exists(self.base_path):
            logger.error(f"Base path does not exist: {self.base_path}")
            raise FileNotFoundError(f"Base path does not exist: {self.base_path}")
        
        if not os.path.isdir(self.base_path):
            logger.error(f"Base path is not a directory: {self.base_path}")
            raise NotADirectoryError(f"Base path is not a directory: {self.base_path}")
        
        logger.info(f"Initialized FileStorage with base path: {self.base_path}")
        
        # Log the collections found
        collections = self.get_all_collections()
        logger.info(f"Found {len(collections)} collections: {', '.join(collections)}")

    def get_all_collections(self) -> List[str]:
        collections = [d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]
        logger.debug(f"Retrieved {len(collections)} collections")
        return collections

    def get_collection(self, collection_name: str) -> List[str]:
        collection_path = os.path.join(self.base_path, collection_name)
        if os.path.isdir(collection_path):
            files = [f for f in os.listdir(collection_path) if os.path.isfile(os.path.join(collection_path, f))]
            logger.debug(f"Retrieved {len(files)} files from collection '{collection_name}'")
            return files
        logger.warning(f"Collection not found: {collection_name}")
        return []

    def get_collection_items(self, collection_name: str) -> Dict[str, str]:
        collection_path = os.path.join(self.base_path, collection_name)
        items = {}
        if os.path.isdir(collection_path):
            for file_name in os.listdir(collection_path):
                file_path = os.path.join(collection_path, file_name)
                if os.path.isfile(file_path):
                    with open(file_path, 'r') as f:
                        items[file_name] = f.read()
            logger.debug(f"Retrieved {len(items)} items from collection '{collection_name}'")
        else:
            logger.warning(f"Collection not found: {collection_name}")
        return items

    def get_item(self, collection_name: str, item_name: str) -> Optional[str]:
        file_path = os.path.join(self.base_path, collection_name, item_name)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                logger.debug(f"Retrieved item '{item_name}' from collection '{collection_name}'")
                return content
            except IOError as e:
                logger.error(f"Error reading file '{item_name}' from collection '{collection_name}': {e}")
        else:
            logger.warning(f"Item '{item_name}' not found in collection '{collection_name}'")
        return None
