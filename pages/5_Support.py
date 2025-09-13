import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database_manager import DatabaseManager
from utils.ai_assistant import AIAssistant
from utils.ai_ui_components import AIUIComponents

st.set_page_config(
    page_title="Support - TrueCraft",
    page_icon="🆘",
    layout="wide"
)

# Initialize database manager
@st.cache_resource
def get_database_manager():
    return DatabaseManager()

db_manager = get_database_manager()

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

# Custom CSS for support interface
st.markdown("""
<style>
    .support-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .faq-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #28a745;
    }
    .contact-form-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    .help-category {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #2196f3;
    }
    .troubleshooting-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #ffc107;
    }
    .resource-link {
        background: #d1ecf1;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
    .search-box {
        margin-bottom: 1.5rem;
    }
    .priority-high {
        background: #f8d7da;
        border-left-color: #dc3545;
    }
    .priority-medium {
        background: #fff3cd;
        border-left-color: #ffc107;
    }
    .priority-low {
        background: #d4edda;
        border-left-color: #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="support-header">
    <h1>🆘 Customer Support Center</h1>
    <p>Find answers, get help, and contact our support team</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for search and filters
if 'support_search_query' not in st.session_state:
    st.session_state.support_search_query = ""
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = "All"

# Search and filter section
st.markdown('<div class="search-box">', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])
with col1:
    search_query = st.text_input("🔍 Search for help topics, FAQs, or keywords", 
                                placeholder="Type your question or keyword...",
                                value=st.session_state.support_search_query)
    st.session_state.support_search_query = search_query

with col2:
    category_filter = st.selectbox("Filter by Category", 
                                  ["All", "Account", "Products", "Orders", "Technical", "General"])
    st.session_state.selected_category = category_filter
st.markdown('</div>', unsafe_allow_html=True)

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 FAQ", 
    "📞 Contact Support", 
    "📚 Help Guides", 
    "🔧 Troubleshooting", 
    "📖 Resources"
])

with tab1:
    st.subheader("❓ Frequently Asked Questions")
    
    # FAQ data with categories
    faq_data = {
        "Account": [
            {
                "question": "How do I create an artisan profile?",
                "answer": "Go to the 'Artisan Profile' page from the main menu. Fill in your personal information, craft specialties, bio, and social media links. Use the AI assistant to help write compelling descriptions of your work and story."
            },
            {
                "question": "Can I have multiple artisan profiles?",
                "answer": "Currently, each account supports one artisan profile. You can update your profile anytime to reflect different specialties or add new craft categories."
            },
            {
                "question": "How do I update my contact information?",
                "answer": "Visit the 'Artisan Profile' page and edit your contact details including email, phone, website, and social media links. Don't forget to save your changes."
            }
        ],
        "Products": [
            {
                "question": "How do I create a product listing?",
                "answer": "Navigate to 'Product Listings' and click 'Add New Product'. Fill in product details like name, category, price, and description. Upload high-quality images and use our AI assistant to generate compelling descriptions and optimize pricing."
            },
            {
                "question": "What image formats are supported?",
                "answer": "We support JPEG, PNG, and WebP image formats. For best results, use high-resolution images (at least 1000x1000 pixels) with good lighting that showcase your product clearly."
            },
            {
                "question": "How do I price my products competitively?",
                "answer": "Use our AI-powered pricing suggestions in the Product Listings page. The system analyzes similar products, material costs, and market trends to recommend optimal pricing strategies."
            },
            {
                "question": "Can I edit my product listings after publishing?",
                "answer": "Yes! You can edit any product listing anytime. Go to 'Product Listings', find your product, and click 'Edit'. Changes are saved immediately and reflected on your marketplace presence."
            }
        ],
        "Orders": [
            {
                "question": "How do I manage customer orders?",
                "answer": "Customer orders are managed through the messaging system. When buyers are interested, they'll contact you directly through the Messages page. You can negotiate pricing, customization, and shipping details."
            },
            {
                "question": "What payment methods do you support?",
                "answer": "Currently, payment arrangements are handled directly between artisans and customers. We recommend using secure payment platforms like PayPal, Stripe, or established marketplace payment systems."
            },
            {
                "question": "How do I handle shipping and delivery?",
                "answer": "Set your shipping costs and processing times in your product listings. Coordinate delivery details with customers through the messaging system. Consider offering multiple shipping options for customer convenience."
            }
        ],
        "Technical": [
            {
                "question": "The AI assistant isn't working. What should I do?",
                "answer": "First, try refreshing the page. If the issue persists, check your internet connection. For persistent AI assistant issues, contact our technical support team using the form below."
            },
            {
                "question": "My images won't upload. How can I fix this?",
                "answer": "Ensure your images are under 10MB and in supported formats (JPEG, PNG, WebP). Try reducing the file size or converting to a different format. Clear your browser cache if problems continue."
            },
            {
                "question": "How do I view analytics for my products?",
                "answer": "Visit the 'Analytics' page to see detailed performance metrics including views, favorites, and engagement data for all your products. Use these insights to optimize your listings."
            },
            {
                "question": "The page is loading slowly. What's wrong?",
                "answer": "Slow loading can be caused by large images or poor internet connection. Try refreshing the page, checking your connection, or reducing image file sizes in your listings."
            }
        ],
        "General": [
            {
                "question": "What is TrueCraft Marketplace Assistant?",
                "answer": "TrueCraft is an AI-powered platform designed to help local artisans create compelling product listings, manage their online presence, and connect with customers. It provides tools for description writing, pricing optimization, and marketplace management."
            },
            {
                "question": "Is there a cost to use the platform?",
                "answer": "Please contact our support team for current pricing information and available plans. We offer various options to support artisans of all sizes."
            },
            {
                "question": "How do I get started as a new artisan?",
                "answer": "Start by creating your artisan profile, then add your first product listing. Use our AI tools to optimize descriptions and pricing. Check out the Help Guides tab for detailed getting started instructions."
            },
            {
                "question": "Can customers contact me directly?",
                "answer": "Yes! Customers can reach you through our secure messaging system. You'll receive notifications for new messages and can manage all communications from the Messages page."
            }
        ]
    }
    
    # Filter FAQs based on search and category
    def filter_faqs(faqs, search_query, category):
        if category == "All":
            all_faqs = []
            for cat, questions in faqs.items():
                for q in questions:
                    all_faqs.append((cat, q))
            filtered_faqs = all_faqs
        else:
            filtered_faqs = [(category, q) for q in faqs.get(category, [])]
        
        if search_query:
            query_lower = search_query.lower()
            filtered_faqs = [
                (cat, q) for cat, q in filtered_faqs 
                if query_lower in q['question'].lower() or query_lower in q['answer'].lower()
            ]
        
        return filtered_faqs
    
    filtered_faqs = filter_faqs(faq_data, search_query, category_filter)
    
    if filtered_faqs:
        for category, faq in filtered_faqs:
            with st.expander(f"**[{category}]** {faq['question']}"):
                st.markdown(f'<div class="faq-container">{faq["answer"]}</div>', unsafe_allow_html=True)
    else:
        st.info("No FAQs found matching your search. Try different keywords or contact support.")

with tab2:
    st.subheader("📞 Contact Support")
    
    st.markdown("""
    <div class="contact-form-container">
        <h4>🎯 Quick Contact Options</h4>
        <p>Choose the best way to get help based on your needs:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Contact options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="priority-high">
            <h5>🚨 Urgent Technical Issues</h5>
            <p>Platform not working, data loss, critical bugs</p>
            <p><strong>Response:</strong> Within 2 hours</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="priority-medium">
            <h5>💼 General Support</h5>
            <p>Account questions, feature requests, how-to guidance</p>
            <p><strong>Response:</strong> Within 24 hours</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="priority-low">
            <h5>💡 Feedback & Suggestions</h5>
            <p>Feature ideas, general feedback, success stories</p>
            <p><strong>Response:</strong> Within 48 hours</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # AI-Powered Support Ticket Assistant
    ai_ui.ai_powered_form_section(
        "🤖 AI Support Ticket Assistant", 
        "Get intelligent assistance for writing clear, effective support tickets that get faster responses!"
    )
    
    # AI Support Ticket Helper (outside form)
    with st.expander("✨ AI Support Ticket Helper", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🚀 Quick Ticket Templates**")
            template_type = st.selectbox("Choose ticket type:", [
                "Technical Issue", "Account Problem", "Product Listing Help", 
                "Payment/Order Issue", "Feature Request", "General Question", "Bug Report"
            ], key="ticket_template_type")
            
            if st.button("Generate Ticket Template", key="gen_ticket_btn"):
                ai_assistant = get_ai_assistant()
                if ai_assistant:
                    try:
                        with st.spinner("Creating ticket template..."):
                            ticket_content = ai_assistant.generate_support_ticket(
                                template_type, 
                                f"Help with {template_type.lower()}", 
                                "medium"
                            )
                            st.session_state['generated_ticket'] = ticket_content
                            st.success("Ticket template generated!")
                            st.rerun()
                    except:
                        st.error("AI unavailable")
                else:
                    st.error("AI features are currently unavailable.")
        
        with col2:
            st.markdown("**🔧 Improve Your Ticket**")
            if 'current_ticket_desc' in st.session_state and st.session_state.current_ticket_desc:
                if st.button("✨ Improve Description", key="improve_ticket_btn"):
                    ai_assistant = get_ai_assistant()
                    if ai_assistant:
                        try:
                            with st.spinner("Improving ticket..."):
                                improved = ai_assistant.improve_text(st.session_state.current_ticket_desc, "professional")
                                st.session_state['improved_ticket'] = improved
                                st.success("Description improved!")
                                st.rerun()
                        except:
                            st.error("AI unavailable")
                    else:
                        st.error("AI features are currently unavailable.")
                
                if st.button("💡 Get Writing Tips", key="ticket_tips_btn"):
                    ai_assistant = get_ai_assistant()
                    if ai_assistant:
                        try:
                            with st.spinner("Getting tips..."):
                                tips = ai_assistant.quick_improve_suggestions(st.session_state.current_ticket_desc, "general")
                                st.info(tips)
                        except:
                            st.error("Tips unavailable")
                    else:
                        st.error("AI features are currently unavailable.")
            else:
                st.info("Write your ticket description first to get improvement suggestions")
        
        # Display generated/improved content
        if 'generated_ticket' in st.session_state:
            st.markdown("**Generated Ticket Template:**")
            st.success(st.session_state['generated_ticket'])
        
        if 'improved_ticket' in st.session_state:
            st.markdown("**Improved Description:**")
            st.text_area("Copy this improved description:", st.session_state['improved_ticket'], height=100, key="improved_desc_display")
    
    # Support ticket form
    st.subheader("📝 Submit Support Ticket")
    
    with st.form("support_ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            support_name = st.text_input("Your Name*", placeholder="Enter your full name")
            support_email = st.text_input("Email Address*", placeholder="your.email@example.com")
        
        with col2:
            support_category = st.selectbox("Issue Category*", [
                "Technical Issue", "Account Problem", "Product Listing Help", 
                "Payment/Order Issue", "Feature Request", "General Question", "Bug Report"
            ])
            priority_level = st.selectbox("Priority Level*", [
                "Low - General inquiry", 
                "Medium - Need help soon", 
                "High - Blocking my work", 
                "Urgent - Critical issue"
            ])
        
        subject = st.text_input("Subject*", 
                               value=st.session_state.get('ticket_subject', ''),
                               placeholder="Brief description of your issue",
                               key="subject_input")
        st.session_state['ticket_subject'] = subject
        
        description = st.text_area(
            "Detailed Description*", 
            value=st.session_state.get('current_ticket_desc', ''),
            placeholder="Please provide as much detail as possible about your issue, including steps to reproduce if it's a technical problem...",
            height=150,
            key="description_input"
        )
        st.session_state['current_ticket_desc'] = description
        
        # Character count for description
        if description:
            char_count = len(description)
            color = "green" if char_count > 100 else "orange" if char_count > 50 else "red"
            st.markdown(f"<small style='color: {color}'>{char_count} characters (aim for 100+ for detailed support)</small>", unsafe_allow_html=True)
        
        # Attachment info
        st.info("📎 For files or screenshots, please mention them in your description and we'll follow up with secure upload instructions.")
        
        submitted = st.form_submit_button("🚀 Submit Support Ticket", use_container_width=True)
        
        if submitted:
            if support_name and support_email and subject and description:
                # Create support ticket using messaging system
                ticket_data = {
                    'sender_type': 'buyer',  # Using buyer type for support tickets
                    'sender_name': support_name,
                    'sender_email': support_email,
                    'product_id': None,  # No specific product for support tickets
                    'subject': f"[{support_category}] {subject}",
                    'message_content': f"Priority: {priority_level}\n\nCategory: {support_category}\n\nDescription:\n{description}",
                    'is_read': False
                }
                
                success = db_manager.send_message(ticket_data)
                if success:
                    st.success("🎉 Support ticket submitted successfully! We'll respond according to the priority level you selected.")
                    st.balloons()
                else:
                    st.error("❌ Failed to submit support ticket. Please try again or contact us directly.")
            else:
                st.error("⚠️ Please fill in all required fields marked with *")

with tab3:
    st.subheader("📚 Help Guides & Getting Started")
    
    # Getting Started Guide
    with st.expander("🚀 **Getting Started Guide for New Artisans**", expanded=True):
        st.markdown('<div class="help-category">', unsafe_allow_html=True)
        
        st.markdown("#### Welcome to TrueCraft! Here's how to get started:")
        
        st.markdown("##### Step 1: Create Your Profile")
        st.markdown("""
        - Go to the **Artisan Profile** page
        - Fill in your personal information and craft specialties  
        - Write a compelling bio using our AI assistant
        - Add social media links and contact information
        """)
        
        st.markdown("##### Step 2: Add Your First Product")
        st.markdown("""
        - Navigate to **Product Listings**
        - Click "Add New Product" and fill in details
        - Upload high-quality product images
        - Use AI assistance for descriptions and pricing
        """)
        
        st.markdown("##### Step 3: Optimize and Promote")
        st.markdown("""
        - Review analytics to understand performance
        - Respond to customer messages promptly
        - Update listings based on feedback
        - Add more products to expand your catalog
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Platform Features Guide
    with st.expander("🎨 **Platform Features Overview**"):
        st.markdown('<div class="help-category">', unsafe_allow_html=True)
        
        st.markdown("#### Key Features and How to Use Them:")
        
        st.markdown("##### 🤖 AI Assistant")
        st.markdown("""
        Get help with product descriptions, pricing suggestions, and profile optimization. 
        The AI analyzes your inputs and provides tailored recommendations.
        """)
        
        st.markdown("##### 📊 Analytics Dashboard")
        st.markdown("""
        Track product views, favorites, and performance metrics. Use insights to 
        improve your listings and understand customer preferences.
        """)
        
        st.markdown("##### 💬 Messaging System")
        st.markdown("""
        Communicate directly with potential customers. Manage inquiries, negotiate 
        custom orders, and build relationships.
        """)
        
        st.markdown("##### ⭐ Reviews & Ratings")
        st.markdown("""
        Collect customer feedback to build trust and credibility. Monitor reviews 
        and respond to customer concerns.
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Best Practices
    with st.expander("🌟 **Best Practices for Success**"):
        st.markdown('<div class="help-category">', unsafe_allow_html=True)
        
        st.markdown("#### Tips for Artisan Success:")
        
        st.markdown("##### 📷 Product Photography")
        st.markdown("""
        - Use natural lighting when possible
        - Show multiple angles and details
        - Include size references (coins, hands, etc.)
        - Keep backgrounds clean and uncluttered
        """)
        
        st.markdown("##### ✍️ Writing Compelling Descriptions")
        st.markdown("""
        - Tell the story behind your piece
        - Highlight unique materials and techniques
        - Mention care instructions and durability
        - Use emotional language that connects with buyers
        """)
        
        st.markdown("##### 💰 Pricing Strategies")
        st.markdown("""
        - Factor in materials, time, and skill level
        - Research similar products in the market
        - Consider offering different price points
        - Don't undervalue your artistic work
        """)
        
        st.markdown("##### 🤝 Customer Relations")
        st.markdown("""
        - Respond to messages within 24 hours
        - Be clear about shipping times and costs
        - Offer customization when possible
        - Follow up after sales for feedback
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.subheader("🔧 Troubleshooting Common Issues")
    
    # Common technical issues
    troubleshooting_guides = [
        {
            "title": "🖼️ Image Upload Problems",
            "symptoms": "Images won't upload, error messages, or very slow uploads",
            "solutions": [
                "Check file size: Images must be under 10MB",
                "Verify format: Use JPEG, PNG, or WebP only",
                "Try compressing images using online tools",
                "Clear browser cache and cookies",
                "Try a different browser or device",
                "Check internet connection stability"
            ]
        },
        {
            "title": "🤖 AI Assistant Not Responding",
            "symptoms": "AI suggestions not loading, timeout errors, or blank responses",
            "solutions": [
                "Refresh the page and try again",
                "Check your internet connection",
                "Try with shorter input text",
                "Clear browser cache",
                "Disable browser extensions temporarily",
                "Contact support if issue persists"
            ]
        },
        {
            "title": "💾 Data Not Saving",
            "symptoms": "Changes lost after saving, form submissions failing",
            "solutions": [
                "Ensure all required fields are filled",
                "Check for stable internet connection",
                "Don't navigate away while saving",
                "Try saving smaller chunks of data",
                "Clear browser cache and reload",
                "Use a different browser to test"
            ]
        },
        {
            "title": "📊 Analytics Not Updating",
            "symptoms": "View counts not increasing, outdated data in analytics",
            "solutions": [
                "Analytics update every few hours",
                "Refresh the analytics page",
                "Check if you're viewing your own products (self-views don't count)",
                "Wait 24 hours for data synchronization",
                "Contact support for persistent issues"
            ]
        },
        {
            "title": "💬 Messages Not Appearing",
            "symptoms": "Missing messages, notifications not working",
            "solutions": [
                "Check spam/junk folders for email notifications",
                "Verify your email address in profile settings",
                "Refresh the Messages page",
                "Check message filters and categories",
                "Ensure JavaScript is enabled in browser"
            ]
        }
    ]
    
    for guide in troubleshooting_guides:
        with st.expander(f"**{guide['title']}**"):
            st.markdown(f"""
            <div class="troubleshooting-card">
                <p><strong>Symptoms:</strong> {guide['symptoms']}</p>
                <p><strong>Solutions to try:</strong></p>
                <ul>
                    {''.join([f'<li>{solution}</li>' for solution in guide['solutions']])}
                </ul>
                <p><em>If none of these solutions work, please contact our support team with details about your specific situation.</em></p>
            </div>
            """, unsafe_allow_html=True)
    
    # Self-help tools
    st.divider()
    st.subheader("🛠️ Self-Help Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Clear Browser Cache Instructions", use_container_width=True):
            st.info("""
            **To clear your browser cache:**
            
            **Chrome/Edge:** Press Ctrl+Shift+Del (Windows) or Cmd+Shift+Del (Mac)
            **Firefox:** Press Ctrl+Shift+Del (Windows) or Cmd+Shift+Del (Mac)
            **Safari:** Press Cmd+Option+E (Mac)
            
            Select "Cached images and files" and click Clear data.
            """)
    
    with col2:
        if st.button("🌐 Browser Compatibility Check", use_container_width=True):
            st.info("""
            **Recommended browsers:**
            - Chrome 90+ ✅
            - Firefox 88+ ✅  
            - Safari 14+ ✅
            - Edge 90+ ✅
            
            Please update your browser if you're using an older version.
            """)

with tab5:
    st.subheader("📖 Resources & Documentation")
    
    # Resource categories
    resource_categories = {
        "📱 Platform Resources": [
            {"title": "User Manual (PDF)", "description": "Complete guide to using all platform features", "link": "#"},
            {"title": "Video Tutorials", "description": "Step-by-step video guides for common tasks", "link": "#"},
            {"title": "API Documentation", "description": "For developers integrating with our platform", "link": "#"},
            {"title": "Mobile App Guide", "description": "Using ArtisanAI on mobile devices", "link": "#"}
        ],
        "🎨 Artisan Resources": [
            {"title": "Photography Tips Guide", "description": "Professional tips for product photography", "link": "#"},
            {"title": "Pricing Calculator", "description": "Tool to help calculate fair pricing for your work", "link": "#"},
            {"title": "Market Research Tools", "description": "Understand your competition and target market", "link": "#"},
            {"title": "Craft Business Basics", "description": "Legal and business considerations for artisans", "link": "#"}
        ],
        "🤝 Community": [
            {"title": "Artisan Forum", "description": "Connect with other artisans and share experiences", "link": "#"},
            {"title": "Success Stories", "description": "Learn from successful artisans on our platform", "link": "#"},
            {"title": "Monthly Newsletters", "description": "Tips, updates, and featured artisans", "link": "#"},
            {"title": "Events & Workshops", "description": "Online and local events for skill building", "link": "#"}
        ],
        "🔧 Technical Support": [
            {"title": "System Status", "description": "Current platform status and known issues", "link": "#"},
            {"title": "Release Notes", "description": "Latest features and improvements", "link": "#"},
            {"title": "Browser Requirements", "description": "Technical requirements and compatibility", "link": "#"},
            {"title": "Data Export Tools", "description": "Download your data and analytics", "link": "#"}
        ]
    }
    
    for category, resources in resource_categories.items():
        with st.expander(f"**{category}**", expanded=False):
            for resource in resources:
                st.markdown(f"""
                <div class="resource-link">
                    <h5>{resource['title']}</h5>
                    <p>{resource['description']}</p>
                    <a href="{resource['link']}" target="_blank">Access Resource →</a>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Contact information
    st.subheader("📞 Direct Contact Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Support Hours:**
        - Monday-Friday: 9 AM - 6 PM EST
        - Saturday: 10 AM - 4 PM EST  
        - Sunday: Closed
        
        **Emergency Support:**
        - Available 24/7 for critical issues
        - Response within 2 hours
        """)
    
    with col2:
        st.markdown("""
        **Contact Methods:**
        - 📧 Email: support@artisanai.com
        - 📱 Phone: 1-800-ARTISAN
        - 💬 Live Chat: Available during business hours
        - 🎫 Support Tickets: Use form above (recommended)
        """)

# Footer with helpful links
st.divider()
st.markdown("""
<div style="text-align: center; padding: 2rem 0; background: #f8f9fa; border-radius: 8px;">
    <h4>🎨 Need More Help?</h4>
    <p>We're here to support your artisan journey every step of the way!</p>
    <p><strong>Quick Links:</strong> 
        <a href="#" style="margin: 0 10px;">Privacy Policy</a> | 
        <a href="#" style="margin: 0 10px;">Terms of Service</a> | 
        <a href="#" style="margin: 0 10px;">Community Guidelines</a>
    </p>
</div>
""", unsafe_allow_html=True)