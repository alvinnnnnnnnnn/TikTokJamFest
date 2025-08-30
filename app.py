import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv
from utils.schema import normalize_df
from models.local_infer import infer_batch
from utils.highlight import render_html_with_spans
from utils.places_api import GooglePlacesClient
import requests

# Load environment variables
load_dotenv()

@st.cache_data
def cached_inference(texts):
    """Cache inference results for identical text inputs"""
    return infer_batch(texts)

def main():
    st.set_page_config(
        page_title="Before → After: Trustworthy Review Feed", 
        layout="wide"
    )
    st.title("🧹 Before → After: Trustworthy Review Feed")
    st.subheader("Clean and classify Google reviews with confidence")
    
    # Sidebar controls
    with st.sidebar:
        # Google Places API Key input
        st.subheader("🔑 Google Places API Key")
        google_api_key = st.text_input(
            "Enter your Google Places API Key:",
            value=os.getenv("GOOGLE_PLACES_API_KEY", ""),
            type="password",
            help="Get your API key from Google Cloud Console",
            placeholder="AIzaSy..."
        )
        
        # Save API key to environment if provided
        if google_api_key:
            os.environ["GOOGLE_PLACES_API_KEY"] = google_api_key
        
        st.divider()
        # Initialize session state for mode if not exists
        if 'mode' not in st.session_state:
            st.session_state.mode = 'business'
        
        # Mode selection with vertical buttons
        st.subheader("Choose your use case:")
        
        if st.button(
            "🏢 Business Mode - CSV Analysis", 
            type="primary" if st.session_state.mode == 'business' else "secondary",
            use_container_width=True,
            help="Upload CSV files for batch processing"
        ):
            st.session_state.mode = 'business'
            st.rerun()
        
        if st.button(
            "🌍 Live Search - Location Reviews", 
            type="primary" if st.session_state.mode == 'live' else "secondary",
            use_container_width=True,
            help="Search locations for real-time review analysis"
        ):
            st.session_state.mode = 'live'
            st.rerun()
    
    # Route to appropriate mode
    if st.session_state.mode == 'business':
        business_mode()
    else:
        live_search_mode(google_api_key)

