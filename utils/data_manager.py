import pandas as pd
import streamlit as st
from datetime import datetime
import json

class DataManager:
    def __init__(self):
        """Initialize data manager with session state storage"""
        self._init_session_data()
    
    def _init_session_data(self):
        """Initialize session state data structures"""
        if 'products_data' not in st.session_state:
            st.session_state.products_data = []
        
        if 'profiles_data' not in st.session_state:
            st.session_state.profiles_data = []
        
        if 'analytics_data' not in st.session_state:
            st.session_state.analytics_data = {
                'product_views': {},
                'search_terms': [],
                'user_interactions': []
            }
    
    def get_products(self):
        """Get all products as DataFrame"""
        try:
            if st.session_state.products_data:
                df = pd.DataFrame(st.session_state.products_data)
                # Ensure datetime columns are properly typed
                if 'created_at' in df.columns:
                    df['created_at'] = pd.to_datetime(df['created_at'])
                # Ensure price is numeric
                if 'price' in df.columns:
                    df['price'] = pd.to_numeric(df['price'], errors='coerce')
                return df
            else:
                # Return empty DataFrame with expected columns
                return pd.DataFrame({
                    'name': [], 'category': [], 'price': [], 'description': [], 'materials': [],
                    'dimensions': [], 'weight': [], 'stock_quantity': [], 'shipping_cost': [],
                    'processing_time': [], 'tags': [], 'image_data': [], 'created_at': [],
                    'views': [], 'favorites': []
                })
        except Exception as e:
            st.error(f"Error loading products: {str(e)}")
            return pd.DataFrame()
    
    def add_product(self, product_data):
        """Add a new product"""
        try:
            # Convert datetime to string for JSON serialization
            if 'created_at' in product_data and isinstance(product_data['created_at'], datetime):
                product_data['created_at'] = product_data['created_at'].isoformat()
            
            st.session_state.products_data.append(product_data)
            return True
        except Exception as e:
            st.error(f"Error adding product: {str(e)}")
            return False
    
    def update_product(self, product_name, updated_data):
        """Update an existing product"""
        try:
            products = st.session_state.products_data
            for i, product in enumerate(products):
                if product['name'] == product_name:
                    # Update the product while preserving the original created_at
                    original_created = product.get('created_at')
                    products[i] = {**updated_data, 'created_at': original_created}
                    return True
            return False
        except Exception as e:
            st.error(f"Error updating product: {str(e)}")
            return False
    
    def delete_product(self, product_name):
        """Delete a product"""
        try:
            products = st.session_state.products_data
            st.session_state.products_data = [p for p in products if p['name'] != product_name]
            return True
        except Exception as e:
            st.error(f"Error deleting product: {str(e)}")
            return False
    
    def get_profiles(self):
        """Get all artisan profiles as DataFrame"""
        try:
            if st.session_state.profiles_data:
                df = pd.DataFrame(st.session_state.profiles_data)
                # Ensure datetime columns are properly typed
                for col in ['created_at', 'updated_at']:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])
                return df
            else:
                # Return empty DataFrame with expected columns
                return pd.DataFrame({
                    'name': [], 'location': [], 'specialties': [], 'years_experience': [],
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
            # Convert datetime to string for JSON serialization
            for date_field in ['created_at', 'updated_at']:
                if date_field in profile_data and isinstance(profile_data[date_field], datetime):
                    profile_data[date_field] = profile_data[date_field].isoformat()
            
            st.session_state.profiles_data.append(profile_data)
            return True
        except Exception as e:
            st.error(f"Error adding profile: {str(e)}")
            return False
    
    def update_profile(self, profile_data):
        """Update existing artisan profile (assumes only one profile per user)"""
        try:
            # Convert datetime to string for JSON serialization
            for date_field in ['created_at', 'updated_at']:
                if date_field in profile_data and isinstance(profile_data[date_field], datetime):
                    profile_data[date_field] = profile_data[date_field].isoformat()
            
            if st.session_state.profiles_data:
                # Update the first (and presumably only) profile
                st.session_state.profiles_data[0] = profile_data
            else:
                # If no profile exists, create one
                st.session_state.profiles_data.append(profile_data)
            return True
        except Exception as e:
            st.error(f"Error updating profile: {str(e)}")
            return False
    
    def increment_views(self, product_name):
        """Increment view count for a product"""
        try:
            products = st.session_state.products_data
            for product in products:
                if product['name'] == product_name:
                    product['views'] = product.get('views', 0) + 1
                    return True
            return False
        except Exception as e:
            st.error(f"Error incrementing views: {str(e)}")
            return False
    
    def increment_favorites(self, product_name):
        """Increment favorite count for a product"""
        try:
            products = st.session_state.products_data
            for product in products:
                if product['name'] == product_name:
                    product['favorites'] = product.get('favorites', 0) + 1
                    return True
            return False
        except Exception as e:
            st.error(f"Error incrementing favorites: {str(e)}")
            return False
    
    def log_search(self, search_term):
        """Log search terms for analytics"""
        try:
            if search_term.strip():
                st.session_state.analytics_data['search_terms'].append({
                    'term': search_term,
                    'timestamp': datetime.now().isoformat()
                })
            return True
        except Exception as e:
            st.error(f"Error logging search: {str(e)}")
            return False
    
    def log_interaction(self, interaction_type, product_name=None, details=None):
        """Log user interactions for analytics"""
        try:
            interaction = {
                'type': interaction_type,
                'product_name': product_name,
                'details': details,
                'timestamp': datetime.now().isoformat()
            }
            st.session_state.analytics_data['user_interactions'].append(interaction)
            return True
        except Exception as e:
            st.error(f"Error logging interaction: {str(e)}")
            return False
    
    def get_product_categories(self):
        """Get all unique product categories"""
        try:
            products_df = self.get_products()
            if not products_df.empty:
                return sorted(products_df['category'].unique().tolist())
            return []
        except Exception as e:
            st.error(f"Error getting categories: {str(e)}")
            return []
    
    def get_analytics_summary(self):
        """Get analytics summary data"""
        try:
            products_df = self.get_products()
            
            if products_df.empty:
                return {
                    'total_products': 0,
                    'total_views': 0,
                    'total_favorites': 0,
                    'avg_price': 0,
                    'top_categories': [],
                    'recent_searches': []
                }
            
            # Calculate basic metrics
            total_products = len(products_df)
            total_views = products_df['views'].sum()
            total_favorites = products_df['favorites'].sum()
            avg_price = products_df['price'].mean()
            
            # Top categories by view count  
            category_views = products_df.groupby('category')['views'].sum()
            top_categories = category_views.nlargest(5).to_dict()
            
            # Recent search terms
            recent_searches = st.session_state.analytics_data.get('search_terms', [])[-10:]
            
            return {
                'total_products': total_products,
                'total_views': int(total_views),
                'total_favorites': int(total_favorites),
                'avg_price': float(avg_price),
                'top_categories': top_categories,
                'recent_searches': recent_searches
            }
        except Exception as e:
            st.error(f"Error getting analytics summary: {str(e)}")
            return {}
    
    def export_data(self):
        """Export all data for backup/download"""
        try:
            export_data = {
                'products': st.session_state.products_data,
                'profiles': st.session_state.profiles_data,
                'analytics': st.session_state.analytics_data,
                'export_timestamp': datetime.now().isoformat()
            }
            return json.dumps(export_data, indent=2, default=str)
        except Exception as e:
            st.error(f"Error exporting data: {str(e)}")
            return None
    
    def import_data(self, import_json):
        """Import data from JSON backup"""
        try:
            data = json.loads(import_json)
            
            if 'products' in data:
                st.session_state.products_data = data['products']
            
            if 'profiles' in data:
                st.session_state.profiles_data = data['profiles']
            
            if 'analytics' in data:
                st.session_state.analytics_data = data['analytics']
            
            return True
        except Exception as e:
            st.error(f"Error importing data: {str(e)}")
            return False
    
    def clear_all_data(self):
        """Clear all stored data (use with caution)"""
        try:
            st.session_state.products_data = []
            st.session_state.profiles_data = []
            st.session_state.analytics_data = {
                'product_views': {},
                'search_terms': [],
                'user_interactions': []
            }
            return True
        except Exception as e:
            st.error(f"Error clearing data: {str(e)}")
            return False
