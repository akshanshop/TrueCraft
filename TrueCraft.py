import streamlit as st
import pandas as pd
import os
from utils.database_factory import create_database_service
from utils.auth_manager import AuthManager
from utils.config import get_public_url

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
    
    # Get the current URL for redirect_uri - works for all environments
    redirect_uri = get_public_url() + "/"
    
    # Handle the OAuth callback
    if auth_manager.handle_oauth_callback(provider, code, state, redirect_uri):
        st.success(f"Successfully signed in with {provider.title()}!")
        # Clear query parameters and refresh
        st.query_params.clear()
        st.rerun()
    else:
        st.error("Authentication failed. Please try again.")
        st.query_params.clear()


# Enhanced CSS for symmetric and aesthetic design
st.markdown("""
<style>
    /* Main layout improvements */
    .main .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    
    /* Enhanced header styling */
    .main-header {
        text-align: center;
        padding: 3rem 0 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    .main-header h1 {
        margin-bottom: 0.5rem;
        font-size: 3rem;
        font-weight: 700;
    }
    
    /* Aesthetic card styling */
    .value-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        padding: 2rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8ecff;
        transition: all 0.3s ease;
        height: 100%;
        min-height: 220px;
        display: flex;
        flex-direction: column;
    }
    
    .value-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    }
    
    .value-card h4 {
        color: #2d3748;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .value-card p {
        color: #4a5568;
        line-height: 1.6;
        flex-grow: 1;
    }
    
    /* Navigation grid styling */
    .nav-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8feff 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8f4ff;
        transition: all 0.3s ease;
        height: 100%;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .nav-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        border-color: #667eea;
    }
    
    .nav-card h3 {
        color: #2d3748;
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }
    
    .nav-card p {
        color: #4a5568;
        margin-bottom: 1.5rem;
        flex-grow: 1;
    }
    
    /* Button enhancements */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
    }
    
    /* Metrics styling */
    .metric-card {
        background: linear-gradient(145deg, #ffffff 0%, #f0f8ff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e8f2ff;
        margin: 0.5rem 0;
    }
    
    /* Info box styling */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #f8f9ff 0%, #ffffff 100%);
        border-radius: 12px;
        border: 1px solid #e8ecff;
    }
    
    /* Divider styling */
    hr {
        margin: 3rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    /* Section headers */
    .section-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #2d3748;
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .value-card, .nav-card {
            margin: 0.5rem 0;
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Main page header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🎨 TrueCraft Marketplace Assistant")
st.markdown("*A movement to empower artisans and preserve culture through AI-powered tools*")
st.markdown("**Not just a marketplace → An AI assistant that helps artisans sell smarter, not harder**")
st.markdown('</div>', unsafe_allow_html=True)

# Value Proposition Section
st.markdown("""---""")
st.subheader("🌟 Why TrueCraft is Different")

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="value-card">
        <h4>🎯 Problem-Solution Fit</h4>
        <p>We identified a real pain point: artisans struggle with digital access, fair pricing, and visibility.</p>
        <p>Our solution is practical, AI-powered, and designed specifically for artisans — not just another e-commerce clone.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="value-card">
        <h4>🤖 Technological Edge</h4>
        <p>Combines AI + voice recognition + personalization + sustainability tagging in one ecosystem.</p>
        <p>Features like AI-generated storytelling and fair price prediction make our project stand out.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="value-card">
        <h4>🌍 Social + Economic Impact</h4>
        <p>Unlike profit-driven platforms, we prioritize artisans' growth, cultural preservation, and fair trade.</p>
        <p>Contributing to SDGs: Decent Work, Reduced Inequalities, and Sustainable Consumption.</p>
    </div>
    """, unsafe_allow_html=True)

# Differentiation from competitors
st.info("""
💡 **Our Focus**: Amazon/Flipkart/Etsy focus on sellers in general. We focus only on artisans, 
breaking their entry barriers with AI-powered, easy-to-use tools. This laser focus + inclusivity makes our platform unique.
""")

