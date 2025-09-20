"""
Database factory for TrueCraft application.
Provides a factory pattern to switch between the old DatabaseManager and new DatabaseService.
"""
import os
from typing import Union

# Import configuration
try:
    from .config import get_app_config
except ImportError:
    def get_app_config():
        return {'database_mode': 'sqlite'}

# Import SQLAlchemy service
try:
    from .db_service import DatabaseService
    SQLALCHEMY_AVAILABLE = True
except Exception as e:
    print(f"SQLAlchemy service unavailable: {e}")
    SQLALCHEMY_AVAILABLE = False
    DatabaseService = None

def create_database_service():
    """
    Factory function to create the appropriate database service.
    Prefers SQLAlchemy service, with safe fallbacks.
    """
    # Try to use new SQLAlchemy service first
    if SQLALCHEMY_AVAILABLE and DatabaseService is not None:
        try:
            service = DatabaseService()
            if service.db_available:
                print("Using SQLAlchemy-based database service")
                return service
            else:
                print("SQLAlchemy service unavailable, trying fallbacks")
        except Exception as e:
            print(f"SQLAlchemy service failed to initialize: {str(e)}")
    
    # Try legacy DatabaseManager as fallback
    try:
        from .database_manager import DatabaseManager
        manager = DatabaseManager()
        if manager.db_available:
            print("Using legacy PostgreSQL database manager")
            return manager
        else:
            print("Legacy database manager unavailable")
    except Exception as e:
        print(f"Legacy database manager failed: {str(e)}")
    
    # Return a mock service if nothing works
    print("No database service available, using mock service for demo mode")
    return MockDatabaseService()

class MockDatabaseService:
    """
    Mock database service that provides empty results when no real database is available.
    Prevents the application from crashing when no database is configured.
    """
    
    def __init__(self):
        self.db_available = False
    
    def get_products(self, user_id=None):
        import pandas as pd
        return pd.DataFrame({
            'id': [], 'user_id': [], 'name': [], 'category': [], 'price': [], 'description': [], 'materials': [],
            'dimensions': [], 'weight': [], 'stock_quantity': [], 'shipping_cost': [],
            'processing_time': [], 'tags': [], 'image_data': [], 'views': [], 'favorites': [],
            'created_at': [], 'updated_at': []
        })
    
    def get_profiles(self):
        import pandas as pd
        return pd.DataFrame({
            'id': [], 'user_id': [], 'name': [], 'location': [], 'specialties': [], 'years_experience': [],
            'bio': [], 'email': [], 'phone': [], 'website': [], 'instagram': [],
            'facebook': [], 'etsy': [], 'education': [], 'awards': [], 'inspiration': [],
            'profile_image': [], 'created_at': [], 'updated_at': []
        })
    
    def add_product(self, product_data, user_id=None):
        import streamlit as st
        st.info("Demo mode: Product not saved (no database configured)")
        return True  # Return True to prevent UI errors
    
    def add_profile(self, profile_data, user_id=None):
        import streamlit as st
        st.info("Demo mode: Profile not saved (no database configured)")
        return True
    
    def update_product(self, product_id, updated_data):
        import streamlit as st
        st.info("Demo mode: Product not updated (no database configured)")
        return True
    
    def update_profile(self, profile_id, profile_data):
        import streamlit as st
        st.info("Demo mode: Profile not updated (no database configured)")
        return True
    
    def delete_product(self, product_id):
        import streamlit as st
        st.info("Demo mode: Product not deleted (no database configured)")
        return True
    
    def increment_views(self, product_id):
        return True  # Silent operation
    
    def increment_favorites(self, product_id):
        return True  # Silent operation
    
    def send_message(self, message_data):
        import streamlit as st
        st.info("Demo mode: Message not sent (no database configured)")
        return True
    
    def get_unread_message_count(self, email=None):
        return 0
    
    def get_analytics_summary(self):
        return {'total_events': 0, 'unique_sessions': 0, 'events_by_type': {}}
    
    def log_analytics_event(self, event_type, product_id=None, metadata=None):
        return True  # Silent operation
    
    def create_user(self, user_data):
        return None  # No user management in demo mode
    
    def get_user_by_id(self, user_id):
        return None  # No user management in demo mode
    
    def get_conversations(self, email=None, sender_type=None):
        return []  # No conversations in demo mode
    
    def mark_conversation_as_read(self, product_id, sender_email):
        return True  # Silent operation in demo mode
    
    def get_message_thread(self, product_id, participant_emails):
        return []  # No message threads in demo mode

def get_database_status():
    """Get information about the current database configuration and status"""
    config = get_app_config()
    
    status = {
        'config': config,
        'sqlalchemy_available': SQLALCHEMY_AVAILABLE,
        'legacy_db_available': True,  # Always try legacy as fallback
        'active_service': None,
        'connection_test': None
    }
    
    # Test which service is actually being used
    try:
        service = create_database_service()
        
        if DatabaseService is not None and isinstance(service, DatabaseService):
            status['active_service'] = 'SQLAlchemy'
            # Test database connection
            try:
                from .db_engine import test_database_connection
                status['connection_test'] = test_database_connection()
            except:
                status['connection_test'] = {'success': False, 'error': 'Connection test failed'}
                
        elif hasattr(service, 'database_url'):  # Legacy DatabaseManager
            status['active_service'] = 'Legacy PostgreSQL'
            status['connection_test'] = {
                'success': service.db_available,
                'mode': 'postgres',
                'info': {'type': 'PostgreSQL', 'configured': bool(getattr(service, 'database_url', None))}
            }
        else:
            status['active_service'] = 'Mock (Demo Mode)'
            status['connection_test'] = {
                'success': False,
                'mode': 'mock',
                'info': {'type': 'Mock Service', 'reason': 'No database configured'}
            }
    except Exception as e:
        status['active_service'] = 'Error'
        status['connection_test'] = {'success': False, 'error': str(e)}
    
    return status

# Export the factory function
__all__ = ['create_database_service', 'get_database_status', 'MockDatabaseService']