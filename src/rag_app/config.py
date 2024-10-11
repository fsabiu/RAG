import os
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Dict, List, Optional

class ChunkingSettings(BaseModel):
    STRATEGY: str = "fixed"  # Options: "semantic", "fixed"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

class ChatModelSettings(BaseModel):
    PROVIDER: str = "oci"  # Options: "oci", "openai", "cohere"
    MODEL_ID: str = "cohere.command-r-plus"
    TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 4000
    TOP_P: float = 0.75

    # OCI settings
    OCI_COMPARTMENT_ID: str = "ocid1.compartment.oc1..aaaaaaaaq3jw5diyfz3ykg5ow76q6nvslelmx75nlg55xzdhfuzbikq77nda"
    OCI_GENAI_ENDPOINT: str = "https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com"
    OCI_CONFIG_PROFILE: str = "IDIKA"
    OCI_CONFIG_PATH: str = "~/.oci/config"
    OCI_DEFAULT_MODEL: str = "cohere.command-r-plus"

class EmbeddingModelSettings(BaseModel):
    PROVIDER: str = "cohere"  # Options: "cohere", "openai"
    MODEL_NAME: str = "embed-english-v3.0"
    EMBEDDING_DIMENSION: int = 1024  # Updated for Cohere's model

class VectorStoreSettings(BaseModel):
    PROVIDER: str = "chroma"  # Options: "chroma", "pinecone", "faiss"
    PERSIST_DIRECTORY: str = "./chroma_db"

class QueryEngineSettings(BaseModel):
    USE_QUERY_OPTIMIZER: bool = True
    USE_RESULT_RE_RANKER: bool = True

class DocumentSettings(BaseModel):
    IMPLEMENTATION: str = "Python"  # Options: "OCI_DB", "Python"
    DB_CONNECTION_STRING: Optional[str] = None  # Required if IMPLEMENTATION is "OCI_DB"

class Settings(BaseSettings):
    APP_NAME: str = "RAG Application"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str
    OCI_API_KEY: str
    COHERE_API_KEY: str
    DATA_FOLDER: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

    # Nested settings
    chunking: ChunkingSettings = ChunkingSettings()
    chat_model: ChatModelSettings = ChatModelSettings()
    embedding_model: EmbeddingModelSettings = EmbeddingModelSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()
    query_engine: QueryEngineSettings = QueryEngineSettings()
    document: DocumentSettings = DocumentSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

settings = Settings()