# Future Vision Section
with st.expander("🚀 **Scalable & Future-Proof Vision**", expanded=False):
    st.markdown("""
    ### Start Local → Scale Globally
    
    **Current Phase**: Empowering local artisans with AI-powered tools
    
    **Future Features**:
    - 🔗 Blockchain authenticity verification for handmade products
    - 🥽 AR/VR craft experiences for immersive shopping
    - 📚 AI-driven financial literacy programs for artisans
    - 🗣️ Voice onboarding in local languages for accessibility
    - 🌿 Advanced sustainability tagging and impact tracking
    
    **Long-Term Vision**: Not just a project → a movement to empower artisans and preserve culture.
    With global demand for authentic, handmade, and sustainable products rising, our platform is timely and future-ready.
    """)

# Team commitment section
with st.expander("💪 **Our Commitment**", expanded=False):
    st.markdown("""
    ### Passion & Commitment of Our Team
    
    We are not just students building a project → we are passionate about solving real-world problems.
    
    Our diverse skill set (tech + design + social awareness) makes us capable of execution beyond the idea stage.
    
    **Our Promise**: Every feature we build, every decision we make, is centered around empowering artisans 
    and preserving the rich cultural heritage embedded in their crafts.
    """)

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
        
        # Get current URL for redirect URI - works for all environments
        redirect_uri = get_public_url() + "/"
        
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
    

st.markdown("""---""")
st.markdown('<div class="section-header">🚀 AI-Powered Tools for Artisan Success</div>', unsafe_allow_html=True)

# Navigation Grid - 2 rows of 3 columns
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    <div class="nav-card">
        <h3>🏠 Home</h3>
        <p>Main dashboard with overview of your TrueCraft marketplace activity.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Home", use_container_width=True):
        st.switch_page("TrueCraft.py")

with col2:
    st.markdown("""
    <div class="nav-card">
        <h3>📝 Product Listings</h3>
        <p>Create and manage your product listings with AI-generated descriptions.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Manage Products", use_container_width=True):
        st.switch_page("pages/1_Product_Listings.py")

with col3:
    st.markdown("""
    <div class="nav-card">
        <h3>👤 Artisan Profile</h3>
        <p>Build your professional artisan profile and showcase your story.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Manage Profile", use_container_width=True):
        st.switch_page("pages/2_Artisan_Profile.py")

# Second row
col4, col5, col6 = st.columns(3, gap="large")

with col4:
    st.markdown("""
    <div class="nav-card">
        <h3>📊 Analytics</h3>
        <p>Get detailed performance insights and track your sales trends.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("View Analytics", use_container_width=True):
        st.switch_page("pages/3_Analytics.py")

with col5:
    unread_count = db_manager.get_unread_message_count()
    if unread_count > 0:
        st.markdown(f"""
        <div class="nav-card">
            <h3>💬 Messages</h3>
            <p>Manage customer communications. <strong>{unread_count} unread messages</strong></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="nav-card">
            <h3>💬 Messages</h3>
            <p>Manage all your customer communications in one place.</p>
        </div>
        """, unsafe_allow_html=True)
    if st.button("View Messages", use_container_width=True):
        st.switch_page("pages/4_Messages.py")

with col6:
    st.markdown("""
    <div class="nav-card">
        <h3>🆘 Support</h3>
        <p>Get help, and access guides, and troubleshoot any issues.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Get Support", use_container_width=True):
        st.switch_page("pages/5_Support.py")

# Quick stats
st.markdown("""---""")
st.markdown('<div class="section-header">📈 Quick Overview</div>', unsafe_allow_html=True)

# Get current data
products_df = db_manager.get_products()
profiles_df = db_manager.get_profiles()

col1, col2, col3, col4 = st.columns(4, gap="medium")
with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>📦</h3>
        <h2>{}</h2>
        <p>Total Products</p>
    </div>
    """.format(len(products_df)), unsafe_allow_html=True)
    
with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>👥</h3>
        <h2>{}</h2>
        <p>Active Profiles</p>
    </div>
    """.format(len(profiles_df)), unsafe_allow_html=True)
    
with col3:
    avg_price = products_df['price'].mean() if not products_df.empty else 0
    st.markdown("""
    <div class="metric-card">
        <h3>💰</h3>
        <h2>${:.2f}</h2>
        <p>Average Price</p>
    </div>
    """.format(avg_price), unsafe_allow_html=True)
    
with col4:
    total_messages = db_manager.get_unread_message_count()
    st.markdown("""
    <div class="metric-card">
        <h3>💬</h3>
        <h2>{}</h2>
        <p>Unread Messages</p>
    </div>
    """.format(total_messages), unsafe_allow_html=True)

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
