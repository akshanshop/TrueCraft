import json
import os
from openai import OpenAI

class AIAssistant:
    def __init__(self):
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-5"
    
    def generate_product_description(self, name, category, materials, price=None):
        """Generate compelling product descriptions for artisan products"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            return "AI assistance temporarily unavailable. Please try again later."
    
    def suggest_pricing(self, name, category, materials, dimensions=None):
        """Provide AI-powered pricing suggestions based on product details"""
        
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
        - min_price: minimum suggested price
        - max_price: maximum suggested price  
        - reasoning: brief explanation of the pricing rationale
        
        Focus on fair pricing that values the artisan's time and skill while remaining market-competitive.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=200,
                temperature=0.3
            )
            content = response.choices[0].message.content
            return json.loads(content) if content else {}
        except Exception as e:
            return {"min_price": 0, "max_price": 0, "reasoning": "AI assistance temporarily unavailable."}
    
    def generate_artist_bio(self, name, craft_type, experience, inspiration, unique_aspect):
        """Generate compelling artist bios and stories"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            return "AI assistance temporarily unavailable. Please try again later."
    
    def generate_social_media_post(self, topic, platform, tone):
        """Generate social media content for artisans"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.8
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            return "AI assistance temporarily unavailable. Please try again later."
    
    def generate_custom_content(self, content_type, context, specific_request):
        """Generate custom content based on user specifications"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            return f"AI assistance temporarily unavailable. Please try again later."
    
    def analyze_product_image(self, image_data):
        """Analyze product images to suggest improvements or generate descriptions"""
        
        prompt = """
        Analyze this product image and provide:
        1. A detailed description of what you see
        2. Suggestions for improving the photo for online sales
        3. Key selling points visible in the image
        4. Any craftsmanship details that should be highlighted
        
        Focus on elements that would help an artisan create better product listings.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                            }
                        ]
                    }
                ],
                max_tokens=400
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"Failed to analyze product image: {str(e)}")
    
    def generate_message_template(self, message_type, product_name=None, context=None):
        """Generate message templates for buyer-seller communications"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"Failed to generate message template: {str(e)}")
    
    def improve_text(self, original_text, improvement_type="general"):
        """Improve existing text content for better clarity and impact"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"Failed to improve text: {str(e)}")
    
    def generate_support_ticket(self, issue_type, description, urgency="medium"):
        """Generate well-structured support ticket content"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.5
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"Failed to generate support ticket: {str(e)}")
    
    def generate_review_response(self, review_text, rating, response_type="thank_you"):
        """Generate professional responses to customer reviews"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"Failed to generate review response: {str(e)}")
    
    def generate_review_template(self, product_category, rating=5):
        """Generate thoughtful review templates for customers"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"Failed to generate review template: {str(e)}")
    
    def quick_improve_suggestions(self, text, field_type="general"):
        """Provide quick, actionable suggestions for improving text"""
        
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
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.5
            )
            content = response.choices[0].message.content
            return content.strip() if content else ""
        except Exception as e:
            raise Exception(f"Failed to generate improvement suggestions: {str(e)}")
