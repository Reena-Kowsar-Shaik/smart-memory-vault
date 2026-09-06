"""
PostgreSQL Database Connection & Repository Operations
Role: Member 1
Handles PostgreSQL engine initialization, session management, and CRUD operations.
"""

import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from core.models import Base, User, Memory, Document

load_dotenv()

# Database credentials from environment (or default local PostgreSQL)
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "memory_vault")

# Connection URL (PostgreSQL with psycopg2)
# Fallback to local SQLite if PostgreSQL isn't running yet (ensures teammates aren't blocked!)
PG_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SQLITE_FALLBACK_URL = "sqlite:///memory_vault.db"

try:
    engine = create_engine(PG_DATABASE_URL, pool_pre_ping=True)
    # Test connection
    with engine.connect() as conn:
        pass
    print("✅ Connected to PostgreSQL successfully!")
except Exception as e:
    print(f"⚠️ PostgreSQL connection failed ({e}). Using local SQLite for seamless testing.")
    engine = create_engine(SQLITE_FALLBACK_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables initialized!")


@contextmanager
def get_db():
    """Context manager for safe database transactions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class MemoryRepository:
    """OOP Repository class for managing memories in the database."""

    @staticmethod
    def create_memory(user_id: int, title: str, description: str, 
                      category: str = "General", summary: str = "", 
                      importance: int = 1, tags: list = None, document_id: int = None) -> dict:
        """Add a new memory record."""
        with get_db() as session:
            memory = Memory(
                user_id=user_id,
                title=title,
                description=description,
                category=category,
                summary=summary,
                importance=importance,
                tags=tags or [],
                document_id=document_id
            )
            session.add(memory)
            session.flush()
            return memory.to_dict()

    @staticmethod
    def get_user_memories(user_id: int) -> list[dict]:
        """Fetch all memories belonging to a specific user, newest first."""
        with get_db() as session:
            memories = session.query(Memory).filter(
                Memory.user_id == user_id
            ).order_by(Memory.created_at.desc()).all()
            return [m.to_dict() for m in memories]

    @staticmethod
    def delete_memory(memory_id: int, user_id: int) -> bool:
        """Delete a memory entry securely."""
        with get_db() as session:
            memory = session.query(Memory).filter(
                Memory.id == memory_id, Memory.user_id == user_id
            ).first()
            if memory:
                session.delete(memory)
                return True
            return False

    @staticmethod
    def update_memory(memory_id: int, user_id: int, **kwargs) -> bool:
        """Update fields of an existing memory."""
        with get_db() as session:
            memory = session.query(Memory).filter(
                Memory.id == memory_id, Memory.user_id == user_id
            ).first()
            if not memory:
                return False
            for key, value in kwargs.items():
                if hasattr(memory, key) and value is not None:
                    setattr(memory, key, value)
            return True


class UserRepository:
    """OOP Repository class for user operations."""

    @staticmethod
    def get_by_email(email: str):
        with get_db() as session:
            return session.query(User).filter(User.email == email.lower().strip()).first()

    @staticmethod
    def create_user(username: str, email: str, password_hash: str) -> dict:
        with get_db() as session:
            user = User(
                username=username.strip(),
                email=email.lower().strip(),
                password_hash=password_hash
            )
            session.add(user)
            session.flush()
            return user.to_dict()
