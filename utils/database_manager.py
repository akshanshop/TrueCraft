import os
import psycopg2
import pandas as pd
import json
from datetime import datetime
import streamlit as st
from psycopg2.extras import RealDictCursor

class DatabaseManager:
    def __init__(self):
        """Initialize database manager with PostgreSQL connection"""
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            st.error("Database connection not configured")
            raise Exception("DATABASE_URL not found")
        self.initialize_schema()
    
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            raise
    
    def initialize_schema(self):
        """Initialize database schema - ensure all required tables exist"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Create users table first (referenced by other tables)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            oauth_provider VARCHAR(50) NOT NULL,
                            oauth_id VARCHAR(255) NOT NULL,
                            email VARCHAR(255) UNIQUE,
                            name VARCHAR(255) NOT NULL,
                            avatar_url TEXT,
                            profile_data JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(oauth_provider, oauth_id)
                        )
                    """)
                    
                    # Create products table with user relationship
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS products (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            name VARCHAR(255) NOT NULL,
                            category VARCHAR(100) NOT NULL,
                            price DECIMAL(10,2) NOT NULL,
                            description TEXT,
                            materials TEXT,
                            dimensions VARCHAR(255),
                            weight DECIMAL(6,2),
                            stock_quantity INTEGER DEFAULT 0,
                            shipping_cost DECIMAL(8,2) DEFAULT 0,
                            processing_time VARCHAR(100),
                            tags TEXT,
                            image_data TEXT,
                            views INTEGER DEFAULT 0,
                            favorites INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create profiles table with user relationship
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS profiles (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            name VARCHAR(255) NOT NULL,
                            location VARCHAR(255),
                            specialties TEXT,
                            years_experience INTEGER,
                            bio TEXT,
                            email VARCHAR(255),
                            phone VARCHAR(50),
                            website VARCHAR(255),
                            instagram VARCHAR(255),
                            facebook VARCHAR(255),
                            etsy VARCHAR(255),
                            education TEXT,
                            awards TEXT,
                            inspiration TEXT,
                            profile_image TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create reviews table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS reviews (
                            id SERIAL PRIMARY KEY,
                            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                            customer_name VARCHAR(255) NOT NULL,
                            customer_email VARCHAR(255) NOT NULL,
                            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                            comment TEXT,
                            approved BOOLEAN DEFAULT TRUE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create messages table with user relationship
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS messages (
                            id SERIAL PRIMARY KEY,
                            sender_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                            sender_type VARCHAR(10) NOT NULL CHECK (sender_type IN ('buyer', 'seller')),
                            sender_name VARCHAR(255) NOT NULL,
                            sender_email VARCHAR(255) NOT NULL,
                            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                            subject VARCHAR(500) NOT NULL,
                            message_content TEXT NOT NULL,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            is_read BOOLEAN DEFAULT FALSE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create analytics table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS analytics (
                            id SERIAL PRIMARY KEY,
                            event_type VARCHAR(100) NOT NULL,
                            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                            user_session VARCHAR(255),
                            metadata JSONB,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create orders table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS orders (
                            id SERIAL PRIMARY KEY,
                            customer_name VARCHAR(255) NOT NULL,
                            customer_email VARCHAR(255) NOT NULL,
                            customer_phone VARCHAR(50),
                            shipping_address TEXT,
                            total_amount DECIMAL(10,2) NOT NULL,
                            status VARCHAR(50) DEFAULT 'pending',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create order_items table
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS order_items (
                            id SERIAL PRIMARY KEY,
                            order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                            product_id INTEGER REFERENCES products(id),
                            quantity INTEGER NOT NULL,
                            price_per_item DECIMAL(10,2) NOT NULL,
                            total_price DECIMAL(10,2) NOT NULL
                        )
                    """)
                    
                    # Add indexes for performance
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_user_id ON products(user_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sender_user_id ON messages(sender_user_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE email IS NOT NULL")
                    
                    conn.commit()
        except Exception as e:
            # Don't show error to user if it's just schema initialization
            print(f"Schema initialization note: {str(e)}")
    
    # Product Management
    def get_products(self, user_id=None):
        """Get all products as DataFrame, optionally filtered by user"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if user_id:
                        cursor.execute("""
                            SELECT * FROM products 
                            WHERE user_id = %s
                            ORDER BY created_at DESC
                        """, (user_id,))
                    else:
                        cursor.execute("""
                            SELECT * FROM products 
                            ORDER BY created_at DESC
                        """)
                    rows = cursor.fetchall()
                    
                    if rows:
                        df = pd.DataFrame([dict(row) for row in rows])
                        # Ensure datetime columns are properly typed
                        if 'created_at' in df.columns:
                            df['created_at'] = pd.to_datetime(df['created_at'])
                        if 'updated_at' in df.columns:
                            df['updated_at'] = pd.to_datetime(df['updated_at'])
                        # Ensure price is numeric
                        if 'price' in df.columns:
                            df['price'] = pd.to_numeric(df['price'], errors='coerce')
                        return df
                    else:
                        # Return empty DataFrame with expected columns
                        return pd.DataFrame({
                            'id': [], 'name': [], 'category': [], 'price': [], 'description': [], 'materials': [],
                            'dimensions': [], 'weight': [], 'stock_quantity': [], 'shipping_cost': [],
                            'processing_time': [], 'tags': [], 'image_data': [], 'views': [], 'favorites': [],
                            'created_at': [], 'updated_at': []
                        })
        except Exception as e:
            st.error(f"Error loading products: {str(e)}")
            return pd.DataFrame()
    
    def add_product(self, product_data, user_id=None):
        """Add a new product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    product_data_with_user = {**product_data, 'user_id': user_id}
                    cursor.execute("""
                        INSERT INTO products (
                            user_id, name, category, price, description, materials, dimensions,
                            weight, stock_quantity, shipping_cost, processing_time,
                            tags, image_data, views, favorites
                        ) VALUES (
                            %(user_id)s, %(name)s, %(category)s, %(price)s, %(description)s, %(materials)s,
                            %(dimensions)s, %(weight)s, %(stock_quantity)s, %(shipping_cost)s,
                            %(processing_time)s, %(tags)s, %(image_data)s, %(views)s, %(favorites)s
                        )
                    """, product_data_with_user)
                    conn.commit()
                    return True
        except Exception as e:
            st.error(f"Error adding product: {str(e)}")
            return False
    
    def update_product(self, product_id, updated_data):
        """Update an existing product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Build dynamic update query
                    set_clauses = []
                    values = {}
                    
                    for key, value in updated_data.items():
                        if key != 'id':  # Don't update the ID
                            set_clauses.append(f"{key} = %({key})s")
                            values[key] = value
                    
                    values['id'] = product_id
                    values['updated_at'] = datetime.now()
                    set_clauses.append("updated_at = %(updated_at)s")
                    
                    query = f"UPDATE products SET {', '.join(set_clauses)} WHERE id = %(id)s"
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error updating product: {str(e)}")
            return False
    
    def delete_product(self, product_id):
        """Delete a product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error deleting product: {str(e)}")
            return False
    
    def increment_views(self, product_id):
        """Increment view count for a product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE products 
                        SET views = views + 1, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    """, (product_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error incrementing views: {str(e)}")
            return False
    
    def increment_favorites(self, product_id):
        """Increment favorite count for a product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE products 
                        SET favorites = favorites + 1, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    """, (product_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error incrementing favorites: {str(e)}")
            return False
    
    # Profile Management
    def get_profiles(self):
        """Get all artisan profiles as DataFrame"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM profiles 
                        ORDER BY created_at DESC
                    """)
                    rows = cursor.fetchall()
                    
                    if rows:
                        df = pd.DataFrame([dict(row) for row in rows])
                        # Ensure datetime columns are properly typed
                        for col in ['created_at', 'updated_at']:
                            if col in df.columns:
                                df[col] = pd.to_datetime(df[col])
                        return df
                    else:
                        # Return empty DataFrame with expected columns
                        return pd.DataFrame({
                            'id': [], 'name': [], 'location': [], 'specialties': [], 'years_experience': [],
                            'bio': [], 'email': [], 'phone': [], 'website': [], 'instagram': [],
                            'facebook': [], 'etsy': [], 'education': [], 'awards': [], 'inspiration': [],
                            'profile_image': [], 'created_at': [], 'updated_at': []
                        })
        except Exception as e:
            st.error(f"Error loading profiles: {str(e)}")
            return pd.DataFrame()
    
    def add_profile(self, profile_data):
        """Add a new artisan profile"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO profiles (
                            name, location, specialties, years_experience, bio,
                            email, phone, website, instagram, facebook, etsy,
                            education, awards, inspiration, profile_image
                        ) VALUES (
                            %(name)s, %(location)s, %(specialties)s, %(years_experience)s, %(bio)s,
                            %(email)s, %(phone)s, %(website)s, %(instagram)s, %(facebook)s, %(etsy)s,
                            %(education)s, %(awards)s, %(inspiration)s, %(profile_image)s
                        )
                    """, profile_data)
                    conn.commit()
                    return True
        except Exception as e:
            st.error(f"Error adding profile: {str(e)}")
            return False
    
    def update_profile(self, profile_id, profile_data):
        """Update existing artisan profile"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Build dynamic update query
                    set_clauses = []
                    values = {}
                    
                    for key, value in profile_data.items():
                        if key not in ['id', 'created_at']:  # Don't update ID or created_at
                            set_clauses.append(f"{key} = %({key})s")
                            values[key] = value
                    
                    values['id'] = profile_id
                    values['updated_at'] = datetime.now()
                    set_clauses.append("updated_at = %(updated_at)s")
                    
                    query = f"UPDATE profiles SET {', '.join(set_clauses)} WHERE id = %(id)s"
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error updating profile: {str(e)}")
            return False
    
    # Analytics and Tracking
    def log_analytics_event(self, event_type, product_id=None, metadata=None):
        """Log analytics events"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    user_session = st.session_state.get('session_id', 'anonymous')
                    cursor.execute("""
                        INSERT INTO analytics (event_type, product_id, user_session, metadata)
                        VALUES (%s, %s, %s, %s)
                    """, (event_type, product_id, user_session, json.dumps(metadata) if metadata else None))
                    conn.commit()
                    return True
        except Exception as e:
            st.error(f"Error logging analytics: {str(e)}")
            return False
    
    def get_analytics_summary(self):
        """Get analytics summary data"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get basic metrics
                    cursor.execute("SELECT COUNT(*) as total_products FROM products")
                    result = cursor.fetchone()
                    total_products = result['total_products'] if result else 0
                    
                    cursor.execute("SELECT COALESCE(SUM(views), 0) as total_views FROM products")
                    result = cursor.fetchone()
                    total_views = result['total_views'] if result else 0
                    
                    cursor.execute("SELECT COALESCE(SUM(favorites), 0) as total_favorites FROM products")
                    result = cursor.fetchone()
                    total_favorites = result['total_favorites'] if result else 0
                    
                    cursor.execute("SELECT COALESCE(AVG(price), 0) as avg_price FROM products")
                    result = cursor.fetchone()
                    avg_price = result['avg_price'] if result else 0
                    
                    return {
                        'total_products': total_products,
                        'total_views': int(total_views),
                        'total_favorites': int(total_favorites),
                        'avg_price': float(avg_price) if avg_price else 0,
                        'top_categories': {},
                        'recent_searches': []
                    }
        except Exception as e:
            st.error(f"Error getting analytics summary: {str(e)}")
            return {}
    
    # Review Management
    def add_review(self, review_data):
        """Add a customer review"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Validate rating is between 1-5
                    rating = review_data.get('rating', 0)
                    if rating < 1 or rating > 5:
                        st.error("Rating must be between 1 and 5 stars")
                        return False
                    
                    cursor.execute("""
                        INSERT INTO reviews (product_id, customer_name, customer_email, rating, comment, approved)
                        VALUES (%(product_id)s, %(customer_name)s, %(customer_email)s, %(rating)s, %(comment)s, %(approved)s)
                        RETURNING id
                    """, {
                        **review_data,
                        'approved': review_data.get('approved', True)  # Default to approved
                    })
                    result = cursor.fetchone()
                    review_id = result[0] if result else None
                    conn.commit()
                    return review_id
        except Exception as e:
            st.error(f"Error adding review: {str(e)}")
            return False
    
    def get_product_reviews(self, product_id, include_unapproved=False):
        """Get reviews for a specific product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if include_unapproved:
                        cursor.execute("""
                            SELECT * FROM reviews 
                            WHERE product_id = %s
                            ORDER BY created_at DESC
                        """, (product_id,))
                    else:
                        cursor.execute("""
                            SELECT * FROM reviews 
                            WHERE product_id = %s AND approved = true
                            ORDER BY created_at DESC
                        """, (product_id,))
                    rows = cursor.fetchall()
                    
                    reviews = []
                    for row in rows:
                        review = dict(row)
                        # Ensure datetime columns are properly formatted
                        if review.get('created_at'):
                            review['created_at'] = pd.to_datetime(review['created_at'])
                        if review.get('updated_at'):
                            review['updated_at'] = pd.to_datetime(review['updated_at'])
                        reviews.append(review)
                    
                    return reviews
        except Exception as e:
            st.error(f"Error loading reviews: {str(e)}")
            return []
    
    def get_average_rating(self, product_id):
        """Get average rating for a product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            COALESCE(AVG(rating), 0) as avg_rating,
                            COUNT(*) as total_reviews,
                            COUNT(CASE WHEN rating = 5 THEN 1 END) as five_star,
                            COUNT(CASE WHEN rating = 4 THEN 1 END) as four_star,
                            COUNT(CASE WHEN rating = 3 THEN 1 END) as three_star,
                            COUNT(CASE WHEN rating = 2 THEN 1 END) as two_star,
                            COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star
                        FROM reviews 
                        WHERE product_id = %s AND approved = true
                    """, (product_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        return {
                            'average_rating': float(result['avg_rating']),
                            'total_reviews': int(result['total_reviews']),
                            'rating_distribution': {
                                '5': int(result['five_star']),
                                '4': int(result['four_star']),
                                '3': int(result['three_star']),
                                '2': int(result['two_star']),
                                '1': int(result['one_star'])
                            }
                        }
                    return {'average_rating': 0, 'total_reviews': 0, 'rating_distribution': {}}
        except Exception as e:
            st.error(f"Error calculating average rating: {str(e)}")
            return {'average_rating': 0, 'total_reviews': 0, 'rating_distribution': {}}
    
    def update_review(self, review_id, review_data):
        """Update an existing review"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Validate rating if provided
                    if 'rating' in review_data:
                        rating = review_data['rating']
                        if rating < 1 or rating > 5:
                            st.error("Rating must be between 1 and 5 stars")
                            return False
                    
                    # Build dynamic update query
                    set_clauses = []
                    values = {}
                    
                    for key, value in review_data.items():
                        if key not in ['id', 'created_at']:  # Don't update ID or created_at
                            set_clauses.append(f"{key} = %({key})s")
                            values[key] = value
                    
                    values['id'] = review_id
                    values['updated_at'] = datetime.now()
                    set_clauses.append("updated_at = %(updated_at)s")
                    
                    query = f"UPDATE reviews SET {', '.join(set_clauses)} WHERE id = %(id)s"
                    cursor.execute(query, values)
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error updating review: {str(e)}")
            return False
    
    def delete_review(self, review_id):
        """Delete a review"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error deleting review: {str(e)}")
            return False
    
    # Order Management (for next phase)
    def create_order(self, order_data, order_items):
        """Create a new order with items"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Insert order
                    cursor.execute("""
                        INSERT INTO orders (customer_name, customer_email, customer_phone, 
                                          shipping_address, total_amount)
                        VALUES (%(customer_name)s, %(customer_email)s, %(customer_phone)s,
                               %(shipping_address)s, %(total_amount)s)
                        RETURNING id
                    """, order_data)
                    result = cursor.fetchone()
                    order_id = result[0] if result else None
                    
                    # Insert order items
                    for item in order_items:
                        item['order_id'] = order_id
                        cursor.execute("""
                            INSERT INTO order_items (order_id, product_id, quantity, price_per_item, total_price)
                            VALUES (%(order_id)s, %(product_id)s, %(quantity)s, %(price_per_item)s, %(total_price)s)
                        """, item)
                    
                    conn.commit()
                    return order_id
        except Exception as e:
            st.error(f"Error creating order: {str(e)}")
            return None
    
    def get_orders(self):
        """Get all orders"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT o.*, 
                               COUNT(oi.id) as item_count,
                               ARRAY_AGG(p.name) as product_names
                        FROM orders o
                        LEFT JOIN order_items oi ON o.id = oi.order_id
                        LEFT JOIN products p ON oi.product_id = p.id
                        GROUP BY o.id
                        ORDER BY o.created_at DESC
                    """)
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            st.error(f"Error loading orders: {str(e)}")
            return []
    
    # User Management
    def create_user(self, oauth_provider, oauth_id, email, name, avatar_url=None, profile_data=None):
        """Create a new user from OAuth data"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO users (oauth_provider, oauth_id, email, name, avatar_url, profile_data)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (oauth_provider, oauth_id) 
                        DO UPDATE SET 
                            email = EXCLUDED.email,
                            name = EXCLUDED.name,
                            avatar_url = EXCLUDED.avatar_url,
                            profile_data = EXCLUDED.profile_data,
                            last_login = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        RETURNING id
                    """, (oauth_provider, oauth_id, email, name, avatar_url, json.dumps(profile_data) if profile_data else None))
                    result = cursor.fetchone()
                    user_id = result[0] if result else None
                    conn.commit()
                    return user_id
        except Exception as e:
            st.error(f"Error creating/updating user: {str(e)}")
            return None
    
    def get_user_by_oauth(self, oauth_provider, oauth_id):
        """Get user by OAuth provider and ID"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM users 
                        WHERE oauth_provider = %s AND oauth_id = %s
                    """, (oauth_provider, oauth_id))
                    row = cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            st.error(f"Error getting user: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                    row = cursor.fetchone()
                    return dict(row) if row else None
        except Exception as e:
            st.error(f"Error getting user: {str(e)}")
            return None
    
    # Messaging System
    def send_message(self, message_data):
        """Send a message between buyer and seller"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Validate sender_type
                    sender_type = message_data.get('sender_type', '')
                    if sender_type not in ['buyer', 'seller']:
                        st.error("Sender type must be 'buyer' or 'seller'")
                        return False
                    
                    cursor.execute("""
                        INSERT INTO messages (
                            sender_type, sender_name, sender_email, product_id,
                            subject, message_content
                        ) VALUES (
                            %(sender_type)s, %(sender_name)s, %(sender_email)s, %(product_id)s,
                            %(subject)s, %(message_content)s
                        ) RETURNING id
                    """, message_data)
                    result = cursor.fetchone()
                    message_id = result[0] if result else None
                    conn.commit()
                    return message_id
        except Exception as e:
            st.error(f"Error sending message: {str(e)}")
            return False
    
    def get_messages_for_product(self, product_id, sender_email=None):
        """Get all messages related to a specific product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if sender_email:
                        cursor.execute("""
                            SELECT * FROM messages 
                            WHERE product_id = %s AND sender_email = %s
                            ORDER BY timestamp DESC
                        """, (product_id, sender_email))
                    else:
                        cursor.execute("""
                            SELECT * FROM messages 
                            WHERE product_id = %s
                            ORDER BY timestamp DESC
                        """, (product_id,))
                    
                    rows = cursor.fetchall()
                    messages = []
                    for row in rows:
                        message = dict(row)
                        # Format timestamp
                        if message.get('timestamp'):
                            message['timestamp'] = pd.to_datetime(message['timestamp'])
                        if message.get('created_at'):
                            message['created_at'] = pd.to_datetime(message['created_at'])
                        if message.get('updated_at'):
                            message['updated_at'] = pd.to_datetime(message['updated_at'])
                        messages.append(message)
                    
                    return messages
        except Exception as e:
            st.error(f"Error loading messages: {str(e)}")
            return []
    
    def get_conversations(self, email=None, sender_type=None):
        """Get conversations grouped by product and participants"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    base_query = """
                        SELECT 
                            m.product_id,
                            p.name as product_name,
                            m.sender_email,
                            m.sender_name,
                            m.sender_type,
                            COUNT(*) as message_count,
                            MAX(m.timestamp) as last_message_time,
                            COUNT(CASE WHEN NOT m.is_read THEN 1 END) as unread_count,
                            STRING_AGG(DISTINCT m.subject, '; ' ORDER BY m.timestamp DESC) as subjects
                        FROM messages m
                        JOIN products p ON m.product_id = p.id
                    """
                    
                    conditions = []
                    params = []
                    
                    if email:
                        conditions.append("m.sender_email = %s")
                        params.append(email)
                    
                    if sender_type:
                        conditions.append("m.sender_type = %s")
                        params.append(sender_type)
                    
                    if conditions:
                        base_query += " WHERE " + " AND ".join(conditions)
                    
                    base_query += """
                        GROUP BY m.product_id, p.name, m.sender_email, m.sender_name, m.sender_type
                        ORDER BY last_message_time DESC
                    """
                    
                    cursor.execute(base_query, params)
                    rows = cursor.fetchall()
                    
                    conversations = []
                    for row in rows:
                        conversation = dict(row)
                        if conversation.get('last_message_time'):
                            conversation['last_message_time'] = pd.to_datetime(conversation['last_message_time'])
                        conversations.append(conversation)
                    
                    return conversations
        except Exception as e:
            st.error(f"Error loading conversations: {str(e)}")
            return []
    
    def mark_message_as_read(self, message_id):
        """Mark a specific message as read"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE messages 
                        SET is_read = true, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (message_id,))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error marking message as read: {str(e)}")
            return False
    
    def mark_conversation_as_read(self, product_id, sender_email):
        """Mark all messages in a conversation as read"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE messages 
                        SET is_read = true, updated_at = CURRENT_TIMESTAMP
                        WHERE product_id = %s AND sender_email = %s
                    """, (product_id, sender_email))
                    conn.commit()
                    return cursor.rowcount > 0
        except Exception as e:
            st.error(f"Error marking conversation as read: {str(e)}")
            return False
    
    def get_message_thread(self, product_id, participant_emails):
        """Get message thread between specific participants for a product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT m.*, p.name as product_name
                        FROM messages m
                        JOIN products p ON m.product_id = p.id
                        WHERE m.product_id = %s AND m.sender_email = ANY(%s)
                        ORDER BY m.timestamp ASC
                    """, (product_id, participant_emails))
                    
                    rows = cursor.fetchall()
                    messages = []
                    for row in rows:
                        message = dict(row)
                        if message.get('timestamp'):
                            message['timestamp'] = pd.to_datetime(message['timestamp'])
                        if message.get('created_at'):
                            message['created_at'] = pd.to_datetime(message['created_at'])
                        if message.get('updated_at'):
                            message['updated_at'] = pd.to_datetime(message['updated_at'])
                        messages.append(message)
                    
                    return messages
        except Exception as e:
            st.error(f"Error loading message thread: {str(e)}")
            return []
    
    def get_unread_message_count(self, email=None):
        """Get count of unread messages for a user"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if email:
                        cursor.execute("""
                            SELECT COUNT(*) as unread_count
                            FROM messages 
                            WHERE sender_email != %s AND is_read = false
                        """, (email,))  # Count messages NOT from this email (messages TO this user)
                    else:
                        cursor.execute("""
                            SELECT COUNT(*) as unread_count
                            FROM messages 
                            WHERE is_read = false
                        """)
                    
                    result = cursor.fetchone()
                    return int(result['unread_count']) if result else 0
        except Exception as e:
            st.error(f"Error getting unread message count: {str(e)}")
            return 0