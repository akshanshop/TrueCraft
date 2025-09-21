import streamlit as st
from utils.ai_assistant import AIAssistant
import time
from utils.i18n import i18n, t

class AIUIComponents:
    def __init__(self):
        # Initialize AI assistant with caching (lazy initialization)
        self.ai_assistant = None
    
    def _get_ai_assistant(self):
        """Get AI assistant with lazy initialization and error handling"""
        if self.ai_assistant is None:
            if 'ai_assistant' not in st.session_state:
                try:
                    st.session_state.ai_assistant = AIAssistant()
                except Exception as e:
                    st.warning(t("ai_features_unavailable"))
                    st.session_state.ai_assistant = None
            self.ai_assistant = st.session_state.ai_assistant
        return self.ai_assistant
    
    def inline_ai_button(self, target_key, ai_function, button_text=None, help_text=None, **kwargs):
        """
        Create an inline AI assistance button that populates a text field
        
        Args:
            target_key: The session state key for the target text field
            ai_function: The AI assistant method to call
            button_text: Text to display on the button
            help_text: Tooltip text for the button
            **kwargs: Arguments to pass to the AI function
        """
        if st.button(button_text or ("✨ " + t("ai_assist")), help=help_text or t("ai_assist_help"), key=f"ai_btn_{target_key}"):
            ai_assistant = self._get_ai_assistant()
            if ai_assistant is None:
                st.error(t("ai_features_unavailable"))
                return
            try:
                with st.spinner(t("ai_thinking")):
                    # Add current language to kwargs if not present
                    if 'target_language' not in kwargs:
                        kwargs['target_language'] = i18n.get_language()
                    result = ai_function(**kwargs)
                    if result and result.strip():
                        st.session_state[target_key] = result
                        st.success("✨ " + t("ai_content_generated"))
                        st.rerun()
                    else:
                        st.error(t("ai_response_error"))
            except Exception as e:
                print(f"AI UI Error: {str(e)}")  # Log server-side for debugging
                st.error(t("ai_technical_error"))
    
    def text_improvement_widget(self, text_input, field_type="general"):
        """
        Create a widget for improving existing text with AI suggestions
        
        Args:
            text_input: The text to improve
            field_type: Type of field for context-specific improvements
        """
        if not text_input or not text_input.strip():
            return None
            
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🔧 Improve", key=f"improve_{hash(text_input)}", help="Get AI suggestions to improve this text"):
                return "improve_requested"
        
        with col2:
            improvement_type = st.selectbox(
                "Improvement focus",
                ["general", "clarity", "professional", "engaging", "concise", "grammar"],
                key=f"improvement_type_{hash(text_input)}",
                label_visibility="collapsed"
            )
        
        return improvement_type if st.session_state.get(f"improve_{hash(text_input)}", False) else None
    
    def ai_suggestions_panel(self, text_content, field_type="general"):
        """
        Display AI improvement suggestions in an expandable panel
        
        Args:
            text_content: The text to analyze
            field_type: Type of field for context-specific suggestions
        """
        if not text_content or len(text_content.strip()) < 10:
            return
        
        with st.expander("💡 AI Suggestions", expanded=False):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Get Quick Tips", key=f"suggestions_{hash(text_content)}"):
                    ai_assistant = self._get_ai_assistant()
                    if ai_assistant is None:
                        st.error("AI suggestions are currently unavailable.")
                        return
                    try:
                        with st.spinner("Analyzing..."):
                            suggestions = ai_assistant.quick_improve_suggestions(text_content, field_type)
                            st.markdown("**Quick Improvements:**")
                            st.markdown(suggestions)
                    except Exception as e:
                        st.error("Unable to get suggestions right now.")
            
            with col2:
                if st.button("Improve Text", key=f"improve_full_{hash(text_content)}"):
                    ai_assistant = self._get_ai_assistant()
                    if ai_assistant is None:
                        st.error("AI text improvement is currently unavailable.")
                        return
                    try:
                        with st.spinner("Improving text..."):
                            improved = ai_assistant.improve_text(text_content, "general")
                            st.markdown("**Improved Version:**")
                            st.text_area("Copy this improved text:", improved, height=100, key=f"improved_{hash(text_content)}")
                            if st.button("📋 Copy to Clipboard", key=f"copy_{hash(text_content)}"):
                                # Note: Actual clipboard functionality would need additional implementation
                                st.info("Copy the text above to your clipboard")
                    except Exception as e:
                        st.error("Unable to improve text right now.")
    
    def message_templates_widget(self, message_type="general", product_name=None):
        """
        Create a widget for selecting and generating message templates
        
        Args:
            message_type: Type of message template to generate
            product_name: Product name for context if applicable
        """
        st.subheader("📝 Message Templates")
        
        template_types = {
            "inquiry": "General Product Inquiry",
            "custom_order": "Custom Order Request", 
            "shipping": "Shipping & Delivery Question",
            "payment": "Payment & Pricing Discussion",
            "follow_up": "Follow-up Message",
            "thank_you": "Thank You Message",
            "complaint": "Issue or Concern",
            "general": "General Business Inquiry"
        }
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_type = st.selectbox(
                "Choose template type:",
                list(template_types.keys()),
                format_func=lambda x: template_types[x],
                key="template_selector"
            )
        
        with col2:
            if st.button("Generate Template", key="generate_template_btn"):
                ai_assistant = self._get_ai_assistant()
                if ai_assistant is None:
                    st.error("AI message templates are currently unavailable.")
                    return
                try:
                    with st.spinner("Creating template..."):
                        template = ai_assistant.generate_message_template(
                            selected_type, 
                            product_name=product_name
                        )
                        st.session_state['generated_template'] = template
                        st.rerun()
                except Exception as e:
                    st.error("Unable to generate template right now.")
        
        # Display generated template
        if 'generated_template' in st.session_state:
            st.markdown("**Generated Template:**")
            st.text_area(
                "Your message template (edit as needed):",
                st.session_state['generated_template'],
                height=120,
                key="template_content"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✨ Generate New", key="new_template"):
                    ai_assistant = self._get_ai_assistant()
                    if ai_assistant is None:
                        st.error("AI message templates are currently unavailable.")
                        return
                    try:
                        with st.spinner("Creating new template..."):
                            template = ai_assistant.generate_message_template(
                                selected_type,
                                product_name=product_name
                            )
                            st.session_state['generated_template'] = template
                            st.rerun()
                    except Exception as e:
                        st.error("Unable to generate new template.")
            
            with col2:
                if st.button("🗑️ Clear", key="clear_template"):
                    if 'generated_template' in st.session_state:
                        del st.session_state['generated_template']
                        st.rerun()
    
    def ai_text_field(self, label, ai_function, key, help_text="", height=100, **ai_kwargs):
        """
        Create a text area with integrated AI assistance (form-safe version)
        
        Args:
            label: Label for the text area
            ai_function: AI function to call for assistance
            key: Unique key for the text area
            help_text: Help text for the field
            height: Height of the text area
            **ai_kwargs: Arguments to pass to AI function
        """
        # Main text area - form compatible
        text_value = st.text_area(
            label,
            value=st.session_state.get(key, ""),
            height=height,
            help=help_text,
            key=f"{key}_input"
        )
        
        # Store the text value in session state
        st.session_state[key] = text_value
        
        # Character count display
        if text_value:
            char_count = len(text_value)
            color = "green" if char_count > 50 else "orange" if char_count > 20 else "red"
            st.markdown(f"<small style='color: {color}'>{char_count} characters</small>", unsafe_allow_html=True)
        
        return text_value
    
    def ai_text_field_with_buttons(self, label, ai_function, key, help_text="", height=100, **ai_kwargs):
        """
        Create a text area with AI assistance buttons (NOT for use inside forms)
        
        Args:
            label: Label for the text area
            ai_function: AI function to call for assistance
            key: Unique key for the text area
            help_text: Help text for the field
            height: Height of the text area
            **ai_kwargs: Arguments to pass to AI function
        """
        # Main text area
        text_value = st.text_area(
            label,
            value=st.session_state.get(key, ""),
            height=height,
            help=help_text,
            key=f"{key}_input"
        )
        
        # Store the text value in session state
        st.session_state[key] = text_value
        
        # AI assistance buttons row
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            if st.button("✨ Generate", key=f"generate_{key}", help="Generate new content with AI"):
                ai_assistant = self._get_ai_assistant()
                if ai_assistant is None:
                    st.error("AI generation is currently unavailable.")
                    return text_value
                try:
                    with st.spinner("Generating..."):
                        result = ai_function(**ai_kwargs)
                        if result and result.strip():
                            st.session_state[key] = result
                            st.success("Generated! 🎉")
                            st.rerun()
                        else:
                            st.error("Generation failed")
                except Exception as e:
                    st.error("AI unavailable")
        
        with col2:
            if text_value and st.button("🔧 Improve", key=f"improve_{key}", help="Improve existing text"):
                ai_assistant = self._get_ai_assistant()
                if ai_assistant is None:
                    st.error("AI text improvement is currently unavailable.")
                    return text_value
                try:
                    with st.spinner("Improving..."):
                        improved = ai_assistant.improve_text(text_value, "general")
                        if improved and improved.strip():
                            st.session_state[key] = improved
                            st.success("Improved! ✨")
                            st.rerun()
                except Exception as e:
                    st.error("Improvement failed")
        
        with col3:
            if text_value and st.button("💡 Tips", key=f"tips_{key}", help="Get improvement suggestions"):
                ai_assistant = self._get_ai_assistant()
                if ai_assistant is None:
                    st.error("AI suggestions are currently unavailable.")
                    return text_value
                try:
                    with st.spinner("Analyzing..."):
                        suggestions = ai_assistant.quick_improve_suggestions(text_value, "general")
                        st.info(suggestions)
                except Exception as e:
                    st.error("Tips unavailable")
        
        with col4:
            if text_value:
                char_count = len(text_value)
                color = "green" if char_count > 50 else "orange" if char_count > 20 else "red"
                st.markdown(f"<small style='color: {color}'>{char_count} characters</small>", unsafe_allow_html=True)
        
        return text_value
    
    def smart_input_field(self, label, key, ai_suggestions=None, input_type="text", help_text=""):
        """
        Create an input field with optional AI suggestions
        
        Args:
            label: Label for the input field  
            key: Unique key for the field
            ai_suggestions: List of AI-generated suggestions
            input_type: Type of input (text, number, etc.)
            help_text: Help text for the field
        """
        # Initialize value with a default
        value = st.session_state.get(key, "" if input_type == "text" else 0)
        
        if input_type == "text":
            value = st.text_input(label, value=st.session_state.get(key, ""), help=help_text, key=f"{key}_input")
        elif input_type == "number":
            value = st.number_input(label, value=st.session_state.get(key, 0), help=help_text, key=f"{key}_input")
        else:
            # Fallback for unsupported input types
            value = st.text_input(label, value=st.session_state.get(key, ""), help=help_text, key=f"{key}_input")
        
        st.session_state[key] = value
        
        # Show AI suggestions if provided
        if ai_suggestions and len(ai_suggestions) > 0:
            st.markdown("**AI Suggestions:**")
            cols = st.columns(min(len(ai_suggestions), 3))
            for i, suggestion in enumerate(ai_suggestions[:3]):
                with cols[i % 3]:
                    if st.button(f"Use: {suggestion[:30]}...", key=f"suggestion_{key}_{i}"):
                        st.session_state[key] = suggestion
                        st.rerun()
        
        return value
    
    def ai_powered_form_section(self, title, ai_help_text="Get AI assistance for this section"):
        """
        Create a form section with integrated AI help
        
        Args:
            title: Title of the form section
            ai_help_text: Help text explaining AI assistance
        """
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(title)
        
        with col2:
            with st.popover("🤖 AI Help"):
                st.markdown(f"**{title} AI Assistance**")
                st.write(ai_help_text)
                st.markdown("*Click AI buttons next to fields for help*")
    
    def review_assistance_widget(self, product_category=None, rating=5):
        """
        Create a widget for AI-assisted review writing
        
        Args:
            product_category: Category of product being reviewed
            rating: Star rating for the review
        """
        st.markdown("### 🤖 AI Review Assistant")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Review Template", key="generate_review_template"):
                ai_assistant = self._get_ai_assistant()
                if ai_assistant is None:
                    st.error("AI review templates are currently unavailable.")
                    return
                try:
                    with st.spinner("Creating review template..."):
                        template = ai_assistant.generate_review_template(
                            product_category or "handmade product", 
                            rating
                        )
                        st.session_state['review_template'] = template
                        st.rerun()
                except Exception as e:
                    st.error("Unable to generate review template.")
        
        with col2:
            if st.button("Improve My Review", key="improve_review"):
                if 'current_review_text' in st.session_state and st.session_state.current_review_text:
                    ai_assistant = self._get_ai_assistant()
                    if ai_assistant is None:
                        st.error("AI text improvement is currently unavailable.")
                        return
                    try:
                        with st.spinner("Improving review..."):
                            improved = ai_assistant.improve_text(
                                st.session_state.current_review_text, 
                                "general"
                            )
                            st.session_state['improved_review'] = improved
                            st.rerun()
                    except Exception as e:
                        st.error("Unable to improve review.")
                else:
                    st.warning("Write your review first, then click to improve it.")
        
        # Display templates/improvements
        if 'review_template' in st.session_state:
            st.markdown("**Review Template:**")
            st.info(st.session_state['review_template'])
        
        if 'improved_review' in st.session_state:
            st.markdown("**Improved Review:**")
            st.success(st.session_state['improved_review'])

# Utility functions for common AI operations
def create_ai_components():
    """Factory function to create AI UI components instance"""
    return AIUIComponents()

def show_ai_loading(message="AI is working..."):
    """Show a consistent loading animation for AI operations"""
    return st.spinner(message)

def display_ai_error(error_message="AI assistance temporarily unavailable"):
    """Display a consistent error message for AI failures"""
    st.error(f"🤖 {error_message}")

def display_ai_success(message="AI content generated successfully!"):
    """Display a consistent success message for AI operations"""
    st.success(f"✨ {message}")

# ===== ENHANCED AI BUSINESS TOOLKIT COMPONENTS =====

def get_ai_assistant():
    """Get AI assistant instance with error handling"""
    try:
        if 'ai_assistant' not in st.session_state:
            st.session_state.ai_assistant = AIAssistant()
        return st.session_state.ai_assistant
    except Exception as e:
        st.warning("AI features are currently unavailable. Please check your API key configuration.")
        return None

def render_seo_title_generator(form_key_suffix=""):
    """Render SEO-optimized title generator"""
    st.subheader("🔍 SEO Title Generator")
    st.write("Generate search engine optimized product titles that attract buyers")
    
    form_key = f"seo_title_generator{form_key_suffix}"
    with st.form(form_key):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name")
            category = st.selectbox("Category", ["Jewelry", "Home Decor", "Clothing", "Art", "Pottery", "Woodwork", "Textiles", "Other"])
        with col2:
            keywords = st.text_input("Target Keywords (optional)", placeholder="handmade, custom, artisan")
        
        if st.form_submit_button("Generate SEO Titles", type="primary"):
            if product_name and category:
                with st.spinner("Generating SEO-optimized titles..."):
                    try:
                        ai = get_ai_assistant()
                        if ai:
                            result = ai.generate_seo_optimized_title(product_name, category, keywords)
                            st.success("SEO titles generated!")
                            st.markdown("**Generated SEO-Optimized Titles:**")
                            st.write(result)
                        else:
                            st.error("AI features are currently unavailable. Please check your API key configuration.")
                    except Exception as e:
                        st.error(f"Error generating SEO titles: {str(e)}")
            else:
                st.warning("Please fill in all required fields")

def render_pricing_analyzer(form_key_suffix=""):
    """Render comprehensive pricing analysis tool"""
    st.subheader("💰 Pricing Analysis & Strategy")
    st.write("Get AI-powered pricing recommendations based on materials, time, and market factors")
    
    form_key = f"pricing_analyzer{form_key_suffix}"
    with st.form(form_key):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product Name")
            materials = st.text_area("Materials Used", placeholder="Sterling silver, gemstones, etc.")
            time_hours = st.number_input("Hours to Create", min_value=0.5, step=0.5)
        with col2:
            skill_level = st.selectbox("Skill Level Required", ["Beginner", "Intermediate", "Advanced", "Expert"])
            category = st.selectbox("Product Category", ["Jewelry", "Home Decor", "Clothing", "Art", "Pottery", "Woodwork", "Textiles", "Other"])
        
        if st.form_submit_button("Analyze Pricing", type="primary"):
            if product_name and materials and time_hours > 0:
                with st.spinner("Analyzing pricing strategy..."):
                    try:
                        ai = get_ai_assistant()
                        if ai:
                            result = ai.generate_pricing_analysis(product_name, materials, time_hours, skill_level, category)
                            st.success("Pricing analysis complete!")
                            st.markdown("**Pricing Analysis & Recommendations:**")
                            st.write(result)
                        else:
                            st.error("AI features are currently unavailable. Please check your API key configuration.")
                    except Exception as e:
                        st.error(f"Error generating pricing analysis: {str(e)}")
            else:
                st.warning("Please fill in all required fields")

def render_photography_tips_generator(form_key_suffix=""):
    """Render personalized product photography tips generator"""
    st.subheader("📸 Product Photography Tips")
    st.write("Get personalized photography advice for your specific products")
    
    form_key = f"photography_tips{form_key_suffix}"
    with st.form(form_key):
        col1, col2 = st.columns(2)
        with col1:
            product_type = st.text_input("Product Type", placeholder="e.g., handmade necklace, ceramic bowl")
            materials = st.text_input("Main Materials", placeholder="e.g., silver, wood, fabric")
        with col2:
            setting = st.selectbox("Photography Setting", ["home", "studio", "outdoor", "workshop"])
        
        if st.form_submit_button("Get Photography Tips", type="primary"):
            if product_type and materials:
                with st.spinner("Generating photography tips..."):
                    try:
                        ai = get_ai_assistant()
                        if ai:
                            result = ai.generate_product_photography_tips(product_type, materials, setting)
                            st.success("Photography tips generated!")
                            st.markdown("**Personalized Photography Tips:**")
                            st.write(result)
                        else:
                            st.error("AI features are currently unavailable. Please check your API key configuration.")
                    except Exception as e:
                        st.error(f"Error generating photography tips: {str(e)}")
            else:
                st.warning("Please fill in the product type and materials")

def render_seasonal_marketing_generator(form_key_suffix=""):
    """Render seasonal marketing content generator"""
    st.subheader("🎄 Seasonal Marketing Content")
    st.write("Create targeted seasonal marketing content for holidays and special occasions")
    
    form_key = f"seasonal_marketing{form_key_suffix}"
    with st.form(form_key):
        col1, col2 = st.columns(2)
        with col1:
            products_list = st.text_area("Your Products", placeholder="List your main products...")
            season_or_holiday = st.selectbox("Season/Holiday", ["Christmas", "Valentine's Day", "Mother's Day", "Halloween", "Spring", "Summer", "Fall", "Winter", "Back to School", "Wedding Season", "Other"])
        with col2:
            target_audience = st.selectbox("Target Audience", ["general", "gift buyers", "home decorators", "fashion enthusiasts", "collectors", "young adults", "families"])
        
        if st.form_submit_button("Generate Marketing Content", type="primary"):
            if products_list:
                with st.spinner("Creating seasonal marketing content..."):
                    try:
                        ai = get_ai_assistant()
                        if ai:
                            result = ai.generate_seasonal_marketing_content(products_list, season_or_holiday, target_audience)
                            st.success("Seasonal marketing content generated!")
                            st.markdown("**Seasonal Marketing Ideas:**")
                            st.write(result)
                        else:
                            st.error("AI features are currently unavailable. Please check your API key configuration.")
                    except Exception as e:
                        st.error(f"Error generating seasonal content: {str(e)}")
            else:
                st.warning("Please describe your products")

def render_brand_voice_analyzer(form_key_suffix=""):
    """Render brand voice analysis and messaging strategy tool"""
    st.subheader("🎯 Brand Voice & Messaging Strategy")
    st.write("Analyze your brand and get personalized messaging recommendations")
    
    form_key = f"brand_voice_analyzer{form_key_suffix}"
    with st.form(form_key):
        bio = st.text_area("Your Bio/Story", placeholder="Tell us about yourself and your craft...")
        products_description = st.text_area("Products Description", placeholder="Describe your products and what makes them unique...")
        target_customers = st.text_area("Target Customers", placeholder="Describe your ideal customers...")
        
        if st.form_submit_button("Analyze Brand Voice", type="primary"):
            if bio and products_description:
                with st.spinner("Analyzing your brand voice..."):
                    try:
                        ai = get_ai_assistant()
                        if ai:
                            result = ai.generate_brand_voice_analysis(bio, products_description, target_customers)
                            st.success("Brand voice analysis complete!")
                            st.markdown("**Brand Voice & Messaging Strategy:**")
                            st.write(result)
                        else:
                            st.error("AI features are currently unavailable. Please check your API key configuration.")
                    except Exception as e:
                        st.error(f"Error analyzing brand voice: {str(e)}")
            else:
                st.warning("Please fill in your bio and product description")

def render_content_calendar_generator(form_key_suffix=""):
    """Render content calendar generator for social media"""
    st.subheader("📅 Content Calendar Generator")
    st.write("Generate a comprehensive 4-week content calendar for your social media")
    
    form_key = f"content_calendar{form_key_suffix}"
    with st.form(form_key):
        col1, col2 = st.columns(2)
        with col1:
            business_type = st.text_input("Business Type", placeholder="e.g., handmade jewelry, pottery studio")
            posting_frequency = st.selectbox("Posting Frequency", ["daily", "every other day", "3 times per week", "twice a week", "weekly"])
        with col2:
            special_events = st.text_input("Special Events (optional)", placeholder="craft fairs, shop anniversaries, etc.")
        
        if st.form_submit_button("Generate Content Calendar", type="primary"):
            if business_type:
                with st.spinner("Creating your content calendar..."):
                    try:
                        ai = get_ai_assistant()
                        if ai:
                            result = ai.generate_content_calendar(business_type, posting_frequency, special_events)
                            st.success("Content calendar generated!")
                            st.markdown("**4-Week Content Calendar:**")
                            st.write(result)
                        else:
                            st.error("AI features are currently unavailable. Please check your API key configuration.")
                    except Exception as e:
                        st.error(f"Error generating content calendar: {str(e)}")
            else:
                st.warning("Please describe your business type")

def render_competitive_analysis_generator(form_key_suffix=""):
    """Render competitive analysis tool"""
    st.subheader("⚖️ Competitive Analysis")
    st.write("Get insights on market positioning and competitive advantages")
    
    form_key = f"competitive_analysis{form_key_suffix}"
    with st.form(form_key):
        col1, col2 = st.columns(2)
        with col1:
            product_type = st.text_input("Product Type", placeholder="e.g., handmade ceramic mugs")
            price_range = st.text_input("Your Price Range", placeholder="e.g., $25-45")
        with col2:
            unique_features = st.text_area("Unique Features", placeholder="What makes your products special?")
        
        if st.form_submit_button("Analyze Competition", type="primary"):
            if product_type and price_range and unique_features:
                with st.spinner("Analyzing competitive landscape..."):
                    try:
                        ai = get_ai_assistant()
                        if ai:
                            result = ai.generate_competitive_analysis(product_type, price_range, unique_features)
                            st.success("Competitive analysis complete!")
                            st.markdown("**Competitive Analysis & Strategy:**")
                            st.write(result)
                        else:
                            st.error("AI features are currently unavailable. Please check your API key configuration.")
                    except Exception as e:
                        st.error(f"Error generating competitive analysis: {str(e)}")
            else:
                st.warning("Please fill in all fields")

def render_ai_business_toolkit():
    """Render comprehensive AI business toolkit with all advanced features"""
    st.header("🚀 Advanced AI Business Toolkit")
    st.write("Comprehensive AI-powered tools to grow your artisan business")
    
    # Create tabs for different tool categories
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Marketing & SEO", "📸 Content & Creative", "📈 Business Strategy", "🎯 Brand & Analysis"])
    
    with tab1:
        st.markdown("### Marketing & SEO Tools")
        col1, col2 = st.columns(2)
        with col1:
            render_seo_title_generator("_toolkit")
        with col2:
            render_seasonal_marketing_generator("_toolkit")
    
    with tab2:
        st.markdown("### Content & Creative Tools")
        col1, col2 = st.columns(2)
        with col1:
            render_photography_tips_generator("_toolkit")
        with col2:
            render_content_calendar_generator("_toolkit")
    
    with tab3:
        st.markdown("### Business Strategy Tools")
        render_pricing_analyzer("_toolkit")
    
    with tab4:
        st.markdown("### Brand & Analysis Tools")
        col1, col2 = st.columns(2)
        with col1:
            render_brand_voice_analyzer("_toolkit")
        with col2:
            render_competitive_analysis_generator("_toolkit")