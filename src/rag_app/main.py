import sys
import os
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..api import routes
from rag_app.private_config import private_settings

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
    allow_origins=["http://localhost:3000"],  # Add your frontend URL explicitly
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Specify methods
    allow_headers=["*"],
    expose_headers=["*"],  # Add this line
)

# Include the API router
app.include_router(routes.router)

def run():
    """Run the FastAPI application."""
    logger.info("Starting the RAG Application...")
    uvicorn.run("rag_app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
