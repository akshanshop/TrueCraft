import streamlit as st
from PIL import Image
import io
import base64

class ImageHandler:
    def __init__(self):
        self.max_size = (800, 600)  # Maximum image dimensions
        self.max_file_size = 5 * 1024 * 1024  # 5MB max file size
        self.supported_formats = ['PNG', 'JPEG', 'JPG', 'WEBP']
    
    def process_uploaded_image(self, uploaded_file):
        """Process uploaded image file and return base64 encoded string"""
        try:
            # Check file size
            if uploaded_file.size > self.max_file_size:
                st.error(f"File size too large. Maximum allowed: {self.max_file_size / (1024*1024):.1f}MB")
                return None
            
            # Open and validate image
            try:
                image = Image.open(uploaded_file)
            except Exception as e:
                st.error(f"Invalid image file: {str(e)}")
                return None
            
            # Check format
            if image.format not in self.supported_formats:
                st.error(f"Unsupported format. Supported formats: {', '.join(self.supported_formats)}")
                return None
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if necessary
            if image.size[0] > self.max_size[0] or image.size[1] > self.max_size[1]:
                image.thumbnail(self.max_size, Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=85, optimize=True)
            img_bytes = img_buffer.getvalue()
            
            # Convert to base64 for storage
            img_base64 = base64.b64encode(img_bytes).decode()
            
            return f"data:image/jpeg;base64,{img_base64}"
            
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            return None
    
    def create_thumbnail(self, image_data, size=(150, 150)):
        """Create thumbnail from image data"""
        try:
            if not image_data or not image_data.startswith('data:image'):
                return None
            
            # Extract base64 data
            base64_data = image_data.split(',')[1]
            img_bytes = base64.b64decode(base64_data)
            
            # Create thumbnail
            image = Image.open(io.BytesIO(img_bytes))
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert back to base64
            thumb_buffer = io.BytesIO()
            image.save(thumb_buffer, format='JPEG', quality=80)
            thumb_bytes = thumb_buffer.getvalue()
            thumb_base64 = base64.b64encode(thumb_bytes).decode()
            
            return f"data:image/jpeg;base64,{thumb_base64}"
            
        except Exception as e:
            st.error(f"Error creating thumbnail: {str(e)}")
            return None
    
    def validate_image_file(self, uploaded_file):
        """Validate uploaded image file before processing"""
        try:
            if uploaded_file is None:
                return False, "No file uploaded"
            
            if uploaded_file.size > self.max_file_size:
                return False, f"File too large. Max size: {self.max_file_size / (1024*1024):.1f}MB"
            
            # Check if it's a valid image
            try:
                image = Image.open(uploaded_file)
                if image.format not in self.supported_formats:
                    return False, f"Unsupported format. Use: {', '.join(self.supported_formats)}"
                
                # Reset file pointer
                uploaded_file.seek(0)
                return True, "Valid image file"
                
            except Exception as e:
                return False, f"Invalid image: {str(e)}"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def get_image_info(self, image_data):
        """Get information about processed image"""
        try:
            if not image_data or not image_data.startswith('data:image'):
                return None
            
            # Extract base64 data
            base64_data = image_data.split(',')[1]
            img_bytes = base64.b64decode(base64_data)
            
            # Get image info
            image = Image.open(io.BytesIO(img_bytes))
            
            return {
                'format': image.format,
                'size': image.size,
                'mode': image.mode,
                'file_size_kb': len(img_bytes) / 1024
            }
            
        except Exception as e:
            st.error(f"Error getting image info: {str(e)}")
            return None
    
    def display_image_with_info(self, image_data, caption="", show_info=False):
        """Display image with optional info overlay"""
        try:
            if not image_data:
                st.info("No image to display")
                return
            
            # Display the image
            st.image(image_data, caption=caption, use_column_width=True)
            
            # Show image info if requested
            if show_info:
                info = self.get_image_info(image_data)
                if info:
                    with st.expander("Image Details"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Format:** {info['format']}")
                            st.write(f"**Size:** {info['size'][0]} × {info['size'][1]} pixels")
                        with col2:
                            st.write(f"**Color Mode:** {info['mode']}")
                            st.write(f"**File Size:** {info['file_size_kb']:.1f} KB")
            
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")
    
    def batch_process_images(self, uploaded_files):
        """Process multiple uploaded images"""
        processed_images = []
        
        if not uploaded_files:
            return processed_images
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f'Processing image {i+1} of {len(uploaded_files)}: {uploaded_file.name}')
            
            # Validate file
            is_valid, message = self.validate_image_file(uploaded_file)
            
            if is_valid:
                processed_image = self.process_uploaded_image(uploaded_file)
                if processed_image:
                    processed_images.append({
                        'name': uploaded_file.name,
                        'data': processed_image,
                        'status': 'success'
                    })
                else:
                    processed_images.append({
                        'name': uploaded_file.name,
                        'data': None,
                        'status': 'failed',
                        'error': 'Processing failed'
                    })
            else:
                processed_images.append({
                    'name': uploaded_file.name,
                    'data': None,
                    'status': 'invalid',
                    'error': message
                })
            
            # Update progress
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text('Processing complete!')
        progress_bar.empty()
        
        return processed_images
