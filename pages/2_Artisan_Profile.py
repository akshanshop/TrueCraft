import streamlit as st
from datetime import datetime
from utils.ai_assistant import AIAssistant
from utils.database_factory import create_database_service
from utils.image_handler import ImageHandler
from utils.ai_ui_components import AIUIComponents, render_ai_business_toolkit, render_brand_voice_analyzer, render_content_calendar_generator, render_seasonal_marketing_generator

# Initialize components
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

image_handler = ImageHandler()
ai_ui = AIUIComponents()

def render_profile_create_edit(current_profile):
    """Render the profile creation/editing form"""
    st.subheader("✏️ " + ("Edit" if current_profile is not None else "Create") + " Your Profile")
    
    # AI-Powered Profile Creation Assistant
    ai_ui.ai_powered_form_section(
        "🤖 AI-Powered Profile Assistant", 
        "Get intelligent assistance for your bio, business descriptions, and social media content!"
    )
    
    with st.form("profile_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Basic information
            st.subheader("Basic Information")
            artisan_name = st.text_input(
                "Artisan/Business Name*", 
                value=current_profile['name'] if current_profile is not None else "",
                placeholder="e.g., Sarah's Ceramics Studio"
            )
            
            location = st.text_input(
                "Location", 
                value=current_profile['location'] if current_profile is not None else "",
                placeholder="e.g., Portland, Oregon"
            )
            
            specialties = st.multiselect(
                "Specialties/Craft Types*",
                ["Pottery & Ceramics", "Jewelry & Accessories", "Textiles & Clothing", 
                 "Woodworking", "Metalwork", "Art & Paintings", "Home Decor", "Other"],
                default=current_profile['specialties'].split(', ') if current_profile is not None and current_profile['specialties'] else []
            )
            
            years_experience = st.number_input(
                "Years of Experience",
                min_value=0,
                max_value=50,
                value=int(current_profile['years_experience']) if current_profile is not None else 1
            )
        
        with col2:
            # Profile photo
            st.subheader("Profile Photo")
            if current_profile is not None and current_profile['profile_image']:
                st.image(current_profile['profile_image'], width=200, caption="Current photo")
            
            uploaded_image = st.file_uploader(
                "Upload profile photo",
                type=['png', 'jpg', 'jpeg'],
                help="Upload a professional photo of yourself or your workshop"
            )
        
        # AI-Enhanced Bio Section
        st.subheader("Your Story")
        # Get AI assistant safely
        ai_assistant = get_ai_assistant()
        if ai_assistant:
            bio = ai_ui.ai_text_field(
                "Artist Bio/Story*",
                ai_assistant.generate_artist_bio,
                "artisan_bio",
                help_text="Share your journey, inspiration, and what makes your craft unique",
                height=200,
                name=artisan_name or "your artisan business",
                craft_type=", ".join(specialties) if specialties else "your craft",
                experience=f"{years_experience} years" if years_experience else "beginner",
                inspiration="your creative inspiration",
                unique_aspect="what makes your work special"
            )
        else:
            bio = st.text_area(
                "Artist Bio/Story*",
                value=st.session_state.get('artisan_bio', ''),
                placeholder="Share your journey, inspiration, and what makes your craft unique",
                height=200,
                key="artisan_bio_fallback"
            )
            st.session_state['artisan_bio'] = bio
        
        # Contact and social
        st.subheader("Contact & Social Media")
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input(
                "Email", 
                value=current_profile['email'] if current_profile is not None else "",
                placeholder="your.email@example.com"
            )
            phone = st.text_input(
                "Phone", 
                value=current_profile['phone'] if current_profile is not None else "",
                placeholder="(555) 123-4567"
            )
            website = st.text_input(
                "Website", 
                value=current_profile['website'] if current_profile is not None else "",
                placeholder="https://yourwebsite.com"
            )
        
        with col2:
            instagram = st.text_input(
                "Instagram", 
                value=current_profile['instagram'] if current_profile is not None else "",
                placeholder="@yourusername"
            )
            facebook = st.text_input(
                "Facebook", 
                value=current_profile['facebook'] if current_profile is not None else "",
                placeholder="facebook.com/yourpage"
            )
            etsy = st.text_input(
                "Etsy Shop", 
                value=current_profile['etsy'] if current_profile is not None else "",
                placeholder="etsy.com/shop/yourshop"
            )
        
        # Additional details
        with st.expander("Additional Details"):
            # Get AI assistant safely for education section
            ai_assistant = get_ai_assistant()
            if ai_assistant:
                education = ai_ui.ai_text_field(
                    "Education/Training",
                    ai_assistant.generate_custom_content,
                    "education_section",
                    help_text="List relevant education, workshops, or training",
                    height=100,
                    content_type="education and training background",
                    context=f"artisan specializing in {', '.join(specialties) if specialties else 'handmade crafts'}",
                    specific_request="professional education and training summary"
                )
            else:
                education = st.text_area(
                    "Education/Training",
                    value=st.session_state.get('education_section', ''),
                    placeholder="List relevant education, workshops, or training",
                    height=100,
                    key="education_fallback"
                )
                st.session_state['education_section'] = education
            
            ai_assistant = get_ai_assistant()
            if ai_assistant:
                awards = ai_ui.ai_text_field(
                    "Awards/Recognition",
                    ai_assistant.generate_custom_content,
                    "awards_section",
                    help_text="List awards, features, or recognition you've received",
                    height=100,
                    content_type="achievements and recognition",
                    context=f"artisan with {years_experience} years experience in {', '.join(specialties) if specialties else 'crafts'}",
                    specific_request="professional achievements and recognition summary"
                )
            else:
                awards = st.text_area(
                    "Awards/Recognition",
                    value=st.session_state.get('awards_section', ''),
                    placeholder="List awards, features, or recognition you've received",
                    height=100,
                    key="awards_fallback"
                )
                st.session_state['awards_section'] = awards
            
            ai_assistant = get_ai_assistant()
            if ai_assistant:
                inspiration = ai_ui.ai_text_field(
                    "Inspiration/Influences",
                    ai_assistant.generate_custom_content,
                    "inspiration_section",
                    help_text="Describe what or who inspires your work",
                    height=100,
                    content_type="creative inspiration and influences",
                    context=f"artisan creating {', '.join(specialties) if specialties else 'handmade items'}",
                    specific_request="description of creative inspiration and artistic influences"
                )
            else:
                inspiration = st.text_area(
                    "Inspiration/Influences",
                    value=st.session_state.get('inspiration_section', ''),
                    placeholder="Describe what or who inspires your work",
                    height=100,
                    key="inspiration_fallback"
                )
                st.session_state['inspiration_section'] = inspiration
        
        # Submit button
        submitted = st.form_submit_button(
            "💾 " + ("Update" if current_profile is not None else "Create") + " Profile", 
            use_container_width=True
        )
        
        if submitted:
            if artisan_name and specialties and bio:
                # Process profile image
                profile_image_data = None
                if uploaded_image:
                    profile_image_data = image_handler.process_uploaded_image(uploaded_image)
                elif current_profile is not None:
                    profile_image_data = current_profile['profile_image']
                
                # Create/update profile data
                profile_data = {
                    'name': artisan_name,
                    'location': location,
                    'specialties': ', '.join(specialties),
                    'years_experience': years_experience,
                    'bio': bio,
                    'email': email,
                    'phone': phone,
                    'website': website,
                    'instagram': instagram,
                    'facebook': facebook,
                    'etsy': etsy,
                    'education': education,
                    'awards': awards,
                    'inspiration': inspiration,
                    'profile_image': profile_image_data,
                    'created_at': current_profile['created_at'] if current_profile is not None else datetime.now(),
                    'updated_at': datetime.now()
                }
                
                # Save profile
                if current_profile is not None:
                    profile_id = int(current_profile['id'])  # Convert numpy.int64 to Python int
                    success = db_manager.update_profile(profile_id, profile_data)
                    message = "Profile updated successfully!"
                else:
                    success = db_manager.add_profile(profile_data)
                    message = "Profile created successfully!"
                
                if success:
                    st.success(f"🎉 {message}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to save profile. Please try again.")
            else:
                st.error("Please fill in all required fields (marked with *).")

def render_profile_view(current_profile):
    """Render the profile view section"""
    st.subheader("📋 Your Profile")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"# {current_profile['name']}")
        if current_profile['location']:
            st.markdown(f"📍 {current_profile['location']}")
        
        if current_profile['specialties']:
            st.markdown(f"🎨 **Specialties:** {current_profile['specialties']}")
        
        st.markdown(f"📅 **Experience:** {current_profile['years_experience']} years")
        
        if current_profile['bio']:
            st.subheader("About Me")
            st.write(current_profile['bio'])
    
    with col2:
        if current_profile['profile_image']:
            st.image(current_profile['profile_image'], width=250)
        else:
            st.info("No profile photo uploaded")
    
    # Contact information
    if any([current_profile['email'], current_profile['phone'], current_profile['website']]):
        st.subheader("Contact Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if current_profile['email']:
                st.write(f"📧 {current_profile['email']}")
        with col2:
            if current_profile['phone']:
                st.write(f"📞 {current_profile['phone']}")
        with col3:
            if current_profile['website']:
                st.write(f"🌐 {current_profile['website']}")
    
    # Social media
    social_links = []
    if current_profile['instagram']:
        social_links.append(f"📷 Instagram: {current_profile['instagram']}")
    if current_profile['facebook']:
        social_links.append(f"📘 Facebook: {current_profile['facebook']}")
    if current_profile['etsy']:
        social_links.append(f"🛒 Etsy: {current_profile['etsy']}")
    
    if social_links:
        st.subheader("Social Media")
        for link in social_links:
            st.write(link)
    
    # Additional details
    additional_sections = [
        ('Education/Training', current_profile['education']),
        ('Awards/Recognition', current_profile['awards']),
        ('Inspiration', current_profile['inspiration'])
    ]
    
    for title, content in additional_sections:
        if content:
            st.subheader(title)
            st.write(content)
    
    # Profile statistics
    products_df = db_manager.get_products()
    if not products_df.empty:
        st.subheader("Your Products")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Products", len(products_df))
        with col2:
            total_views = products_df['views'].sum()
            st.metric("Total Views", total_views)
        with col3:
            avg_price = products_df['price'].mean()
            st.metric("Average Price", f"${avg_price:.2f}")

def render_profile_ai_helper():
    """Render the AI writing assistant section"""
    st.subheader("✨ AI Writing Assistant")
    st.write("Get AI-powered help with writing compelling bios, product stories, and marketing content.")
    
    writing_type = st.selectbox(
        "What do you need help writing?",
        [
            "Artist Bio/Story",
            "Product Description", 
            "About My Process",
            "Social Media Post",
            "Email to Customers",
            "Artist Statement"
        ]
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if writing_type == "Artist Bio/Story":
            st.write("**Tell me about yourself and I'll help create a compelling bio:**")
            
            name = st.text_input("Your name/business name")
            craft_type = st.text_input("Your main craft/medium")
            experience = st.text_input("Years of experience or how you got started")
            inspiration = st.text_area("What inspires your work?")
            unique_aspect = st.text_area("What makes your work unique?")
            
            if st.button("✨ Generate Bio"):
                if name and craft_type:
                    ai_assistant = get_ai_assistant()
                    if ai_assistant:
                        with st.spinner("Generating your bio..."):
                            try:
                                bio = ai_assistant.generate_artist_bio(
                                    name, craft_type, experience, inspiration, unique_aspect
                                )
                                st.session_state.generated_bio = bio
                            except Exception as e:
                                st.error(f"Failed to generate bio: {str(e)}")
                    else:
                        st.error("AI features are currently unavailable. Please try again later.")
        
        elif writing_type == "Product Description":
            st.write("**Provide product details for an enhanced description:**")
            
            product_name = st.text_input("Product name")
            category = st.text_input("Category/type")
            materials = st.text_input("Materials used")
            features = st.text_area("Key features or benefits")
            
            if st.button("✨ Enhance Description"):
                if product_name and materials:
                    ai_assistant = get_ai_assistant()
                    if ai_assistant:
                        with st.spinner("Creating description..."):
                            try:
                                description = ai_assistant.generate_product_description(
                                    product_name, category, materials, features
                                )
                                st.session_state.generated_content = description
                            except Exception as e:
                                st.error(f"Failed to generate description: {str(e)}")
                    else:
                        st.error("AI features are currently unavailable. Please try again later.")
        
        elif writing_type == "Social Media Post":
            st.write("**Create engaging social media content:**")
            
            post_topic = st.text_input("What's the post about?", placeholder="New product launch, behind-the-scenes, etc.")
            platform = st.selectbox("Platform", ["Instagram", "Facebook", "Twitter", "General"])
            tone = st.selectbox("Tone", ["Professional", "Casual", "Inspirational", "Educational"])
            
            if st.button("✨ Create Post"):
                if post_topic:
                    ai_assistant = get_ai_assistant()
                    if ai_assistant:
                        with st.spinner("Creating post..."):
                            try:
                                post = ai_assistant.generate_social_media_post(
                                    post_topic, platform, tone
                                )
                                st.session_state.generated_content = post
                            except Exception as e:
                                st.error(f"Failed to generate post: {str(e)}")
                    else:
                        st.error("AI features are currently unavailable. Please try again later.")
        
        else:
            st.write("**Describe what you need help writing:**")
            context = st.text_area("Provide context and details", height=100)
            specific_request = st.text_area("What specifically do you need?", height=100)
            
            if st.button("✨ Get Writing Help"):
                if context and specific_request:
                    ai_assistant = get_ai_assistant()
                    if ai_assistant:
                        with st.spinner("Creating content..."):
                            try:
                                content = ai_assistant.generate_custom_content(
                                    writing_type, context, specific_request
                                )
                                st.session_state.generated_content = content
                            except Exception as e:
                                st.error(f"Failed to generate content: {str(e)}")
                    else:
                        st.error("AI features are currently unavailable. Please try again later.")
    
    with col2:
        st.write("**Tips for Better Results:**")
        st.info("""
        • Be specific with details
        • Mention your target audience
        • Include your brand personality
        • Specify the desired length
        • Mention any keywords to include
        """)
    
    # Display generated content
    if 'generated_bio' in st.session_state:
        st.subheader("🎯 Generated Bio")
        st.write(st.session_state.generated_bio)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy Bio"):
                st.write("Copy the text above to use in your profile!")
        with col2:
            if st.button("🔄 Generate New Version"):
                del st.session_state.generated_bio
                st.rerun()
    
    if 'generated_content' in st.session_state:
        st.subheader("🎯 Generated Content")
        st.write(st.session_state.generated_content)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy Content"):
                st.write("Copy the text above to use!")
        with col2:
            if st.button("🔄 Generate New Version"):
                del st.session_state.generated_content
                st.rerun()

st.set_page_config(
    page_title="Artisan Profile - TrueCraft", 
    page_icon="👤",
    layout="wide"
)

st.title("👤 Artisan Profile")
st.markdown("Create and manage your artisan profile with comprehensive AI-powered tools and advanced branding assistance")

# Add AI Business Toolkit Tab for Artisan Profile
tab1, tab2, tab3 = st.tabs(["👤 Profile Management", "🚀 AI Business Toolkit", "🎯 Branding & Marketing AI"])

with tab1:
    # Get existing profile
    profiles_df = db_manager.get_profiles()
    current_profile = profiles_df.iloc[0] if not profiles_df.empty else None

    # Sidebar
    with st.sidebar:
        st.subheader("Profile Actions")
        if current_profile is not None:
            profile_mode = st.radio("Choose Action", ["View Profile", "Edit Profile", "AI Writing Assistant"])
        else:
            profile_mode = st.radio("Choose Action", ["Create Profile", "AI Writing Assistant"])

    if profile_mode in ["Create Profile", "Edit Profile"]:
        render_profile_create_edit(current_profile)

    elif profile_mode == "View Profile":
        if current_profile is not None:
            render_profile_view(current_profile)
        else:
            st.info("No profile found. Create your profile to get started!")

    elif profile_mode == "AI Writing Assistant":
        render_profile_ai_helper()

    # Profile completion reminder
    if current_profile is None:
        st.info("💡 **Get Started:** Create your artisan profile to unlock all features and start building your online presence!")

with tab2:
    render_ai_business_toolkit()

with tab3:
    render_brand_voice_analyzer("_standalone")
    render_content_calendar_generator("_standalone")
    render_seasonal_marketing_generator("_standalone_profile")