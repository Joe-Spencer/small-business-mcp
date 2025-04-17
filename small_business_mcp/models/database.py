from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String(512), unique=True, nullable=False)
    file_name = Column(String(256), nullable=False)
    file_type = Column(String(32), nullable=False)
    mime_type = Column(String(128), nullable=False)
    content = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    versions = relationship("DocumentVersion", back_populates="document")
    categories = relationship("DocumentCategory", secondary="document_category_association")

class DocumentVersion(Base):
    __tablename__ = 'document_versions'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    version_number = Column(Integer, nullable=False)
    content = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="versions")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", secondary="document_category_association")

class DocumentCategory(Base):
    __tablename__ = 'document_category_association'
    
    document_id = Column(Integer, ForeignKey('documents.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatHistory(Base):
    __tablename__ = 'chat_histories'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(String(64), nullable=False)
    role = Column(String(32), nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class BusinessData(Base):
    __tablename__ = 'business_data'
    
    id = Column(Integer, primary_key=True)
    data_type = Column(String(64), nullable=False)
    content = Column(JSON, nullable=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 