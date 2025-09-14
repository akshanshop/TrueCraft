import streamlit as st
import pandas as pd
import os
from utils.database_factory import create_database_service
from utils.auth_manager import AuthManager

# Initialize database service with new portable system
@st.cache_resource
def get_database_service():
    return create_database_service()

# Initialize authentication manager
@st.cache_resource
def get_auth_manager():
    return AuthManager()

db_manager = get_database_service()  # Using new portable database service
auth_manager = get_auth_manager()

st.set_page_config(
    page_title="TrueCraft Marketplace Assistant",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Handle OAuth callback if present
query_params = st.query_params
if 'code' in query_params and 'state' in query_params:
    provider = query_params.get('provider', 'google')  # Default to google if not specified
    code = query_params['code']
    state = query_params['state']
    
    # Get the current URL for redirect_uri - Replit environment
    redirect_uri = "https://" + str(os.getenv('REPL_ID', 'localhost')) + ".replit.app/"
    
    # Handle the OAuth callback
    if auth_manager.handle_oauth_callback(provider, code, state, redirect_uri):
        st.success(f"Successfully signed in with {provider.title()}!")
        # Clear query parameters and refresh
        st.query_params.clear()
        st.rerun()
    else:
        st.error("Authentication failed. Please try again.")
        st.query_params.clear()


# Custom CSS for warm, crafted aesthetic using Streamlit's built-in styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .welcome-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    /* Remove left and right padding from main content */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Main page header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🎨 TrueCraft Marketplace Assistant")
st.markdown("*Empowering local artisans with AI-powered tools for online success*")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar with permanent user profile
with st.sidebar:
    # User profile at top of sidebar
    if auth_manager.is_authenticated():
        user = auth_manager.get_current_user()
        if user:
            st.markdown("### 👤 Your Account")
            
            # Profile picture and name
            col1, col2 = st.columns([1, 2])
            with col1:
                if user.get('avatar_url'):
                    st.image(user['avatar_url'], width=60)
                else:
                    st.markdown("<div style='font-size: 40px; text-align: center;'>👤</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{user['name']}**")
                st.caption(f"Connected via {user['oauth_provider'].title()}")
            
            st.divider()
            
            if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
                auth_manager.logout_user()
                st.success("Successfully logged out!")
                st.rerun()
    else:
        st.markdown("### 🔐 Sign In")
        st.markdown("Connect to access your profile and saved data.")
        
        # Get current URL for redirect URI - Replit environment
        redirect_uri = "https://" + str(os.getenv('REPL_ID', 'localhost')) + ".replit.app/"
        
        # Google Login - Real OAuth
        if auth_manager.is_provider_configured('google'):
            google_url = auth_manager.get_oauth_url('google', redirect_uri)
            if google_url:
                st.markdown(f'<a href="{google_url}" target="_self"><button style="width:100%; padding:8px; background:#db4437; color:white; border:none; border-radius:5px; font-size:14px; cursor:pointer; margin:5px 0;">🔴 Continue with Google</button></a>', unsafe_allow_html=True)
        
        # GitHub Login - Real OAuth
        if auth_manager.is_provider_configured('github'):
            github_url = auth_manager.get_oauth_url('github', redirect_uri)
            if github_url:
                st.markdown(f'<a href="{github_url}" target="_self"><button style="width:100%; padding:8px; background:#333; color:white; border:none; border-radius:5px; font-size:14px; cursor:pointer; margin:5px 0;">⚫ Continue with GitHub</button></a>', unsafe_allow_html=True)
        
        if not any(auth_manager.is_provider_configured(p) for p in ['google', 'github']):
            st.info("💡 **Demo Mode**: You're using TrueCraft without authentication. All features are available!")
            st.markdown("*To enable social login, add your OAuth credentials to environment variables.*")
    

# Main Navigation Section
st.subheader("🚀 TrueCraft Tools & Features")

# Navigation Grid - 2 rows of 3 columns
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🏠 Home")
    st.markdown("Main dashboard with overview of your TrueCraft marketplace activity.")
    if st.button("Go to Home", use_container_width=True):
        st.switch_page("TrueCraft.py")

with col2:
    st.subheader("📝 Product Listings")
    st.markdown("Create and manage your product listings with AI-generated descriptions.")
    if st.button("Manage Products", use_container_width=True):
        st.switch_page("pages/1_Product_Listings.py")

with col3:
    st.subheader("👤 Artisan Profile")
    st.markdown("Build your professional artisan profile and showcase your story.")
    if st.button("Manage Profile", use_container_width=True):
        st.switch_page("pages/2_Artisan_Profile.py")

# Second row
col4, col5, col6 = st.columns(3)

with col4:
    st.subheader("📊 Analytics")
    st.markdown("Get detailed performance insights and track your sales trends.")
    if st.button("View Analytics", use_container_width=True):
        st.switch_page("pages/3_Analytics.py")

with col5:
    st.subheader("💬 Messages")
    unread_count = db_manager.get_unread_message_count()
    if unread_count > 0:
        st.markdown(f"Manage customer communications. **{unread_count} unread messages**")
    else:
        st.markdown("Manage all your customer communications in one place.")
    if st.button("View Messages", use_container_width=True):
        st.switch_page("pages/4_Messages.py")

with col6:
    st.subheader("🆘 Support")
    st.markdown("Get help, and access guides, and troubleshoot any issues.")
    if st.button("Get Support", use_container_width=True):
        st.switch_page("pages/5_Support.py")

# Quick stats
st.divider()
st.subheader("📈 Quick Overview")

# Get current data
products_df = db_manager.get_products()
profiles_df = db_manager.get_profiles()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Products", len(products_df))
with col2:
    st.metric("Active Profiles", len(profiles_df))
with col3:
    avg_price = products_df['price'].mean() if not products_df.empty else 0
    st.metric("Average Price", f"${avg_price:.2f}")
with col4:
    total_messages = db_manager.get_unread_message_count()
    st.metric("Unread Messages", total_messages)

# Recent activity
if not products_df.empty:
    st.subheader("🆕 Recent Products")
    recent_products = products_df.sort_values('created_at', ascending=False).head(3)
    
    for _, product in recent_products.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                image_data = product.get('image_data', '')
                if image_data and not pd.isna(image_data) and str(image_data).strip():
                    st.image(str(image_data), width=100)
                else:
                    st.write("📷 No image")
            with col2:
                st.write(f"**{product.get('name', 'Unknown')}**")
                price = product.get('price', 0)
                price = float(price) if price is not None else 0.0
                st.write(f"${price:.2f} | {product.get('category', 'Unknown')}")
                st.write(f"Views: {product.get('views', 0)}")
else:
    st.info("Welcome to TrueCraft! Start by creating your first product listing.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #666;">
    <p>🎨 TrueCraft Marketplace Assistant - Crafted for Artisans, Powered by AI</p>
</div>
""", unsafe_allow_html=True)
