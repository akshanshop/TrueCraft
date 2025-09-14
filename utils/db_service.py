"""
SQLAlchemy-based Database Service for TrueCraft application.
Provides cross-database compatible database operations using SQLAlchemy.
"""
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text, desc, func, and_, or_
import streamlit as st

from .db_engine import create_db_engine, test_database_connection
from .db_models import (
    Base, User, Product, Profile, Review, Message, Analytics, Order, OrderItem,
    create_tables
)

class DatabaseService:
    """
    SQLAlchemy-based database service that works with both PostgreSQL and SQLite.
    Provides the same interface as the original DatabaseManager for compatibility.
    """
    
    def __init__(self):
        """Initialize the database service"""
        try:
            self.engine = create_db_engine()
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables if they don't exist
            create_tables(self.engine)
            
            # Test connection
            connection_test = test_database_connection()
            self.db_available = connection_test['success']
            
            if not self.db_available:
                print(f"Database connection failed: {connection_test.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Database service initialization failed: {str(e)}")
            self.db_available = False
            self.engine = None
            self.SessionLocal = None
    
    def get_session(self) -> Optional[Session]:
        """Get a database session"""
        if not self.db_available or not self.SessionLocal:
            return None
        try:
            return self.SessionLocal()
        except Exception as e:
            print(f"Failed to create database session: {str(e)}")
            return None
    
    # Product Management Methods
    def get_products(self, user_id: Optional[int] = None) -> pd.DataFrame:
        """Get all products as DataFrame, optionally filtered by user"""
        if not self.db_available:
            return self._empty_products_df()
        
        session = self.get_session()
        if not session:
            return self._empty_products_df()
        
        try:
            query = session.query(Product)
            if user_id:
                query = query.filter(Product.user_id == user_id)
            query = query.order_by(desc(Product.created_at))
            
            products = query.all()
            
            if not products:
                return self._empty_products_df()
            
            # Convert to DataFrame
            data = []
            for product in products:
                data.append({
                    'id': product.id,
                    'user_id': product.user_id,
                    'name': product.name,
                    'category': product.category,
                    'price': float(product.price) if product.price else 0.0,
                    'description': product.description,
                    'materials': product.materials,
                    'dimensions': product.dimensions,
                    'weight': float(product.weight) if product.weight else 0.0,
                    'stock_quantity': product.stock_quantity,
                    'shipping_cost': float(product.shipping_cost) if product.shipping_cost else 0.0,
                    'processing_time': product.processing_time,
                    'tags': product.tags,
                    'image_data': product.image_data,
                    'views': product.views,
                    'favorites': product.favorites,
                    'created_at': product.created_at,
                    'updated_at': product.updated_at
                })
            
            df = pd.DataFrame(data)
            # Ensure datetime columns are properly typed
            for col in ['created_at', 'updated_at']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
            
            return df
            
        except Exception as e:
            print(f"Error loading products: {str(e)}")
            return self._empty_products_df()
        finally:
            session.close()
    
    def add_product(self, product_data: Dict[str, Any], user_id: Optional[int] = None) -> bool:
        """Add a new product"""
        if not self.db_available:
            st.warning("Database unavailable - product not saved")
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            product = Product(
                user_id=user_id,
                name=product_data.get('name', ''),
                category=product_data.get('category', ''),
                price=product_data.get('price', 0),
                description=product_data.get('description', ''),
                materials=product_data.get('materials', ''),
                dimensions=product_data.get('dimensions', ''),
                weight=product_data.get('weight'),
                stock_quantity=product_data.get('stock_quantity', 0),
                shipping_cost=product_data.get('shipping_cost', 0),
                processing_time=product_data.get('processing_time', ''),
                tags=product_data.get('tags', ''),
                image_data=product_data.get('image_data', ''),
                views=product_data.get('views', 0),
                favorites=product_data.get('favorites', 0)
            )
            
            session.add(product)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            st.error(f"Error adding product: {str(e)}")
            return False
        finally:
            session.close()
    
    def update_product(self, product_id: int, updated_data: Dict[str, Any]) -> bool:
        """Update an existing product"""
        if not self.db_available:
            st.warning("Database unavailable - product not updated")
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return False
            
            # Update fields
            for key, value in updated_data.items():
                if key not in ['id', 'created_at'] and hasattr(product, key):
                    setattr(product, key, value)
            
            product.updated_at = datetime.now()
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            st.error(f"Error updating product: {str(e)}")
            return False
        finally:
            session.close()
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        if not self.db_available:
            st.warning("Database unavailable - product not deleted")
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                session.delete(product)
                session.commit()
                return True
            return False
            
        except Exception as e:
            session.rollback()
            st.error(f"Error deleting product: {str(e)}")
            return False
        finally:
            session.close()
    
    def increment_views(self, product_id: int) -> bool:
        """Increment view count for a product"""
        if not self.db_available:
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                product.views = (product.views or 0) + 1
                product.updated_at = datetime.now()
                session.commit()
                return True
            return False
            
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()
    
    def increment_favorites(self, product_id: int) -> bool:
        """Increment favorite count for a product"""
        if not self.db_available:
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                product.favorites = (product.favorites or 0) + 1
                product.updated_at = datetime.now()
                session.commit()
                return True
            return False
            
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()
    
    # Profile Management Methods
    def get_profiles(self) -> pd.DataFrame:
        """Get all artisan profiles as DataFrame"""
        if not self.db_available:
            return self._empty_profiles_df()
        
        session = self.get_session()
        if not session:
            return self._empty_profiles_df()
        
        try:
            profiles = session.query(Profile).order_by(desc(Profile.created_at)).all()
            
            if not profiles:
                return self._empty_profiles_df()
            
            # Convert to DataFrame
            data = []
            for profile in profiles:
                data.append({
                    'id': profile.id,
                    'user_id': profile.user_id,
                    'name': profile.name,
                    'location': profile.location,
                    'specialties': profile.specialties,
                    'years_experience': profile.years_experience,
                    'bio': profile.bio,
                    'email': profile.email,
                    'phone': profile.phone,
                    'website': profile.website,
                    'instagram': profile.instagram,
                    'facebook': profile.facebook,
                    'etsy': profile.etsy,
                    'education': profile.education,
                    'awards': profile.awards,
                    'inspiration': profile.inspiration,
                    'profile_image': profile.profile_image,
                    'created_at': profile.created_at,
                    'updated_at': profile.updated_at
                })
            
            df = pd.DataFrame(data)
            # Ensure datetime columns are properly typed
            for col in ['created_at', 'updated_at']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
            
            return df
            
        except Exception as e:
            print(f"Error loading profiles: {str(e)}")
            return self._empty_profiles_df()
        finally:
            session.close()
    
    def add_profile(self, profile_data: Dict[str, Any], user_id: Optional[int] = None) -> bool:
        """Add a new artisan profile"""
        if not self.db_available:
            st.warning("Database unavailable - profile not saved")
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            profile = Profile(
                user_id=user_id,
                name=profile_data.get('name', ''),
                location=profile_data.get('location', ''),
                specialties=profile_data.get('specialties', ''),
                years_experience=profile_data.get('years_experience'),
                bio=profile_data.get('bio', ''),
                email=profile_data.get('email', ''),
                phone=profile_data.get('phone', ''),
                website=profile_data.get('website', ''),
                instagram=profile_data.get('instagram', ''),
                facebook=profile_data.get('facebook', ''),
                etsy=profile_data.get('etsy', ''),
                education=profile_data.get('education', ''),
                awards=profile_data.get('awards', ''),
                inspiration=profile_data.get('inspiration', ''),
                profile_image=profile_data.get('profile_image', '')
            )
            
            session.add(profile)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            st.error(f"Error adding profile: {str(e)}")
            return False
        finally:
            session.close()
    
    def update_profile(self, profile_id: int, profile_data: Dict[str, Any]) -> bool:
        """Update existing artisan profile"""
        if not self.db_available:
            st.warning("Database unavailable - profile not updated")
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            profile = session.query(Profile).filter(Profile.id == profile_id).first()
            if not profile:
                return False
            
            # Update fields
            for key, value in profile_data.items():
                if key not in ['id', 'created_at'] and hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.updated_at = datetime.now()
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            st.error(f"Error updating profile: {str(e)}")
            return False
        finally:
            session.close()
    
    # User Management Methods
    def create_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """Create or update a user from OAuth data"""
        if not self.db_available:
            return None
        
        session = self.get_session()
        if not session:
            return None
        
        try:
            # Check if user already exists
            user = session.query(User).filter(
                and_(
                    User.oauth_provider == user_data['oauth_provider'],
                    User.oauth_id == user_data['oauth_id']
                )
            ).first()
            
            if user:
                # Update existing user
                user.name = user_data.get('name', user.name)
                user.email = user_data.get('email', user.email)
                user.avatar_url = user_data.get('avatar_url', user.avatar_url)
                user.profile_data = user_data.get('profile_data', user.profile_data)
                user.last_login = datetime.now()
                user.updated_at = datetime.now()
            else:
                # Create new user
                user = User(
                    oauth_provider=user_data['oauth_provider'],
                    oauth_id=user_data['oauth_id'],
                    email=user_data.get('email'),
                    name=user_data['name'],
                    avatar_url=user_data.get('avatar_url'),
                    profile_data=user_data.get('profile_data'),
                    last_login=datetime.now()
                )
                session.add(user)
            
            session.commit()
            return user.id
            
        except Exception as e:
            session.rollback()
            print(f"Error creating/updating user: {str(e)}")
            return None
        finally:
            session.close()
    
    # Analytics Methods
    def log_analytics_event(self, event_type: str, product_id: Optional[int] = None, metadata: Optional[Dict] = None) -> bool:
        """Log analytics events"""
        if not self.db_available:
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            user_session = st.session_state.get('session_id', 'anonymous')
            analytics = Analytics(
                event_type=event_type,
                product_id=product_id,
                user_session=user_session,
                event_metadata=metadata
            )
            
            session.add(analytics)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        if not self.db_available:
            return {'total_events': 0, 'unique_sessions': 0, 'events_by_type': {}}
        
        session = self.get_session()
        if not session:
            return {'total_events': 0, 'unique_sessions': 0, 'events_by_type': {}}
        
        try:
            # Total events
            total_events = session.query(Analytics).count()
            
            # Unique sessions
            unique_sessions = session.query(Analytics.user_session).distinct().count()
            
            # Events by type
            events_by_type = {}
            event_type_counts = session.query(
                Analytics.event_type,
                func.count(Analytics.id)
            ).group_by(Analytics.event_type).all()
            
            for event_type, count in event_type_counts:
                events_by_type[event_type] = count
            
            return {
                'total_events': total_events,
                'unique_sessions': unique_sessions,
                'events_by_type': events_by_type
            }
            
        except Exception as e:
            print(f"Error getting analytics summary: {str(e)}")
            return {'total_events': 0, 'unique_sessions': 0, 'events_by_type': {}}
        finally:
            session.close()
    
    # Message Management Methods
    def send_message(self, message_data: Dict[str, Any]) -> bool:
        """Send a message"""
        if not self.db_available:
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            message = Message(
                sender_user_id=message_data.get('sender_user_id'),
                sender_type=message_data.get('sender_type', 'buyer'),
                sender_name=message_data['sender_name'],
                sender_email=message_data['sender_email'],
                product_id=message_data.get('product_id'),
                subject=message_data['subject'],
                message_content=message_data['message_content'],
                is_read=message_data.get('is_read', False)
            )
            
            session.add(message)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            st.error(f"Error sending message: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_unread_message_count(self, email: Optional[str] = None) -> int:
        """Get count of unread messages for a user"""
        if not self.db_available:
            return 0
        
        session = self.get_session()
        if not session:
            return 0
        
        try:
            query = session.query(Message).filter(Message.is_read == False)
            
            if email:
                # Count messages NOT from this email (messages TO this user)
                query = query.filter(Message.sender_email != email)
            
            count = query.count()
            return count
            
        except Exception as e:
            print(f"Error getting unread message count: {str(e)}")
            return 0
        finally:
            session.close()
    
    # User Management Methods
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        if not self.db_available:
            return None
        
        session = self.get_session()
        if not session:
            return None
        
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                return {
                    'id': user.id,
                    'oauth_provider': user.oauth_provider,
                    'oauth_id': user.oauth_id,
                    'email': user.email,
                    'name': user.name,
                    'avatar_url': user.avatar_url,
                    'profile_data': user.profile_data,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at,
                    'last_login': user.last_login
                }
            return None
        except Exception as e:
            print(f"Error getting user by ID: {str(e)}")
            return None
        finally:
            session.close()
    
    # Conversation Management Methods
    def get_conversations(self, email: Optional[str] = None, sender_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get conversations grouped by product and participants"""
        if not self.db_available:
            return []
        
        session = self.get_session()
        if not session:
            return []
        
        try:
            # Build the query with joins
            query = session.query(
                Message.product_id,
                Product.name.label('product_name'),
                Message.sender_email,
                Message.sender_name,
                Message.sender_type,
                func.count().label('message_count'),
                func.max(Message.timestamp).label('last_message_time'),
                func.sum(
                    func.case(
                        (Message.is_read == False, 1),
                        else_=0
                    )
                ).label('unread_count'),
                func.string_agg(func.distinct(Message.subject), '; ').label('subjects')
            ).join(Product, Message.product_id == Product.id)
            
            # Apply filters
            if email:
                query = query.filter(Message.sender_email == email)
            
            if sender_type:
                query = query.filter(Message.sender_type == sender_type)
            
            # Group and order
            query = query.group_by(
                Message.product_id,
                Product.name,
                Message.sender_email,
                Message.sender_name,
                Message.sender_type
            ).order_by(desc('last_message_time'))
            
            results = query.all()
            
            conversations = []
            for result in results:
                conversations.append({
                    'product_id': result.product_id,
                    'product_name': result.product_name,
                    'sender_email': result.sender_email,
                    'sender_name': result.sender_name,
                    'sender_type': result.sender_type,
                    'message_count': result.message_count,
                    'last_message_time': result.last_message_time,
                    'unread_count': result.unread_count or 0,
                    'subjects': result.subjects or ''
                })
            
            return conversations
            
        except Exception as e:
            print(f"Error getting conversations: {str(e)}")
            return []
        finally:
            session.close()
    
    def mark_conversation_as_read(self, product_id: int, sender_email: str) -> bool:
        """Mark all messages in a conversation as read"""
        if not self.db_available:
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            messages = session.query(Message).filter(
                and_(
                    Message.product_id == product_id,
                    Message.sender_email == sender_email
                )
            ).all()
            
            for message in messages:
                message.is_read = True
                message.updated_at = datetime.now()
            
            session.commit()
            return True
            
        except Exception as e:
            print(f"Error marking conversation as read: {str(e)}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_message_thread(self, product_id: int, participant_emails: List[str]) -> List[Dict[str, Any]]:
        """Get message thread between specific participants for a product"""
        if not self.db_available:
            return []
        
        session = self.get_session()
        if not session:
            return []
        
        try:
            messages = session.query(Message, Product.name.label('product_name')).join(
                Product, Message.product_id == Product.id
            ).filter(
                and_(
                    Message.product_id == product_id,
                    Message.sender_email.in_(participant_emails)
                )
            ).order_by(Message.timestamp.asc()).all()
            
            thread = []
            for message, product_name in messages:
                thread.append({
                    'id': message.id,
                    'sender_type': message.sender_type,
                    'sender_name': message.sender_name,
                    'sender_email': message.sender_email,
                    'product_id': message.product_id,
                    'product_name': product_name,
                    'subject': message.subject,
                    'message_content': message.message_content,
                    'is_read': message.is_read,
                    'timestamp': message.timestamp,
                    'created_at': message.created_at,
                    'updated_at': message.updated_at
                })
            
            return thread
            
        except Exception as e:
            print(f"Error getting message thread: {str(e)}")
            return []
        finally:
            session.close()
    
    # Helper methods for empty DataFrames
    def _empty_products_df(self) -> pd.DataFrame:
        """Return empty products DataFrame with expected columns"""
        return pd.DataFrame({
            'id': [], 'user_id': [], 'name': [], 'category': [], 'price': [], 'description': [], 'materials': [],
            'dimensions': [], 'weight': [], 'stock_quantity': [], 'shipping_cost': [],
            'processing_time': [], 'tags': [], 'image_data': [], 'views': [], 'favorites': [],
            'created_at': [], 'updated_at': []
        })
    
    def _empty_profiles_df(self) -> pd.DataFrame:
        """Return empty profiles DataFrame with expected columns"""
        return pd.DataFrame({
            'id': [], 'user_id': [], 'name': [], 'location': [], 'specialties': [], 'years_experience': [],
            'bio': [], 'email': [], 'phone': [], 'website': [], 'instagram': [],
            'facebook': [], 'etsy': [], 'education': [], 'awards': [], 'inspiration': [],
            'profile_image': [], 'created_at': [], 'updated_at': []
        })

# Export the service
__all__ = ['DatabaseService']