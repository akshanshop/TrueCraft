import streamlit as st
import pandas as pd
import os
from utils.database_factory import create_database_service
from utils.auth_manager import AuthManager
from utils.config import get_public_url
from utils.i18n import i18n, t
from utils.ai_assistant import AIAssistant

# Initialize AI Assistant for chatbot
@st.cache_resource
def get_ai_assistant():
    return AIAssistant()

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
    page_title=t("app_title"),
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
        st.success(f"{t('successfully_signed_in_with')} {provider.title()}!")
        # Clear query parameters and refresh
        st.query_params.clear()
        st.rerun()
    else:
        st.error(t('authentication_failed'))
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
st.title(f"🎨 {t('app_title')}")
st.markdown(f"*{t('app_tagline')}*")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar with permanent user profile
with st.sidebar:
    # Language selector at top
    st.markdown(f"### 🌐 {t('language')}")
    i18n.language_selector("main_language_selector")
    st.divider()
    
    # User profile at top of sidebar
    if auth_manager.is_authenticated():
        user = auth_manager.get_current_user()
        if user:
            st.markdown(f"### 👤 {t('your_account')}")
            
            # Profile picture and name
            col1, col2 = st.columns([1, 2])
            with col1:
                if user.get('avatar_url'):
                    st.image(user['avatar_url'], width=60)
                else:
                    st.markdown("<div style='font-size: 40px; text-align: center;'>👤</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{user['name']}**")
                st.caption(f"{t('connected_via')} {user['oauth_provider'].title()}")
            
            st.divider()
            
            if st.button(f"🚪 {t('sign_out')}", use_container_width=True, type="secondary"):
                auth_manager.logout_user()
                st.success(t("successfully_logged_out"))
                st.rerun()
    else:
        st.markdown(f"### 🔐 {t('sign_in')}")
        st.markdown(t("connect_to_access"))
        
        # Get current URL for redirect URI - works for all environments
        redirect_uri = get_public_url() + "/"
        
        # Google Login - Real OAuth
        if auth_manager.is_provider_configured('google'):
            google_url = auth_manager.get_oauth_url('google', redirect_uri)
            if google_url:
                st.markdown(f'<a href="{google_url}" target="_self"><button style="width:100%; padding:8px; background:#db4437; color:white; border:none; border-radius:5px; font-size:14px; cursor:pointer; margin:5px 0;">🔴 {t("continue_with_google")}</button></a>', unsafe_allow_html=True)
        
        # GitHub Login - Real OAuth
        if auth_manager.is_provider_configured('github'):
            github_url = auth_manager.get_oauth_url('github', redirect_uri)
            if github_url:
                st.markdown(f'<a href="{github_url}" target="_self"><button style="width:100%; padding:8px; background:#333; color:white; border:none; border-radius:5px; font-size:14px; cursor:pointer; margin:5px 0;">⚫ {t("continue_with_github")}</button></a>', unsafe_allow_html=True)
        
        if not any(auth_manager.is_provider_configured(p) for p in ['google', 'github']):
            st.info(f"💡 **{t('demo_mode')}**")
            st.markdown(f"*{t('enable_social_login')}*")
    
    # AI Assistant Chat Section in Sidebar - Just the button
    st.divider()
    st.markdown("### 🤖 AI Assistant")
    
    # Initialize chat messages in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "👋 Hello! I'm your TrueCraft AI assistant. I can help you with product descriptions, pricing advice, business tips, and more. How can I assist you today?"}
        ]
    
    # Chat toggle button in sidebar
    if 'chat_open' not in st.session_state:
        st.session_state.chat_open = False
    
    if st.button("💬 Chat with AI", type="primary", use_container_width=True):
        st.session_state.chat_open = not st.session_state.chat_open
    

# Main Navigation Section
st.subheader(f"🚀 TrueCraft {t('tools_features')}")

