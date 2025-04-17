from mcp.server.fastmcp import FastMCP, Context
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
from pathlib import Path
from datetime import datetime

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