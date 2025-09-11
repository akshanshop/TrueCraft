import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database_manager import DatabaseManager

# Initialize database manager
@st.cache_resource
def get_database_manager():
    return DatabaseManager()

db_manager = get_database_manager()

st.set_page_config(
    page_title="Messages - ArtisanAI",
    page_icon="💬",
    layout="wide"
)

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
    # New message form
    st.subheader("📝 Send New Message")
    
    with st.container():
        st.markdown('<div class="contact-form-container">', unsafe_allow_html=True)
        
        # Get products for selection
        products_df = db_manager.get_products()
        
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
                
                recipient_type = "seller" if st.session_state.user_type == "buyer" else "buyer"
                recipient_name = st.text_input("Recipient Name", placeholder=f"Enter {recipient_type} name")
                recipient_email = st.text_input("Recipient Email", placeholder=f"Enter {recipient_type} email")
            
            with col2:
                subject = st.text_input("Subject", placeholder="Enter message subject")
                message_content = st.text_area("Message", placeholder="Type your message here...", height=100)
            
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
    
    # Reply form
    st.divider()
    st.subheader("📝 Reply")
    
    with st.form("reply_form"):
        reply_message = st.text_area("Your Reply", placeholder="Type your reply here...", height=100)
        
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