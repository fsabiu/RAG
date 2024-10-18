import sys
import os
import logging
import uvicorn
import json
import glob
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..api import routes
from rag_app.private_config import private_settings
from rag_app.core.implementations.query_engine.query_engine import QueryEngine
from rag_app.initialization import initialize_rag_components

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title=private_settings.APP_NAME, version=private_settings.APP_VERSION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://84.235.246.54:3000"],  # Add your frontend URL explicitly
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Specify methods
    allow_headers=["*"],
    expose_headers=["*"],  # Add this line
)

# Include the API router
app.include_router(routes.router)

def merge_configs(base_config: dict, new_config: dict) -> dict:
    merged_config = base_config.copy()
    for key, value in new_config.items():
        if key in merged_config:
            if isinstance(merged_config[key], dict) and isinstance(value, dict):
                merged_config[key] = merge_configs(merged_config[key], value)
            elif isinstance(merged_config[key], (list, set)) and isinstance(value, (list, set)):
                merged_config[key] = list(set(merged_config[key]).union(value))
            else:
                merged_config[key] = value
        else:
            merged_config[key] = value
    return merged_config

async def init_query_engine():
    try:
        # 1. Read the last filename in the CONFIGS_FOLDER
        config_files = glob.glob(os.path.join(private_settings.CONFIGS_FOLDER, "config_*.json"))
        if not config_files:
            logger.warning("No configuration files found. Using default configuration.")
            return

        latest_config_file = max(config_files)
        logger.info(f"Using configuration file: {latest_config_file}")

        # 2. Load the JSON from the latest config file
        with open(latest_config_file, 'r') as f:
            config_data = json.load(f)

        # 3. Merge with the private config
        merged_config = merge_configs(private_settings.dict(), config_data)

        # 4. Call initialize_rag_components with the merged config
        domain_manager, chat_model, embedding_model, chunk_strategy = initialize_rag_components(merged_config)

        # 5. Initialize the Query Engine
        query_engine = QueryEngine(
            domain_manager=domain_manager,
            vector_stores=domain_manager.vector_stores,
            embedding_model=embedding_model,
            chat_model=chat_model,
            chunk_strategy=chunk_strategy,
            query_optimizer=merged_config['query_engine'].get('USE_QUERY_OPTIMIZER', True),
            result_re_ranker=merged_config['query_engine'].get('USE_RESULT_RE_RANKER', True)
        )

        # Update the global query_engine in the routes module
        routes.query_engine = query_engine
        routes.domain_manager = domain_manager

        logger.info("Query engine initialized successfully on startup")
    except Exception as e:
        logger.error(f"Error initializing query engine on startup: {str(e)}")
        raise

# Add startup event to initialize query engine
@app.on_event("startup")
async def startup_event():
    await init_query_engine()

def run():
    """Run the FastAPI application."""
    logger.info("Starting the RAG Application...")
    uvicorn.run("rag_app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
