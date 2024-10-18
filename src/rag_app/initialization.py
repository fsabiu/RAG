import logging
import sys
import time
import traceback  # Add this import

# Interfaces and Implementations
from rag_app.core.interfaces.chat_model_interface import ChatModelInterface
from rag_app.core.implementations.chat_model.oci_chat_model import OCI_CommandRplus
from rag_app.core.implementations.chunk_strategy.fixed_size_strategy import FixedSizeChunkStrategy
from rag_app.core.implementations.chunk_strategy.semantic_strategy import SemanticChunkStrategy
from rag_app.core.implementations.document.document_factory import DocumentFactory
from rag_app.core.implementations.domain.domain_factory import DomainFactory
from rag_app.core.implementations.domain_manager.domain_manager import DomainManager
from rag_app.core.implementations.embedding_model.cohere_embedding import CohereEmbedding
from rag_app.core.implementations.embedding_model.ollama_embedding import OllamaEmbedding
from rag_app.core.implementations.vector_store.vector_store_factory import VectorStoreFactory
from rag_app.core.implementations.storage.file_storage import FileStorage

logger = logging.getLogger(__name__)

def initialize_rag_components(config_data: dict):
    try:
        chat_model: ChatModelInterface = OCI_CommandRplus(config_data["chat_model"])
        logger.info(f"{chat_model.__class__.__name__} chat model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize or test chat model: {str(e)}")
        sys.exit(1)

    try:
        storage = FileStorage(config_data["DATA_FOLDER"])
    except (FileNotFoundError, NotADirectoryError) as e:
        logger.error(f"Failed to initialize storage: {e}")
        sys.exit(1)

    collections = storage.get_all_collections()
    logger.info(f"Found {len(collections)} collections:")
    for collection in collections:
        logger.info(f"  - {collection}")

    logger.info("Initializing embedding model...")
    try:
        if config_data['embedding_model']['PROVIDER'].lower() == "cohere":
            embedding_model = CohereEmbedding(model_name=config_data['embedding_model']['MODEL_NAME'])
            logger.info(f"CohereEmbedding model '{config_data['embedding_model']['MODEL_NAME']}' initialized successfully")
        elif config_data['embedding_model']['PROVIDER'].lower() == "ollama":
            ollama_url = f"http://{config_data['embedding_model']['OLLAMA_HOST']}:{config_data['embedding_model']['OLLAMA_PORT']}"
            
            embedding_model = OllamaEmbedding(
                model_name=config_data['embedding_model']['MODEL_NAME'],
                ollama_host=config_data['embedding_model']['OLLAMA_HOST'],
                ollama_port=config_data['embedding_model']['OLLAMA_PORT']
            )
            logger.info(f"OllamaEmbedding model '{config_data['embedding_model']['MODEL_NAME']}' initialized successfully with URL: {ollama_url}")
        else:
            raise ValueError(f"Unsupported embedding model provider: {config_data['embedding_model']['PROVIDER']}")
    except Exception as e:
        logger.error(f"Failed to initialize embedding model: {str(e)}")
        sys.exit(1)
        
    logger.info("Initializing chunking strategy...")
    if config_data['chunking']['STRATEGY'] == "fixed":
        chunk_strategy = FixedSizeChunkStrategy(
            chunk_size=config_data['chunking']['CHUNK_SIZE'],
            overlap=config_data['chunking']['CHUNK_OVERLAP']
        )
        logger.info(f"Using FixedSizeChunkStrategy with chunk size {config_data['chunking']['CHUNK_SIZE']} and overlap {config_data['chunking']['CHUNK_OVERLAP']}")
    elif config_data['chunking']['STRATEGY'] == "semantic":
        chunk_strategy = SemanticChunkStrategy(
            max_chunk_size=config_data['chunking']['MAX_CHUNK_SIZE'],
            embedding_model=embedding_model
        )
        logger.info(f"Using SemanticChunkStrategy with max chunk size {config_data['chunking']['MAX_CHUNK_SIZE']}")
    else:
        logger.error(f"Invalid chunking strategy: {config_data['chunking']['STRATEGY']}")
        sys.exit(1)

    # Initialize domain and document factories
    domain_factory = DomainFactory()
    logger.info("Initializing document factory...")
    document_factory = DocumentFactory(config_data['document']['IMPLEMENTATION'])
    logger.info(f"Document factory initialized with {config_data['document']['IMPLEMENTATION']} implementation")
    logger.info("Initializing vector store factory...")
    vector_store_factory = VectorStoreFactory()
    logger.info("Vector store factory initialized")

    logger.info("Initializing DomainManager...")
    start_time = time.time()
    try:
        domain_manager = DomainManager(
            storage=storage,
            chunk_strategy=chunk_strategy,
            chat_model=chat_model,
            domain_factory=domain_factory,
            document_factory=document_factory,
            vector_store_factory=vector_store_factory,
            vector_stores_config=config_data['vector_store'],
            embedding_model=embedding_model
        )
    except Exception as e:
        logger.error(f"Failed to initialize DomainManager: {str(e)}")
        logger.error("Full traceback:")
        logger.error(traceback.format_exc())
        raise

    end_time = time.time()
    logger.info(f"DomainManager initialized in {end_time - start_time:.2f} seconds")

    return domain_manager, chat_model, embedding_model, chunk_strategy
