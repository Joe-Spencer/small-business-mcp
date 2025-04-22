from mcp.server.fastmcp import FastMCP, Context
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
from pathlib import Path
from datetime import datetime
import json

from ..config.database import get_db
from ..models.database import Document, Category, DocumentVersion, ChatHistory, BusinessData
from ..utils.file_processor import (
    process_directory,
    extract_pdf_content,
    process_image,
    process_text_file
)

# Create MCP server instance
mcp = FastMCP("Small Business Data Manager")

# ===== Resource implementations =====
@mcp.resource("schema://database")
async def get_database_schema(ctx: Context) -> str:
    """Provide the database schema as a resource for context"""
    db: Session = next(get_db())
    try:
        # Get table information from database
        # This is a simplified example - real implementation would query metadata
        schema = {
            "Document": {
                "id": "Integer, primary key",
                "file_path": "String",
                "file_name": "String",
                "file_type": "String",
                "mime_type": "String",
                "content": "Text, nullable",
                "metadata": "JSON",
                "created_at": "DateTime",
                "updated_at": "DateTime"
            },
            "Category": {
                "id": "Integer, primary key",
                "name": "String",
                "description": "String, nullable"
            },
            "DocumentVersion": {
                "id": "Integer, primary key",
                "document_id": "Integer, foreign key",
                "version": "Integer",
                "changes": "JSON",
                "created_at": "DateTime"
            },
            "ChatHistory": {
                "id": "Integer, primary key",
                "conversation_id": "String",
                "role": "String",
                "content": "Text",
                "created_at": "DateTime"
            },
            "BusinessData": {
                "id": "Integer, primary key",
                "data_type": "String",
                "data": "JSON",
                "created_at": "DateTime",
                "updated_at": "DateTime"
            }
        }
        return json.dumps(schema, indent=2)
    except Exception as e:
        return f"Error retrieving schema: {str(e)}"
    finally:
        db.close()

@mcp.resource("doc://{document_id}")
async def get_document_content(ctx: Context, document_id: str) -> Dict[str, Any]:
    """Provide document content as a resource"""
    db: Session = next(get_db())
    try:
        doc = db.query(Document).filter_by(id=int(document_id)).first()
        if not doc:
            return f"Document not found: {document_id}"
        
        return {
            "id": doc.id,
            "file_name": doc.file_name,
            "file_type": doc.file_type,
            "content": doc.content,
            "metadata": doc.metadata
        }
    except Exception as e:
        return f"Error retrieving document: {str(e)}"
    finally:
        db.close()

@mcp.resource("stats://business")
async def get_business_stats(ctx: Context) -> str:
    """Provide business statistics as a resource"""
    db: Session = next(get_db())
    try:
        doc_count = db.query(Document).count()
        category_count = db.query(Category).count()
        chat_count = db.query(ChatHistory).count()
        
        # Get counts by document type
        doc_types = {}
        for doc_type in db.query(Document.file_type).distinct():
            count = db.query(Document).filter_by(file_type=doc_type[0]).count()
            doc_types[doc_type[0]] = count
        
        stats = {
            "total_documents": doc_count,
            "total_categories": category_count,
            "total_conversations": chat_count,
            "documents_by_type": doc_types,
            "last_update": datetime.utcnow().isoformat()
        }
        
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error retrieving business stats: {str(e)}"
    finally:
        db.close()

# ===== Prompt implementations =====
@mcp.prompt()
async def generate_report(report_type: str, time_period: str = "last_month") -> str:
    """Create a prompt for generating a business report"""
    prompt = f"""
Please generate a comprehensive {report_type} business report for the {time_period}.

Your report should include:
1. Executive summary
2. Key metrics and performance indicators
3. Detailed analysis of the data
4. Comparison with previous periods
5. Recommendations for improvement

Please use the available tools to query the necessary data and format the report in a professional manner.
"""
    return prompt

