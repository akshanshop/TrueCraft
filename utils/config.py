"""
Configuration management for TrueCraft application.
Handles environment detection and provides deployment-agnostic settings.
"""
import os
from typing import Optional, Dict, Any
from pathlib import Path

def load_environment():
    """Load environment variables from .env file if it exists"""
    try:
        from dotenv import load_dotenv
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        # python-dotenv not available, continue without it
        pass

def get_public_url() -> str:
    """
    Get the public URL for the application, checking various deployment platforms.
    Priority order: PUBLIC_URL, RENDER_EXTERNAL_URL, CODESPACE_NAME, VERCEL_URL, REPLIT_URL, localhost
    """
    # Load environment first
    load_environment()
    
    # Explicit PUBLIC_URL override
    if public_url := os.getenv('PUBLIC_URL'):
        return public_url.rstrip('/')
    
    # Render.com
    if render_url := os.getenv('RENDER_EXTERNAL_URL'):
        return render_url.rstrip('/')
    
    # GitHub Codespaces
    if codespace_name := os.getenv('CODESPACE_NAME'):
        return f"https://{codespace_name}-5000.githubpreview.dev"
    
    # Vercel
    if vercel_url := os.getenv('VERCEL_URL'):
        return f"https://{vercel_url}"
    
    # Replit
    if repl_slug := os.getenv('REPL_SLUG'):
        repl_owner = os.getenv('REPL_OWNER', 'user')
        return f"https://{repl_slug}.{repl_owner}.replit.app"
    
    # Default to localhost for local development
    return "http://localhost:5000"

def get_database_mode() -> str:
    """
    Determine which database mode to use.
    Returns 'postgres' if PostgreSQL is configured, 'sqlite' otherwise.
    """
    load_environment()
    
    # Check if PostgreSQL is available and configured
    if os.getenv('DATABASE_URL') and _is_postgres_available():
        return 'postgres'
    
    # Default to SQLite for local development
    return 'sqlite'

def _is_postgres_available() -> bool:
    """Check if psycopg2 is available for PostgreSQL connections"""
    try:
        import psycopg2
        return True
    except ImportError:
        return False

def get_auth_config() -> Dict[str, Any]:
    """
    Get authentication configuration based on available secrets and settings.
    """
    load_environment()
    
    config = {
        'auth_enabled': os.getenv('AUTH_ENABLED', 'true').lower() == 'true',
        'require_oauth': os.getenv('REQUIRE_OAUTH', 'false').lower() == 'true',
        'google_oauth_available': bool(
            os.getenv('GOOGLE_CLIENT_ID') and 
            os.getenv('GOOGLE_CLIENT_SECRET') and 
            _is_oauth_available()
        ),
        'github_oauth_available': bool(
            os.getenv('GITHUB_CLIENT_ID') and 
            os.getenv('GITHUB_CLIENT_SECRET') and 
            _is_oauth_available()
        )
    }
    
    config['oauth_available'] = config['google_oauth_available'] or config['github_oauth_available']
    
    return config

def _is_oauth_available() -> bool:
    """Check if OAuth dependencies are available"""
    try:
        import authlib
        import requests
        return True
    except ImportError:
        return False

def get_database_url() -> str:
    """Get the appropriate database URL based on the mode"""
    load_environment()
    
    if get_database_mode() == 'postgres':
        return os.getenv('DATABASE_URL', '')
    else:
        # SQLite database in data directory
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        return f"sqlite:///{data_dir}/truecraft.db"

def is_development_mode() -> bool:
    """Check if running in development mode"""
    load_environment()
    return os.getenv('ENVIRONMENT', 'development').lower() == 'development'

def get_app_config() -> Dict[str, Any]:
    """Get complete application configuration"""
    return {
        'public_url': get_public_url(),
        'database_mode': get_database_mode(),
        'database_url': get_database_url(),
        'auth': get_auth_config(),
        'development_mode': is_development_mode(),
        'app_name': os.getenv('APP_NAME', 'TrueCraft Marketplace Assistant'),
        'app_version': os.getenv('APP_VERSION', '1.0.0')
    }

# Environment validation helpers
def validate_environment() -> Dict[str, Any]:
    """Validate the current environment and return status information"""
    config = get_app_config()
    
    status = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'config': config
    }
    
    # Check database connectivity
    if config['database_mode'] == 'postgres':
        if not config['database_url']:
            status['errors'].append("PostgreSQL mode selected but no DATABASE_URL provided")
            status['valid'] = False
        elif not _is_postgres_available():
            status['errors'].append("PostgreSQL mode selected but psycopg2 not installed")
            status['valid'] = False
    
    # Check OAuth configuration
    auth_config = config['auth']
    if auth_config['require_oauth'] and not auth_config['oauth_available']:
        status['errors'].append("OAuth required but no OAuth providers configured or dependencies missing")
        status['valid'] = False
    
    if auth_config['auth_enabled'] and not auth_config['oauth_available'] and auth_config['require_oauth']:
        status['warnings'].append("Authentication enabled but no OAuth providers available - consider guest mode")
    
    return status

# Export main configuration function
__all__ = ['get_app_config', 'get_public_url', 'get_database_mode', 'get_auth_config', 'validate_environment']