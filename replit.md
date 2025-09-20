# TrueCraft Marketplace Assistant

## Overview

TrueCraft Marketplace Assistant is a Streamlit-based web application designed to empower local artisans with AI-powered tools for online marketplace success. The application provides three core functionalities: AI-assisted product listing creation, artisan profile management, and analytics dashboard for tracking product performance. The system leverages Google's Gemini-2.5-pro model to generate compelling product descriptions, pricing suggestions, and writing assistance for artisan profiles.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**September 20, 2025** - Project import setup and credential configuration completed:
- Configured Google Gemini API integration for AI-powered features  
- Set up Google OAuth (Client ID and Secret) for social authentication
- Set up GitHub OAuth (Client ID and Secret) for social authentication
- PostgreSQL database connection established
- All credentials securely stored in Replit Secrets
- Application fully configured for Replit environment with proper host settings

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application with multi-page navigation
- **Layout**: Wide layout with responsive design using Streamlit's column system
- **Styling**: Custom CSS integrated through Streamlit's markdown functionality for warm, crafted aesthetic
- **Page Structure**: Main app.py serving as homepage with dedicated pages for Product Listings, Artisan Profile, and Analytics

### Data Management
- **Storage**: Session-based data persistence using Streamlit's session state
- **Data Structure**: In-memory storage with DataFrame-based data manipulation using pandas
- **Data Models**: 
  - Products: name, category, price, description, materials, dimensions, stock, shipping details
  - Profiles: artisan information and business details
  - Analytics: product views, search terms, user interactions

### AI Integration
- **AI Provider**: Google Gemini API integration using the Gemini-2.5-pro model
- **Core AI Features**:
  - Product description generation based on product details and materials
  - Pricing suggestions with market analysis
  - Writing assistance for artisan profiles
  - Image analysis for product listings
- **AI Assistant Architecture**: Centralized AIAssistant class handling all Gemini API interactions

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
- **Google Gemini API**: Gemini-2.5-pro model for content generation and AI assistance
- **Authentication**: API key-based authentication for Gemini services
- **Image Analysis**: Multimodal capabilities for product image analysis

### Python Libraries
- **Streamlit**: Web application framework and UI components
- **Pandas**: Data manipulation and DataFrame operations
- **Plotly**: Interactive data visualization and charting
- **PIL (Pillow)**: Image processing and optimization
- **Google Gemini Python Client**: Official Google Gemini API client library

### Data Storage
- **Session State**: Streamlit's built-in session state for temporary data persistence
- **JSON Serialization**: Data conversion for session state compatibility

### Development Tools
- **Base64**: Image encoding for web display and storage
- **IO**: In-memory file operations for image processing
- **Datetime**: Time-based operations and filtering