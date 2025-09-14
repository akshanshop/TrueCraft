import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database_factory import create_database_service
from utils.ai_assistant import AIAssistant
from utils.ai_ui_components import AIUIComponents

st.set_page_config(
    page_title="Messages - TrueCraft",
    page_icon="💬",
    layout="wide"
)

# Initialize database manager
@st.cache_resource
def get_database_service():
    return create_database_service()

db_manager = get_database_service()

# Initialize AI components safely
def get_ai_assistant():
    """Get AI assistant with error handling"""
    try:
        if 'ai_assistant' not in st.session_state:
            st.session_state.ai_assistant = AIAssistant()
        return st.session_state.ai_assistant
    except Exception as e:
        st.warning("AI features are currently unavailable. Some functionality may be limited.")
        return None

ai_ui = AIUIComponents()

# Custom CSS for messaging interface
st.markdown("""
<style>
    .conversation-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #007BFF;
        cursor: pointer;
    }
    .conversation-card:hover {
        background: #e9ecef;
    }
    .unread-badge {
        background: #dc3545;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .message-bubble-sender {
        background: #007BFF;
        color: white;
        padding: 0.75rem;
        border-radius: 12px 12px 4px 12px;
        margin: 0.5rem 0;
        margin-left: 20%;
    }
    .message-bubble-receiver {
        background: #f8f9fa;
        color: #333;
        padding: 0.75rem;
        border-radius: 12px 12px 12px 4px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border: 1px solid #dee2e6;
    }
    .message-meta {
        font-size: 0.75rem;
        color: #6c757d;
        margin-top: 0.25rem;
    }
    .contact-form-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

st.title("💬 Messages")
st.markdown("Manage your buyer-seller communications")

# Initialize session state
if 'current_conversation' not in st.session_state:
    st.session_state.current_conversation = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = "demo@artisan.com"  # Default demo email
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Demo User"
if 'user_type' not in st.session_state:
    st.session_state.user_type = "seller"  # Default to seller view

# Sidebar for user profile and navigation
with st.sidebar:
    st.subheader("👤 Your Profile")
    
    # User type selection
    user_type = st.selectbox("View as:", ["seller", "buyer"], 
                            index=0 if st.session_state.user_type == "seller" else 1)
    st.session_state.user_type = user_type
    
    # User information
    user_email = st.text_input("Your Email", value=st.session_state.user_email)
    user_name = st.text_input("Your Name", value=st.session_state.user_name)
    
    if st.button("Update Profile", use_container_width=True):
        st.session_state.user_email = user_email
        st.session_state.user_name = user_name
        st.success("Profile updated!")
    
    st.divider()
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    if st.button("📝 New Message", use_container_width=True):
        st.session_state.current_conversation = "new"
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    
    # Stats
    st.divider()
    st.subheader("📊 Message Stats")
    unread_count = db_manager.get_unread_message_count(st.session_state.user_email)
    conversations = db_manager.get_conversations()
    st.metric("Unread Messages", unread_count)
    st.metric("Total Conversations", len(conversations))

# Main content area
if st.session_state.current_conversation == "new":
    # AI-Enhanced New Message Form
    st.subheader("📝 Send New Message")
    
    # AI-Powered Message Assistant
    ai_ui.ai_powered_form_section(
        "🤖 AI Message Assistant", 
        "Get intelligent assistance for professional communication with templates and content improvement!"
    )
    
    with st.container():
        st.markdown('<div class="contact-form-container">', unsafe_allow_html=True)
        
        # Get products for selection
        products_df = db_manager.get_products()
        
        # Initialize variables with default values
        if not products_df.empty:
            product_options = ["General Inquiry"] + [f"{row['name']} (${row['price']:.2f})" for _, row in products_df.iterrows()]
            selected_product_idx = 0  # Default to General Inquiry
        else:
            product_options = ["General Inquiry"]
            selected_product_idx = 0
        
        # Initialize form variables in session state
        recipient_name = st.session_state.get('recipient_name', '')
        subject = st.session_state.get('message_subject', '')
        
        # Message Templates Section
        with st.expander("📝 Quick Message Templates", expanded=False):
            template_col1, template_col2 = st.columns(2)
            
            with template_col1:
                ai_ui.message_templates_widget(
                    message_type="inquiry",
                    product_name=product_options[selected_product_idx] if selected_product_idx < len(product_options) else None
                )
            
            with template_col2:
                st.markdown("**Quick Template Actions:**")
                if st.button("✨ Generate Custom Message", key="custom_msg_btn"):
                    if recipient_name and subject:
                        ai_assistant = get_ai_assistant()
                        if ai_assistant:
                            try:
                                with st.spinner("Creating message..."):
                                    custom_msg = ai_assistant.generate_custom_content(
                                        "business message",
                                        f"Message from {st.session_state.user_type} to {recipient_name} about {subject}",
                                        f"Professional {st.session_state.user_type} inquiry"
                                    )
                                    st.session_state['generated_message'] = custom_msg
                                    st.success("Message generated!")
                            except:
                                st.error("AI unavailable")
                        else:
                            st.error("AI features are currently unavailable.")
                    else:
                        st.warning("Please fill in recipient name and subject first.")
                
                if 'generated_message' in st.session_state:
                    st.text_area("Generated Message:", st.session_state['generated_message'], height=80, key="gen_msg_display")
        
        with st.form("new_message_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                if not products_df.empty:
                    product_options = ["General Inquiry"] + [f"{row['name']} (${row['price']:.2f})" for _, row in products_df.iterrows()]
                    product_ids = [None] + products_df['id'].tolist()
                    
                    selected_product_idx = st.selectbox("About Product", range(len(product_options)), 
                                                       format_func=lambda x: product_options[x])
                    selected_product_id = product_ids[selected_product_idx]
                else:
                    st.info("No products available")
                    selected_product_id = None
                    product_options = ["General Inquiry"]
                    selected_product_idx = 0
                
                recipient_type = "seller" if st.session_state.user_type == "buyer" else "buyer"
                recipient_name = st.text_input("Recipient Name", 
                                              value=st.session_state.get('recipient_name', ''),
                                              placeholder=f"Enter {recipient_type} name",
                                              key="recipient_name_input")
                st.session_state['recipient_name'] = recipient_name
                
                recipient_email = st.text_input("Recipient Email", placeholder=f"Enter {recipient_type} email")
            
            with col2:
                subject = st.text_input("Subject", 
                                      value=st.session_state.get('message_subject', ''),
                                      placeholder="Enter message subject",
                                      key="subject_input")
                st.session_state['message_subject'] = subject
                
                # AI suggestions for subjects
                if subject and len(subject) > 5:
                    ai_ui.ai_suggestions_panel(subject, "message")
                
                # AI-Enhanced Message Content
                product_name = product_options[selected_product_idx] if selected_product_idx < len(product_options) else None
                message_content = st.text_area(
                    "Message*", 
                    value=st.session_state.get('message_content', ''),
                    placeholder="Type your message here...",
                    height=120,
                    key="message_content_input"
                )
                st.session_state['message_content'] = message_content
            
            if st.form_submit_button("📤 Send Message", use_container_width=True):
                if recipient_name and recipient_email and subject and message_content:
                    message_data = {
                        'sender_type': st.session_state.user_type,
                        'sender_name': st.session_state.user_name,
                        'sender_email': st.session_state.user_email,
                        'product_id': selected_product_id,
                        'subject': subject,
                        'message_content': message_content
                    }
                    
                    message_id = db_manager.send_message(message_data)
                    if message_id:
                        st.success("Message sent successfully! 🎉")
                        st.session_state.current_conversation = None
                        st.rerun()
                    else:
                        st.error("Failed to send message. Please try again.")
                else:
                    st.error("Please fill in all required fields.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("← Back to Conversations"):
        st.session_state.current_conversation = None
        st.rerun()

elif st.session_state.current_conversation:
    # Show specific conversation
    conversation = st.session_state.current_conversation
    
    st.subheader(f"💬 Conversation: {conversation.get('product_name', 'General')}")
    
    # Conversation header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**Participant:** {conversation['sender_name']} ({conversation['sender_email']})")
        st.write(f"**Product:** {conversation.get('product_name', 'General Inquiry')}")
    with col2:
        st.write(f"**Messages:** {conversation['message_count']}")
        if conversation['unread_count'] > 0:
            st.markdown(f'<span class="unread-badge">{conversation["unread_count"]} unread</span>', 
                       unsafe_allow_html=True)
    with col3:
        if st.button("Mark as Read"):
            db_manager.mark_conversation_as_read(conversation['product_id'], conversation['sender_email'])
            st.success("Marked as read!")
            st.rerun()
    
    st.divider()
    
    # Load message thread
    participant_emails = [conversation['sender_email'], st.session_state.user_email]
    messages = db_manager.get_message_thread(conversation['product_id'], participant_emails)
    
    # Display messages
    if messages:
        st.subheader("Message History")
        
        for message in messages:
            is_sender = message['sender_email'] == st.session_state.user_email
            
            if is_sender:
                # Message from current user (right aligned)
                st.markdown(f"""
                <div class="message-bubble-sender">
                    <div>{message['message_content']}</div>
                    <div class="message-meta">
                        You • {message['timestamp'].strftime('%b %d, %Y at %I:%M %p')}
                        {' • Read' if message['is_read'] else ' • Unread'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Message from other user (left aligned)
                st.markdown(f"""
                <div class="message-bubble-receiver">
                    <div>{message['message_content']}</div>
                    <div class="message-meta">
                        {message['sender_name']} • {message['timestamp'].strftime('%b %d, %Y at %I:%M %p')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No messages in this conversation yet.")
    
    # AI-Enhanced Reply Section
    st.divider()
    st.subheader("📝 Reply")
    
    # AI Reply Assistant (outside form)
    with st.expander("🤖 AI Reply Assistant", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            ai_ui.message_templates_widget(
                message_type="follow_up",
                product_name=conversation.get('product_name', 'General')
            )
        
        with col2:
            if st.button("✨ Generate Professional Reply", key="gen_reply_btn"):
                ai_assistant = get_ai_assistant()
                if ai_assistant:
                    try:
                        with st.spinner("Generating reply..."):
                            reply_context = f"Reply to {conversation['sender_name']} about {conversation.get('product_name', 'inquiry')}"
                            generated_reply = ai_assistant.generate_custom_content(
                                "professional reply message",
                                reply_context,
                                f"Courteous {st.session_state.user_type} response"
                            )
                            st.session_state['generated_reply'] = generated_reply
                            st.success("Reply generated!")
                            st.rerun()
                    except:
                        st.error("AI unavailable")
                else:
                    st.error("AI features are currently unavailable.")
            
            if 'generated_reply' in st.session_state:
                st.text_area("Generated Reply:", st.session_state['generated_reply'], height=80, key="gen_reply_display")
    
    # Reply form
    with st.form("reply_form"):
        reply_message = st.text_area("Your Reply", 
                                   value=st.session_state.get('reply_text', ''),
                                   placeholder="Type your reply here...", 
                                   height=100,
                                   key="reply_input")
        st.session_state['reply_text'] = reply_message
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.form_submit_button("📤 Send Reply", use_container_width=True):
                if reply_message:
                    reply_data = {
                        'sender_type': st.session_state.user_type,
                        'sender_name': st.session_state.user_name,
                        'sender_email': st.session_state.user_email,
                        'product_id': conversation['product_id'],
                        'subject': f"Re: {conversation.get('subjects', 'Conversation')}",
                        'message_content': reply_message
                    }
                    
                    message_id = db_manager.send_message(reply_data)
                    if message_id:
                        st.success("Reply sent! 🎉")
                        st.rerun()
                    else:
                        st.error("Failed to send reply. Please try again.")
                else:
                    st.error("Please enter a message.")
    
    if st.button("← Back to Conversations"):
        st.session_state.current_conversation = None
        st.rerun()

else:
    # Main conversations view
    st.subheader("📋 Your Conversations")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        show_filter = st.selectbox("Show", ["All Messages", "Unread Only", "By Product"])
    with col2:
        product_filter = "All Products"  # Default value
        if show_filter == "By Product":
            products_df = db_manager.get_products()
            if not products_df.empty:
                product_filter = st.selectbox("Select Product", 
                                             ["All Products"] + products_df['name'].tolist())
            else:
                product_filter = "All Products"
    with col3:
        sort_by = st.selectbox("Sort by", ["Recent First", "Oldest First", "Most Messages"])
    
    # Get conversations based on user type and email
    if st.session_state.user_type == "seller":
        # Seller sees messages from buyers
        conversations = db_manager.get_conversations(sender_type='buyer')
    else:
        # Buyer sees their own messages
        conversations = db_manager.get_conversations(email=st.session_state.user_email)
    
    # Apply filters
    filtered_conversations = conversations.copy()
    
    if show_filter == "Unread Only":
        filtered_conversations = [conv for conv in filtered_conversations if conv['unread_count'] > 0]
    elif show_filter == "By Product" and 'product_filter' in locals() and product_filter != "All Products":
        filtered_conversations = [conv for conv in filtered_conversations if conv['product_name'] == product_filter]
    
    # Apply sorting
    if sort_by == "Recent First":
        filtered_conversations.sort(key=lambda x: x['last_message_time'], reverse=True)
    elif sort_by == "Oldest First":
        filtered_conversations.sort(key=lambda x: x['last_message_time'])
    elif sort_by == "Most Messages":
        filtered_conversations.sort(key=lambda x: x['message_count'], reverse=True)
    
    # Display conversations
    if filtered_conversations:
        for conversation in filtered_conversations:
            # Create clickable conversation card
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{conversation['product_name']}**")
                    st.write(f"With: {conversation['sender_name']}")
                    # Show latest subjects (truncated)
                    subjects = conversation.get('subjects', '').split(';')[0]  # Get first subject
                    if len(subjects) > 50:
                        subjects = subjects[:50] + "..."
                    st.caption(subjects)
                
                with col2:
                    st.write(f"📧 {conversation['sender_email']}")
                    st.write(f"💬 {conversation['message_count']} messages")
                
                with col3:
                    if conversation['last_message_time']:
                        time_str = conversation['last_message_time'].strftime('%b %d, %Y')
                        st.write(f"🕒 {time_str}")
                    
                    if conversation['unread_count'] > 0:
                        st.markdown(f'<span class="unread-badge">{conversation["unread_count"]} unread</span>', 
                                   unsafe_allow_html=True)
                
                with col4:
                    if st.button("💬 Open", key=f"open_{conversation['product_id']}_{conversation['sender_email']}", 
                                use_container_width=True):
                        st.session_state.current_conversation = conversation
                        st.rerun()
                
                st.divider()
        
        # Summary stats
        st.subheader("📊 Conversation Summary")
        total_conversations = len(filtered_conversations)
        total_unread = sum(conv['unread_count'] for conv in filtered_conversations)
        total_messages = sum(conv['message_count'] for conv in filtered_conversations)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Conversations", total_conversations)
        with col2:
            st.metric("Unread Messages", total_unread)
        with col3:
            st.metric("Total Messages", total_messages)
            
    else:
        if show_filter == "Unread Only":
            st.info("📬 No unread messages. Great job staying on top of your communications!")
        else:
            st.info("💬 No conversations yet. Start by browsing products and contacting sellers, or wait for buyers to reach out!")
        
        # Quick action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Send New Message", use_container_width=True):
                st.session_state.current_conversation = "new"
                st.rerun()
        with col2:
            if st.button("🛍️ Browse Products", use_container_width=True):
                st.switch_page("pages/1_Product_Listings.py")

# Footer with helpful tips
st.divider()
st.markdown("""
### 💡 Messaging Tips
- **For Sellers**: Respond promptly to buyer inquiries to build trust and increase sales
- **For Buyers**: Be specific about your questions - mention size, color, customization needs
- **General**: Use the subject line to summarize your main question or request
- **Privacy**: Never share personal financial information through messages
""")