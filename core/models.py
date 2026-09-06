"""
Core Data Models (OOP & SQLAlchemy ORM)
Role: Member 1
Defines database entities for Users, Memories, Documents, and Categories.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """Represents a registered user in the vault system."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships (OOP association)
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        """Serialize user object to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Document(Base):
    """Represents an uploaded document (PDF, DOCX, TXT)."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # in bytes
    extracted_text = Column(Text, nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA256 for de-duplication
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")
    memories = relationship("Memory", back_populates="document")

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if self.uploaded_at else None
        }


class Memory(Base):
    """Represents a stored memory, note, or entry."""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), default="General", index=True)  # e.g., Work, Health, Personal
    summary = Column(Text, nullable=True)  # AI generated summary
    importance = Column(Integer, default=1)  # 1 (low) to 5 (critical)
    tags = Column(JSON, default=list)  # list of tags, e.g. ["receipt", "october"]
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memories")
    document = relationship("Document", back_populates="memories")

    def to_dict(self):
        """Serialize memory record to dictionary for Streamlit UI."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "summary": self.summary or "No summary available.",
            "importance": self.importance,
            "tags": self.tags or [],
            "document_id": self.document_id,
            "created_at": self.created_at.strftime("%Y-%m-%d") if self.created_at else "",
        }

    def __repr__(self):
        return f"<Memory(id={self.id}, title='{self.title}', category='{self.category}')>"