# Navigation Grid - 2 rows of 3 columns
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader(f"🏠 {t('home')}")
    st.markdown(t("home_desc"))
    if st.button(t("go_to_home"), use_container_width=True):
        st.switch_page("TrueCraft.py")

with col2:
    st.subheader(f"📝 {t('product_listings')}")
    st.markdown(t("product_listings_desc"))
    if st.button(t("manage_products"), use_container_width=True):
        st.switch_page("pages/1_Product_Listings.py")

with col3:
    st.subheader(f"👤 {t('artisan_profile')}")
    st.markdown(t("artisan_profile_desc"))
    if st.button(t("manage_profile"), use_container_width=True):
        st.switch_page("pages/2_Artisan_Profile.py")

# Second row
col4, col5, col6 = st.columns(3)

with col4:
    st.subheader(f"📊 {t('analytics')}")
    st.markdown(t('analytics_desc'))
    if st.button(t('view_analytics'), use_container_width=True):
        st.switch_page("pages/3_Analytics.py")

with col5:
    st.subheader(f"💬 {t('messages')}")
    unread_count = db_manager.get_unread_message_count()
    if unread_count > 0:
        st.markdown(f"{t('manage_customer_communications')} **{unread_count} {t('unread_messages_count')}**")
    else:
        st.markdown(t('messages_desc'))
    if st.button(t('view_messages'), use_container_width=True):
        st.switch_page("pages/4_Messages.py")

with col6:
    st.subheader(f"🆘 {t('support')}")
    st.markdown(t('support_desc'))
    if st.button(t('get_support'), use_container_width=True):
        st.switch_page("pages/5_Support.py")

# Third row - Advanced AI Features
st.markdown(f"### 🚀 {t('advanced_ai_features')}")
col7, col8, col9 = st.columns(3)

with col7:
    st.subheader(f"🎙️ {t('voice_onboarding')}")
    st.markdown(t('voice_onboarding_desc'))
    if st.button(t('start_voice_setup'), use_container_width=True):
        st.switch_page("pages/6_Voice_Onboarding.py")

with col8:
    st.subheader(f"🌱 {t('sustainability_hub')}")
    st.markdown(t('sustainability_desc'))
    if st.button(t('sustainability_assessment'), use_container_width=True):
        st.info(f"🌿 {t('sustainability_features_info')}")

with col9:
    st.subheader(f"🏛️ {t('cultural_heritage')}")
    st.markdown(t('cultural_desc'))
    if st.button(t('cultural_storytelling'), use_container_width=True):
        st.info(f"🎨 {t('cultural_storytelling_info')}")

# Quick stats
st.divider()
st.subheader(f"📈 {t('quick_overview')}")

# Get current data
products_df = db_manager.get_products()
profiles_df = db_manager.get_profiles()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(t('total_products'), len(products_df))
with col2:
    st.metric(t('active_profiles'), len(profiles_df))
with col3:
    avg_price = products_df['price'].mean() if not products_df.empty else 0
    st.metric(t('average_price'), f"${avg_price:.2f}")
with col4:
    total_messages = db_manager.get_unread_message_count()
    st.metric(t('unread_messages'), total_messages)

# Recent activity
if not products_df.empty:
    st.subheader(f"🆕 {t('recent_products')}")
    recent_products = products_df.sort_values('created_at', ascending=False).head(3)
    
    for _, product in recent_products.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                image_data = product.get('image_data', '')
                if image_data and not pd.isna(image_data) and str(image_data).strip():
                    st.image(str(image_data), width=100)
                else:
                    st.write(f"📷 {t('no_image')}")
            with col2:
                st.write(f"**{product.get('name', t('unknown'))}**")
                price = product.get('price', 0)
                price = float(price) if price is not None else 0.0
                st.write(f"${price:.2f} | {product.get('category', t('unknown'))}")
                st.write(f"{t('views')}: {product.get('views', 0)}")
else:
    st.info(t('welcome_message'))