def business_mode():
    st.header("🏢 Business Mode - CSV Analysis")
    
    # CSV uploader
    uploaded_file = st.file_uploader(
        "Upload CSV file", 
        type=['csv'],
        help="CSV should contain review text in columns like 'text', 'review', 'content', or 'body'"
    )
    
    if uploaded_file is not None:
        try:
            # Load and normalize data
            with st.spinner("Loading and normalizing data..."):
                df = pd.read_csv(uploaded_file)
                df = normalize_df(df)
                
                st.success(f"Loaded {len(df)} reviews")
            
            # Get predictions
            with st.spinner("Classifying reviews..."):
                texts = df['review_text'].tolist()
                
                predictions = cached_inference(texts)
                
                # Merge predictions into dataframe
                df['label'] = [pred['label'] for pred in predictions]
                df['scores'] = [pred['scores'] for pred in predictions]  
                df['violations'] = [pred['violations'] for pred in predictions]
                df['spans'] = [pred['spans'] for pred in predictions]
                df['top_conf'] = [max(pred['scores'].values()) for pred in predictions]
                df['is_violation'] = [
                    pred['label'] in ['ad', 'irrelevant', 'rant'] and 
                    max(pred['scores'].values()) >= 0.6
                    for pred in predictions
                ]
                
                st.success("Classification complete!")
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["📋 Feed", "📊 Metrics", "💾 Export"])
            
            with tab1:
                st.header("Review Feed Comparison")
                
                # Search bar for reviews
                search_text = st.text_input(
                    "🔎 Search reviews:",
                    placeholder="Filter by review content...",
                    key="business_search"
                )
                
                # Filter options
                show_filter = st.radio(
                    "Show:",
                    ["All", "Valid only", "Violations only"],
                    horizontal=True,
                    key="business_filter"
                )
                
                # Filter dataframe based on selection
                if show_filter == "Valid only":
                    filtered_df = df[df['label'] == 'valid']
                elif show_filter == "Violations only":
                    filtered_df = df[df['is_violation'] == True]
                else:
                    filtered_df = df
                
                # Apply text search filter if provided
                if search_text:
                    filtered_df = filtered_df[
                        filtered_df['review_text'].str.contains(
                            search_text, 
                            case=False, 
                            na=False
                        )
                    ]
                    if len(filtered_df) == 0:
                        st.info(f"No reviews found matching '{search_text}'")
                    else:
                        st.info(f"Found {len(filtered_df)} reviews matching '{search_text}'")
                
                # Column headers
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🔍 Raw Reviews")
                with col2:
                    st.subheader("✨ Processed Reviews")
                
                # Process reviews in aligned pairs
                for idx, row in filtered_df.iterrows():
                    col1, col2 = st.columns(2)
                    
                    # Left column - Raw review
                    with col1:
                        with st.container():
                            # Basic metadata
                            meta_cols = st.columns([1, 1, 2])
                            if 'rating' in row:
                                meta_cols[0].caption(f"⭐ {row['rating']}")
                            if 'user' in row:
                                meta_cols[1].caption(f"👤 {row['user']}")
                            if 'timestamp' in row:
                                meta_cols[2].caption(f"📅 {row['timestamp']}")
                            
                            # Raw text
                            st.write(row['review_text'])
                    
                    # Right column - Processed review  
                    with col2:
                        with st.container():
                            # Badge and confidence
                            badge_col, conf_col = st.columns([1, 2])
                            
                            if row['label'] == 'valid':
                                badge_col.success("✅ Valid")
                            else:
                                badge_col.error(f"🚫 {row['label'].title()}")
                            
                            conf_col.caption(f"Confidence: {row['top_conf']:.2f}")
                            
                            # Highlighted text
                            highlighted_html = render_html_with_spans(
                                row['review_text'], 
                                [(span[0], span[1], span[2]) for span in row['spans']]
                            )
                            st.markdown(highlighted_html, unsafe_allow_html=True)
                            
                            # Violations
                            if row['violations']:
                                st.warning(f"⚠️ Issues: {', '.join(row['violations'])}")
                            
                            # Scores (sorted descending)
                            sorted_scores = sorted(row['scores'].items(), key=lambda x: x[1], reverse=True)
                            scores_text = " | ".join([f"{k}: {v:.2f}" for k, v in sorted_scores])
                            st.caption(f"Scores: {scores_text}")
                    
                    # Add divider after each pair
                    st.divider()
            
            with tab2:
                st.header("📊 Classification Metrics")
                
                # Label counts
                label_counts = df['label'].value_counts()
                label_order = ['valid', 'ad', 'irrelevant', 'rant']
                ordered_counts = [label_counts.get(label, 0) for label in label_order]
                
                # Bar chart
                chart_df = pd.DataFrame({
                    'Label': label_order,
                    'Count': ordered_counts
                })
                st.bar_chart(chart_df.set_index('Label'))
                
                # Summary stats
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Reviews", len(df))
                col2.metric("Valid Reviews", len(df[df['label'] == 'valid']))
                col3.metric("Flagged Reviews", len(df[df['is_violation'] == True]))
                col4.metric("Flag Rate", f"{(len(df[df['is_violation'] == True]) / len(df) * 100):.1f}%")
                
                # Detailed breakdown
                st.subheader("Detailed Breakdown")
                breakdown_df = df['label'].value_counts().reset_index()
                breakdown_df.columns = ['Label', 'Count']
                breakdown_df['Percentage'] = (breakdown_df['Count'] / len(df) * 100).round(1)
                st.dataframe(breakdown_df, width='stretch')
            
            with tab3:
                st.header("💾 Export Clean Dataset")
                
                # Filter for valid reviews only
                clean_df = df[df['label'] == 'valid'].copy()
                clean_df['reason'] = ""  # Empty reason column
                
                # Select relevant columns for export
                export_columns = ['review_text']
                if 'rating' in clean_df.columns:
                    export_columns.append('rating')
                if 'user' in clean_df.columns:
                    export_columns.append('user')
                if 'timestamp' in clean_df.columns:
                    export_columns.append('timestamp')
                export_columns.extend(['top_conf', 'reason'])
                
                export_df = clean_df[export_columns]
                
                st.write(f"**Clean dataset contains {len(export_df)} valid reviews**")
                st.dataframe(export_df.head(), width='stretch')
                
                # Download button
                csv_data = export_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download cleaned_reviews.csv",
                    data=csv_data,
                    file_name="cleaned_reviews.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.stop()
            
    else:
        # Sample data preview when no file uploaded
        st.info("👆 Upload a CSV file to get started")
        st.subheader("Expected CSV Format")
        sample_df = pd.DataFrame({
            'review_text': [
                'Great food and service!',
                'Check out our website at example.com for deals!',
                'Terrible experience, worst restaurant ever!!!',
                'Nice ambiance, will come again'
            ],
            'rating': [5, 4, 1, 4],
            'user': ['Alice', 'Bob', 'Charlie', 'Dana'],
            'timestamp': ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18']
        })
        st.dataframe(sample_df, width='stretch')

