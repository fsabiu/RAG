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
# ... (import statements from the original file)

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Set the logger level to WARNING to suppress info and debug logs
logging.getLogger('cohere').setLevel(logging.WARNING)

# Suppress unwanted logs
# ... (logging configurations from the original file)

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
        return FixedChunkStrategy(chunk_size=settings.chunking.CHUNK_SIZE, chunk_overlap=settings.chunking.CHUNK_OVERLAP)
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
    domain_manager = DomainManager(storage, chunk_strategy, chat_model, domain_factory, document_factory)

    # Apply chunking strategy
    logger.info("Applying chunking strategy...")
    start_time = time.time()
    domain_manager.apply_chunking_strategy()
    end_time = time.time()
    logger.info(f"Chunking strategy applied in {end_time - start_time:.2f} seconds")

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
