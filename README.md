# Small Business MCP Server

A Model Context Protocol (MCP) server designed to help small businesses organize and manage their data through PostgreSQL. This server provides tools to:

- Import and organize existing files (PDFs, images, documents)
- Process and store chat histories
- Create and maintain a structured PostgreSQL database
- Provide natural language interfaces for data queries
- Automate data organization and categorization

## Features

- **File Processing**
  - PDF text extraction and metadata processing
  - Image metadata and content analysis
  - Document organization and categorization
  - Directory structure analysis

- **Data Management**
  - Automatic schema generation based on content
  - Data normalization and deduplication
  - Relationship mapping between different data types
  - Version control for document changes

- **Natural Language Interface**
  - Query data using natural language
  - Generate reports and summaries
  - Create data visualizations
  - Schedule automated tasks

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

1. Start the MCP server:
   ```bash
   python -m MCPServer.server
   ```

2. Connect using an MCP client:
   ```python
   from mcp import ClientSession, StdioServerParameters
   
   async with ClientSession(server_params) as session:
       # Initialize connection
       await session.initialize()
       
       # List available tools
       tools = await session.list_tools()
       
       # Process a directory
       result = await session.call_tool(
           "process_directory",
           arguments={"path": "/path/to/business/files"}
       )
   ```

## Available Tools

- `process_directory`: Import and organize files from a directory
- `query_data`: Natural language query interface
- `generate_report`: Create business reports
- `manage_documents`: Document organization and versioning
- `analyze_chats`: Process and store chat histories
- `create_visualization`: Generate data visualizations

## Security

- All database credentials and API keys are managed through environment variables
- File access is restricted to specified directories
- Data encryption for sensitive information
- Regular backup procedures

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