# AI Assistant Chat Interface in Main Area
if st.session_state.chat_open:
    st.divider()
    st.markdown("## 🤖 TrueCraft AI Assistant")
    st.markdown("Ask me anything about your artisan business - product descriptions, pricing, marketing, or general business advice!")
    
    # Default prompt options
    if len(st.session_state.messages) <= 1:
        st.markdown("**💡 Quick Start - Choose a topic or type your own question:**")
        
        # Define default prompts for artisan business
        default_prompts = [
            "How should I price my handmade products?",
            "Write a compelling product description for my jewelry",
            "What are the best marketing strategies for artisans?", 
            "Help me create an engaging artisan profile bio",
            "What materials should I mention in my product listings?",
            "How can I improve my product photography?",
            "What shipping options work best for handmade items?",
            "Help me write a social media post about my craft"
        ]
        
        # Display default prompts in a grid
        col1, col2 = st.columns(2)
        for i, prompt in enumerate(default_prompts):
            with col1 if i % 2 == 0 else col2:
                if st.button(f"💬 {prompt}", key=f"main_prompt_{i}", help="Click to ask this question"):
                    # Process the selected default prompt
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    
                    # Get AI response for the selected prompt
                    try:
                        ai_assistant = get_ai_assistant()
                    except:
                        ai_assistant = None
                    if ai_assistant and ai_assistant.enabled:
                        try:
                            with st.spinner("AI is thinking..."):
                                response = ai_assistant.generate_custom_content(
                                    "conversational assistance",
                                    f"User is asking about their artisan business: {prompt}",
                                    "Provide helpful, friendly advice about artisan business, crafts, product creation, pricing, marketing, or general business questions. Keep responses concise but informative. Be encouraging and supportive."
                                )
                                
                                if response and response.strip():
                                    st.session_state.messages.append({"role": "assistant", "content": response})
                                else:
                                    st.session_state.messages.append({
                                        "role": "assistant", 
                                        "content": "I apologize, but I'm having trouble generating a response right now. Please try again later."
                                    })
                        except Exception as e:
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": "I'm sorry, but I'm experiencing technical difficulties. Please try again later."
                            })
                    else:
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "AI features are currently unavailable. Please check your API configuration."
                        })
                    st.rerun()
        
        st.markdown("**Or type your own question below:**")
    
    # Create a container for chat messages
    chat_container = st.container(height=400)
    with chat_container:
        # Display chat messages using Streamlit's chat message components
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    # Chat input using Streamlit's built-in chat input
    if prompt := st.chat_input("Ask me anything about your artisan business..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get AI response
        try:
            ai_assistant = get_ai_assistant()
        except:
            ai_assistant = None
        if ai_assistant and ai_assistant.enabled:
            try:
                with st.spinner("AI is thinking..."):
                    # Use the AI assistant to generate response
                    response = ai_assistant.generate_custom_content(
                        "conversational assistance",
                        f"User is asking about their artisan business: {prompt}",
                        "Provide helpful, friendly advice about artisan business, crafts, product creation, pricing, marketing, or general business questions. Keep responses concise but informative. Be encouraging and supportive."
                    )
                    
                    if response and response.strip():
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        error_msg = "I apologize, but I'm having trouble generating a response right now. Please try again later."
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = "I'm sorry, but I'm experiencing technical difficulties. Please try again later."
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            error_msg = "AI features are currently unavailable. Please check your API configuration."
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.rerun()
    
    # Chat controls
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "👋 Hello! I'm your TrueCraft AI assistant. I can help you with product descriptions, pricing advice, business tips, and more. How can I assist you today?"}
            ]
            st.rerun()
    
    with col2:
        if st.button("❌ Close Chat", use_container_width=True):
            st.session_state.chat_open = False
            st.rerun()

# Footer
st.divider()
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0; color: #666;">
    <p>🎨 {t('footer_tagline')}</p>
</div>
""", unsafe_allow_html=True)

