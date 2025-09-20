import json
import os
import requests
from typing import Optional, Dict, Any

# Import i18n support
try:
    from .i18n import i18n
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    i18n = None

class AIAssistant:
    def __init__(self):
        # Using Hugging Face API for AI features
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            self.enabled: bool = False
        else:
            self.enabled: bool = True
        
        # Hugging Face Inference API headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _check_enabled(self):
        """Check if AI features are enabled, return error message if not"""
        if not self.enabled:
            if I18N_AVAILABLE and i18n:
                return i18n.t("ai_unavailable")
            return "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."
        return None
    
    def _generate_content(self, prompt: str, use_json: bool = False, max_output_tokens: int = 300, temperature: float = 0.7, target_language: Optional[str] = None):
        """Helper method to generate content using Hugging Face API"""
        try:
            if not self.enabled:
                return None
            
            # Add language support to prompt if available
            if target_language and I18N_AVAILABLE and i18n and hasattr(i18n, 'generate_ai_prompt_in_language'):
                try:
                    prompt = i18n.generate_ai_prompt_in_language(prompt, target_language)
                except:
                    # Skip language modification if it fails
                    pass
            
            # Add JSON instruction to prompt if needed
            if use_json:
                prompt += "\n\nPlease respond in valid JSON format only."
                
            # Use a more suitable model for instruction following and JSON generation
            api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_output_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
            
            response = requests.post(api_url, headers=self.headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
                return ''
            else:
                print(f"HuggingFace API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            # Log error server-side for debugging, return None to trigger proper error handling
            print(f"AI API Error: {str(e)}")
            return None
    
    def generate_product_description(self, name, category, materials, price=None, target_language=None):
        """Generate compelling product descriptions for artisan products"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.enabled:
            return "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."
        
        price_context = f" with a price point of ${price}" if price else ""
        
        prompt = f"""
        Create a compelling, authentic product description for a handmade artisan product with these details:
        - Product name: {name}
        - Category: {category}
        - Materials: {materials}
        - Price context: {price_context}
        
        The description should:
        - Highlight the craftsmanship and artisan quality
        - Mention the materials and their benefits
        - Create an emotional connection with potential buyers
        - Be 2-3 paragraphs long
        - Sound authentic and personal, not overly commercial
        - Include sensory details where appropriate
        
        Write in a warm, personal tone that reflects the artisan's passion for their craft.
        """
        
        content = self._generate_content(prompt, max_output_tokens=300, temperature=0.7, target_language=target_language)
        if content:
            return content.strip()
        else:
            if I18N_AVAILABLE and i18n:
                return i18n.t("ai_error")
            return "AI assistance temporarily unavailable. Please try again later."
    
    def suggest_pricing(self, name, category, materials, dimensions=None):
        """Provide AI-powered pricing suggestions based on product details"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return {"min_price": 0, "max_price": 0, "reasoning": error_msg}
        
        if not self.enabled:
            return {"min_price": 0, "max_price": 0, "reasoning": "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."}
        
        dimensions_context = f" with dimensions {dimensions}" if dimensions else ""
        
        prompt = f"""
        Analyze this handmade artisan product and provide pricing suggestions:
        - Product: {name}
        - Category: {category}  
        - Materials: {materials}
        - Dimensions: {dimensions_context}
        
        Consider:
        - Material costs and quality
        - Time and skill required
        - Market positioning for handmade items
        - Category-typical pricing ranges
        - Value proposition
        
        Provide your response in JSON format with:
        - min_price: minimum suggested price (number)
        - max_price: maximum suggested price (number)
        - reasoning: brief explanation of the pricing rationale (string)
        
        Focus on fair pricing that values the artisan's time and skill while remaining market-competitive.
        """
        
        try:
            content = self._generate_content(prompt, use_json=True, max_output_tokens=200, temperature=0.3)
            if content:
                # Clean the content in case of code fences or extra formatting
                clean_content = content.strip()
                if clean_content.startswith('```json'):
                    clean_content = clean_content.replace('```json', '').replace('```', '').strip()
                elif clean_content.startswith('```'):
                    clean_content = clean_content.replace('```', '').strip()
                
                data = json.loads(clean_content)
                
                # Validate required keys exist
                if 'min_price' in data and 'max_price' in data and 'reasoning' in data:
                    return data
                else:
                    return {"min_price": 0, "max_price": 0, "reasoning": "AI response format invalid."}
            else:
                return {"min_price": 0, "max_price": 0, "reasoning": "AI assistance temporarily unavailable."}
        except Exception as e:
            return {"min_price": 0, "max_price": 0, "reasoning": "AI assistance temporarily unavailable."}
    
    def generate_artist_bio(self, name, craft_type, experience, inspiration, unique_aspect):
        """Generate compelling artist bios and stories"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.enabled:
            return "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."
        
        prompt = f"""
        Create a compelling artisan bio for:
        - Name/Business: {name}
        - Craft: {craft_type}
        - Experience: {experience}
        - Inspiration: {inspiration}
        - What makes them unique: {unique_aspect}
        
        The bio should:
        - Be engaging and personal
        - Tell a story about their journey
        - Highlight their passion and expertise
        - Be 2-3 paragraphs long
        - Connect with potential customers emotionally
        - Sound authentic and avoid clichés
        - Include their creative process or philosophy
        
        Write in first person and make it warm and approachable.
        """
        
        content = self._generate_content(prompt, max_output_tokens=400, temperature=0.7)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_social_media_post(self, topic, platform, tone):
        """Generate social media content for artisans"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.enabled:
            return "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."
        
        platform_guidelines = {
            "Instagram": "Visual-focused, use relevant hashtags, engaging captions",
            "Facebook": "Community-oriented, longer form content acceptable", 
            "Twitter": "Concise, punchy, use relevant hashtags",
            "General": "Adaptable to multiple platforms"
        }
        
        prompt = f"""
        Create a {tone.lower()} social media post for {platform} about: {topic}
        
        Platform considerations: {platform_guidelines.get(platform, "General social media")}
        
        The post should:
        - Match the {tone.lower()} tone
        - Be appropriate for artisan/maker audience
        - Include a call-to-action if relevant
        - Be engaging and authentic
        - Include 3-5 relevant hashtags
        - Stay within typical character limits for the platform
        
        Make it personal and showcase the human side of the craft business.
        """
        
        content = self._generate_content(prompt, max_output_tokens=200, temperature=0.8)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_custom_content(self, content_type, context, specific_request):
        """Generate custom content based on user specifications"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.enabled:
            return "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."
        
        prompt = f"""
        Help create {content_type} content with this context:
        
        Context: {context}
        
        Specific request: {specific_request}
        
        Create content that:
        - Directly addresses the specific request
        - Is appropriate for an artisan/maker business
        - Maintains a professional yet personal tone
        - Is practical and actionable
        - Reflects authenticity and craftsmanship values
        
        Provide clear, well-structured content that the user can immediately use.
        """
        
        content = self._generate_content(prompt, max_output_tokens=500, temperature=0.7)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def analyze_product_image(self, image_data, mime_type=None):
        """Analyze product images to suggest improvements or generate descriptions"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.enabled:
            return "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."
        
        # Note: Image analysis requires multimodal models not available in basic HuggingFace API
        return "Image analysis feature is not available with the current AI configuration. Consider using a multimodal model service."
    
    def voice_onboarding_guide(self, step_name, user_input="", language="English"):
        """Generate AI guidance for voice onboarding steps"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.enabled:
            return "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."
        
        prompt = f"""
        Provide helpful guidance for the '{step_name}' step of artisan onboarding.
        User's previous input: {user_input}
        Language: {language}
        
        Create encouraging, helpful guidance that:
        - Explains what information is needed for this step
        - Provides specific examples relevant to artisan businesses
        - Encourages authentic storytelling
        - Is warm and supportive in tone
        - Helps the user feel confident about sharing their story
        
        Keep the guidance concise but inspiring.
        """
        
        content = self._generate_content(prompt, max_output_tokens=300, temperature=0.7, target_language=language)
        return content.strip() if content else "AI guidance temporarily unavailable. Please try again later."
    
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio to text"""
        # Note: Audio transcription requires specialized models not available in basic HuggingFace API
        return {"text": "", "error": "Audio transcription not yet implemented with HuggingFace. Consider using Whisper API or similar service."}
    
    def translate_text(self, text, target_language):
        """Translate text to target language"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return {"translated_text": text, "error": error_msg}
        
        if not self.enabled:
            return {"translated_text": text, "error": "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."}
        
        prompt = f"""
        Translate the following text to {target_language}:
        
        {text}
        
        Provide only the translation, no additional text or explanation.
        """
        
        content = self._generate_content(prompt, max_output_tokens=200, temperature=0.3, target_language=target_language)
        if content:
            return {"translated_text": content.strip(), "error": None}
        else:
            return {"translated_text": text, "error": "Translation temporarily unavailable."}
    
    def generate_message_template(self, message_type, product_name=None, context=None):
        """Generate message templates for buyer-seller communications"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.enabled:
            return "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."
        
        product_context = f" about {product_name}" if product_name else ""
        additional_context = f"Additional context: {context}" if context else ""
        
        templates = {
            "inquiry": "professional inquiry asking for product details, customization options, or availability",
            "custom_order": "request for custom product modifications or personalized items",
            "shipping": "question about shipping costs, delivery times, and packaging options", 
            "payment": "discussion about payment methods, pricing, or invoicing",
            "follow_up": "follow-up message after initial contact or order placement",
            "thank_you": "appreciation message after purchase or interaction",
            "complaint": "professional complaint or concern about product or service",
            "general": "general business inquiry or introduction"
        }
        
        template_description = templates.get(message_type, templates["general"])
        
        prompt = f"""
        Create a professional, friendly message template for {message_type} communication{product_context}.
        
        The message should be a {template_description}.
        
        {additional_context}
        
        Requirements:
        - Professional yet warm and personal tone
        - Clear and concise language
        - Include placeholders [like this] where users can customize
        - Appropriate for artisan/handmade product context
        - Show respect for craftsmanship and quality
        - 2-4 sentences maximum
        
        Make it ready-to-use with minimal editing needed.
        """
        
        content = self._generate_content(prompt, max_output_tokens=200, temperature=0.7)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def improve_text(self, original_text, improvement_type="general"):
        """Improve existing text content for better clarity and impact"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.enabled:
            return "AI assistance temporarily unavailable. Please configure HUGGINGFACE_API_KEY to enable AI features."
        
        improvement_types = {
            "grammar": "Correct grammar, spelling, and punctuation while maintaining the original tone and meaning",
            "clarity": "Improve clarity and readability while keeping the core message intact", 
            "professional": "Make the text more professional while maintaining a personal touch",
            "engaging": "Make the text more engaging and compelling for potential customers",
            "concise": "Make the text more concise without losing important information",
            "general": "Improve overall quality including grammar, clarity, and engagement"
        }
        
        instruction = improvement_types.get(improvement_type, improvement_types["general"])
        
        prompt = f"""
        Please improve this text by focusing on: {instruction}
        
        Original text:
        "{original_text}"
        
        Requirements:
        - Maintain the original meaning and intent
        - Keep the personal, artisan-friendly tone
        - Make it suitable for handmade/craft business context
        - Preserve any specific details or technical information
        - Don't make it overly formal or corporate
        
        Provide only the improved text without additional commentary.
        """
        
        content = self._generate_content(prompt, max_output_tokens=300, temperature=0.3)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."