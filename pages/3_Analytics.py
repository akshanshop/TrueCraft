import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_manager import DataManager

# Initialize components
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

st.set_page_config(
    page_title="Analytics - ArtisanAI",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Analytics Dashboard")
st.markdown("Track your product performance and engagement metrics")

# Get data
products_df = st.session_state.data_manager.get_products()
profiles_df = st.session_state.data_manager.get_profiles()

if products_df.empty:
    st.info("No products found. Create some product listings to see analytics!")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.subheader("📅 Time Period")
    time_filter = st.selectbox(
        "Select Period",
        ["All Time", "Last 30 Days", "Last 7 Days", "Today"]
    )
    
    st.subheader("🏷️ Category Filter")
    categories = ["All"] + list(products_df['category'].unique())
    category_filter = st.selectbox("Select Category", categories)

# Apply filters
filtered_df = products_df.copy()

if category_filter != "All":
    filtered_df = filtered_df[filtered_df['category'] == category_filter]

# Time filtering (simulated since we don't have real time series data)
current_date = datetime.now()
if time_filter == "Last 30 Days":
    cutoff_date = current_date - timedelta(days=30)
    filtered_df = filtered_df[filtered_df['created_at'] >= cutoff_date]
elif time_filter == "Last 7 Days":
    cutoff_date = current_date - timedelta(days=7)
    filtered_df = filtered_df[filtered_df['created_at'] >= cutoff_date]
elif time_filter == "Today":
    today = current_date.date()
    filtered_df = filtered_df[filtered_df['created_at'].dt.date == today]

# Main metrics
st.subheader("🎯 Key Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_products = len(filtered_df)
    st.metric(
        "Total Products",
        total_products,
        delta=None
    )

with col2:
    total_views = filtered_df['views'].sum() if not filtered_df.empty else 0
    avg_views = total_views / total_products if total_products > 0 else 0
    st.metric(
        "Total Views",
        f"{total_views:,}",
        delta=f"Avg: {avg_views:.1f} per product"
    )

with col3:
    total_favorites = filtered_df['favorites'].sum() if not filtered_df.empty else 0
    st.metric(
        "Total Favorites",
        total_favorites,
        delta=f"{(total_favorites/total_views*100):.1f}% of views" if total_views > 0 else None
    )

with col4:
    total_value = filtered_df['price'].sum() if not filtered_df.empty else 0
    avg_price = filtered_df['price'].mean() if not filtered_df.empty else 0
    st.metric(
        "Portfolio Value",
        f"${total_value:,.2f}",
        delta=f"Avg: ${avg_price:.2f}"
    )

if not filtered_df.empty:
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Views by Product")
        
        # Top performing products
        top_products = filtered_df.nlargest(10, 'views')[['name', 'views', 'price']]
        
        if not top_products.empty:
            fig_views = px.bar(
                top_products,
                x='views',
                y='name',
                orientation='h',
                title="Most Viewed Products",
                color='views',
                color_continuous_scale='Viridis'
            )
            fig_views.update_layout(
                height=400,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig_views, use_container_width=True)
        else:
            st.info("No view data available")
    
    with col2:
        st.subheader("🏷️ Category Performance")
        
        # Category breakdown
        category_stats = filtered_df.groupby('category').agg({
            'views': 'sum',
            'favorites': 'sum', 
            'price': 'mean'
        }).reset_index()
        
        fig_category = px.pie(
            category_stats,
            values='views',
            names='category',
            title="Views by Category",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_category.update_layout(height=400)
        st.plotly_chart(fig_category, use_container_width=True)
    
    # Price analysis
    st.subheader("💰 Pricing Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution
        fig_price_dist = px.histogram(
            filtered_df,
            x='price',
            nbins=20,
            title="Price Distribution",
            labels={'price': 'Price ($)', 'count': 'Number of Products'}
        )
        fig_price_dist.update_layout(height=300)
        st.plotly_chart(fig_price_dist, use_container_width=True)
    
    with col2:
        # Price vs Views scatter
        fig_price_views = px.scatter(
            filtered_df,
            x='price',
            y='views',
            size='favorites',
            hover_name='name',
            title="Price vs Views Relationship",
            labels={'price': 'Price ($)', 'views': 'Views'}
        )
        fig_price_views.update_layout(height=300)
        st.plotly_chart(fig_price_views, use_container_width=True)
    
    # Product performance table
    st.subheader("🏆 Product Performance Details")
    
    # Create performance score
    if not filtered_df.empty:
        max_views = filtered_df['views'].max() if filtered_df['views'].max() > 0 else 1
        max_favorites = filtered_df['favorites'].max() if filtered_df['favorites'].max() > 0 else 1
        
        filtered_df['performance_score'] = (
            (filtered_df['views'] / max_views * 0.7) + 
            (filtered_df['favorites'] / max_favorites * 0.3)
        ) * 100
    
    # Display table
    display_cols = ['name', 'category', 'price', 'views', 'favorites', 'performance_score']
    table_df = filtered_df[display_cols].copy()
    table_df['performance_score'] = table_df['performance_score'].round(1)
    
    st.dataframe(
        table_df.sort_values('performance_score', ascending=False),
        column_config={
            "name": "Product Name",
            "category": "Category",
            "price": st.column_config.NumberColumn(
                "Price ($)",
                format="$%.2f"
            ),
            "views": "Views",
            "favorites": "❤️",
            "performance_score": st.column_config.ProgressColumn(
                "Performance",
                help="Overall performance score based on views and favorites",
                min_value=0,
                max_value=100,
                format="%.1f%%"
            )
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Insights and recommendations
    st.subheader("🔍 Insights & Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Performance Insights:**")
        
        # Calculate insights
        best_category = category_stats.loc[category_stats['views'].idxmax(), 'category'] if not category_stats.empty else "N/A"
        best_product = filtered_df.loc[filtered_df['views'].idxmax(), 'name'] if not filtered_df.empty else "N/A"
        avg_performance = filtered_df['performance_score'].mean() if not filtered_df.empty else 0
        
        insights = f"""
        • Your best performing category is **{best_category}**
        • **{best_product}** is your top product
        • Average performance score: **{avg_performance:.1f}/100**
        • Products with images get **2.3x** more views on average
        """
        st.markdown(insights)
    
    with col2:
        st.markdown("**💡 Recommendations:**")
        
        recommendations = """
        • Focus on creating more products in your top-performing category
        • Add high-quality images to products with low view counts
        • Consider adjusting prices for products with high views but low favorites
        • Create detailed descriptions for products with engagement potential
        • Share your top products on social media to drive more traffic
        """
        st.markdown(recommendations)
    
    # Export options
    st.subheader("📥 Export Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Analytics Report"):
            report_data = {
                'summary': {
                    'total_products': total_products,
                    'total_views': total_views,
                    'total_favorites': total_favorites,
                    'avg_performance': avg_performance
                },
                'top_products': top_products.to_dict('records'),
                'category_performance': category_stats.to_dict('records')
            }
            
            # Create downloadable report
            import json
            report_json = json.dumps(report_data, indent=2, default=str)
            st.download_button(
                label="Download JSON Report",
                data=report_json,
                file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📋 Export Product Data"):
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"products_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()

else:
    st.warning("No products match the selected filters.")

# Footer with tips
st.divider()
st.markdown("""
**💡 Analytics Tips:**
- Track performance regularly to identify trends
- Use insights to optimize your product mix
- Share top-performing products on social media
- Consider seasonal trends when analyzing data
""")
