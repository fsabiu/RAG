# RAG Application

This is a sophisticated Retrieval-Augmented Generation (RAG) application leveraging FastAPI, OCI GenAI, and Oracle Database 23ai. The application is designed with a modular architecture, emphasizing clean abstractions and separation of concerns.

## Features

- Modular architecture with well-defined interfaces
- Support for multiple chunking strategies (fixed-size and semantic)
- Integration with OCI GenAI for chat model functionality
- Flexible document and domain management
- Customizable query engine with optimization and re-ranking capabilities
- Vector store integration for efficient similarity search

## Requirements

- Python 3.10+
- FastAPI
- OCI GenAI
- Oracle Database 23ai
- Additional dependencies listed in `requirements.txt`

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rag-application.git
   cd rag-application
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your `.env` file with the necessary environment variables (see `.env.example` for reference)

5. Run the application:
   ```
   python src/rag_app/main.py
   ```

## Architecture Overview

The application is built on a set of abstract interfaces, promoting loose coupling and easier testing. Below is a high-level architecture diagram of the RAG Application:

![RAG Application Architecture](docs/architecture_diagram.png)

*Figure 1: High-level architecture diagram of the RAG Application*

The diagram illustrates the main components of the system and their interactions:

1. The FastAPI application serves as the entry point, handling HTTP requests.
2. The Query Engine orchestrates the question-answering process.
3. The Domain Manager handles document and domain management.
4. Various models (Chat Model, Embedding Model) and stores (Vector Store) provide core functionalities.
5. The system integrates with external services like OCI GenAI and Oracle Database 23ai.

The application uses the following key interfaces:

- `ChatModelInterface`: Defines the contract for chat model implementations
- `ChunkStrategyInterface`: Abstracts different text chunking strategies
- `DocumentInterface` and `DocumentFactoryInterface`: Handle document representation and creation
- `DomainInterface` and `DomainFactoryInterface`: Manage domain-specific information and creation
- `DomainManagerInterface`: Orchestrates domain and document management
- `EmbeddingModelInterface`: Defines methods for generating and comparing embeddings
- `QueryEngineInterface`: Handles the core question-answering functionality
- `QueryOptimizerInterface`: Allows for query optimization implementations
- `ReRankerInterface`: Provides an interface for re-ranking search results
- `StorageInterface`: Abstracts storage operations for collections and items
- `VectorStoreInterface`: Defines methods for storing and querying vector embeddings

## Usage

The application exposes a `/ask` endpoint that accepts POST requests with a question and domain description. Detailed API documentation is available at the `/docs` endpoint when running the application.

## Development

To run tests:
```
pytest tests/

To build the Docker image:
```
docker build -t rag-app .

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


