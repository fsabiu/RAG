import sys
import os
import time
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import uvicorn
from fastapi import FastAPI
from api import routes
from rag_app.config import settings

# Interfaces
from rag_app.core.interfaces.chat_model_interface import ChatModelInterface
from rag_app.core.interfaces.chunk_strategy_interface import ChunkStrategyInterface
from rag_app.core.interfaces.document_interface import DocumentFactoryInterface
from rag_app.core.interfaces.domain_interface import DomainFactoryInterface
from rag_app.core.interfaces.domain_manager_interface import DomainManagerInterface
from rag_app.core.interfaces.embedding_model_interface import EmbeddingModelInterface
from rag_app.core.interfaces.query_engine_interface import QueryEngineInterface
from rag_app.core.interfaces.storage_interface import StorageInterface
from rag_app.core.interfaces.vector_store_interface import VectorStoreInterface

# Implementations
from rag_app.core.implementations.chat_model.oci_chat_model import OCI_CommandRplus
from rag_app.core.implementations.chunk_strategy.fixed_size_strategy import FixedSizeChunkStrategy
from rag_app.core.implementations.chunk_strategy.semantic_strategy import SemanticChunkStrategy
from rag_app.core.implementations.document.document_factory import DocumentFactory
from rag_app.core.implementations.domain.domain_factory import DomainFactory
from rag_app.core.implementations.domain_manager.domain_manager import DomainManager
from rag_app.core.implementations.embedding_model.cohere_embedding import CohereEmbedding
from rag_app.core.implementations.query_engine.query_engine import QueryEngine
from rag_app.core.implementations.query_optimizer.query_optimizer import QueryOptimizer
from rag_app.core.implementations.reranker.reranker import ResultReRanker
from rag_app.core.implementations.storage.file_storage import FileStorage
from rag_app.core.implementations.vector_store.vector_store import ChromaVectorStore

load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Set the logger level to WARNING to suppress info and debug logs
logging.getLogger('cohere').setLevel(logging.WARNING)

# Suppress unwanted logs
logging.getLogger('botocore').setLevel(logging.ERROR)
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('posthog').setLevel(logging.ERROR)
logging.getLogger('sagemaker').setLevel(logging.ERROR)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)


def main():
    logger.info("Initializing application...")

    logger.info("Initializing chat model...")
    try:
        chat_model: ChatModel = OCI_CommandRplus()
        logger.info(f"{chat_model.__class__.__name__} chat model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize or test chat model: {str(e)}")
        sys.exit(1)

    try:
        storage = FileStorage(settings.DATA_FOLDER)
    except (FileNotFoundError, NotADirectoryError) as e:
        logger.error(f"Failed to initialize storage: {e}")
        sys.exit(1)

    collections = storage.get_all_collections()
    logger.info(f"Found {len(collections)} collections:")
    for collection in collections:
        logger.info(f"  - {collection}")

    logger.info("Initializing CohereEmbedding model...")
    try:
        embedding_model = CohereEmbedding(model_name="embed-english-v3.0")
        logger.info("CohereEmbedding model initialized successfully")
    except ValueError as e:
        logger.error(f"Failed to initialize CohereEmbedding model: {str(e)}")
        sys.exit(1)
        
    logger.info("Initializing chunking strategy...")
    if settings.chunking.STRATEGY == "fixed":
        chunk_strategy = FixedSizeChunkStrategy(
            chunk_size=settings.chunking.CHUNK_SIZE,
            overlap=settings.chunking.CHUNK_OVERLAP
        )
        logger.info(f"Using FixedSizeChunkStrategy with chunk size {settings.chunking.CHUNK_SIZE} and overlap {settings.chunking.CHUNK_OVERLAP}")
    elif settings.chunking.STRATEGY == "semantic":
        chunk_strategy = SemanticChunkStrategy(
            max_chunk_size=settings.chunking.CHUNK_SIZE,
            embedding_model=embedding_model
        )
        logger.info(f"Using SemanticChunkStrategy with max chunk size {settings.chunking.CHUNK_SIZE}")
    else:
        logger.error(f"Invalid chunking strategy: {settings.chunking.STRATEGY}")
        sys.exit(1)

    logger.info("Initializing document factory...")
    document_factory = DocumentFactory(settings.document.IMPLEMENTATION)
    logger.info(f"Document factory initialized with {settings.document.IMPLEMENTATION} implementation")

    # Initialize domain and document factories
    domain_factory = DomainFactory()
    document_factory = DocumentFactory()

    logger.info("Initializing ChromaVectorStores...")
    vector_stores = {}
        
    logger.info("Initializing DomainManager...")
    start_time = time.time()
    domain_manager = DomainManager(
        storage=storage,
        chunk_strategy=chunk_strategy,
        chat_model=chat_model,
        domain_factory=domain_factory,
        document_factory=document_factory,
        vector_stores=vector_stores,
        embedding_model=embedding_model
    )
    end_time = time.time()

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
    """
    Domain manager will have:
    - Storage
    - Chunk strategy
    - Chat model
    - Domains, that are dicts of:
        - Domain name -> Domain
        where Domains are lists of Documents (i.e. doc name, collection_name, title)
    """
    logger.info(f"DomainManager initialized in {end_time - start_time:.2f} seconds")


    query_engine = QueryEngine(
        domain_manager=domain_manager,
        vector_stores=vector_stores,
        embedding_model=embedding_model,
        chat_model=chat_model,
        chunk_strategy=chunk_strategy,
        query_optimizer=QueryOptimizer(),
        result_re_ranker=ResultReRanker()
    )

    logger.info("Applying chunking strategy...")
    start_time = time.time()
    domain_manager.apply_chunking_strategy()
    end_time = time.time()
    logger.info(f"Chunking strategy applied in {end_time - start_time:.2f} seconds")

    # Get all documents per domain
    logger.info("Fetching documents for each domain:")
    domains = domain_manager.get_domains()
    for domain in domains:
        documents = domain_manager.get_domain_documents(domain.name)
        logger.info(f"  Domain: {domain.name}")
        for doc in documents:
            logger.info(f"    - {doc}")

    # Fetch the first document of the first domain and print its chunks
    for domain in domains:
        first_document = domain.documents[0]
        logger.info(f"Fetching chunks for the first document of {domain.name}:")
        document = domain_manager.get_domain_document(domain.name, first_document.name)
        chunks = document.chunks
        logger.info(f"  Chunk lenght: {str(len(chunks))}")
        logger.info(f"  Document: {document.name}")
        logger.info(f"  Number of chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks[:5], 1):  # Print first 5 chunks
            logger.info(f"    Chunk {i}: {chunk[:100]}...")  # Print first 100 characters of each chunk

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
