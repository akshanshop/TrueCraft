"""
SQLAlchemy models for TrueCraft application.
Cross-database compatible models that work with both PostgreSQL and SQLite.
"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """User account information from OAuth providers"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    oauth_provider = Column(String(50), nullable=False)
    oauth_id = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    name = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    profile_data = Column(JSON, nullable=True)  # Works with both PostgreSQL JSONB and SQLite JSON
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, server_default=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="user", cascade="all, delete-orphan")
    profiles = relationship("Profile", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", foreign_keys="Message.sender_user_id")

class Product(Base):
    """Product listings by artisans"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)  # Decimal with 2 decimal places
    description = Column(Text, nullable=True)
    materials = Column(Text, nullable=True)
    dimensions = Column(String(255), nullable=True)
    weight = Column(Numeric(6, 2), nullable=True)
    stock_quantity = Column(Integer, default=0)
    shipping_cost = Column(Numeric(8, 2), default=0)
    processing_time = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)
    image_data = Column(Text, nullable=True)  # Base64 or file paths
    views = Column(Integer, default=0)
    favorites = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="products")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")

class Profile(Base):
    """Artisan profile information"""
    __tablename__ = 'profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    specialties = Column(Text, nullable=True)
    years_experience = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    instagram = Column(String(255), nullable=True)
    facebook = Column(String(255), nullable=True)
    etsy = Column(String(255), nullable=True)
    education = Column(Text, nullable=True)
    awards = Column(Text, nullable=True)
    inspiration = Column(Text, nullable=True)
    profile_image = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profiles")

class Review(Base):
    """Product reviews and ratings"""
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    approved = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="reviews")

class Message(Base):
    """Messages between buyers and sellers"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    sender_type = Column(String(10), nullable=False)  # 'buyer' or 'seller'
    sender_name = Column(String(255), nullable=False)
    sender_email = Column(String(255), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=True)
    subject = Column(String(500), nullable=False)
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="messages", foreign_keys=[sender_user_id])
    product = relationship("Product", back_populates="messages")

class Analytics(Base):
    """Analytics events for tracking user behavior"""
    __tablename__ = 'analytics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(100), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=True)
    user_session = Column(String(255), nullable=True)
    event_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid reserved word
    timestamp = Column(DateTime, server_default=func.now())

class Order(Base):
    """Customer orders"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=True)
    shipping_address = Column(Text, nullable=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    """Individual items within an order"""
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    quantity = Column(Integer, nullable=False)
    price_per_item = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

# Function to create all tables
def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)

def drop_tables(engine):
    """Drop all tables in the database (use with caution!)"""
    Base.metadata.drop_all(engine)

# Export the models and functions
__all__ = [
    'Base', 'User', 'Product', 'Profile', 'Review', 'Message', 
    'Analytics', 'Order', 'OrderItem', 'create_tables', 'drop_tables'
]