def live_search_mode(google_api_key):
    st.header("🌍 Live Location Search")
    
    if not google_api_key:
        st.warning("⚠️ Please configure Google Places API key in the sidebar to use live search.")
        st.info("Get your API key from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)")
        
        # Show usage instructions
        with st.expander("ℹ️ How to use Live Search"):
            st.write("""
            **Search Tips:**
            - Use specific business names: "McDonald's Times Square"
            - Search by category and location: "Pizza restaurants in San Francisco" 
            - Use full addresses for precise results
            - Try different variations if no results found
            
            **What happens:**
            1. Searches Google Places for matching locations
            2. Fetches up to 5 reviews per location (Google API limit)
            3. Runs the same classification model as CSV uploads
            4. Shows results with same visualizations and export options
            
            **Note:** Google Places API has usage limits and costs. Monitor your usage in Google Cloud Console.
            """)
    else:
        # Location search input
        col1, col2 = st.columns([3, 1])
        with col1:
            # Add geolocation button
            col_geo1, col_geo2 = st.columns([1, 2])
            with col_geo1:
                use_current_location = st.button("📍 Use My Location", key="geo_button")
            with col_geo2:
                st.caption("Click to automatically detect your current location")
                
            # Get user's IP address
            if use_current_location:
                try:
                    with st.spinner("🔄 Detecting your location..."):
                        # Get location from IP address using a free geolocation API
                        response = requests.get("http://ip-api.com/json/", timeout=5)
                        data = response.json()
                        
                        if data['status'] == 'success':
                            user_lat = data['lat']
                            user_lng = data['lon']
                            city = data.get('city', 'Unknown')
                            country = data.get('country', 'Unknown')
                            
                            # Store coordinates in session state
                            st.session_state.user_lat = user_lat
                            st.session_state.user_lng = user_lng
                            st.session_state.location_enabled = True
                            st.session_state.user_location = f"{city}, {country}"
                            
                            st.success(f"📍 Location detected: {city}, {country} ({user_lat:.4f}, {user_lng:.4f})")
                            st.rerun()
                        else:
                            st.error("Could not detect location from IP address")
                            
                except Exception as e:
                    st.error(f"Error detecting location: {str(e)}")
                
        with col2:
            # Only show search button if location is enabled and query is provided
            if st.session_state.get('location_enabled', False):
                search_query = st.text_input(
                    "🔍 Search for places near you:",
                    placeholder="e.g., 'Italian restaurants', 'coffee shops', 'pizza'",
                    key="search_query"
                )
                place_type = st.selectbox(
                    "Place type:",
                    ["restaurant", "cafe", "bar", "bakery", "meal_takeaway", "food"],
                    help="Type of places to search for"
                )
                
                search_button = st.button("🔍 Search", type="primary")
            else:
                search_button = st.button("🔍 Search", type="primary", disabled=True)
        
        if search_button and st.session_state.get('location_enabled', False):
            try:
                with st.spinner("Finding relevant places near you..."):
                    # Initialize Places client
                    places_client = GooglePlacesClient(google_api_key)
                    
                    # Use combined search: user location + search query for better results
                    places_with_reviews, place_info = places_client.fetch_reviews_for_query_and_location(
                        search_query,
                        (st.session_state.user_lat, st.session_state.user_lng),
                        place_type=place_type,
                        max_places=5
                    )
                    
                    if not places_with_reviews:
                        st.warning(f"No '{search_query}' places found near your location. Try a different search term.")
                    else:
                        # Store results in session state
                        st.session_state.search_results = places_with_reviews
                        st.session_state.search_place_info = place_info
                        st.session_state.search_query_text = search_query
                        st.session_state.current_place_page = 0  # Reset to first page
                        
                        # Process organized by place
                        process_reviews_by_place(places_with_reviews, place_info, search_query)
            except Exception as e:
                st.error(f"Error fetching live reviews: {str(e)}")
        
        # Show existing results if they exist in session state
        elif 'search_results' in st.session_state and st.session_state.search_results:
            process_reviews_by_place(
                st.session_state.search_results, 
                st.session_state.search_place_info, 
                st.session_state.search_query_text
            )
        
        # Show usage instructions when not searching
        if not search_button:
            with st.expander("ℹ️ How to use Live Search"):
                st.write("""
                **Search Tips:**
                - Use specific business names: "McDonald's Times Square"
                - Search by category and location: "Pizza restaurants in San Francisco" 
                - Use full addresses for precise results
                - Try different variations if no results found
                
                **What happens:**
                1. Searches Google Places for matching locations
                2. Fetches up to 5 reviews per location (Google API limit)
                3. Runs the same classification model as CSV uploads
                4. Shows results with same visualizations and export options
                
                **Note:** Google Places API has usage limits and costs. Monitor your usage in Google Cloud Console.
                """)

