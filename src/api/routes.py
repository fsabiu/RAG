import os
import sys
import logging
import json
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import datetime
import glob
import traceback
from pydantic import BaseModel
from typing import List, Dict
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Interfaces
from rag_app.core.interfaces.query_engine_interface import QueryEngineInterface
from rag_app.core.interfaces.domain_manager_interface import DomainManagerInterface

# Implementations
from rag_app.core.implementations.conversation.conversation import Conversation
from rag_app.core.implementations.query_engine.query_engine import QueryEngine
from rag_app.private_config import private_settings

# Config
from rag_app.initialization import initialize_rag_components

# Logs
logger = logging.getLogger(__name__)

# App
router = APIRouter()

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


# Add this new model
class AskRequest(BaseModel):
    message: str
    genModel: str
    conversation: List[Dict[str, str]] = []

# Add this global variable
global_conversation = None

@router.post("/setup_rag")
async def setup_rag(config_data: dict = Body(...)):
    global query_engine, domain_manager
    
    try:
        # Merge public settings with incoming config_data
        merged_config = merge_configs(private_settings.dict(), config_data)
        
        # Write the merged configuration to a file
        merged_config_path = os.path.join(private_settings.DOCS_FOLDER, "rag_setup_merged.json")
        with open(merged_config_path, "w") as merged_config_file:
            json.dump(merged_config, merged_config_file, indent=4)
        
        # Initialize components using the merged configuration
        domain_manager, chat_model, embedding_model, chunk_strategy = initialize_rag_components(merged_config)
        domain_manager.apply_chunking_strategy()
        
        # Initialize the query engine with the components
        query_engine = QueryEngine(
            domain_manager=domain_manager,
            vector_stores=domain_manager.vector_stores,
            embedding_model=embedding_model,
            chat_model=chat_model,
            chunk_strategy=chunk_strategy,
            query_optimizer=merged_config['query_engine'].get('USE_QUERY_OPTIMIZER', True),
            result_re_ranker=merged_config['query_engine'].get('USE_RESULT_RE_RANKER', True)
        )
        
        # Logging before saving the configuration
        logger.info("RAG system initialized successfully. Preparing to save configuration.")
        logger.debug(f"CONFIGS_FOLDER path: {private_settings.CONFIGS_FOLDER}")
        
        # Store the original config_data with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        config_filename = f"config_{timestamp}.json"
        config_path = os.path.join(private_settings.CONFIGS_FOLDER, config_filename)
        
        logger.info(f"Saving configuration to file: {config_path}")
        
        try:
            with open(config_path, "w") as config_file:
                json.dump(config_data, config_file, indent=4)
            logger.info("Configuration saved successfully.")
        except IOError as e:
            logger.error(f"Error writing configuration file: {str(e)}")
        return {"message": "RAG system setup successfully"}
    except Exception as e:
        logger.error(f"Error during setup: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An error occurred during setup")

@router.get("/setup_rag_template")
async def get_setup_rag_template():
    try:
        with open(os.path.join(private_settings.DOCS_FOLDER, "rag_setup_template.json"), "r") as template_file:
            template_data = json.load(template_file)
        return JSONResponse(content=template_data)
    except Exception as e:
        logger.error(f"Error loading setup RAG template: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while loading the template")

@router.post("/ask")
async def ask(question: str, domain_name: str, query_engine: QueryEngineInterface = Depends(get_query_engine)):
    """
    Ask a question within a specific domain.
    """
    try:
        global global_conversation
        
        if not request.conversation:
            # Use the global conversation if the request doesn't provide one
            if global_conversation is None:
                global_conversation = Conversation()
            conversation = global_conversation
        else:
            # Create a new Conversation instance with the provided messages
            conversation = Conversation()
            for msg in request.conversation:
                conversation.add_message(role=msg['role'], content=msg['content'])
        
        full_response = ""
        
        async def content_generator():
            nonlocal full_response
            async for chunk in await query_engine.ask_question(
                query=request.message,
                model_name=request.genModel,
                conversation=conversation,
                stream=True
            ):
                full_response += chunk
                response = {
                    'content': chunk, 
                    'type': 'content',
                    'timestamp': time.time()
                }
                logging.info(f"Yielding content: {response}")
                yield f"data: {json.dumps(response)}\n\n"
            
            # Add the user's message to the conversation
            conversation.add_message("User", request.message)

            # Add the assistant's message to the conversation
            conversation.add_message("Assistant", full_response)
            
            # Update the global conversation after processing
            global_conversation = conversation
            
            # Include the updated conversation in the final response
            done_response = {
                'type': 'done', 
                'timestamp': time.time(),
                'conversation': [{"role": msg.role, "content": msg.content} for msg in conversation.get_history()]
            }
            yield f"data: {json.dumps(done_response)}\n\n"

        return StreamingResponse(content_generator(), media_type="text/event-stream")
    except Exception as e:
        error_message = str(e)
        logging.error(f"Error in /ask endpoint: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)

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

@router.get("/rag_config")
async def rag_config():
    """
    Retrieve the most recent RAG configuration.
    """
    try:
        config_folder = private_settings.CONFIGS_FOLDER
        config_files = glob.glob(os.path.join(config_folder, "config_*.json"))
        
        if not config_files:
            raise HTTPException(status_code=404, detail="No configuration files found")
        
        # Sort files by name (which includes timestamp) in descending order
        latest_config_file = max(config_files)
        
        with open(latest_config_file, "r") as file:
            config_data = json.load(file)
        
        logger.info(f"Successfully retrieved latest RAG configuration: {latest_config_file}")
        return JSONResponse(content=config_data)
    except Exception as e:
        logger.error(f"Error retrieving RAG configuration: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the configuration")

def merge_configs(base_config: dict, new_config: dict) -> dict:
    """
    Merge two configuration dictionaries. If both dictionaries have the same key
    and their values are lists, sets, or dictionaries, the values are combined.
    """
    merged_config = base_config.copy()
    for key, value in new_config.items():
        logger.debug(f"Processing key: {key}")
        logger.debug(f"Base config value: {merged_config.get(key)} (type: {type(merged_config.get(key))})")
        logger.debug(f"New config value: {value} (type: {type(value)})")
        
        if key in merged_config:
            if isinstance(merged_config[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                merged_config[key] = merge_configs(merged_config[key], value)
                logger.debug(f"Merged dictionary for key '{key}': {merged_config[key]}")
            elif isinstance(merged_config[key], (list, set)) and isinstance(value, (list, set)):
                # Combine the values if both are lists or sets
                merged_config[key] = list(set(merged_config[key]).union(value))
                logger.debug(f"Combined value for key '{key}': {merged_config[key]}")
            else:
                # Overwrite the value if they are not both lists, sets, or dicts
                merged_config[key] = value
                logger.debug(f"Overwritten value for key '{key}': {merged_config[key]}")
        else:
            # Add the new key-value pair
            merged_config[key] = value
            logger.debug(f"Set value for key '{key}': {merged_config[key]}")
    
    return merged_config