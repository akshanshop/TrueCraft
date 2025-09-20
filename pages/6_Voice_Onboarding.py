import streamlit as st
import tempfile
import os
from utils.ai_assistant import AIAssistant
from utils.database_factory import create_database_service

# Initialize services
ai_assistant = AIAssistant()
db_manager = create_database_service()

st.set_page_config(
    page_title="Voice Onboarding - TrueCraft",
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS for voice interface
st.markdown("""
<style>
    .voice-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
    }
    .step-indicator {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .recording-button {
        font-size: 2rem;
        padding: 1rem 2rem;
        border-radius: 50px;
        border: none;
        background: #ff6b6b;
        color: white;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="voice-container">', unsafe_allow_html=True)
st.title("🎙️ AI-Powered Voice Onboarding")
st.markdown("*Welcome to TrueCraft! Let's tell your story in your own voice and language.*")
st.markdown('</div>', unsafe_allow_html=True)

# Language selection
languages = [
    "English", "Spanish", "French", "Hindi", "Mandarin", "Arabic", 
    "Portuguese", "Bengali", "Russian", "Japanese", "German", "Italian"
]

col1, col2 = st.columns(2)
with col1:
    selected_language = st.selectbox("🌍 Choose your preferred language:", languages)
with col2:
    voice_mode = st.selectbox("🎯 Onboarding mode:", ["Guided Interview", "Free Form", "Quick Setup"])

# Initialize session state for onboarding progress
if 'onboarding_step' not in st.session_state:
    st.session_state.onboarding_step = 0
if 'onboarding_data' not in st.session_state:
    st.session_state.onboarding_data = {}
if 'voice_responses' not in st.session_state:
    st.session_state.voice_responses = []

# Onboarding steps
onboarding_steps = [
    "welcome",
    "craft_expertise", 
    "business_goals",
    "product_portfolio",
    "cultural_heritage",
    "sustainability",
    "pricing_strategy",
    "market_positioning"
]

step_titles = {
    "welcome": "🌟 Welcome to TrueCraft",
    "craft_expertise": "🎨 Your Craft & Expertise", 
    "business_goals": "🎯 Business Goals",
    "product_portfolio": "📦 Product Portfolio",
    "cultural_heritage": "🏛️ Cultural Heritage",
    "sustainability": "🌱 Sustainability Practices",
    "pricing_strategy": "💰 Pricing Strategy",
    "market_positioning": "📈 Market Positioning"
}

# Progress indicator
current_step = st.session_state.onboarding_step
progress_percent = (current_step / len(onboarding_steps)) * 100

st.markdown(f'<div class="step-indicator">', unsafe_allow_html=True)
st.progress(progress_percent / 100)
st.markdown(f"**Step {current_step + 1} of {len(onboarding_steps)}:** {step_titles.get(onboarding_steps[current_step], 'Setup')}")
st.markdown('</div>', unsafe_allow_html=True)

# Current step content
if current_step < len(onboarding_steps):
    current_step_name = onboarding_steps[current_step]
    
    # Get AI guidance for current step
    user_input = st.session_state.get('last_voice_input', '')
    ai_guidance = ai_assistant.voice_onboarding_guide(
        current_step_name, 
        user_input, 
        selected_language
    )
    
    # Display AI guidance
    st.markdown("### 🤖 AI Guide")
    st.info(ai_guidance)
    
    # Voice recording section
    st.markdown("### 🎙️ Record Your Response")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Simulated voice recording (placeholder for actual audio recording)
        if st.button("🔴 Start Recording", use_container_width=True, type="primary"):
            st.success("Recording started! (Feature will be available with audio integration)")
            
        # Text input as fallback
        st.markdown("**Or type your response:**")
        text_response = st.text_area(
            "Your response:", 
            placeholder=f"Tell us about your {current_step_name.replace('_', ' ')}...",
            height=100
        )
    
    # Audio file upload for testing
    st.markdown("### 📁 Upload Audio File (Testing)")
    uploaded_audio = st.file_uploader(
        "Upload an audio file for transcription testing", 
        type=['wav', 'mp3', 'mp4', 'm4a']
    )
    
    if uploaded_audio is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(uploaded_audio.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            # Transcribe audio
            transcription_result = ai_assistant.transcribe_audio(tmp_file_path)
            
            if transcription_result['error']:
                st.error(f"Transcription failed: {transcription_result['error']}")
            else:
                st.success("Audio transcribed successfully!")
                transcribed_text = transcription_result['text']
                st.write(f"**Transcribed text:** {transcribed_text}")
                
                # Translate if needed
                if selected_language != "English":
                    translation_result = ai_assistant.translate_text(transcribed_text, "English")
                    if not translation_result['error']:
                        st.write(f"**English translation:** {translation_result['translated_text']}")
                        text_response = translation_result['translated_text']
                    else:
                        text_response = transcribed_text
                else:
                    text_response = transcribed_text
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️ Previous Step") and current_step > 0:
            st.session_state.onboarding_step -= 1
            st.rerun()
    
    with col2:
        if st.button("💾 Save & Continue", type="primary"):
            if text_response:
                # Store response
                st.session_state.onboarding_data[current_step_name] = text_response
                st.session_state.last_voice_input = text_response
                
                # Move to next step
                if current_step < len(onboarding_steps) - 1:
                    st.session_state.onboarding_step += 1
                    st.success("Response saved! Moving to next step...")
                    st.rerun()
                else:
                    st.success("Onboarding completed! Generating your profile...")
                    st.balloons()
            else:
                st.warning("Please provide a response before continuing.")
    
    with col3:
        if st.button("⏩ Skip Step"):
            if current_step < len(onboarding_steps) - 1:
                st.session_state.onboarding_step += 1
                st.rerun()

# Onboarding completion
else:
    st.success("🎉 Congratulations! Your voice onboarding is complete!")
    
    # Generate comprehensive profile using AI
    if st.session_state.onboarding_data:
        st.markdown("### 📋 Your Generated Profile")
        
        # Cultural storytelling
        if st.button("🏛️ Generate Cultural Story", use_container_width=True):
            artisan_data = {
                'name': st.session_state.onboarding_data.get('welcome', 'Unknown'),
                'craft': st.session_state.onboarding_data.get('craft_expertise', 'Various crafts'),
                'culture': st.session_state.onboarding_data.get('cultural_heritage', 'Not specified'),
                'experience': 'Experienced artisan',
                'techniques': st.session_state.onboarding_data.get('craft_expertise', 'Traditional methods'),
                'heritage': st.session_state.onboarding_data.get('cultural_heritage', 'Family traditions')
            }
            
            cultural_story = ai_assistant.cultural_storytelling(
                artisan_data.get('culture', 'Not specified'),
                artisan_data.get('craft', 'Various crafts'), 
                artisan_data.get('heritage', 'Family traditions')
            )
            st.markdown("#### 🌟 Your Cultural Story")
            st.write(cultural_story)
        
        # Business analysis
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💼 Generate Business Plan", use_container_width=True):
                business_guidance = ai_assistant.financial_literacy_guidance(
                    "business planning",
                    "beginner",
                    f"Artisan specializing in {st.session_state.onboarding_data.get('craft_expertise', 'handmade products')}"
                )
                st.markdown("#### 📈 Business Guidance")
                st.write(business_guidance)
        
        with col2:
            if st.button("🌱 Sustainability Assessment", use_container_width=True):
                product_data = {
                    'materials': st.session_state.onboarding_data.get('sustainability', 'Traditional materials'),
                    'production_method': 'Handmade',
                    'origin': 'Local artisan',
                    'packaging': 'Eco-friendly'
                }
                
                sustainability = ai_assistant.sustainability_assessment(
                    product_data.get('materials', 'Traditional materials'),
                    product_data.get('production_method', 'Handmade'),
                    product_data.get('packaging', 'Eco-friendly')
                )
                
                st.markdown("#### 🌿 Sustainability Assessment")
                st.write(sustainability)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Go to Dashboard", use_container_width=True):
            st.switch_page("TrueCraft.py")
    
    with col2:
        if st.button("📝 Create Product Listing", use_container_width=True):
            st.switch_page("pages/1_Product_Listings.py")
    
    with col3:
        if st.button("🔄 Restart Onboarding", use_container_width=True):
            # Reset onboarding state
            st.session_state.onboarding_step = 0
            st.session_state.onboarding_data = {}
            st.session_state.voice_responses = []
            st.rerun()

# Sidebar with help and resources
with st.sidebar:
    st.markdown("### 🆘 Voice Onboarding Help")
    
    st.markdown("""
    **How it works:**
    1. 🎤 Record your voice or type responses
    2. 🌍 Automatic translation if needed
    3. 🤖 AI generates personalized guidance
    4. 📊 Creates your artisan profile
    
    **Supported features:**
    - ✅ Multi-language support
    - ✅ Voice-to-text transcription
    - ✅ Cultural storytelling
    - ✅ Business guidance
    - ✅ Sustainability assessment
    """)
    
    if st.button("📞 Get Support", use_container_width=True):
        st.switch_page("pages/5_Support.py")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; padding: 1rem; color: #666;">
    <p>🎙️ Voice Onboarding powered by AI • Celebrating artisan heritage worldwide</p>
</div>
""", unsafe_allow_html=True)