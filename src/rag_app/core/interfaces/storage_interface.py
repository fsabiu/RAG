from abc import ABC, abstractmethod
from typing import Dict, List

class Storage(ABC):
    @abstractmethod
    def get_all_collections(self) -> List[str]:
        """Return a list of all collection names."""
        pass

    @abstractmethod
    def get_collection(self, collection_name: str) -> List[str]:
        """Return a list of file names in the specified collection."""
        pass

    @abstractmethod
    def get_collection_items(self, collection_name: str) -> Dict[str, str]:
        """Return a dictionary of file names and their contents for the specified collection."""
        pass
