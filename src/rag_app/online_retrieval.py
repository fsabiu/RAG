import sys
import os
import pickle
from dotenv import load_dotenv
import logging
import uvicorn
from fastapi import FastAPI

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_app.config import settings
from api import routes

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

def load_prepared_data():
    with open('prepared_data.pkl', 'rb') as f:
        prepared_data = pickle.load(f)
    return prepared_data

def main():
    logger.info("Initializing online retrieval application...")

    # Load prepared data
    prepared_data = load_prepared_data()
    
    domain_manager = prepared_data['domain_manager']
    vector_stores = prepared_data['vector_stores']
    embedding_model = prepared_data['embedding_model']
    chat_model = prepared_data['chat_model']
    query_engine = prepared_data['query_engine']

    # Update the dependency injection
    def get_query_engine():
        return query_engine

    # Update the routes to use the new dependency
    routes.get_query_engine = get_query_engine

    app.include_router(routes.router)

    logger.info("Online retrieval application initialized successfully.")

if __name__ == "__main__":
    main()
    uvicorn.run("online_retrieval:app", host="0.0.0.0", port=8000, reload=True)
