from ...interfaces.vector_store_interface import VectorStoreInterface, VectorStoreFactoryInterface
from src.rag_app.core.implementations.vector_store.vector_store import ChromaVectorStore
from src.rag_app.core.implementations.vector_store.oracle_23ai import Oracle23aiVectorStore

class VectorStoreFactory(VectorStoreFactoryInterface):  # Implementing the interface
    @staticmethod
    def create_vector_store(store_type: str, collection_name: str, persist_directory: str = None) -> VectorStoreInterface:
        if store_type == "Chroma":
            return ChromaVectorStore(collection_name, persist_directory)
        elif store_type == "Oracle23ai":
            return Oracle23aiVectorStore(collection_name)  # No persist_directory needed
        else:
            raise ValueError(f"Unsupported vector store type: {store_type}")
