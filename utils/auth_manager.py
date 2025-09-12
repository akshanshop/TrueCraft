import streamlit as st
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from utils.database_manager import DatabaseManager

class AuthManager:
    def __init__(self):
        """Initialize authentication manager"""
        self.db_manager = DatabaseManager()
        
    def generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get currently logged in user from session"""
        if 'user_id' in st.session_state and 'session_token' in st.session_state:
            user = self.db_manager.get_user_by_id(st.session_state['user_id'])
            if user:
                return user
        return None
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self.get_current_user() is not None
    
    def create_or_update_user(self, provider: str, user_data: Dict[str, Any]) -> Optional[int]:
        """Create or update user from OAuth data"""
        try:
            # Extract common fields from different providers
            oauth_id = str(user_data.get('id', ''))
            email = user_data.get('email', '')
            name = user_data.get('name', user_data.get('display_name', ''))
            avatar_url = user_data.get('picture', user_data.get('avatar_url', user_data.get('profile_image_url', '')))
            
            # Create user in database
            user_id = self.db_manager.create_user(
                oauth_provider=provider,
                oauth_id=oauth_id,
                email=email,
                name=name,
                avatar_url=avatar_url,
                profile_data=user_data
            )
            
            return user_id
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
            return None
    
    def login_user(self, user_id: int) -> bool:
        """Log in user by setting session state"""
        try:
            user = self.db_manager.get_user_by_id(user_id)
            if user:
                # Set session state
                st.session_state['user_id'] = user_id
                st.session_state['session_token'] = self.generate_session_token()
                st.session_state['user_email'] = user['email']
                st.session_state['user_name'] = user['name']
                st.session_state['user_avatar'] = user['avatar_url']
                st.session_state['login_time'] = datetime.now()
                
                return True
        except Exception as e:
            st.error(f"Login error: {str(e)}")
        return False
    
    def logout_user(self):
        """Log out user by clearing session state"""
        # Clear all authentication-related session state
        for key in ['user_id', 'session_token', 'user_email', 'user_name', 'user_avatar', 'login_time']:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_oauth_url(self, provider: str, redirect_uri: str) -> str:
        """Generate OAuth URL for different providers"""
        # Note: In a real implementation, you would use the actual OAuth URLs
        # For demo purposes, these are placeholder URLs
        oauth_urls = {
            'google': f'https://accounts.google.com/oauth/authorize?client_id=YOUR_GOOGLE_CLIENT_ID&redirect_uri={redirect_uri}&scope=openid email profile&response_type=code',
            'facebook': f'https://www.facebook.com/v18.0/dialog/oauth?client_id=YOUR_FACEBOOK_CLIENT_ID&redirect_uri={redirect_uri}&scope=email,public_profile&response_type=code',
            'twitter': f'https://twitter.com/i/oauth2/authorize?client_id=YOUR_TWITTER_CLIENT_ID&redirect_uri={redirect_uri}&scope=tweet.read users.read&response_type=code&code_challenge=CHALLENGE',
            'linkedin': f'https://www.linkedin.com/oauth/v2/authorization?client_id=YOUR_LINKEDIN_CLIENT_ID&redirect_uri={redirect_uri}&scope=r_liteprofile r_emailaddress&response_type=code'
        }
        
        return oauth_urls.get(provider, '')
    
    def handle_oauth_callback(self, provider: str, code: str) -> bool:
        """Handle OAuth callback and create/login user"""
        # Note: In a real implementation, you would exchange the code for a token
        # and fetch user data from the provider's API
        # For demo purposes, we'll simulate this
        
        if code == 'demo_code':
            # Simulate user data from different providers
            demo_users = {
                'google': {
                    'id': '123456789',
                    'email': 'user@gmail.com',
                    'name': 'Demo User',
                    'picture': 'https://via.placeholder.com/100'
                },
                'facebook': {
                    'id': '987654321',
                    'email': 'user@facebook.com',
                    'name': 'Facebook User',
                    'picture': 'https://via.placeholder.com/100'
                },
                'twitter': {
                    'id': '555666777',
                    'email': 'user@twitter.com',
                    'name': 'Twitter User',
                    'profile_image_url': 'https://via.placeholder.com/100'
                },
                'linkedin': {
                    'id': '111222333',
                    'email': 'user@linkedin.com',
                    'name': 'LinkedIn User',
                    'picture': 'https://via.placeholder.com/100'
                }
            }
            
            user_data = demo_users.get(provider)
            if user_data:
                user_id = self.create_or_update_user(provider, user_data)
                if user_id:
                    return self.login_user(user_id)
        
        return False
    
    def require_auth(self, redirect_to_login: bool = True):
        """Decorator-like function to require authentication"""
        if not self.is_authenticated():
            if redirect_to_login:
                st.warning("Please log in to access this feature.")
                self.show_login_form()
                st.stop()
            return False
        return True
    
    def show_login_form(self):
        """Display login form with social providers"""
        st.subheader("🔐 Sign In to TrueCraft")
        st.markdown("Connect with your favorite social platform to save your data and access all features.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Quick Sign In")
            
            # Google Login
            if st.button("🔴 Continue with Google", use_container_width=True, type="primary"):
                # In real implementation, redirect to OAuth URL
                if self.handle_oauth_callback('google', 'demo_code'):
                    st.success("Successfully logged in with Google!")
                    st.rerun()
            
            # Facebook Login
            if st.button("🔵 Continue with Facebook", use_container_width=True):
                if self.handle_oauth_callback('facebook', 'demo_code'):
                    st.success("Successfully logged in with Facebook!")
                    st.rerun()
        
        with col2:
            st.markdown("### Professional Networks")
            
            # LinkedIn Login
            if st.button("🔗 Continue with LinkedIn", use_container_width=True):
                if self.handle_oauth_callback('linkedin', 'demo_code'):
                    st.success("Successfully logged in with LinkedIn!")
                    st.rerun()
            
            # Twitter Login
            if st.button("🐦 Continue with Twitter", use_container_width=True):
                if self.handle_oauth_callback('twitter', 'demo_code'):
                    st.success("Successfully logged in with Twitter!")
                    st.rerun()
        
        st.divider()
        st.markdown("*Your data is secure and we only access basic profile information.*")
    
    def show_user_profile(self):
        """Display logged-in user profile"""
        user = self.get_current_user()
        if user:
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if user['avatar_url']:
                    st.image(user['avatar_url'], width=80)
                st.write(f"**{user['name']}**")
                st.write(f"📧 {user['email']}")
                st.write(f"🔗 Connected via {user['oauth_provider'].title()}")
                
                if st.button("🚪 Sign Out", use_container_width=True):
                    self.logout_user()
                    st.success("Successfully logged out!")
                    st.rerun()