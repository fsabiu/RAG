import os
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Dict, List

class ChunkingSettings(BaseModel):
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

class ChatModelSettings(BaseModel):
    MODEL_ID: str = "cohere.command-r-plus"  # Changed from "cohere.command-r-plus"
    TEMPERATURE: float = 0.0  # Changed from 0.1
    MAX_TOKENS: int = 4000  # Changed from 1000
    TOP_P: float = 0.75  # Added this setting

    # OCI settings
    OCI_COMPARTMENT_ID: str = "ocid1.compartment.oc1..aaaaaaaaq3jw5diyfz3ykg5ow76q6nvslelmx75nlg55xzdhfuzbikq77nda"
    OCI_GENAI_ENDPOINT: str = "https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com"
    OCI_CONFIG_PROFILE: str = "IDIKA"
    OCI_CONFIG_PATH: str = "~/.oci/config"
    OCI_DEFAULT_MODEL: str = "cohere.command-r-plus"  # Changed from "oci-command-r-plus"

class EmbeddingModelSettings(BaseModel):
    MODEL_NAME: str = "text-embedding-ada-002"
    EMBEDDING_DIMENSION: int = 1536


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

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

settings = Settings()
