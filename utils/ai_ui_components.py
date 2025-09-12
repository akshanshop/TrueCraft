import streamlit as st
from utils.ai_assistant import AIAssistant
import time

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
                    st.warning("AI features are currently unavailable. Some functionality may be limited.")
                    st.session_state.ai_assistant = None
            self.ai_assistant = st.session_state.ai_assistant
        return self.ai_assistant
    
    def inline_ai_button(self, target_key, ai_function, button_text="✨ AI Assist", help_text="Get AI writing assistance", **kwargs):
        """
        Create an inline AI assistance button that populates a text field
        
        Args:
            target_key: The session state key for the target text field
            ai_function: The AI assistant method to call
            button_text: Text to display on the button
            help_text: Tooltip text for the button
            **kwargs: Arguments to pass to the AI function
        """
        if st.button(button_text, help=help_text, key=f"ai_btn_{target_key}"):
            ai_assistant = self._get_ai_assistant()
            if ai_assistant is None:
                st.error("AI features are currently unavailable.")
                return
            try:
                with st.spinner("AI is writing..."):
                    result = ai_function(**kwargs)
                    if result and result.strip():
                        st.session_state[target_key] = result
                        st.success("AI content generated! 🎉")
                        st.rerun()
                    else:
                        st.error("Failed to generate content. Please try again.")
            except Exception as e:
                st.error(f"AI assistance error: {str(e)}")
    
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
                try:
                    with st.spinner("Creating template..."):
                        template = self.ai_assistant.generate_message_template(
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
                    try:
                        with st.spinner("Creating new template..."):
                            template = self.ai_assistant.generate_message_template(
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
                try:
                    with st.spinner("Improving..."):
                        improved = self.ai_assistant.improve_text(text_value, "general")
                        if improved and improved.strip():
                            st.session_state[key] = improved
                            st.success("Improved! ✨")
                            st.rerun()
                except Exception as e:
                    st.error("Improvement failed")
        
        with col3:
            if text_value and st.button("💡 Tips", key=f"tips_{key}", help="Get improvement suggestions"):
                try:
                    with st.spinner("Analyzing..."):
                        suggestions = self.ai_assistant.quick_improve_suggestions(text_value, "general")
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
                try:
                    with st.spinner("Creating review template..."):
                        template = self.ai_assistant.generate_review_template(
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
                    try:
                        with st.spinner("Improving review..."):
                            improved = self.ai_assistant.improve_text(
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