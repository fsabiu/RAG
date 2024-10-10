# Add the parent directory of 'api' (which should be 'src') to the Python path
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException
from rag_app.core.interfaces.query_engine_interface import QueryEngineInterface
from rag_app.core.interfaces.domain_manager_interface import DomainManagerInterface
from rag_app.config import settings
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

# This will be updated in main.py
def get_query_engine():
    pass

def get_domain_manager():
    pass

# API Routes

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
