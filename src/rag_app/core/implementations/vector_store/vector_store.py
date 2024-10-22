from typing import List, Dict, Any
import logging
import chromadb
from src.rag_app.core.interfaces.vector_store_interface import VectorStoreInterface

logger = logging.getLogger(__name__)

class ChromaVectorStore(VectorStoreInterface):
    def __init__(self, collection_name: str, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        logger.info(f"Initialized Chroma vector store with collection: {collection_name}")

    def store_embeddings(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]], ids: List[str], documents: List[str]) -> None:
        logger.info(f"Storing {len(embeddings)} embeddings")
        self.collection.add(
            embeddings=embeddings,
            metadatas=metadata,
            ids=ids,
            documents=documents
        )

    def query(self, query_embedding: List[float], n_results: int = 10) -> List[Dict[str, Any]]:
        logger.info(f"Querying vector store for top {n_results} results")
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["metadatas", "distances", "documents"]
        )
        return [
            {
                "id": id,
                "distance": distance,
                "metadata": metadata,
                "document": document
            }
            for id, metadata, distance, document in zip(
                results['ids'][0],
                results['metadatas'][0],
                results['distances'][0],
                results['documents'][0]
            )
        ]
