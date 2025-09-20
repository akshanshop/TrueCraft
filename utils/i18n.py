"""
Internationalization (i18n) support for TrueCraft Marketplace Assistant.
Provides translation functionality and language management.
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import streamlit as st

class I18nManager:
    """Manages internationalization for the TrueCraft application"""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.current_language = "en"
        self.supported_languages = {
            "en": "English",
            "es": "Español", 
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "pt": "Português",
            "zh": "中文",
            "ja": "日本語",
            "ko": "한국어",
            "hi": "हिंदी",
            "ar": "العربية",
            "ru": "Русский"
        }
        self._load_translations()
    
    def _load_translations(self):
        """Load translation files from locales directory"""
        locales_dir = Path("locales")
        
        # Create default English translations if they don't exist
        if not locales_dir.exists():
            locales_dir.mkdir(exist_ok=True)
            self._create_default_translations()
        
        # Load all available translation files
        for lang_code in self.supported_languages.keys():
            lang_file = locales_dir / f"{lang_code}.json"
            if lang_file.exists():
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Error loading {lang_code} translations: {e}")
            else:
                # If translation file doesn't exist, create it with English as base
                if lang_code == "en":
                    self._create_default_translations()
    
    def _create_default_translations(self):
        """Create default English translation file"""
        default_translations = {
            # Common UI elements
            "app_title": "TrueCraft Marketplace Assistant",
            "app_tagline": "Empowering local artisans with AI-powered tools for online success",
            
            # Navigation
            "home": "Home",
            "product_listings": "Product Listings", 
            "artisan_profile": "Artisan Profile",
            "analytics": "Analytics",
            "messages": "Messages", 
            "support": "Support",
            "voice_onboarding": "Voice Onboarding",
            "sustainability_hub": "Sustainability Hub",
            "cultural_heritage": "Cultural Heritage",
            
            # Navigation descriptions
            "home_desc": "Main dashboard with overview of your TrueCraft marketplace activity.",
            "product_listings_desc": "Create and manage your product listings with AI-generated descriptions.",
            "artisan_profile_desc": "Build your professional artisan profile and showcase your story.",
            "analytics_desc": "Get detailed performance insights and track your sales trends.",
            "messages_desc": "Manage all your customer communications in one place.",
            "support_desc": "Get help, and access guides, and troubleshoot any issues.", 
            "voice_onboarding_desc": "Complete your artisan profile using AI-powered voice guidance in your language.",
            "sustainability_desc": "Assess your environmental impact and get sustainability certifications.",
            "cultural_desc": "Preserve and showcase your cultural traditions and stories.",
            
            # Buttons
            "go_to_home": "Go to Home",
            "manage_products": "Manage Products", 
            "manage_profile": "Manage Profile",
            "view_analytics": "View Analytics",
            "view_messages": "View Messages",
            "get_support": "Get Support",
            "start_voice_setup": "Start Voice Setup",
            "sustainability_assessment": "Sustainability Assessment", 
            "cultural_storytelling": "Cultural Storytelling",
            "sign_out": "Sign Out",
            "sign_in": "Sign In",
            "continue_with_google": "Continue with Google",
            "continue_with_github": "Continue with GitHub",
            
            # Account/Auth
            "your_account": "Your Account",
            "connected_via": "Connected via",
            "connect_to_access": "Connect to access your profile and saved data.",
            "demo_mode": "Demo Mode: You're using TrueCraft without authentication. All features are available!",
            "enable_social_login": "To enable social login, add your OAuth credentials to environment variables.",
            "successfully_logged_out": "Successfully logged out!",
            
            # Metrics
            "total_products": "Total Products",
            "active_profiles": "Active Profiles", 
            "average_price": "Average Price",
            "unread_messages": "Unread Messages",
            "quick_overview": "Quick Overview",
            "recent_products": "Recent Products",
            
            # Product related
            "no_image": "No image",
            "unknown": "Unknown", 
            "views": "Views",
            "welcome_message": "Welcome to TrueCraft! Start by creating your first product listing.",
            "product_name": "Product Name",
            "category": "Category",
            "price": "Price",
            "description": "Description",
            "materials": "Materials",
            "dimensions": "Dimensions",
            "weight": "Weight",
            "stock_quantity": "Stock Quantity",
            "shipping_cost": "Shipping Cost",
            "processing_time": "Processing Time",
            "tags": "Tags",
            
            # AI features
            "ai_assist": "AI Assist",
            "ai_suggestions": "AI Suggestions", 
            "generate_description": "Generate Description",
            "pricing_suggestions": "Pricing Suggestions",
            "ai_unavailable": "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features.",
            "ai_error": "AI assistance temporarily unavailable. Please try again later.",
            
            # Language selection
            "select_language": "Select Language",
            "language": "Language",
            
            # Common actions
            "save": "Save",
            "cancel": "Cancel", 
            "delete": "Delete",
            "edit": "Edit",
            "create": "Create",
            "update": "Update",
            "submit": "Submit",
            "clear": "Clear",
            "refresh": "Refresh",
            "copy": "Copy",
            "download": "Download",
            "upload": "Upload",
            "search": "Search",
            "filter": "Filter",
            "sort": "Sort",
            
            # Status messages
            "success": "Success",
            "error": "Error", 
            "warning": "Warning",
            "info": "Information",
            "loading": "Loading...",
            "processing": "Processing...",
            "saving": "Saving...",
            "uploading": "Uploading...",
            
            # Time periods
            "all_time": "All Time",
            "last_30_days": "Last 30 Days",
            "last_7_days": "Last 7 Days", 
            "last_24_hours": "Last 24 Hours",
            "today": "Today",
            "yesterday": "Yesterday",
            "this_week": "This Week",
            "this_month": "This Month",
            "this_year": "This Year",
            
            # Form labels
            "name": "Name",
            "email": "Email",
            "phone": "Phone",
            "website": "Website", 
            "location": "Location",
            "bio": "Bio",
            "experience": "Experience",
            "specialties": "Specialties",
            "inspiration": "Inspiration",
            "education": "Education",
            "awards": "Awards",
            
            # Social media
            "instagram": "Instagram",
            "facebook": "Facebook",
            "etsy": "Etsy",
            "social_media": "Social Media",
            
            # Cultural features
            "cultural_storytelling_info": "Cultural storytelling is available in Voice Onboarding and Profile pages!",
            "sustainability_features_info": "Sustainability features are integrated into product creation and analytics!",
            
            # Voice onboarding
            "start_recording": "Start Recording",
            "stop_recording": "Stop Recording", 
            "record_response": "Record Your Response",
            "save_continue": "Save & Continue",
            "previous_step": "Previous Step",
            "skip_step": "Skip Step",
            "generate_profile": "Generate Your Profile",
            "generate_story": "Generate Cultural Story",
            "generate_plan": "Generate Business Plan",
            
            # Advanced AI features
            "advanced_ai_features": "Advanced AI Features",
            
            # Tools and features
            "tools_features": "Tools & Features",
            
            # AI features and warnings
            "ai_features_unavailable": "AI features are currently unavailable. Some functionality may be limited.",
            "rating_stars": "Rating (stars)",
            "customer_reviews": "Customer Reviews",
            "write_review": "Write a Review",
            "your_name": "Your Name",
            "your_review": "Your Review",
            "submit_review": "Submit Review",
            "improve_review": "Improve Review"
        }
        
        # Save default translations
        locales_dir = Path("locales")
        locales_dir.mkdir(exist_ok=True)
        
        with open(locales_dir / "en.json", 'w', encoding='utf-8') as f:
            json.dump(default_translations, f, ensure_ascii=False, indent=2)
        
        self.translations["en"] = default_translations
    
    def set_language(self, lang_code: str):
        """Set the current language"""
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            # Store in session state for persistence
            st.session_state.language = lang_code
        else:
            print(f"Unsupported language: {lang_code}")
    
    def get_language(self) -> str:
        """Get current language from session state or default"""
        if hasattr(st.session_state, 'language'):
            self.current_language = st.session_state.language
        return self.current_language
    
    def t(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """Translate a key to the current or specified language"""
        target_lang = lang or self.get_language()
        
        # Get translation
        if target_lang in self.translations:
            translation = self.translations[target_lang].get(key)
        else:
            translation = None
        
        # Fallback to English if translation not found
        if translation is None and target_lang != "en":
            translation = self.translations.get("en", {}).get(key)
        
        # Final fallback to the key itself
        if translation is None:
            translation = key.replace("_", " ").title()
        
        # Format with kwargs if provided
        if kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                return translation
        
        return translation
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names"""
        return self.supported_languages
    
    def language_selector(self, key: str = "language_selector") -> str:
        """Render language selector widget"""
        current_lang = self.get_language()
        
        # Create selectbox with language names
        lang_names = list(self.supported_languages.values())
        lang_codes = list(self.supported_languages.keys())
        
        # Find current index
        try:
            current_index = lang_codes.index(current_lang)
        except ValueError:
            current_index = 0  # Default to English
        
        selected_name = st.selectbox(
            self.t("select_language"),
            lang_names,
            index=current_index,
            key=key
        )
        
        # Get selected language code
        selected_code = lang_codes[lang_names.index(selected_name)]
        
        # Update language if changed
        if selected_code != current_lang:
            self.set_language(selected_code)
            st.rerun()
        
        return selected_code
    
    def generate_ai_prompt_in_language(self, base_prompt: str, target_lang: Optional[str] = None) -> str:
        """Generate AI prompts that consider the target language"""
        target_lang = target_lang or self.get_language()
        
        if target_lang == "en":
            return base_prompt
        
        # Language-specific prompt additions
        lang_names = {
            "es": "Spanish",
            "fr": "French", 
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese", 
            "ko": "Korean",
            "hi": "Hindi",
            "ar": "Arabic",
            "ru": "Russian"
        }
        
        lang_name = lang_names.get(target_lang, "the user's preferred language")
        
        # Add language instruction to prompt
        language_instruction = f"\n\nIMPORTANT: Please respond in {lang_name}. The user prefers to receive content in {lang_name}, so all generated text should be in that language."
        
        return base_prompt + language_instruction

# Global instance
i18n = I18nManager()

# Convenience function for easy import
def t(key: str, **kwargs) -> str:
    """Shorthand translation function"""
    return i18n.t(key, **kwargs)

def set_language(lang_code: str):
    """Shorthand for setting language"""
    i18n.set_language(lang_code)

def get_language() -> str:
    """Shorthand for getting current language"""
    return i18n.get_language()

def language_selector(key: str = "language_selector") -> str:
    """Shorthand for language selector"""
    return i18n.language_selector(key)