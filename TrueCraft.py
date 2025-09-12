import streamlit as st
import pandas as pd
from utils.database_manager import DatabaseManager
from utils.auth_manager import AuthManager

# Initialize database manager
@st.cache_resource
def get_database_manager():
    return DatabaseManager()

# Initialize authentication manager
@st.cache_resource
def get_auth_manager():
    return AuthManager()

db_manager = get_database_manager()
auth_manager = get_auth_manager()

st.set_page_config(
    page_title="TrueCraft Marketplace Assistant",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Make sidebar permanent and non-collapsible
st.markdown("""
<style>
    .css-1d391kg {display: none;}
    .css-164nlkn {display: none;}
    .css-1rs6os {display: none;}
    .css-17eq0hr {display: none;}
    .css-qbe2hs {display: none;}
    .css-1lcbmhc {display: none;}
    .sidebar .sidebar-content {
        transition: none;
        margin-left: 0;
    }
    section[data-testid="stSidebar"] {
        width: 300px !important;
        min-width: 300px !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 300px !important;
        min-width: 300px !important;
    }
</style>
""", unsafe_allow_html=True)

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
            
            # Quick actions in sidebar
            if st.button("⚙️ Profile Settings", use_container_width=True):
                st.switch_page("pages/2_Artisan_Profile.py")
            
            if st.button("📊 Analytics", use_container_width=True):
                st.switch_page("pages/3_Analytics.py")
            
            if st.button("💬 Messages", use_container_width=True):
                st.switch_page("pages/4_Messages.py")
            
            st.divider()
            
            if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
                auth_manager.logout_user()
                st.success("Successfully logged out!")
                st.rerun()
    else:
        st.markdown("### 🔐 Sign In Required")
        st.info("Sign in to access your profile and saved data.")
        
        if st.button("🔐 Sign In", use_container_width=True, type="primary"):
            # Scroll to sign-in section on main page
            st.info("Please use the sign-in buttons on the main page above.")
    
    st.divider()
    st.markdown("### 🧭 Quick Navigation")
    st.page_link("TrueCraft.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/1_Product_Listings.py", label="📝 Product Listings", icon="📝")
    st.page_link("pages/2_Artisan_Profile.py", label="👤 Artisan Profile", icon="👤")
    st.page_link("pages/3_Analytics.py", label="📊 Analytics", icon="📊")
    st.page_link("pages/4_Messages.py", label="💬 Messages", icon="💬")
    st.page_link("pages/5_Support.py", label="🆘 Support", icon="🆘")

# Account & Profile Section at Top
st.markdown("---")
if auth_manager.is_authenticated():
    # Show user profile prominently at top
    user = auth_manager.get_current_user()
    if user:
        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
        
        with col1:
            if user.get('avatar_url'):
                st.image(user['avatar_url'], width=80)
            else:
                st.markdown("👤")
        
        with col2:
            st.markdown(f"### Welcome back, **{user['name']}**!")
            st.write(f"📧 {user['email']} | 🔗 Connected via {user['oauth_provider'].title()}")
            st.write("🎨 *All your TrueCraft data is automatically saved to your account*")
        
        with col3:
            st.markdown("### Account Settings")
            if st.button("⚙️ Profile Settings", use_container_width=True):
                st.switch_page("pages/2_Artisan_Profile.py")
            if st.button("📊 View Analytics", use_container_width=True):
                st.switch_page("pages/3_Analytics.py")
        
        with col4:
            st.markdown("### Actions")
            if st.button("🚪 Sign Out", use_container_width=True, type="secondary"):
                auth_manager.logout_user()
                st.success("Successfully logged out!")
                st.rerun()
    else:
        st.error("Authentication error. Please sign in again.")
        auth_manager.logout_user()
else:
    # Show sign-in prompt at top for non-authenticated users
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.warning("🔐 **Sign in to save your data and access all TrueCraft features!**")
        st.markdown("Connect with your social account to save listings, profiles, and analytics.")
        
        # Compact sign-in buttons
        sign_col1, sign_col2, sign_col3, sign_col4 = st.columns(4)
        
        with sign_col1:
            if st.button("🔴 Google", use_container_width=True):
                if auth_manager.handle_oauth_callback('google', 'demo_code'):
                    st.success("Logged in with Google!")
                    st.rerun()
        
        with sign_col2:
            if st.button("🔵 Facebook", use_container_width=True):
                if auth_manager.handle_oauth_callback('facebook', 'demo_code'):
                    st.success("Logged in with Facebook!")
                    st.rerun()
        
        with sign_col3:
            if st.button("🔗 LinkedIn", use_container_width=True):
                if auth_manager.handle_oauth_callback('linkedin', 'demo_code'):
                    st.success("Logged in with LinkedIn!")
                    st.rerun()
        
        with sign_col4:
            if st.button("🐦 Twitter", use_container_width=True):
                if auth_manager.handle_oauth_callback('twitter', 'demo_code'):
                    st.success("Logged in with Twitter!")
                    st.rerun()
st.markdown("---")

# Platform Navigation - Organized in Two Rows
st.subheader("🚀 TrueCraft Tools & Features")

# First Row - Main Features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.subheader("📝 Product Listings")
    st.write("Create compelling product listings with AI-generated descriptions and smart pricing suggestions.")
    if st.button("Create Listing", use_container_width=True):
        st.switch_page("pages/1_Product_Listings.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.subheader("👤 Artisan Profile")
    st.write("Build your artisan profile and showcase your story with AI-powered writing assistance.")
    if st.button("Manage Profile", use_container_width=True):
        st.switch_page("pages/2_Artisan_Profile.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.subheader("💬 Messages")
    # Get unread message count
    unread_count = db_manager.get_unread_message_count()
    if unread_count > 0:
        st.write(f"Manage buyer-seller communications with integrated messaging. **{unread_count} unread messages**")
    else:
        st.write("Manage buyer-seller communications with integrated messaging and customer inquiries.")
    if st.button("View Messages", use_container_width=True):
        st.switch_page("pages/4_Messages.py")
    st.markdown('</div>', unsafe_allow_html=True)

# Second Row - Tools & Support
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.subheader("📊 Analytics & Reports")
    st.write("Get detailed analytics and performance insights for your products.")
    if st.button("View Analytics", use_container_width=True):
        st.switch_page("pages/3_Analytics.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.subheader("🆘 Customer Support")
    st.write("Get help with FAQ, troubleshooting guides, and support contact.")
    if st.button("Get Support", use_container_width=True):
        st.switch_page("pages/5_Support.py")
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.subheader("📚 TrueCraft Platform Guide")
    st.write("Get help with guides, tutorials.\nAccess knowledge base and instructions.")
    if st.button("View Help", use_container_width=True):
        st.switch_page("pages/5_Support.py")
    st.markdown('</div>', unsafe_allow_html=True)

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
                image_data = product['image_data']
                if (image_data is not None and not pd.isna(image_data) and str(image_data).strip()):
                    st.image(str(image_data), width=100)
                else:
                    st.write("📷 No image")
            with col2:
                st.write(f"**{product['name']}**")
                st.write(f"${product['price']:.2f} | {product['category']}")
                st.write(f"Views: {product['views']}")
else:
    st.info("Welcome to TrueCraft! Start by creating your first product listing.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; padding: 2rem 0; color: #666;">
    <p>🎨 TrueCraft Marketplace Assistant - Crafted for Artisans, Powered by AI</p>
</div>
""", unsafe_allow_html=True)
