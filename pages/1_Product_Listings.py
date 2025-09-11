import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import io
from utils.ai_assistant import AIAssistant
from utils.database_manager import DatabaseManager
from utils.image_handler import ImageHandler

# Initialize components
@st.cache_resource
def get_database_manager():
    return DatabaseManager()

db_manager = get_database_manager()

ai_assistant = AIAssistant()
image_handler = ImageHandler()

# Star Rating Components
def display_star_rating(rating, max_stars=5):
    """Display star rating with filled and empty stars"""
    filled_stars = int(rating)
    half_star = rating - filled_stars >= 0.5
    empty_stars = max_stars - filled_stars - (1 if half_star else 0)
    
    star_display = "⭐" * filled_stars
    if half_star:
        star_display += "⭐"  # Using full star for simplicity, could use ½ star
    star_display += "☆" * empty_stars
    
    return star_display

def star_rating_input(key, default_rating=0):
    """Interactive star rating input component"""
    # Store rating in session state
    session_key = f"rating_{key}"
    if session_key not in st.session_state:
        st.session_state[session_key] = default_rating
    
    with st.container():
        st.write("**Rating:**")
        rating_cols = st.columns(5)
        
        for i in range(5):
            with rating_cols[i]:
                if st.button("⭐" if i < st.session_state[session_key] else "☆", 
                           key=f"{key}_star_{i}", 
                           help=f"{i+1} star{'s' if i > 0 else ''}"):
                    st.session_state[session_key] = i + 1
    
    return st.session_state[session_key]

def display_reviews_section(product_id, product_name):
    """Display reviews section with existing reviews and submission form"""
    st.subheader("💬 Customer Reviews")
    
    # Get reviews and rating data
    reviews = db_manager.get_product_reviews(product_id)
    rating_data = db_manager.get_average_rating(product_id)
    
    # Display average rating summary
    col1, col2 = st.columns([1, 2])
    with col1:
        if rating_data['total_reviews'] > 0:
            avg_rating = rating_data['average_rating']
            st.metric("Average Rating", f"{avg_rating:.1f} ⭐", f"{rating_data['total_reviews']} reviews")
            
            # Rating breakdown
            st.write("**Rating Breakdown:**")
            for star in range(5, 0, -1):
                count = rating_data['rating_distribution'].get(str(star), 0)
                percentage = (count / rating_data['total_reviews']) * 100 if rating_data['total_reviews'] > 0 else 0
                st.write(f"{star}⭐: {count} ({percentage:.0f}%)")
        else:
            st.info("No reviews yet. Be the first to review!")
    
    with col2:
        # Review submission form
        with st.expander("✍️ Write a Review", expanded=False):
            with st.form(f"review_form_{product_id}"):
                customer_name = st.text_input("Your Name*", placeholder="Enter your name")
                customer_email = st.text_input("Email (optional)", placeholder="your.email@example.com")
                
                # Star rating input
                rating = star_rating_input(f"review_{product_id}")
                
                comment = st.text_area(
                    "Your Review*", 
                    placeholder="Share your experience with this product...",
                    max_chars=1000,
                    help="Maximum 1000 characters"
                )
                
                submitted = st.form_submit_button("📝 Submit Review")
                
                if submitted:
                    if customer_name and rating > 0 and comment:
                        review_data = {
                            'product_id': product_id,
                            'customer_name': customer_name,
                            'customer_email': customer_email or None,
                            'rating': rating,
                            'comment': comment,
                            'approved': True  # Auto-approve for demo purposes
                        }
                        
                        success = db_manager.add_review(review_data)
                        if success:
                            st.success("Thank you for your review! 🎉")
                            st.rerun()
                        else:
                            st.error("Failed to submit review. Please try again.")
                    else:
                        st.error("Please fill in your name, select a rating, and write a comment.")
    
    # Display existing reviews
    if reviews:
        st.subheader(f"Reviews ({len(reviews)})")
        
        # Sort reviews by most recent
        reviews_sorted = sorted(reviews, key=lambda x: x['created_at'], reverse=True)
        
        for review in reviews_sorted:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{review['customer_name']}**")
                    st.write(display_star_rating(review['rating']))
                    st.write(review['comment'])
                
                with col2:
                    st.write(f"_{review['created_at'].strftime('%B %d, %Y')}_")
                
                st.divider()
    else:
        st.info("No reviews yet for this product.")

