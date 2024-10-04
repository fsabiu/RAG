# RAG Application

This is a Retrieval-Augmented Generation (RAG) application using FastAPI, OCI GenAI, and Oracle Database 23ai.

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file with the necessary environment variables
4. Run the application: `python src/rag_app/main.py`

## Usage

The application exposes a `/ask` endpoint that accepts POST requests with a question and domain description.

## Development

To run tests: `pytest tests/`

To build the Docker image: `docker build -t rag-app .`


