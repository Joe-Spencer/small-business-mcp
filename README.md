# Small Business MCP Server

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP SDK](https://img.shields.io/badge/mcp--sdk-1.6.0+-blue.svg)](https://github.com/modelcontextprotocol/python-sdk)

A [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk) server that connects language models with small business data systems. This server implements the MCP paradigm to create a structured, context-aware interface between LLMs and business information, providing tools for data manipulation, contextual resources, and interactive prompt templates.

## MCP Primitives

This server implements all three core MCP primitives:

| Primitive | Control                | Description                                     | Implementation                      |
| --------- | ---------------------- | ----------------------------------------------- | ----------------------------------- |
| Tools     | Model-controlled       | Functions for LLMs to take actions on data      | Document processing, data queries   |
| Resources | Application-controlled | Contextual data for LLM context                 | Business documents, database schema |
| Prompts   | User-controlled        | Interactive templates for common operations     | Report generation, data analysis    |

## Features

- **Structured Model Context**
  - Exposes business data through MCP resources
  - Provides contextual information to improve model reasoning
  - Maintains consistent representation of business concepts
  - Enables precise knowledge retrieval

- **AI-Powered Operations**
  - Model-controlled tools for data manipulation
  - File content extraction and categorization
  - Automated relationship mapping between entities
  - Version-controlled document management

- **Interactive Business Intelligence**
  - Natural language querying of business data
  - Templated prompts for common business tasks
  - Customizable report generation
  - Contextual analysis of business metrics

## Requirements

- Python 3.8+
- PostgreSQL 12+
- Required Python packages:
  - `mcp` (Model Context Protocol SDK)
  - `psycopg2` (PostgreSQL adapter)
  - `PyPDF2` (PDF processing)
  - `Pillow` (Image processing)
  - `python-magic` (File type detection)
  - `langchain` (NLP processing)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/small-business-mcp.git
   cd small-business-mcp
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL:
   ```bash
   # Create database
   createdb small_business_db
   
   # Set environment variables
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=small_business_db
   export DB_USER=your_username
   export DB_PASSWORD=your_password
   ```

## Usage

The MCP server acts as a bridge between language models and your business systems, structured around the three core MCP primitives (tools, resources, and prompts). This architecture allows LLMs to:

1. Retrieve contextual information about your business via resources
2. Take actions on your business data via tools
3. Leverage specialized templates for common tasks via prompts

### Starting the Server

You can start the MCP server using either of these methods:

```bash
# Method 1: Direct Python execution
python -m MCPServer.server

# Method 2: Using MCP CLI
mcp run MCPServer/server/server.py
```

The server uses FastMCP to expose tools, resources, and prompts to LLMs.

### Connecting with a Client

Connect to the server using the MCP client SDK:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters

async def main():
    # Create server parameters for connecting to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "MCPServer.server"],
        env=None,  # Optional environment variables
    )
    
    async with ClientSession(server_params) as session:
        # Initialize connection
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {[tool.name for tool in tools]}")
        
        # Process a directory
        result = await session.call_tool(
            "process_business_directory",
            arguments={"directory_path": "/path/to/business/files"}
        )
        print(f"Directory processing result: {result}")
        
        # Query business data
        query_result = await session.call_tool(
            "query_business_data",
            arguments={"query": "Show me all PDF documents from 2023"}
        )
        print(f"Query result: {query_result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Mounting to an Existing ASGI Server

You can integrate the MCP server with existing ASGI applications:

```python
from starlette.applications import Starlette
from starlette.routing import Mount
from MCPServer.server.server import mcp  # Import the FastMCP instance

# Mount the MCP server to an existing ASGI server
app = Starlette(
    routes=[
        Mount('/mcp', app=mcp.sse_app()),
    ]
)
```

## Available MCP Primitives

MCP defines a structured way for LLMs to interact with external systems through three core primitives, each with a distinct control model and purpose. This server implements:

### Tools

Models can use these tools to interact with business data:

- `process_business_directory`: Import and organize files from a directory
- `analyze_document`: Process a specific document and extract its content/metadata
- `query_business_data`: Natural language query interface for business data
- `store_chat_history`: Record conversation history in the database
- `create_business_report`: Generate reports based on stored data

### Resources

Resources provide contextual information to LLMs, exposing data that helps models reason about business objects. Unlike tools, resources are passively accessed rather than executed:

- `schema://database`: Database schema for reasoning about data structure
- `doc://{document_id}`: Access to specific document content
- `stats://business`: Business statistics and metrics

### Prompts

Prompts are user-controlled templates that guide how LLMs approach specific tasks, providing a standardized way to frame common business operations:

- `generate_report`: Template for creating various business reports
- `analyze_data`: Template for analyzing business data patterns
- `setup_assistant`: Template for configuring a business data assistant

## Server Capabilities

The server declares these capabilities during initialization:

| Capability | Feature Flag        | Description                            |
| ---------- | ------------------- | -------------------------------------- |
| tools      | listChanged         | Business data tools                    |
| resources  | subscribelistChanged| Document and schema access             |
| prompts    | listChanged         | Business report templates              |
| logging    | -                   | Server logging configuration           |
| completion | -                   | Argument completion suggestions        |

## Security

- All database credentials and API keys are managed through environment variables
- File access is restricted to specified directories
- Data encryption for sensitive information
- Regular backup procedures

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
