import json
import os
from typing import Dict, List, Optional
import logging
from src.rag_app.core.interfaces.storage_interface import StorageInterface
from docx import Document
from PyPDF2 import PdfReader
import chardet

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
                    content = self._read_file_content(file_path)
                    if content is not None:
                        items[file_name] = content
            logger.debug(f"Retrieved {len(items)} items from collection '{collection_name}'")
        else:
            logger.warning(f"Collection not found: {collection_name}")
        return items

    def get_item(self, collection_name: str, item_name: str) -> Optional[str]:
        file_path = os.path.join(self.base_path, collection_name, item_name)
        if os.path.isfile(file_path):
            return self._read_file_content(file_path)
        else:
            logger.warning(f"Item '{item_name}' not found in collection '{collection_name}'")
        return None

    def _read_file_content(self, file_path: str) -> Optional[str]:
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        try:
            if file_extension in ['.txt', '.md']:
                return self._read_text_file(file_path)
            elif file_extension == '.docx':
                return self._read_docx(file_path)
            elif file_extension == '.pdf':
                return self._read_pdf(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return None
        except Exception as e:
            logger.error(f"Error reading file '{file_path}': {e}")
            return None

    def _read_text_file(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        detected = chardet.detect(raw_data)
        encoding = detected['encoding'] or 'utf-8'  # Default to utf-8 if detection fails
        try:
            return raw_data.decode(encoding)
        except UnicodeDecodeError:
            # If decoding fails, try with 'latin-1' as a fallback
            logger.warning(f"Failed to decode {file_path} with {encoding}, falling back to latin-1")
            return raw_data.decode('latin-1')

    def _read_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    def _read_pdf(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            pdf = PdfReader(f)
            return '\n'.join([page.extract_text() for page in pdf.pages])