def process_reviews_by_place(places_with_reviews, place_info, search_query):
    # Initialize pagination state
    if 'current_place_page' not in st.session_state:
        st.session_state.current_place_page = 0
        
    total_places = len(places_with_reviews)
    current_page = st.session_state.current_place_page
    
    # Ensure current page is within bounds
    if current_page >= total_places:
        st.session_state.current_place_page = 0
        current_page = 0
    
    # Pagination controls at the top
    if total_places > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("◀ Previous", disabled=(current_page == 0)):
                st.session_state.current_place_page = max(0, current_page - 1)
                st.rerun()
        
        with col2:
            st.markdown(f"<div style='text-align: center; padding: 8px;'><strong>Place {current_page + 1} of {total_places}</strong></div>", unsafe_allow_html=True)
        
        with col3:
            if st.button("Next ▶", disabled=(current_page >= total_places - 1)):
                st.session_state.current_place_page = min(total_places - 1, current_page + 1)
                st.rerun()
        
        st.divider()
    
    # Show current place
    place = places_with_reviews[current_page]
    st.subheader(f"📍 {place['name']}")
    
    # Normalize the reviews DataFrame
    normalized_df = normalize_df(place['reviews'].copy())
    
    # Limit to 200 reviews (hard-coded)
    if len(normalized_df) > 200:
        normalized_df = normalized_df.head(200)
        st.info(f"Showing first 200 reviews out of {len(place['reviews'])} total")
    
    # Run classification
    with st.spinner("Classifying live reviews..."):
        texts = normalized_df['review_text'].tolist()
        predictions = cached_inference(texts)
        
        # Merge predictions
        normalized_df['label'] = [pred['label'] for pred in predictions]
        normalized_df['scores'] = [pred['scores'] for pred in predictions]
        normalized_df['violations'] = [pred['violations'] for pred in predictions]
        normalized_df['spans'] = [pred['spans'] for pred in predictions]
        normalized_df['top_conf'] = [max(pred['scores'].values()) for pred in predictions]
        normalized_df['is_violation'] = [
            pred['label'] in ['ad', 'irrelevant', 'rant'] and 
            max(pred['scores'].values()) >= 0.6
            for pred in predictions
        ]
    
    st.success(f"✅ Processed {len(normalized_df)} live reviews")
    
    # Create tabs for results
    tab1 = st.tabs(["📋 Review Feed"])
    
    with tab1[0]:
        # Show quick stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Reviews", len(normalized_df))
        col2.metric("Valid Reviews", len(normalized_df[normalized_df['label'] == 'valid']))
        col3.metric("Flagged Reviews", len(normalized_df[normalized_df['is_violation'] == True]))
        
        # Filter options
        show_filter = st.radio(
            "Show:",
            ["All", "Valid only", "Violations only"],
            horizontal=True,
            key=f"place_filter_{current_page}"
        )
        
        # Filter dataframe based on selection
        if show_filter == "Valid only":
            filtered_df = normalized_df[normalized_df['label'] == 'valid']
        elif show_filter == "Violations only":
            filtered_df = normalized_df[normalized_df['is_violation'] == True]
        else:
            filtered_df = normalized_df
        
        # Search bar
        search_text = st.text_input("🔎 Search reviews", key=f"live_search_filter_{current_page}")
        
        # Apply text search filter if provided
        if search_text:
            filtered_df = filtered_df[
                filtered_df['review_text'].str.contains(
                    search_text, 
                    case=False, 
                    na=False
                )
            ]
            if len(filtered_df) == 0:
                st.info(f"No reviews found matching '{search_text}'")
            else:
                st.info(f"Found {len(filtered_df)} reviews matching '{search_text}'")
        
        # Show sample of results
        st.subheader("📋 Review Feed")
        for idx, row in filtered_df.head(10).iterrows():
            # Single row layout for each review
            with st.container():
                # Metadata row with status beside date
                meta_cols = st.columns([1, 1, 2, 1])
                meta_cols[0].caption(f"⭐ {row['rating']}")
                meta_cols[1].caption(f"👤 {row['user']}")
                meta_cols[2].caption(f"📅 {row['timestamp']}")
                
                # Status with colored boxes (lighter versions of Streamlit colors)
                if row['label'] == 'valid':
                    meta_cols[3].markdown('<div style="background-color: #e8f5e8; color: #0f5132; padding: 4px 8px; border-radius: 4px; border: 1px solid #badbcc; text-align: center; font-size: 0.9em; font-weight: bold;">✅ Valid</div>', unsafe_allow_html=True)
                else:
                    meta_cols[3].markdown(f'<div style="background-color: #f8e8e8; color: #58151c; padding: 4px 8px; border-radius: 4px; border: 1px solid #f1aeb5; text-align: center; font-size: 0.8em;">🚫 {row["label"].title()}</div>', unsafe_allow_html=True)
                
                # Review text takes full width
                st.write(row['review_text'])
                
                # Violations if any
                if row['violations']:
                    st.warning(f"⚠️ Issues: {', '.join(row['violations'])}")
            
            st.divider()
    
    # Pagination controls at the bottom
    if total_places > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("◀ Previous Place", disabled=(current_page == 0), key="prev_bottom"):
                st.session_state.current_place_page = max(0, current_page - 1)
                st.rerun()
        
        with col2:
            st.markdown(f"<div style='text-align: center; padding: 8px;'><strong>Place {current_page + 1} of {total_places}</strong></div>", unsafe_allow_html=True)
        
        with col3:
            if st.button("Next Place ▶", disabled=(current_page >= total_places - 1), key="next_bottom"):
                st.session_state.current_place_page = min(total_places - 1, current_page + 1)
                st.rerun()

if __name__ == "__main__":
    main()
