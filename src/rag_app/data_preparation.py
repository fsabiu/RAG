import sys
import os
import time
from dotenv import load_dotenv
import logging
import pickle

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_app.config import settings

# Import necessary interfaces and implementations
from rag_app.core.implementations.chat_model.oci_chat_model import OCI_CommandRplus
from rag_app.core.implementations.chunk_strategy.fixed_size_strategy import FixedSizeChunkStrategy
from rag_app.core.implementations.chunk_strategy.semantic_strategy import SemanticChunkStrategy
from rag_app.core.implementations.document.document_factory import DocumentFactory
from rag_app.core.implementations.domain.domain_factory import DomainFactory
from rag_app.core.implementations.domain_manager.domain_manager import DomainManager
from rag_app.core.implementations.embedding_model.embedding_model import CohereEmbedding
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

def get_chat_model():
    if settings.chat_model.PROVIDER == "oci":
        return OCI_CommandRplus()
    # Add other providers as needed
    raise ValueError(f"Unsupported chat model provider: {settings.chat_model.PROVIDER}")

def get_embedding_model():
    if settings.embedding_model.PROVIDER == "cohere":
        return CohereEmbedding(model_name=settings.embedding_model.MODEL_NAME)
    # Add other providers as needed
    raise ValueError(f"Unsupported embedding model provider: {settings.embedding_model.PROVIDER}")

def get_chunk_strategy(embedding_model):
    if settings.chunking.STRATEGY == "semantic":
        return SemanticChunkStrategy(max_chunk_size=settings.chunking.CHUNK_SIZE, embedding_model=embedding_model)
    elif settings.chunking.STRATEGY == "fixed":
        return FixedSizeChunkStrategy(chunk_size=settings.chunking.CHUNK_SIZE, overlap=settings.chunking.CHUNK_OVERLAP)
    raise ValueError(f"Unsupported chunking strategy: {settings.chunking.STRATEGY}")

def get_vector_store(collection_name):
    if settings.vector_store.PROVIDER == "chroma":
        return ChromaVectorStore(collection_name=collection_name, persist_directory=settings.vector_store.PERSIST_DIRECTORY)
    # Add other providers as needed
    raise ValueError(f"Unsupported vector store provider: {settings.vector_store.PROVIDER}")

def prepare_data():
    logger.info("Initializing data preparation...")

    # Initialize components
    chat_model = get_chat_model()
    storage = FileStorage(settings.DATA_FOLDER)
    embedding_model = get_embedding_model()
    chunk_strategy = get_chunk_strategy(embedding_model)
    domain_factory = DomainFactory()
    document_factory = DocumentFactory()

    # Initialize DomainManager
    domain_manager = DomainManager(storage, chunk_strategy, chat_model, domain_factory, document_factory, embedding_model=embedding_model)

    # Initialize VectorStores
    vector_stores = {}
    for domain in domain_manager.get_domains():
        collection_name = f"{domain.name.lower().replace(' ', '_')}"
        try:
            vector_store = get_vector_store(collection_name)
            vector_stores[domain.name] = vector_store
            logger.info(f"Created VectorStore for collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to create VectorStore for collection '{collection_name}': {str(e)}")
            continue

    # Apply chunking strategy and store embeddings
    logger.info("Applying chunking strategy and storing embeddings...")
    start_time = time.time()
    domain_manager.apply_chunking_strategy()
    end_time = time.time()
    logger.info(f"Chunking strategy applied and embeddings stored in {end_time - start_time:.2f} seconds")

    # Create QueryEngine
    query_engine = QueryEngine(
        domain_manager=domain_manager,
        vector_stores=vector_stores,
        embedding_model=embedding_model,
        chat_model=chat_model,
        chunk_strategy=chunk_strategy,
        query_optimizer=QueryOptimizer() if settings.query_engine.USE_QUERY_OPTIMIZER else None,
        result_re_ranker=ResultReRanker() if settings.query_engine.USE_RESULT_RE_RANKER else None
    )

    # Save necessary components for online retrieval
    with open('prepared_data.pkl', 'wb') as f:
        pickle.dump({
            'domain_manager': domain_manager,
            'vector_stores': vector_stores,
            'embedding_model': embedding_model,
            'chat_model': chat_model,
            'query_engine': query_engine
        }, f)

    logger.info("Data preparation completed and saved.")

if __name__ == "__main__":
    prepare_data()