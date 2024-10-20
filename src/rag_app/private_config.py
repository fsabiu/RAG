import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional

class ChatModelSettings(BaseModel):
    # OCI settings
    OCI_COMPARTMENT_ID: str = "ocid1.compartment.oc1..aaaaaaaaq3jw5diyfz3ykg5ow76q6nvslelmx75nlg55xzdhfuzbikq77nda"
    OCI_GENAI_ENDPOINT: str = "https://inference.generativeai.eu-frankfurt-1.oci.oraclecloud.com"
    OCI_CONFIG_PROFILE: str = "IDIKA"
    OCI_CONFIG_PATH: str = "~/.oci/config"
    OCI_DEFAULT_MODEL: str = "cohere.command-r-plus"

class EmbeddingModelSettings(BaseModel):
    OLLAMA_HOST: str = "10.0.0.135"
    OLLAMA_PORT: int = 11434

class VectorStoreSettings(BaseModel):
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db" # Required if DEFAULT_PROVIDER = "Chroma"

class DocumentSettings(BaseModel):
    DB_CONNECTION_STRING: Optional[str] = None  # Required if IMPLEMENTATION is "OCI_DB"

class PrivateSettings(BaseSettings):
    APP_NAME: str = "OrAsk"
    APP_VERSION: str = "0.1"
    DEBUG: bool = False
    LOG_LEVEL: str = "DEBUG"
    DATABASE_URL: str
    OCI_API_KEY: str
    COHERE_API_KEY: str
    DATA_FOLDER: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    DOCS_FOLDER: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs")
    CONFIGS_FOLDER: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "configs")

    # New INIT_PROMPT
    INIT_PROMPT: str = """You are a helpful Oracle chat assistant called AskOra developed to help the customers with the Oracle Documentation.
        You have to provide a welcome message to the user. Maximum three lines.
    """

    # Nested settings
    chat_model: ChatModelSettings = ChatModelSettings()
    embedding_model: EmbeddingModelSettings = EmbeddingModelSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()
    document: DocumentSettings = DocumentSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

private_settings = PrivateSettings()
