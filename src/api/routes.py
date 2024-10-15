# Add the parent directory of 'api' (which should be 'src') to the Python path
import os
import sys
import logging
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException, Body

# Interfaces
from rag_app.core.interfaces.query_engine_interface import QueryEngineInterface
from rag_app.core.interfaces.domain_manager_interface import DomainManagerInterface

# Implementations
from rag_app.core.implementations.query_engine.query_engine import QueryEngine
from rag_app.config import settings



from rag_app.initialization import initialize_rag_components

router = APIRouter()

logger = logging.getLogger(__name__)

# These will be updated in the /setup_RAG endpoint
query_engine = None
domain_manager = None

def get_query_engine():
    if query_engine is None:
        raise HTTPException(status_code=500, detail="Query engine not initialized")
    return query_engine

def get_domain_manager():
    if domain_manager is None:
        raise HTTPException(status_code=500, detail="Domain manager not initialized")
    return domain_manager

# API Routes

@router.post("/setup_rag")
async def setup_rag(config_data: dict = Body(...)):
    global query_engine, domain_manager
    
    try:
        # Initialize components using the provided config_data
        domain_manager, chat_model, embedding_model, chunk_strategy = initialize_rag_components(config_data)
        
        # Initialize the query engine with the components
        query_engine = QueryEngine(
            domain_manager=domain_manager,
            vector_stores=domain_manager.vector_stores,
            embedding_model=embedding_model,
            chat_model=chat_model,
            chunk_strategy=chunk_strategy,
            query_optimizer=config_data['query_engine'].get('USE_QUERY_OPTIMIZER', True),
            result_re_ranker=config_data['query_engine'].get('USE_RESULT_RE_RANKER', True)
        )
        
        return {"message": "RAG system setup successfully"}
    except Exception as e:
        logger.error(f"Error during setup: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during setup")

@router.post("/ask")
async def ask(question: str, domain_name: str, query_engine: QueryEngineInterface = Depends(get_query_engine)):
    """
    Ask a question within a specific domain.
    """
    try:
        logger.info(f"Received question: {question} for domain: {domain_name}")
        result = query_engine.ask_question(question, domain_name)
        logger.info(f"Successfully processed question.")
        return result
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/domains")
async def get_domains(domain_manager=Depends(get_domain_manager)):
    """
    Get a list of all domains.
    """
    try:
        domains = domain_manager.get_domains()
        return {"domains": domains}
    except Exception as e:
        logger.error(f"Error retrieving domains: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/domains")
async def add_domain(name: str, description: str, domain_manager=Depends(get_domain_manager)):
    """
    Add a new domain.
    """
    try:
        domain_manager.add_domain(name, description)
        logger.info(f"Successfully added domain: {name}")
        return {"message": f"Domain '{name}' added successfully"}
    except ValueError as ve:
        logger.error(f"Error adding domain: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error adding domain: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.delete("/domains/{domain_name}")
async def delete_domain(domain_name: str, domain_manager=Depends(get_domain_manager)):
    """
    Delete a domain.
    """
    try:
        domain_manager.delete_domain(domain_name)
        logger.info(f"Successfully deleted domain: {domain_name}")
        return {"message": f"Domain '{domain_name}' deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_name}' not found")
    except Exception as e:
        logger.error(f"Error deleting domain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configure")
async def configure(config_data: dict):
    try:
        # Write the configuration data to a file
        with open("src/rag_app/config.json", "w") as config_file:
            json.dump(config_data, config_file)
        
        # Optionally, trigger the preparation phase here
        # prepare_data()

        return {"message": "Configuration updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
