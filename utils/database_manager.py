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
    
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(self.database_url)
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            raise
    
    # Product Management
    def get_products(self):
        """Get all products as DataFrame"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
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
                        return pd.DataFrame(columns=[
                            'id', 'name', 'category', 'price', 'description', 'materials',
                            'dimensions', 'weight', 'stock_quantity', 'shipping_cost',
                            'processing_time', 'tags', 'image_data', 'views', 'favorites',
                            'created_at', 'updated_at'
                        ])
        except Exception as e:
            st.error(f"Error loading products: {str(e)}")
            return pd.DataFrame()
    
    def add_product(self, product_data):
        """Add a new product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO products (
                            name, category, price, description, materials, dimensions,
                            weight, stock_quantity, shipping_cost, processing_time,
                            tags, image_data, views, favorites
                        ) VALUES (
                            %(name)s, %(category)s, %(price)s, %(description)s, %(materials)s,
                            %(dimensions)s, %(weight)s, %(stock_quantity)s, %(shipping_cost)s,
                            %(processing_time)s, %(tags)s, %(image_data)s, %(views)s, %(favorites)s
                        )
                    """, product_data)
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
                        return pd.DataFrame(columns=[
                            'id', 'name', 'location', 'specialties', 'years_experience',
                            'bio', 'email', 'phone', 'website', 'instagram',
                            'facebook', 'etsy', 'education', 'awards', 'inspiration',
                            'profile_image', 'created_at', 'updated_at'
                        ])
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
                    total_products = cursor.fetchone()['total_products']
                    
                    cursor.execute("SELECT COALESCE(SUM(views), 0) as total_views FROM products")
                    total_views = cursor.fetchone()['total_views']
                    
                    cursor.execute("SELECT COALESCE(SUM(favorites), 0) as total_favorites FROM products")
                    total_favorites = cursor.fetchone()['total_favorites']
                    
                    cursor.execute("SELECT COALESCE(AVG(price), 0) as avg_price FROM products")
                    avg_price = cursor.fetchone()['avg_price']
                    
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
    
    # Review Management (for next phase)
    def add_review(self, review_data):
        """Add a customer review"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO reviews (product_id, customer_name, customer_email, rating, comment)
                        VALUES (%(product_id)s, %(customer_name)s, %(customer_email)s, %(rating)s, %(comment)s)
                    """, review_data)
                    conn.commit()
                    return True
        except Exception as e:
            st.error(f"Error adding review: {str(e)}")
            return False
    
    def get_product_reviews(self, product_id):
        """Get reviews for a specific product"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT * FROM reviews 
                        WHERE product_id = %s AND approved = true
                        ORDER BY created_at DESC
                    """, (product_id,))
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            st.error(f"Error loading reviews: {str(e)}")
            return []
    
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
                    order_id = cursor.fetchone()[0]
                    
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