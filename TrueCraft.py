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


# Platform Navigation - Organized in Two Rows
st.subheader("🚀 TrueCraft Tools & Features")

# Add robust CSS for perfect button alignment
st.markdown("""
<style>
/* Scope to features grid */
#features-grid [data-testid="column"] > div { 
    display: flex; 
    flex-direction: column; 
    height: 100%; 
}
#features-grid [data-testid="column"] [data-testid="stVerticalBlock"] { 
    display: flex; 
    flex-direction: column; 
    height: 100%; 
    padding: 1.5rem; 
    border-radius: 10px; 
    background: var(--secondary-background-color);
    margin: 1rem 0;
}
/* Normalize description height */
#features-grid .feature-desc { 
    min-height: 4rem; 
    flex-grow: 1;
}
/* Pin the call-to-action to the bottom */
#features-grid [data-testid="column"] .stButton { 
    margin-top: auto; 
}
</style>
""", unsafe_allow_html=True)

# Start features grid
st.markdown('<div id="features-grid">', unsafe_allow_html=True)

# First Row - Main Features
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📝 Product Listings<br>& Smart Pricing")
    st.markdown('<div class="feature-desc">Create compelling product listings with AI-generated descriptions.<br>Get smart pricing suggestions for your handcrafted items.<br>Optimize your marketplace presence and boost sales.</div>', unsafe_allow_html=True)
    if st.button("Create Listing", use_container_width=True):
        st.switch_page("pages/1_Product_Listings.py")

with col2:
    st.subheader("👤 Artisan Profile<br>& Your Story")
    st.markdown('<div class="feature-desc">Build your professional artisan profile and showcase your unique story.<br>Use AI-powered writing assistance to craft compelling descriptions.<br>Connect with customers through authentic storytelling.</div>', unsafe_allow_html=True)
    if st.button("Manage Profile", use_container_width=True):
        st.switch_page("pages/2_Artisan_Profile.py")

with col3:
    st.subheader("💬 Customer Messages<br>& Communication")
    # Get unread message count
    unread_count = db_manager.get_unread_message_count()
    if unread_count > 0:
        st.markdown(f'<div class="feature-desc">Manage all buyer-seller communications in one place.<br>Integrated messaging system for customer inquiries.<br><strong>{unread_count} unread messages waiting for response.</strong></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="feature-desc">Manage all buyer-seller communications in one place.<br>Integrated messaging system for customer inquiries.<br>Stay connected with your customers effortlessly.</div>', unsafe_allow_html=True)
    if st.button("View Messages", use_container_width=True):
        st.switch_page("pages/4_Messages.py")

# Second Row - Tools & Support
col4, col5, col6 = st.columns(3)

with col4:
    st.subheader("📊 Analytics")
    st.markdown('<div class="feature-desc">Get detailed performance insights for your products.<br>Track sales trends and customer engagement metrics.</div>', unsafe_allow_html=True)
    if st.button("View Analytics", use_container_width=True):
        st.switch_page("pages/3_Analytics.py")

with col5:
    st.subheader("🆘 Support")
    st.markdown('<div class="feature-desc">Get help with frequently asked questions.<br>Access troubleshooting guides and contact support.</div>', unsafe_allow_html=True)
    if st.button("Get Support", use_container_width=True):
        st.switch_page("pages/5_Support.py")

with col6:
    st.subheader("📚 Platform Guide")
    st.markdown('<div class="feature-desc">Access comprehensive guides and tutorials.<br>Learn platform features and best practices.</div>', unsafe_allow_html=True)
    if st.button("View Help", use_container_width=True):
        st.switch_page("pages/5_Support.py")

# End features grid
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
                image_data = product.get('image_data', '')
                if image_data and not pd.isna(image_data) and str(image_data).strip():
                    st.image(str(image_data), width=100)
                else:
                    st.write("📷 No image")
            with col2:
                st.write(f"**{product.get('name', 'Unknown')}**")
                st.write(f"${float(product.get('price', 0)):.2f} | {product.get('category', 'Unknown')}")
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
