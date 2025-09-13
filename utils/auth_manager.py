import streamlit as st
import os
import json
import hashlib
import secrets
import base64
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from utils.database_manager import DatabaseManager

try:
    from authlib.integrations.requests_client import OAuth2Session
    import requests
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    requests = None  # type: ignore
    st.warning("OAuth functionality requires authlib and requests packages.")

class AuthManager:
    def __init__(self):
        """Initialize authentication manager"""
        self.db_manager = DatabaseManager()
        self.oauth_available = OAUTH_AVAILABLE
        
        # OAuth provider configurations
        self.providers = {
            'google': {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'userinfo_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
                'scope': 'openid email profile'
            },
            'github': {
                'client_id': os.getenv('GITHUB_CLIENT_ID'),
                'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
                'auth_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'userinfo_url': 'https://api.github.com/user',
                'scope': 'user:email'
            }
        }
        
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
    
    def _generate_pkce_challenge(self):
        """Generate PKCE code verifier and challenge"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8').rstrip('=')
        return code_verifier, code_challenge
    
    def get_oauth_url(self, provider: str, redirect_uri: str) -> str:
        """Generate real OAuth URL for provider"""
        if not self.oauth_available:
            return ''
            
        provider_config = self.providers.get(provider)
        if not provider_config or not provider_config['client_id']:
            return ''
        
        # Generate state and PKCE for security
        state = secrets.token_urlsafe(32)
        code_verifier, code_challenge = self._generate_pkce_challenge()
        
        # Store in session for later verification
        st.session_state[f'oauth_state_{provider}'] = state
        st.session_state[f'oauth_code_verifier_{provider}'] = code_verifier
        
        # Build OAuth URL
        params = {
            'client_id': provider_config['client_id'],
            'redirect_uri': redirect_uri,
            'scope': provider_config['scope'],
            'response_type': 'code',
            'state': state
        }
        
        # Add PKCE for providers that support it
        if provider in ['google']:
            params['code_challenge'] = code_challenge
            params['code_challenge_method'] = 'S256'
        
        query_string = urllib.parse.urlencode(params)
        return f"{provider_config['auth_url']}?{query_string}"
    
    def handle_oauth_callback(self, provider: str, code: str, state: str, redirect_uri: str) -> bool:
        """Handle OAuth callback and create/login user"""
        if not self.oauth_available:
            st.error("OAuth functionality is not available. Please install required packages.")
            return False
            
        # Verify state to prevent CSRF attacks
        expected_state = st.session_state.get(f'oauth_state_{provider}')
        if not expected_state or state != expected_state:
            st.error("Invalid OAuth state. Please try again.")
            return False
        
        provider_config = self.providers.get(provider)
        if not provider_config or not provider_config['client_id']:
            st.error(f"OAuth provider {provider} is not configured.")
            return False
        
        try:
            # Exchange code for access token
            token_data = self._exchange_code_for_token(provider, code, redirect_uri)
            if not token_data:
                return False
            
            # Fetch user data
            user_data = self._fetch_user_data(provider, token_data['access_token'])
            if not user_data:
                return False
            
            # Create or update user
            user_id = self.create_or_update_user(provider, user_data)
            if user_id:
                # Clean up OAuth session data
                if f'oauth_state_{provider}' in st.session_state:
                    del st.session_state[f'oauth_state_{provider}']
                if f'oauth_code_verifier_{provider}' in st.session_state:
                    del st.session_state[f'oauth_code_verifier_{provider}']
                
                return self.login_user(user_id)
                
        except Exception as e:
            st.error(f"OAuth authentication failed: {str(e)}")
        
        return False
    
    def _exchange_code_for_token(self, provider: str, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        if not self.oauth_available or requests is None:
            return None
            
        provider_config = self.providers[provider]
        
        data = {
            'client_id': provider_config['client_id'],
            'client_secret': provider_config['client_secret'],
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        # Add PKCE verifier for providers that support it
        if provider in ['google']:
            code_verifier = st.session_state.get(f'oauth_code_verifier_{provider}')
            if code_verifier:
                data['code_verifier'] = code_verifier
        
        headers = {'Accept': 'application/json'}
        
        response = requests.post(provider_config['token_url'], data=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Token exchange failed: {response.text}")
            return None
    
    def _fetch_user_data(self, provider: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Fetch user data from provider API"""
        if not self.oauth_available or requests is None:
            return None
            
        provider_config = self.providers[provider]
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(provider_config['userinfo_url'], headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            
            # For GitHub, we need to fetch email separately if it's not public
            if provider == 'github' and not user_data.get('email'):
                email_response = requests.get('https://api.github.com/user/emails', headers=headers)
                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next((e['email'] for e in emails if e['primary']), None)
                    if primary_email:
                        user_data['email'] = primary_email
            
            return user_data
        else:
            st.error(f"Failed to fetch user data: {response.text}")
            return None
    
    def get_available_providers(self) -> list:
        """Get list of configured OAuth providers"""
        available = []
        for provider, config in self.providers.items():
            if config['client_id'] and config['client_secret']:
                available.append(provider)
        return available
    
    def is_provider_configured(self, provider: str) -> bool:
        """Check if OAuth provider is properly configured"""
        config = self.providers.get(provider, {})
        return bool(config.get('client_id') and config.get('client_secret'))
    
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
                # Demo implementation - in real app, redirect to OAuth URL
                st.info("Google OAuth would redirect here. This is a demo implementation.")
            
            # Facebook Login
            if st.button("🔵 Continue with Facebook", use_container_width=True):
                # Demo implementation - in real app, redirect to OAuth URL
                st.info("Facebook OAuth would redirect here. This is a demo implementation.")
        
        with col2:
            st.markdown("### Professional Networks")
            
            # LinkedIn Login
            if st.button("🔗 Continue with LinkedIn", use_container_width=True):
                # Demo implementation - in real app, redirect to OAuth URL
                st.info("LinkedIn OAuth would redirect here. This is a demo implementation.")
            
            # Twitter Login
            if st.button("🐦 Continue with Twitter", use_container_width=True):
                # Demo implementation - in real app, redirect to OAuth URL
                st.info("Twitter OAuth would redirect here. This is a demo implementation.")
        
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