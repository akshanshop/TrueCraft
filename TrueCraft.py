import streamlit as st
import pandas as pd
import os
from utils.database_factory import create_database_service
from utils.auth_manager import AuthManager
from utils.config import get_public_url
from utils.i18n import i18n, t
from utils.ai_assistant import AIAssistant

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
    
    /* AI Chatbot Floating Widget */
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border: 2px solid #8B4513;
        width: 350px;
        max-height: 500px;
        font-family: inherit;
    }
    
    .chatbot-header {
        background: linear-gradient(135deg, #8B4513, #A0522D);
        color: white;
        padding: 12px 15px;
        border-radius: 12px 12px 0 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        cursor: pointer;
        font-weight: 500;
    }
    
    .chatbot-header .logo {
        font-size: 20px;
        margin-right: 8px;
    }
    
    .chatbot-messages {
        height: 300px;
        overflow-y: auto;
        padding: 15px;
        background: #FFF8DC;
        border-bottom: 1px solid #F5E6D3;
    }
    
    .message {
        margin-bottom: 10px;
        padding: 8px 12px;
        border-radius: 12px;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 14px;
        line-height: 1.4;
    }
    
    .user-message {
        background: #8B4513;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .bot-message {
        background: white;
        color: #2F1B14;
        border: 1px solid #F5E6D3;
        margin-right: auto;
    }
    
    .chatbot-input {
        padding: 12px 15px;
        border-radius: 0 0 12px 12px;
        background: white;
        display: flex;
        gap: 8px;
        align-items: center;
    }
    
    .chatbot-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        background: linear-gradient(135deg, #8B4513, #A0522D);
        color: white;
        border: none;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        transition: all 0.3s ease;
    }
    
    .chatbot-toggle:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .chatbot-hidden {
        display: none;
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        padding: 8px 12px;
        background: white;
        border: 1px solid #F5E6D3;
        border-radius: 12px;
        max-width: 85%;
        margin-right: auto;
        font-size: 14px;
        color: #666;
    }
    
    .typing-dots {
        display: inline-flex;
        margin-left: 8px;
    }
    
    .typing-dots span {
        background: #8B4513;
        border-radius: 50%;
        width: 4px;
        height: 4px;
        margin: 0 1px;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { opacity: 0.3; }
        40% { opacity: 1; }
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

# Footer
st.divider()
st.markdown(f"""
<div style="text-align: center; padding: 2rem 0; color: #666;">
    <p>🎨 {t('footer_tagline')}</p>
</div>
""", unsafe_allow_html=True)

# Initialize AI Assistant for chatbot
@st.cache_resource
def get_ai_assistant():
    return AIAssistant()

# AI Chatbot Component
def render_ai_chatbot():
    """Render the floating AI chatbot in the bottom right corner"""
    
    # Initialize session state for chatbot
    if 'chatbot_open' not in st.session_state:
        st.session_state.chatbot_open = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": f"👋 Hello! I'm your TrueCraft AI assistant. I can help you with product descriptions, pricing advice, business tips, and more. How can I assist you today?"}
        ]
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ""
    
    # Chatbot toggle button
    if not st.session_state.chatbot_open:
        chatbot_html = """
        <div class="chatbot-toggle" onclick="toggleChatbot()">
            🤖
        </div>
        """
    else:
        # Build messages HTML
        messages_html = ""
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                messages_html += f'<div class="message user-message">{msg["content"]}</div>'
            else:
                messages_html += f'<div class="message bot-message">{msg["content"]}</div>'
        
        chatbot_html = f"""
        <div class="chatbot-container">
            <div class="chatbot-header" onclick="toggleChatbot()">
                <div>
                    <span class="logo">🤖</span>
                    <strong>TrueCraft AI Assistant</strong>
                </div>
                <span style="cursor: pointer;">✕</span>
            </div>
            <div class="chatbot-messages" id="chatbot-messages">
                {messages_html}
            </div>
            <div class="chatbot-input">
                <div style="flex: 1; font-size: 14px; color: #666;">
                    Type your message below and click "Ask AI Assistant" to send...
                </div>
            </div>
        </div>
        """
    
    # JavaScript for toggle functionality
    chatbot_script = """
    <script>
    function toggleChatbot() {
        window.parent.postMessage({type: 'chatbot_toggle'}, '*');
    }
    
    // Auto-scroll to bottom of messages
    function scrollChatToBottom() {
        var messagesDiv = document.getElementById('chatbot-messages');
        if (messagesDiv) {
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    }
    setTimeout(scrollChatToBottom, 100);
    </script>
    """
    
    # Render the chatbot
    st.markdown(chatbot_html + chatbot_script, unsafe_allow_html=True)
    
    # Handle chatbot toggle via JavaScript message
    if st.session_state.get('chatbot_toggle_requested', False):
        st.session_state.chatbot_open = not st.session_state.chatbot_open
        st.session_state.chatbot_toggle_requested = False
        st.rerun()

# Chatbot input and response handling
if st.session_state.get('chatbot_open', False):
    st.markdown("---")
    st.markdown("### 🤖 Chat with AI Assistant")
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    with col1:
        user_input = st.text_input(
            "Ask me anything about your artisan business:",
            value="",
            placeholder="e.g., How should I price my handmade jewelry? or Help me write a product description...",
            key="chatbot_input_field"
        )
    
    with col2:
        send_button = st.button("Ask AI Assistant", type="primary", key="send_chat")
    
    # Handle send button or enter key
    if send_button and user_input.strip():
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        # Get AI response
        ai_assistant = get_ai_assistant()
        if ai_assistant and ai_assistant.enabled:
            try:
                with st.spinner("AI is thinking..."):
                    # Use the general content generation for chatbot responses
                    response = ai_assistant.generate_custom_content(
                        "conversational assistance",
                        f"User is asking about their artisan business: {user_input}",
                        "Provide helpful, friendly advice about artisan business, crafts, product creation, pricing, marketing, or general business questions. Keep responses concise but informative."
                    )
                    
                    if response and response.strip():
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    else:
                        st.session_state.chat_messages.append({
                            "role": "assistant", 
                            "content": "I apologize, but I'm having trouble generating a response right now. Please try again later."
                        })
            except Exception as e:
                st.session_state.chat_messages.append({
                    "role": "assistant", 
                    "content": "I'm sorry, but I'm experiencing technical difficulties. Please try again later."
                })
        else:
            st.session_state.chat_messages.append({
                "role": "assistant", 
                "content": "AI features are currently unavailable. Please check your API configuration."
            })
        
        st.rerun()
    
    # Display chat messages
    if st.session_state.chat_messages:
        st.markdown("#### Conversation")
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**🤖 AI Assistant:** {msg['content']}")
        
        # Clear chat button
        if st.button("Clear Chat", key="clear_chat"):
            st.session_state.chat_messages = [
                {"role": "assistant", "content": f"👋 Hello! I'm your TrueCraft AI assistant. I can help you with product descriptions, pricing advice, business tips, and more. How can I assist you today?"}
            ]
            st.rerun()

# Render the chatbot
render_ai_chatbot()
