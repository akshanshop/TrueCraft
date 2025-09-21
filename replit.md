# TrueCraft Marketplace Assistant

## Overview

TrueCraft Marketplace Assistant is a Streamlit-based web application designed to empower local artisans with AI-powered tools for online marketplace success. The application provides three core functionalities: AI-assisted product listing creation, artisan profile management, and analytics dashboard for tracking product performance. The system leverages Hugging Face API for text generation to create compelling product descriptions, pricing suggestions, and writing assistance for artisan profiles.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**September 20, 2025** - Project import setup and AI/OAuth configuration completed:
- **CHANGED**: Migrated from Google Gemini to Hugging Face API for AI-powered features
- Configured Hugging Face API integration for product descriptions, pricing suggestions, and artisan assistance
- Set up Google OAuth (Client ID and Secret) for social authentication
- Set up GitHub OAuth (Client ID and Secret) for social authentication  
- PostgreSQL database connection established
- All credentials securely stored in Replit Secrets
- Application fully configured for Replit environment with proper host settings
- Deployment configuration set for autoscale production deployment
- All authentication and AI features now fully functional

**September 21, 2025** - Complete multilingual support and API configuration:
- **ADDED**: Comprehensive Indian language support for AI assistant chatbot
- Added offline AI assistant translations for Bengali (বাংলা), Gujarati (ગુજરાતી), Marathi (मराठी), Tamil (தமிழ்), and Telugu (తెలుగు)
- Hindi (हिन्दी) already had complete AI assistant translations
- **CONFIGURED**: All API credentials successfully configured in Replit Secrets
- Google OAuth (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET) - Active
- GitHub OAuth (GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET) - Active  
- Hugging Face API (HUGGINGFACE_API_KEY) - Active
- All social authentication and AI features fully operational
- Application running successfully with complete multilingual offline support

**Note**: OAuth credentials configured manually as environment variables rather than using Replit's OAuth integration system per user preference. Hugging Face API used for AI features with limitations on audio transcription and multimodal image analysis.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page navigation
- **Layout**: Wide layout with responsive design using Streamlit's column system
- **Styling**: Custom CSS integrated through Streamlit's markdown functionality for warm, crafted aesthetic
- **Page Structure**: Main TrueCraft.py serving as homepage with dedicated pages for Product Listings, Artisan Profile, and Analytics

### Data Management
- **Storage**: Session-based data persistence using Streamlit's session state
- **Data Structure**: In-memory storage with DataFrame-based data manipulation using pandas
- **Data Models**: 
  - Products: name, category, price, description, materials, dimensions, stock, shipping details
  - Profiles: artisan information and business details
  - Analytics: product views, search terms, user interactions

### AI Integration
- **AI Provider**: Hugging Face API integration using text generation models
- **Core AI Features**:
  - Product description generation based on product details and materials
  - Pricing suggestions with market analysis
  - Writing assistance for artisan profiles
  - Limited image analysis (requires multimodal model upgrade)
- **AI Assistant Architecture**: Centralized AIAssistant class handling all Hugging Face API interactions

### Image Processing
- **Image Handling**: PIL (Python Imaging Library) for image processing and optimization
- **Storage Format**: Base64 encoding for image storage in session state
- **Constraints**: Maximum 5MB file size, 800x600px resolution, supports PNG/JPEG/WEBP formats
- **Processing**: Automatic format conversion, resizing, and quality optimization

### Analytics System
- **Visualization**: Plotly integration for interactive charts and graphs
- **Metrics Tracking**: Product performance, engagement metrics, and time-based filtering
- **Data Analysis**: Category-based filtering and time period analysis

## External Dependencies

### AI Services
- **Hugging Face API**: Text generation using mistralai/Mistral-7B-Instruct-v0.1 model for content generation and AI assistance
- **Authentication**: API key-based authentication via HUGGINGFACE_API_KEY environment variable
- **Limitations**: Audio transcription and advanced image analysis require additional service integration

### Python Libraries
- **Streamlit**: Web application framework and UI components
- **Pandas**: Data manipulation and DataFrame operations
- **Plotly**: Interactive data visualization and charting
- **PIL (Pillow)**: Image processing and optimization
- **Requests**: HTTP library for Hugging Face API communication

### Data Storage
- **Session State**: Streamlit's built-in session state for temporary data persistence
- **JSON Serialization**: Data conversion for session state compatibility

### Development Tools
- **Base64**: Image encoding for web display and storage
- **IO**: In-memory file operations for image processing
- **Datetime**: Time-based operations and filtering