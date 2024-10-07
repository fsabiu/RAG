import sys
import os
import time

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import uvicorn
from fastapi import FastAPI
from api import routes
from rag_app.config import settings
from rag_app.core.implementations.storage.file_storage import FileStorage
from rag_app.core.implementations.domain_manager.domain_manager import DomainManager
from rag_app.core.implementations.chunk_strategy.sentence_strategy import SentenceChunkStrategy
from rag_app.core.implementations.chat_model.oci_chat_model import OCI_CommandRplus, OCI_Llama3_70
from rag_app.core.implementations.vector_store.vector_store import ChromaVectorStore
from rag_app.core.implementations.embedding_model.embedding_model import CohereEmbedding
from rag_app.core.implementations.query_engine.query_engine import QueryEngine
from dotenv import load_dotenv

load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

def main():
    logger.info("Initializing application...")

    # Initialize chat model
    logger.info("Initializing chat model...")
    try:
        chat_model: ChatModel = OCI_CommandRplus()
        logger.info(f"{chat_model.__class__.__name__} chat model initialized successfully")
        
        # Test chat model
        test_message = "Hi, how are you?"
        logger.info(f"Testing chat model with message: '{test_message}'")
        response = chat_model.chat("Prompt:", test_message)
        logger.info(f"Chat model response: '{response}'")
        
    except Exception as e:
        logger.error(f"Failed to initialize or test chat model: {str(e)}")
        sys.exit(1)

    # Initialize storage
    try:
        logger.info(f"Attempting to initialize FileStorage with path: {settings.DATA_FOLDER}")
        storage = FileStorage(settings.DATA_FOLDER)
    except (FileNotFoundError, NotADirectoryError) as e:
        logger.error(f"Failed to initialize storage: {e}")
        sys.exit(1)

    # Log successful initialization
    logger.info("Storage initialized successfully")

    # Get and log all collections from Storage
    collections = storage.get_all_collections()
    logger.info(f"Found {len(collections)} collections:")
    for collection in collections:
        logger.info(f"  - {collection}")

    # Initialize chunking strategy
    logger.info("Initializing chunking strategy...")
    chunk_strategy = SentenceChunkStrategy()

    # Initialize DomainManager
    logger.info("Initializing DomainManager...")
    start_time = time.time()
    domain_manager = DomainManager(storage, chunk_strategy, chat_model)
    end_time = time.time()
    logger.info(f"DomainManager initialized in {end_time - start_time:.2f} seconds")

    # Apply chunking strategy
    logger.info("Applying chunking strategy...")
    start_time = time.time()
    domain_manager.apply_chunking_strategy()
    end_time = time.time()
    logger.info(f"Chunking strategy applied in {end_time - start_time:.2f} seconds")

    # Print domain info
    logger.info("Domain information:")
    for domain in domain_manager.get_domains():
        logger.info(f"  Domain: {domain.name}")
        logger.info(f"    Description: {domain.description}")
        logger.info(f"    Number of documents: {len(domain.documents)}")
        for doc in domain.documents:
            logger.info(f"      - {doc.name} (Chunks: {len(doc.get_chunks())})")

    # Initialize vector stores
    logger.info("Initializing ChromaVectorStores...")
    vector_stores = {}
    for domain in domain_manager.get_domains():
        collection_name = f"{domain.name.lower().replace(' ', '_')}"
        try:
            vector_store = ChromaVectorStore(collection_name=collection_name, persist_directory="./chroma_db")
            vector_stores[domain.name] = vector_store
            logger.info(f"Created ChromaVectorStore for collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to create ChromaVectorStore for collection '{collection_name}': {str(e)}")
            # Continue with the next domain instead of exiting
            continue
    
     # Initialize embedding model
    logger.info("Initializing CohereEmbedding model...")
    try:
        embedding_model = CohereEmbedding(model_name="embed-english-v3.0")
        logger.info("CohereEmbedding model initialized successfully")
    except ValueError as e:
        logger.error(f"Failed to initialize CohereEmbedding model: {str(e)}")
        sys.exit(1)

    # Initialize QueryEngine with the vector stores
    query_engine = QueryEngine(domain_manager, vector_stores, embedding_model)

    """
    # Perform offline initializations
    # vector_store = VectorStore(settings.DATABASE_URL)

    # embedding_model = EmbeddingModel(model_name=settings.EMBEDDING_MODEL_NAME)

    # Create QueryEngine with the initialized models
    # query_engine = QueryEngine(domain_manager, vector_store, chat_model, embedding_model)

    # Prepare domains (chunk, embed, and store)
    # query_engine.prepare_domains()

    # Update the dependency injection
    # def get_query_engine():
    #     return query_engine

    # Update the routes to use the new dependency
    # routes.get_query_engine = get_query_engine

    # app.include_router(routes.router)
    """

if __name__ == "__main__":
    main()
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
