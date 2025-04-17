import os
import magic
from pathlib import Path
from typing import Dict, Any, Tuple
import PyPDF2
from PIL import Image
import json
from datetime import datetime

def get_file_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from a file"""
    file_path = Path(file_path)
    mime = magic.Magic(mime=True)
    
    metadata = {
        'file_name': file_path.name,
        'file_path': str(file_path),
        'file_size': os.path.getsize(file_path),
        'created_at': datetime.fromtimestamp(os.path.getctime(file_path)),
        'modified_at': datetime.fromtimestamp(os.path.getmtime(file_path)),
        'mime_type': mime.from_file(str(file_path)),
        'file_type': file_path.suffix.lower()[1:] if file_path.suffix else 'unknown'
    }
    
    return metadata

def extract_pdf_content(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extract text content and metadata from a PDF file"""
    metadata = get_file_metadata(file_path)
    content = ""
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata['page_count'] = len(pdf_reader.pages)
            metadata['pdf_metadata'] = pdf_reader.metadata
            
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
    except Exception as e:
        content = f"Error extracting PDF content: {str(e)}"
    
    return content, metadata

def process_image(file_path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Process image file and extract metadata"""
    metadata = get_file_metadata(file_path)
    image_metadata = {}
    
    try:
        with Image.open(file_path) as img:
            image_metadata = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
                'info': img.info
            }
    except Exception as e:
        image_metadata = {'error': str(e)}
    
    return image_metadata, metadata

def process_text_file(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Process text file and extract content"""
    metadata = get_file_metadata(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        content = f"Error reading file: {str(e)}"
    
    return content, metadata

def process_directory(directory_path: str) -> Dict[str, Any]:
    """Process all files in a directory"""
    directory_path = Path(directory_path)
    results = {
        'files': [],
        'directories': [],
        'total_files': 0,
        'total_directories': 0
    }
    
    for root, dirs, files in os.walk(directory_path):
        # Add directories
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            results['directories'].append({
                'name': dir_name,
                'path': str(dir_path),
                'created_at': datetime.fromtimestamp(os.path.getctime(dir_path))
            })
            results['total_directories'] += 1
        
        # Process files
        for file_name in files:
            file_path = Path(root) / file_name
            try:
                metadata = get_file_metadata(str(file_path))
                results['files'].append(metadata)
                results['total_files'] += 1
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
    
    return results 