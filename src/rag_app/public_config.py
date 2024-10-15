import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, Dict

class ChunkingSettings(BaseModel):
    STRATEGY: str = "semantic"  # Options: "semantic", "fixed"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

class QueryEngineSettings(BaseModel):
    USE_QUERY_OPTIMIZER: bool = True
    USE_RESULT_RE_RANKER: bool = True

class ChatModelSettings(BaseModel):
    PROVIDER: str = "oci"
    MODEL_ID: str = "cohere.command-r-plus"
    TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 4000
    TOP_P: float = 0.75

class EmbeddingModelSettings(BaseModel):
    PROVIDER: str = "ollama" # Options: "cohere", "ollama"
    MODEL_NAME: str = "mxbai-embed-large" # Options: "embed-english-v3.0" for cohere, "mxbai-embed-large" for ollama
    EMBEDDING_DIMENSION: int = 1024

class VectorStoreSettings(BaseModel):
    DEFAULT_PROVIDER: str = "Chroma" # Options: "OCI_DB", "Python"
    DOMAIN_CONFIG: Dict[str, str] = { # Options for values: "OCI_DB", "Python"
        "domain_name1": "Chroma", 
        "domain_name2": "Oracle23ai"
    }

class DocumentSettings(BaseModel):
    IMPLEMENTATION: str = "Python"
    DB_CONNECTION_STRING: Optional[str] = None

class PublicSettings(BaseModel):
    # Nested settings
    chunking: ChunkingSettings = ChunkingSettings()
    query_engine: QueryEngineSettings = QueryEngineSettings()
    chat_model: ChatModelSettings = ChatModelSettings()  # Added
    embedding_model: EmbeddingModelSettings = EmbeddingModelSettings()  # Added
    vector_store: VectorStoreSettings = VectorStoreSettings()  # Added
    document: DocumentSettings = DocumentSettings()  # Added

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

public_settings = PublicSettings()
