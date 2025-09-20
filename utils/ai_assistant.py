import json
import os
from typing import Optional, Dict, Any
from google import genai
from google.genai import types

# Import i18n support
try:
    from .i18n import i18n
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    i18n = None

class AIAssistant:
    def __init__(self):
        # IMPORTANT: KEEP THIS COMMENT - Using Gemini blueprint integration
        # Follow these instructions when using this blueprint:
        # - Note that the newest Gemini model series is "gemini-2.5-flash" or gemini-2.5-pro"
        #   - do not change this unless explicitly requested by the user
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.enabled: bool = False
            self.client = None
            self.model: str = "gemini-2.5-pro"
        else:
            self.enabled: bool = True
            self.client = genai.Client(api_key=api_key)
            self.model: str = "gemini-2.5-pro"
    
    def _check_enabled(self):
        """Check if AI features are enabled, return error message if not"""
        if not self.enabled:
            if I18N_AVAILABLE and i18n:
                return i18n.t("ai_unavailable")
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        return None
    
    def _generate_content(self, prompt: str, use_json: bool = False, max_output_tokens: int = 300, temperature: float = 0.7, target_language: Optional[str] = None):
        """Helper method to generate content using Gemini API"""
        try:
            if not self.client:
                return None
            
            # Add language support to prompt if available
            if target_language and I18N_AVAILABLE and i18n:
                prompt = i18n.generate_ai_prompt_in_language(prompt, target_language)
                
            if use_json:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    max_output_tokens=max_output_tokens,
                    temperature=temperature
                )
            else:
                config = types.GenerateContentConfig(
                    max_output_tokens=max_output_tokens,
                    temperature=temperature
                )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            return response.text if response.text else ""
        except Exception as e:
            return None
    
    def generate_product_description(self, name, category, materials, price=None, target_language=None):
        """Generate compelling product descriptions for artisan products"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
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
        
        if not self.client:
            return {"min_price": 0, "max_price": 0, "reasoning": "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."}
        
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
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
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
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
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
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
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
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        prompt = """
        Analyze this product image and provide:
        1. A detailed description of what you see
        2. Suggestions for improving the photo for online sales
        3. Key selling points visible in the image
        4. Any craftsmanship details that should be highlighted
        
        Focus on elements that would help an artisan create better product listings.
        """
        
        try:
            # Convert base64 image data to bytes for Gemini
            import base64
            image_bytes = base64.b64decode(image_data)
            
            # Detect MIME type from image header if not provided
            if not mime_type:
                # Check image headers to determine format
                if image_bytes.startswith(b'\x89PNG'):
                    mime_type = "image/png"
                elif image_bytes.startswith(b'\xff\xd8\xff'):
                    mime_type = "image/jpeg"
                elif image_bytes.startswith(b'RIFF') and b'WEBP' in image_bytes[:12]:
                    mime_type = "image/webp"
                else:
                    # Default to jpeg if we can't detect
                    mime_type = "image/jpeg"
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                    prompt
                ]
            )
            content = response.text if response.text else ""
            return content.strip() if content else "AI image analysis temporarily unavailable."
        except Exception as e:
            return "AI image analysis temporarily unavailable. Please try again later."
    
    def generate_message_template(self, message_type, product_name=None, context=None):
        """Generate message templates for buyer-seller communications"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
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
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
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
    
    def generate_support_ticket(self, issue_type, description, urgency="medium"):
        """Generate well-structured support ticket content"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        prompt = f"""
        Help create a clear, professional support ticket for this issue:
        
        Issue Type: {issue_type}
        Description: {description}
        Urgency: {urgency}
        
        Create a well-structured support ticket that includes:
        - Clear, descriptive subject line
        - Detailed problem description
        - Steps already taken (if applicable)
        - Expected outcome
        - Professional but friendly tone
        
        Format the response as:
        **Subject:** [subject line]
        **Description:** [detailed description]
        
        Make it clear and actionable for support staff to understand and resolve quickly.
        """
        
        content = self._generate_content(prompt, max_output_tokens=300, temperature=0.5)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_review_response(self, review_text, rating, response_type="thank_you"):
        """Generate professional responses to customer reviews"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        response_types = {
            "thank_you": "grateful response acknowledging positive feedback",
            "address_concern": "professional response addressing concerns or issues raised",
            "neutral": "balanced response to neutral feedback",
            "encourage_contact": "response encouraging further communication or future business"
        }
        
        response_description = response_types.get(response_type, response_types["thank_you"])
        
        prompt = f"""
        Create a professional response to this customer review:
        
        Review: "{review_text}"
        Rating: {rating}/5 stars
        
        Generate a {response_description}.
        
        Requirements:
        - Personal and authentic tone (from the artisan)
        - Show appreciation for the feedback
        - Address specific points mentioned in the review
        - Keep it concise (1-2 sentences)
        - Maintain professional standards
        - Reflect the handmade/artisan business values
        
        Make it sound genuine and caring, not generic.
        """
        
        content = self._generate_content(prompt, max_output_tokens=150, temperature=0.7)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_review_template(self, product_category, rating=5):
        """Generate thoughtful review templates for customers"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        prompt = f"""
        Create a thoughtful review template for a {product_category} product with {rating} stars.
        
        The review should:
        - Include specific aspects customers typically evaluate (quality, craftsmanship, delivery, etc.)
        - Use placeholders [like this] for customizable details
        - Sound authentic and helpful to other buyers
        - Be appropriate for handmade/artisan products
        - Mention the personal touch of working with an artisan
        - Be 2-3 sentences with genuine appreciation
        
        Make it a template that customers can easily customize with their specific experience.
        """
        
        content = self._generate_content(prompt, max_output_tokens=200, temperature=0.7)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def quick_improve_suggestions(self, text, field_type="general"):
        """Provide quick, actionable suggestions for improving text"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        field_contexts = {
            "product_name": "product title that needs to be catchy and descriptive",
            "description": "product description that should highlight benefits and features", 
            "bio": "artisan bio that should be personal and engaging",
            "message": "business message that should be professional yet friendly",
            "general": "general text content"
        }
        
        context = field_contexts.get(field_type, field_contexts["general"])
        
        prompt = f"""
        Analyze this {context} and provide 2-3 quick, specific suggestions for improvement:
        
        Text: "{text}"
        
        Provide suggestions in this format:
        • [Specific actionable suggestion]
        • [Another specific suggestion]
        • [Third suggestion if applicable]
        
        Focus on:
        - Making it more compelling for customers
        - Improving clarity and impact
        - Adding artisan/handmade appeal
        - Practical improvements that are easy to implement
        
        Keep suggestions brief and actionable.
        """
        
        content = self._generate_content(prompt, max_output_tokens=200, temperature=0.5)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    # ===== ENHANCED AI BUSINESS TOOLS =====
    
    def generate_seo_optimized_title(self, product_name, category, keywords=None, target_language=None):
        """Generate SEO-optimized product titles"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        keywords_context = f" with keywords: {keywords}" if keywords else ""
        
        prompt = f"""
        Create 5 SEO-optimized product titles for this handmade artisan product:
        - Product name: {product_name}
        - Category: {category}
        - Keywords to include: {keywords_context}
        
        Each title should:
        - Be 50-70 characters long (ideal for search engines)
        - Include the main product name and category
        - Incorporate relevant keywords naturally
        - Appeal to customers searching for handmade/artisan products
        - Be compelling and click-worthy
        - Follow best practices for marketplace listings
        
        Format as a numbered list with brief explanations for each title's SEO strategy.
        """
        
        content = self._generate_content(prompt, max_output_tokens=400, temperature=0.7, target_language=target_language)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_pricing_analysis(self, product_name, materials, time_hours, skill_level, category, target_language=None):
        """Generate comprehensive pricing analysis"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        prompt = f"""
        Provide a comprehensive pricing analysis for this handmade product:
        - Product: {product_name}
        - Materials: {materials}
        - Time to create: {time_hours} hours
        - Skill level required: {skill_level}
        - Category: {category}
        
        Include:
        1. Material cost estimation
        2. Labor value calculation (considering skill level)
        3. Market positioning analysis
        4. Competitive pricing range
        5. Profit margin recommendations
        6. Pricing strategy suggestions (premium, competitive, value)
        
        Provide specific price ranges and reasoning for each recommendation.
        """
        
        content = self._generate_content(prompt, max_output_tokens=500, temperature=0.5, target_language=target_language)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_product_photography_tips(self, product_type, materials, setting, target_language=None):
        """Generate photography tips for product images"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        prompt = f"""
        Provide specific photography tips for taking professional product photos:
        - Product type: {product_type}
        - Materials: {materials}
        - Setting/location: {setting}
        
        Include:
        1. Lighting recommendations (natural vs artificial)
        2. Background and staging suggestions
        3. Camera angles and composition tips
        4. Props and styling ideas
        5. How to highlight the handmade quality
        6. Common mistakes to avoid
        7. Mobile phone photography tips
        
        Make it practical and actionable for artisans without professional equipment.
        """
        
        content = self._generate_content(prompt, max_output_tokens=400, temperature=0.6, target_language=target_language)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_seasonal_marketing_content(self, products_list, season_or_holiday, target_audience, target_language=None):
        """Generate seasonal marketing content"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        prompt = f"""
        Create seasonal marketing content for these handmade products:
        - Products: {products_list}
        - Season/Holiday: {season_or_holiday}
        - Target audience: {target_audience}
        
        Provide:
        1. Marketing campaign theme
        2. 3 social media post ideas with captions
        3. Email newsletter content
        4. Product bundling suggestions
        5. Seasonal keywords to use
        6. Promotional ideas that align with the season
        
        Focus on connecting the handmade nature of products with seasonal emotions and needs.
        """
        
        content = self._generate_content(prompt, max_output_tokens=500, temperature=0.7, target_language=target_language)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_brand_voice_analysis(self, bio, products_description, target_customers, target_language=None):
        """Analyze and define brand voice"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        prompt = f"""
        Analyze this artisan business and define their brand voice:
        - Bio: {bio}
        - Products: {products_description}
        - Target customers: {target_customers}
        
        Provide:
        1. Brand personality analysis (3-4 key traits)
        2. Tone of voice recommendations
        3. Language style guidelines
        4. Do's and don'ts for communication
        5. Example phrases that match the brand voice
        6. How to adapt voice for different platforms
        
        Make it practical for consistent brand communication across all channels.
        """
        
        content = self._generate_content(prompt, max_output_tokens=400, temperature=0.6, target_language=target_language)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_content_calendar(self, business_type, posting_frequency, special_events, target_language=None):
        """Generate social media content calendar"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        prompt = f"""
        Create a 4-week social media content calendar for:
        - Business type: {business_type}
        - Posting frequency: {posting_frequency}
        - Special events: {special_events}
        
        Include:
        1. Week-by-week content themes
        2. Post type variety (behind-scenes, products, tips, personal)
        3. Best posting times for artisan audiences
        4. Engagement strategies
        5. Hashtag suggestions for each post type
        6. Content ideas that showcase the handmade process
        
        Format as a clear weekly schedule with specific post ideas.
        """
        
        content = self._generate_content(prompt, max_output_tokens=500, temperature=0.7, target_language=target_language)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def generate_competitive_analysis(self, product_type, price_range, unique_features, target_language=None):
        """Generate competitive analysis and positioning"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return error_msg
        
        if not self.client:
            return "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."
        
        prompt = f"""
        Provide a competitive analysis for this handmade product:
        - Product type: {product_type}
        - Your price range: {price_range}
        - Unique features: {unique_features}
        
        Analyze:
        1. Market positioning strategy
        2. Competitive advantages to highlight
        3. Pricing strategy vs competitors
        4. Unique selling propositions
        5. Market differentiation opportunities
        6. Customer value propositions
        7. Areas for improvement or expansion
        
        Focus on how to stand out in the handmade/artisan marketplace.
        """
        
        content = self._generate_content(prompt, max_output_tokens=400, temperature=0.6, target_language=target_language)
        return content.strip() if content else "AI assistance temporarily unavailable. Please try again later."
    
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio files for voice onboarding and communication"""
        
        error_msg = self._check_enabled()
        if error_msg:
            return {"text": "", "error": error_msg}
        
        if not self.client:
            return {"text": "", "error": "AI assistance temporarily unavailable. Please configure GEMINI_API_KEY to enable AI features."}
        
        # Note: Gemini doesn't have direct audio transcription like OpenAI's Whisper
        # This would need to be implemented using Google Cloud Speech-to-Text or similar
        # For now, return a placeholder
        return {"text": "", "error": "Audio transcription not yet implemented with Gemini. Consider using Google Cloud Speech-to-Text."}