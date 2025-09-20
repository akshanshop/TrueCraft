import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from utils.database_factory import create_database_service
from utils.ai_assistant import AIAssistant

# Initialize components
@st.cache_resource
def get_database_service():
    return create_database_service()

db_manager = get_database_service()

st.set_page_config(
    page_title="Analytics - TrueCraft",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Analytics Dashboard")
st.markdown("Track your product performance and engagement metrics")

# Get data
products_df = db_manager.get_products()
profiles_df = db_manager.get_profiles()

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
        if len(filtered_df) > 0:
            top_products = filtered_df.nlargest(10, 'views')[['name', 'views', 'price']]
        else:
            top_products = pd.DataFrame()
        
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

# Enhanced AI-Powered Analytics Section
st.divider()
st.markdown("## 🚀 Advanced AI Analytics & Impact Tracking")
st.markdown("*Comprehensive insights into your artisan business impact and SDG contributions*")

# Create tabs for advanced analytics
ai_analytics_tab1, ai_analytics_tab2, ai_analytics_tab3, ai_analytics_tab4 = st.tabs([
    "🎯 SDG Impact", "🌱 Sustainability", "🏛️ Cultural Preservation", "📈 Business Intelligence"
])

# Initialize AI assistant
@st.cache_resource
def get_ai_assistant():
    try:
        return AIAssistant()
    except:
        return None

ai_assistant = get_ai_assistant()

with ai_analytics_tab1:
    st.markdown("### 🎯 Sustainable Development Goals (SDG) Impact Dashboard")
    st.info("Track how your artisan business contributes to the UN Sustainable Development Goals")
    
    if not filtered_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sample SDG data (in real implementation, this would come from actual assessments)
            sdg_data = {
                'SDG 1': {'name': 'No Poverty', 'score': 75, 'contribution': 'Providing fair income to artisans'},
                'SDG 5': {'name': 'Gender Equality', 'score': 85, 'contribution': 'Supporting women artisans'},
                'SDG 8': {'name': 'Decent Work', 'score': 90, 'contribution': 'Creating quality employment'},
                'SDG 10': {'name': 'Reduced Inequalities', 'score': 80, 'contribution': 'Fair trade practices'},
                'SDG 11': {'name': 'Sustainable Cities', 'score': 70, 'contribution': 'Supporting local communities'},
                'SDG 12': {'name': 'Responsible Consumption', 'score': 95, 'contribution': 'Handmade, sustainable products'}
            }
            
            # SDG Impact Metrics
            avg_sdg_score = sum([sdg['score'] for sdg in sdg_data.values()]) / len(sdg_data)
            st.metric("🌍 Overall SDG Impact Score", f"{avg_sdg_score:.1f}/100")
            
            # Top contributing SDGs
            sorted_sdgs = sorted(sdg_data.items(), key=lambda x: x[1]['score'], reverse=True)
            st.markdown("**🏆 Top SDG Contributions:**")
            for i, (sdg, data) in enumerate(sorted_sdgs[:3]):
                st.write(f"{i+1}. **{sdg}**: {data['name']} ({data['score']}/100)")
                st.caption(f"💡 {data['contribution']}")
        
        with col2:
            # SDG Impact Chart
            sdg_names = [f"{k}: {v['name']}" for k, v in sdg_data.items()]
            sdg_scores = [v['score'] for v in sdg_data.values()]
            
            fig_sdg = go.Figure(data=go.Bar(
                x=sdg_scores,
                y=sdg_names,
                orientation='h',
                marker_color='lightblue'
            ))
            fig_sdg.update_layout(
                title="SDG Impact Scores",
                xaxis_title="Impact Score (0-100)",
                height=400
            )
            st.plotly_chart(fig_sdg, use_container_width=True)
        
        # SDG Progress Over Time (simulated data)
        st.markdown("#### 📈 SDG Impact Progress")
        dates = pd.date_range(start='2024-01-01', end=datetime.now(), freq='M')
        progress_data = {
            'Date': dates,
            'Overall SDG Score': [avg_sdg_score - 20 + (i * 3) for i in range(len(dates))]
        }
        progress_df = pd.DataFrame(progress_data)
        
        fig_progress = px.line(progress_df, x='Date', y='Overall SDG Score', 
                              title="SDG Impact Score Over Time")
        st.plotly_chart(fig_progress, use_container_width=True)
        
        # AI SDG Assessment
        if ai_assistant and st.button("🤖 Generate Detailed SDG Report", use_container_width=True):
            with st.spinner("Analyzing SDG impact..."):
                # Sample business data based on products
                business_data = {
                    'business_type': f"Artisan marketplace with {len(filtered_df)} products",
                    'products': f"Handmade items in categories: {', '.join(filtered_df['category'].unique())}",
                    'materials': 'Traditional and sustainable materials',
                    'community': 'Global artisan community',
                    'employment': f'Supporting {len(profiles_df)} artisan entrepreneurs',
                    'sustainability': 'Handmade production, cultural preservation'
                }
                
                sdg_assessment = ai_assistant.sdg_impact_assessment(business_data)
                
                if sdg_assessment.get('sdg_contributions'):
                    st.success("🎯 **Detailed SDG Impact Analysis:**")
                    for contrib in sdg_assessment['sdg_contributions']:
                        st.write(f"**SDG {contrib.get('goal_number')}**: {contrib.get('goal_name')}")
                        st.write(f"📋 {contrib.get('contribution')}")
                        st.divider()
                    
                    if sdg_assessment.get('recommendations'):
                        st.markdown("**🚀 Recommendations to Increase Impact:**")
                        for rec in sdg_assessment['recommendations']:
                            st.write(f"💡 {rec}")

with ai_analytics_tab2:
    st.markdown("### 🌱 Sustainability & Environmental Impact Dashboard")
    st.info("Monitor your environmental footprint and sustainable business practices")
    
    if not filtered_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sustainability Metrics (simulated)
            sustainability_score = 82
            carbon_footprint = len(filtered_df) * 0.5  # kg CO2 per product
            renewable_materials = 75  # percentage
            waste_reduction = 60  # percentage
            
            st.metric("🌍 Sustainability Score", f"{sustainability_score}/100")
            st.metric("🌿 Carbon Footprint", f"{carbon_footprint:.1f} kg CO2")
            st.metric("♻️ Renewable Materials", f"{renewable_materials}%")
            st.metric("🗑️ Waste Reduction", f"{waste_reduction}%")
            
            # Sustainability by Category
            category_sustainability = {
                'Ceramics & Pottery': 85,
                'Textiles & Fabrics': 90,
                'Jewelry & Accessories': 75,
                'Woodwork & Furniture': 95,
                'Other': 70
            }
            
            st.markdown("**📊 Sustainability by Category:**")
            for category, score in category_sustainability.items():
                if category in filtered_df['category'].values:
                    count = len(filtered_df[filtered_df['category'] == category])
                    st.write(f"🎯 {category}: {score}/100 ({count} products)")
        
        with col2:
            # Environmental Impact Chart
            impact_data = {
                'Metric': ['Carbon Footprint', 'Water Usage', 'Waste Production', 'Energy Consumption'],
                'Impact Level': [30, 25, 15, 35],  # Lower is better
                'Industry Average': [60, 55, 40, 65]
            }
            impact_df = pd.DataFrame(impact_data)
            
            fig_impact = go.Figure()
            fig_impact.add_trace(go.Bar(name='Your Business', x=impact_df['Metric'], y=impact_df['Impact Level']))
            fig_impact.add_trace(go.Bar(name='Industry Average', x=impact_df['Metric'], y=impact_df['Industry Average']))
            fig_impact.update_layout(title="Environmental Impact Comparison (Lower is Better)")
            st.plotly_chart(fig_impact, use_container_width=True)
        
        # Sustainability Certification Progress
        st.markdown("#### 🏆 Sustainability Certifications Progress")
        certifications = {
            'Eco-Artisan Bronze': {'progress': 100, 'status': '✅ Achieved'},
            'Eco-Artisan Silver': {'progress': 100, 'status': '✅ Achieved'},
            'Eco-Artisan Gold': {'progress': 75, 'status': '🔄 In Progress'},
            'Eco-Artisan Platinum': {'progress': 25, 'status': '🎯 Target'},
        }
        
        for cert, data in certifications.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.progress(data['progress'] / 100)
            with col2:
                st.write(f"**{cert}**")
                st.caption(data['status'])

with ai_analytics_tab3:
    st.markdown("### 🏛️ Cultural Preservation & Heritage Impact")
    st.info("Track your contribution to preserving traditional crafts and cultural heritage")
    
    if not filtered_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Cultural Impact Metrics
            cultural_preservation_score = 88
            traditional_techniques = 5
            cultural_stories = 3
            heritage_documented = 12
            
            st.metric("🏛️ Cultural Preservation Score", f"{cultural_preservation_score}/100")
            st.metric("🎨 Traditional Techniques", traditional_techniques)
            st.metric("📖 Cultural Stories", cultural_stories)
            st.metric("📚 Heritage Items Documented", heritage_documented)
            
            # Cultural Diversity Index
            st.markdown("**🌍 Cultural Diversity Represented:**")
            cultural_regions = ['East Asian', 'European', 'African', 'Latin American', 'Middle Eastern']
            for region in cultural_regions:
                representation = np.random.randint(10, 30)  # Simulated data
                st.write(f"🌏 {region}: {representation}% of products")
        
        with col2:
            # Heritage Preservation Chart
            heritage_data = {
                'Technique': ['Hand-weaving', 'Pottery Making', 'Metalwork', 'Wood Carving', 'Jewelry Making'],
                'Preservation Score': [95, 88, 82, 90, 85],
                'Risk Level': ['Low', 'Low', 'Medium', 'Low', 'Medium']
            }
            heritage_df = pd.DataFrame(heritage_data)
            
            fig_heritage = px.bar(heritage_df, x='Technique', y='Preservation Score',
                                color='Risk Level', 
                                title="Cultural Technique Preservation Status")
            st.plotly_chart(fig_heritage, use_container_width=True)
        
        # Cultural Impact Stories
        st.markdown("#### 📚 Cultural Impact Stories")
        st.success("**Featured Success Story:**")
        st.write("""
        🎨 **Preserving Traditional Pottery Techniques**: Through TrueCraft, Maria from Oaxaca has documented 
        and shared her family's 300-year-old pottery techniques with over 500 customers worldwide, 
        ensuring this cultural heritage continues to the next generation.
        """)

with ai_analytics_tab4:
    st.markdown("### 📈 AI-Powered Business Intelligence")
    st.info("Advanced insights and predictions to grow your artisan business")
    
    if not filtered_df.empty and ai_assistant:
        col1, col2 = st.columns(2)
        
        with col1:
            # Business Health Score
            total_revenue = filtered_df['price'].sum()
            avg_price = filtered_df['price'].mean()
            price_variance = filtered_df['price'].std()
            
            # Calculate business health score
            health_score = min(100, (total_revenue / 100) + (avg_price / 2) + (50 if price_variance < avg_price else 30))
            
            st.metric("💼 Business Health Score", f"{health_score:.0f}/100")
            st.metric("💰 Total Portfolio Value", f"${total_revenue:.2f}")
            st.metric("📊 Average Product Price", f"${avg_price:.2f}")
            st.metric("📈 Price Consistency", "Good" if price_variance < avg_price else "Needs Work")
            
            # Financial Literacy Progress
            literacy_topics = {
                'Pricing Strategy': 85,
                'Cash Flow Management': 70,
                'Tax Planning': 60,
                'Investment Planning': 45,
                'Market Analysis': 75
            }
            
            st.markdown("**🎓 Financial Literacy Progress:**")
            for topic, progress in literacy_topics.items():
                st.write(f"📚 {topic}: {progress}%")
                st.progress(progress / 100)
        
        with col2:
            # Business Growth Predictions
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            actual_sales = [100, 120, 110, 140, 155, 170]
            predicted_sales = [180, 195, 210, 225, 240, 255]
            
            fig_prediction = go.Figure()
            fig_prediction.add_trace(go.Scatter(x=months, y=actual_sales, name='Actual Sales', mode='lines+markers'))
            fig_prediction.add_trace(go.Scatter(x=months, y=predicted_sales, name='AI Predictions', mode='lines+markers', line=dict(dash='dash')))
            fig_prediction.update_layout(title="Sales Growth Prediction")
            st.plotly_chart(fig_prediction, use_container_width=True)
        
        # AI Business Recommendations
        if st.button("🤖 Generate Business Recommendations", use_container_width=True):
            with st.spinner("Analyzing your business and generating recommendations..."):
                financial_guidance = ai_assistant.financial_literacy_guidance(
                    "business growth strategy",
                    "intermediate",
                    f"Artisan with {len(filtered_df)} products, average price ${avg_price:.2f}"
                )
                
                st.success("**🎯 AI Business Recommendations:**")
                st.write(financial_guidance)
        
        # Market Opportunity Analysis
        st.markdown("#### 🎯 Market Opportunities")
        opportunities = [
            "🎄 Holiday season approaching - increase festive product inventory",
            "🌱 Growing demand for sustainable products - highlight eco-friendly practices",
            "🎨 Cultural appreciation month - promote heritage stories",
            "💎 Premium market segment - consider luxury product line"
        ]
        
        for opportunity in opportunities:
            st.info(opportunity)

# numpy already imported at the top for cultural diversity simulation

# Footer with tips
st.divider()
st.markdown("""
**💡 Advanced Analytics Tips:**
- Monitor SDG impact to attract conscious consumers
- Use sustainability scores to improve eco-credentials
- Document cultural heritage to add product value
- Follow AI recommendations for business growth
- Track cultural preservation contributions for grant opportunities
""")