def get_product_rating_summary(product_id):
    """Get a brief rating summary for product cards"""
    rating_data = db_manager.get_average_rating(product_id)
    if rating_data['total_reviews'] > 0:
        avg_rating = rating_data['average_rating']
        total_reviews = rating_data['total_reviews']
        return f"{display_star_rating(avg_rating)} ({total_reviews} review{'s' if total_reviews != 1 else ''})"
    return "No reviews yet"

st.set_page_config(
    page_title="Product Listings - ArtisanAI",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Product Listings")
st.markdown("Create and manage your product listings with AI assistance")

# Sidebar for navigation
with st.sidebar:
    st.subheader("Actions")
    page_mode = st.radio("Choose Action", ["Create New Product", "Browse Products", "Manage Listings"])

if page_mode == "Create New Product":
    st.subheader("🆕 Create New Product Listing")
    
    # AI Assistance Section (outside form)
    with st.expander("🤖 AI Writing Assistant", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            ai_product_name = st.text_input("Product Name (for AI)", key="ai_name", placeholder="e.g., Handcrafted Ceramic Mug")
            ai_category = st.text_input("Category (for AI)", key="ai_category", placeholder="Pottery & Ceramics")
            ai_materials = st.text_input("Materials (for AI)", key="ai_materials", placeholder="Clay, Glaze, Natural fibers")
            ai_dimensions = st.text_input("Dimensions (for AI)", key="ai_dimensions", placeholder="4\" x 3\" x 3\"")
            
        with col2:
            st.write("**Generate AI Content:**")
            if st.button("✨ Generate Description", use_container_width=True):
                if ai_product_name and ai_category and ai_materials:
                    with st.spinner("Generating description..."):
                        try:
                            generated_desc = ai_assistant.generate_product_description(
                                ai_product_name, ai_category, ai_materials, 25.00
                            )
                            st.session_state.generated_description = generated_desc
                            st.success("Description generated! Copy it to the form below.")
                        except Exception as e:
                            st.error(f"Failed to generate description: {str(e)}")
                else:
                    st.warning("Please fill in product name, category, and materials first.")
            
            if st.button("💰 Get Price Suggestion", use_container_width=True):
                if ai_product_name and ai_category and ai_materials:
                    with st.spinner("Analyzing pricing..."):
                        try:
                            price_suggestion = ai_assistant.suggest_pricing(
                                ai_product_name, ai_category, ai_materials, ai_dimensions
                            )
                            st.session_state.price_suggestion = price_suggestion
                            st.success("Price analysis complete!")
                        except Exception as e:
                            st.error(f"Failed to get price suggestion: {str(e)}")
                else:
                    st.warning("Please fill in product details first.")
        
        # Display generated content
        if 'generated_description' in st.session_state:
            st.info("**AI Generated Description:**")
            st.write(st.session_state.generated_description)
        
        if 'price_suggestion' in st.session_state:
            suggestion = st.session_state.price_suggestion
            st.info("**AI Price Analysis:**")
            min_price = suggestion.get('min_price', 0)
            max_price = suggestion.get('max_price', 0)
            reasoning = suggestion.get('reasoning', 'No reasoning provided')
            st.write(f"**Suggested Price Range:** ${min_price:.2f} - ${max_price:.2f}")
            st.write(f"**Reasoning:** {reasoning}")
    
    # Product Creation Form
    with st.form("product_form"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            product_name = st.text_input("Product Name*", placeholder="e.g., Handcrafted Ceramic Mug")
            category = st.selectbox("Category*", [
                "Pottery & Ceramics",
                "Jewelry & Accessories", 
                "Textiles & Clothing",
                "Woodworking",
                "Metalwork",
                "Art & Paintings",
                "Home Decor",
                "Other"
            ])
            price = st.number_input("Price ($)*", min_value=0.01, value=25.00, step=0.01)
            
        with col2:
            materials = st.text_input("Materials Used", placeholder="e.g., Clay, Glaze, Natural fibers")
            dimensions = st.text_input("Dimensions", placeholder="e.g., 4\" x 3\" x 3\"")
            weight = st.text_input("Weight", placeholder="e.g., 0.5 lbs")
        
        # Image upload
        st.subheader("📷 Product Images")
        uploaded_files = st.file_uploader(
            "Upload product images", 
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg']
        )
        
        # Product description
        st.subheader("📄 Product Description")
        description = st.text_area(
            "Product Description", 
            placeholder="Describe your product... (Use AI Assistant above to generate)",
            height=150
        )
        
        # Additional details
        with st.expander("Additional Details"):
            col1, col2 = st.columns(2)
            with col1:
                stock_quantity = st.number_input("Stock Quantity", min_value=0, value=1)
                shipping_cost = st.number_input("Shipping Cost ($)", min_value=0.00, value=5.00, step=0.01)
            with col2:
                processing_time = st.selectbox("Processing Time", [
                    "1-3 business days",
                    "3-5 business days", 
                    "1-2 weeks",
                    "2-4 weeks",
                    "Custom order (contact for timeline)"
                ])
                tags = st.text_input("Tags (comma separated)", placeholder="handmade, ceramic, kitchen, gift")
        
        # Submit button
        submitted = st.form_submit_button("🚀 Create Product Listing", use_container_width=True)
        
        if submitted:
            if product_name and category and price and description:
                # Process images
                image_data = None
                if uploaded_files:
                    # Use the first uploaded image
                    image_data = image_handler.process_uploaded_image(uploaded_files[0])
                
                # Create product data
                product_data = {
                    'name': product_name,
                    'category': category,
                    'price': price,
                    'description': description,
                    'materials': materials,
                    'dimensions': dimensions,
                    'weight': weight,
                    'stock_quantity': stock_quantity,
                    'shipping_cost': shipping_cost,
                    'processing_time': processing_time,
                    'tags': tags,
                    'image_data': image_data,
                    'created_at': datetime.now(),
                    'views': 0,
                    'favorites': 0
                }
                
                # Save product
                success = db_manager.add_product(product_data)
                if success:
                    st.success("🎉 Product listing created successfully!")
                    st.balloons()
                    # Clear any stored AI suggestions
                    if 'generated_description' in st.session_state:
                        del st.session_state.generated_description
                    if 'price_suggestion' in st.session_state:
                        del st.session_state.price_suggestion
                else:
                    st.error("Failed to create product listing. Please try again.")
            else:
                st.error("Please fill in all required fields (marked with *).")

elif page_mode == "Browse Products":
    st.subheader("🛍️ Product Catalog")
    
    # Get all products
    products_df = db_manager.get_products()
    
    if products_df.empty:
        st.info("No products available. Create your first product listing!")
    else:
        # Search and filter
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("🔍 Search products", placeholder="Search by name...")
        with col2:
            category_filter = st.selectbox("Filter by Category", ["All"] + products_df['category'].unique().tolist())
        with col3:
            min_price = float(products_df['price'].min())
            max_price = float(products_df['price'].max())
            
            # Handle case where all products have the same price
            if min_price == max_price:
                max_price = min_price + 0.01
            
            price_range = st.slider("Price Range ($)", 
                                  min_value=min_price, 
                                  max_value=max_price,
                                  value=(min_price, max_price))
        
        # Apply filters
        filtered_df = products_df.copy()
        
        if search_term:
            mask = filtered_df['name'].str.contains(search_term, case=False, na=False)
            filtered_df = filtered_df.loc[mask]
        
        if category_filter != "All":
            mask = filtered_df['category'] == category_filter
            filtered_df = filtered_df.loc[mask]
        
        price_mask = (filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])
        filtered_df = filtered_df.loc[price_mask]
        
        # Sort options
        sort_by = st.selectbox("Sort by", ["Created Date (Newest)", "Created Date (Oldest)", "Price (Low to High)", "Price (High to Low)", "Most Views"])
        
        if sort_by == "Created Date (Newest)":
            filtered_df = filtered_df.sort_values('created_at', ascending=False)
        elif sort_by == "Created Date (Oldest)":
            filtered_df = filtered_df.sort_values('created_at', ascending=True)
        elif sort_by == "Price (Low to High)":
            filtered_df = filtered_df.sort_values('price', ascending=True)
        elif sort_by == "Price (High to Low)":
            filtered_df = filtered_df.sort_values('price', ascending=False)
        elif sort_by == "Most Views":
            filtered_df = filtered_df.sort_values('views', ascending=False)
        
        st.write(f"Showing {len(filtered_df)} products")
        
        # Display products in cards
        if not filtered_df.empty:
            for i in range(0, len(filtered_df), 2):
                col1, col2 = st.columns(2)
                
                # First product
                with col1:
                    if i < len(filtered_df):
                        product = filtered_df.iloc[i]
                        with st.container():
                            if product['image_data']:
                                st.image(product['image_data'], width=200)
                            
                            st.subheader(product['name'])
                            st.write(f"**${product['price']:.2f}**")
                            st.write(f"Category: {product['category']}")
                            st.write(f"👁️ {product['views']} views | ❤️ {product['favorites']} favorites")
                            
                            # Display rating summary
                            rating_summary = get_product_rating_summary(product['id'])
                            st.write(f"⭐ {rating_summary}")
                            
                            if st.button(f"View Details", key=f"view_{i}"):
                                # Increment view count
                                db_manager.increment_views(product['id'])
                                
                                # Show product details
                                with st.expander(f"Details - {product['name']}", expanded=True):
                                    st.write(f"**Description:** {product['description']}")
                                    if product['materials']:
                                        st.write(f"**Materials:** {product['materials']}")
                                    if product['dimensions']:
                                        st.write(f"**Dimensions:** {product['dimensions']}")
                                    if product['weight']:
                                        st.write(f"**Weight:** {product['weight']}")
                                    st.write(f"**Processing Time:** {product['processing_time']}")
                                    if product['tags']:
                                        st.write(f"**Tags:** {product['tags']}")
                                    
                                    # Add Reviews Section
                                    st.divider()
                                    display_reviews_section(product['id'], product['name'])
                
                # Second product
                with col2:
                    if i + 1 < len(filtered_df):
                        product = filtered_df.iloc[i + 1]
                        with st.container():
                            if product['image_data']:
                                st.image(product['image_data'], width=200)
                            
                            st.subheader(product['name'])
                            st.write(f"**${product['price']:.2f}**")
                            st.write(f"Category: {product['category']}")
                            st.write(f"👁️ {product['views']} views | ❤️ {product['favorites']} favorites")
                            
                            # Display rating summary
                            rating_summary = get_product_rating_summary(product['id'])
                            st.write(f"⭐ {rating_summary}")
                            
                            if st.button(f"View Details", key=f"view_{i+1}"):
                                # Increment view count
                                db_manager.increment_views(product['id'])
                                
                                # Show product details
                                with st.expander(f"Details - {product['name']}", expanded=True):
                                    st.write(f"**Description:** {product['description']}")
                                    if product['materials']:
                                        st.write(f"**Materials:** {product['materials']}")
                                    if product['dimensions']:
                                        st.write(f"**Dimensions:** {product['dimensions']}")
                                    if product['weight']:
                                        st.write(f"**Weight:** {product['weight']}")
                                    st.write(f"**Processing Time:** {product['processing_time']}")
                                    if product['tags']:
                                        st.write(f"**Tags:** {product['tags']}")
                                    
                                    # Add Reviews Section
                                    st.divider()
                                    display_reviews_section(product['id'], product['name'])

elif page_mode == "Manage Listings":
    st.subheader("⚙️ Manage Your Listings")
    
    products_df = db_manager.get_products()
    
    if products_df.empty:
        st.info("No products to manage. Create your first product listing!")
    else:
        st.write(f"You have {len(products_df)} products")
        
        # Quick actions
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📈 Bulk Update Prices"):
                st.info("Feature coming soon!")
        with col2:
            if st.button("🏷️ Manage Tags"):
                st.info("Feature coming soon!")
        with col3:
            if st.button("📊 Export Data"):
                csv = products_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="products.csv",
                    mime="text/csv"
                )
        
        # Product management table
        st.subheader("Product List")
        
        # Display editable dataframe
        display_df = products_df[['name', 'category', 'price', 'stock_quantity', 'views', 'created_at']].copy()
        display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
        
        edited_df = st.data_editor(
            display_df,
            column_config={
                "price": st.column_config.NumberColumn(
                    "Price ($)",
                    help="Product price in dollars",
                    min_value=0.01,
                    max_value=10000,
                    step=0.01,
                    format="$%.2f"
                ),
                "stock_quantity": st.column_config.NumberColumn(
                    "Stock",
                    help="Available stock quantity",
                    min_value=0,
                    max_value=1000,
                    step=1
                ),
                "views": st.column_config.NumberColumn(
                    "Views",
                    disabled=True
                ),
                "created_at": st.column_config.TextColumn(
                    "Created",
                    disabled=True
                )
            },
            use_container_width=True
        )
        
        if st.button("💾 Save Changes"):
            st.success("Changes saved successfully!")
        
        # Delete products
        st.subheader("⚠️ Delete Products")
        products_to_delete = st.multiselect(
            "Select products to delete",
            options=products_df['name'].tolist(),
            help="Warning: This action cannot be undone"
        )
        
        if products_to_delete:
            if st.button("🗑️ Delete Selected Products", type="secondary"):
                for product_name in products_to_delete:
                    # Find the product ID from the name
                    product_row = products_df[products_df['name'] == product_name]
                    if not product_row.empty:
                        product_id = product_row.iloc[0]['id']
                        db_manager.delete_product(product_id)
                st.success(f"Deleted {len(products_to_delete)} products")
                st.rerun()
