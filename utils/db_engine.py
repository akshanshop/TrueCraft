"""
Database engine factory for TrueCraft application.
Provides SQLAlchemy engine that works with both PostgreSQL and SQLite.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from pathlib import Path

from .config import get_database_url, get_database_mode

def create_db_engine():
    """
    Create SQLAlchemy engine based on configuration.
    Returns engine that works with PostgreSQL or SQLite.
    """
    database_url = get_database_url()
    database_mode = get_database_mode()
    
    if database_mode == 'postgres':
        # PostgreSQL configuration
        engine = create_engine(
            database_url,
            future=True,
            pool_pre_ping=True,
            echo=False  # Set to True for SQL debugging
        )
    else:
        # SQLite configuration
        # Handle sqlite:/// URL format
        if database_url.startswith('sqlite:///'):
            db_path = database_url.replace('sqlite:///', '')
        else:
            db_path = database_url
            
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create SQLite engine with proper configuration
        sqlite_url = f"sqlite:///{db_path}"
        engine = create_engine(
            sqlite_url,
            future=True,
            echo=False,  # Set to True for SQL debugging
            connect_args={
                "check_same_thread": False,  # Allow multi-threading
                "timeout": 30  # 30 second timeout for locked database
            },
            poolclass=StaticPool,  # Use static pool for SQLite
            pool_pre_ping=True
        )
    
    return engine

def get_database_info():
    """Get information about the current database configuration"""
    database_mode = get_database_mode()
    database_url = get_database_url()
    
    if database_mode == 'postgres':
        # Parse PostgreSQL URL for info (without exposing credentials)
        try:
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            info = {
                'type': 'PostgreSQL',
                'host': parsed.hostname or 'localhost',
                'port': parsed.port or 5432,
                'database': parsed.path.lstrip('/') if parsed.path else 'unknown'
            }
        except:
            info = {'type': 'PostgreSQL', 'host': 'configured', 'port': 'N/A', 'database': 'N/A'}
    else:
        # SQLite info
        db_path = database_url.replace('sqlite:///', '')
        info = {
            'type': 'SQLite',
            'path': db_path,
            'exists': Path(db_path).exists() if db_path else False,
            'size': Path(db_path).stat().st_size if Path(db_path).exists() else 0
        }
    
    return info

def test_database_connection():
    """Test database connection and return status"""
    try:
        engine = create_db_engine()
        with engine.connect() as conn:
            # Test basic query
            if get_database_mode() == 'postgres':
                result = conn.execute(text("SELECT version()"))
            else:
                result = conn.execute(text("SELECT sqlite_version()"))
            
            version = result.fetchone()[0]
            return {
                'success': True,
                'version': version,
                'mode': get_database_mode(),
                'info': get_database_info()
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'mode': get_database_mode(),
            'info': get_database_info()
        }

# Export the main functions
__all__ = ['create_db_engine', 'get_database_info', 'test_database_connection']