@mcp.prompt()
async def analyze_data(data_type: str, analysis_focus: str) -> str:
    """Create a prompt for analyzing business data patterns"""
    prompt = f"""
Please analyze the {data_type} data with a focus on {analysis_focus}.

Your analysis should:
1. Identify key patterns and trends
2. Highlight anomalies or outliers
3. Provide insights into potential causes
4. Suggest actions based on the findings

Use the available tools to access the necessary data and perform your analysis.
"""
    return prompt

@mcp.prompt()
async def setup_assistant(business_type: str, focus_areas: List[str]) -> str:
    """Create a prompt for configuring a business data assistant"""
    areas = ", ".join(focus_areas)
    prompt = f"""
You are a specialized business data assistant for a {business_type} business.
Your primary focus areas are: {areas}.

Your responsibilities include:
1. Organizing and categorizing business documents
2. Answering queries about business data
3. Generating reports and insights
4. Providing recommendations based on data analysis

Please use the available tools to access and manage the business data effectively.
"""
    return prompt

# ===== Tool implementations =====
@mcp.tool()
async def process_business_directory(ctx: Context, directory_path: str) -> Dict[str, Any]:
    """Process a directory containing business files and documents"""
    # Validate directory path
    if not os.path.isdir(directory_path):
        return {"error": f"Directory not found: {directory_path}"}
    
    # Process directory
    results = process_directory(directory_path)
    
    # Store results in database
    db: Session = next(get_db())
    try:
        for file_info in results['files']:
            # Create document record
            document = Document(
                file_path=file_info['file_path'],
                file_name=file_info['file_name'],
                file_type=file_info['file_type'],
                mime_type=file_info['mime_type'],
                metadata=file_info
            )
            db.add(document)
        
        db.commit()
        return {"status": "success", "processed_files": len(results['files'])}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@mcp.tool()
async def analyze_document(ctx: Context, file_path: str) -> Dict[str, Any]:
    """Analyze and process a specific document"""
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}
    
    file_path = Path(file_path)
    file_type = file_path.suffix.lower()[1:]
    
    try:
        if file_type == 'pdf':
            content, metadata = extract_pdf_content(str(file_path))
        elif file_type in ['jpg', 'jpeg', 'png', 'gif']:
            content, metadata = process_image(str(file_path))
        else:
            content, metadata = process_text_file(str(file_path))
        
        # Store in database
        db: Session = next(get_db())
        try:
            document = Document(
                file_path=str(file_path),
                file_name=file_path.name,
                file_type=file_type,
                mime_type=metadata['mime_type'],
                content=content if isinstance(content, str) else None,
                metadata=metadata
            )
            db.add(document)
            db.commit()
            
            return {
                "status": "success",
                "document_id": document.id,
                "metadata": metadata
            }
        except Exception as e:
            db.rollback()
            return {"error": str(e)}
        finally:
            db.close()
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def query_business_data(ctx: Context, query: str) -> Dict[str, Any]:
    """Query business data using natural language"""
    db: Session = next(get_db())
    try:
        # TODO: Implement natural language query processing
        # For now, return basic document information
        documents = db.query(Document).all()
        return {
            "status": "success",
            "documents": [
                {
                    "id": doc.id,
                    "file_name": doc.file_name,
                    "file_type": doc.file_type,
                    "created_at": doc.created_at.isoformat()
                }
                for doc in documents
            ]
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@mcp.tool()
async def store_chat_history(ctx: Context, conversation_id: str, role: str, content: str) -> Dict[str, Any]:
    """Store chat history in the database"""
    db: Session = next(get_db())
    try:
        chat = ChatHistory(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        db.add(chat)
        db.commit()
        return {"status": "success", "chat_id": chat.id}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

@mcp.tool()
async def create_business_report(ctx: Context, report_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a business report based on stored data"""
    db: Session = next(get_db())
    try:
        # TODO: Implement report generation logic
        # For now, return a basic report structure
        return {
            "status": "success",
            "report_type": report_type,
            "parameters": parameters,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

if __name__ == "__main__":
    mcp.run() 