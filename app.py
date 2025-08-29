import streamlit as st
import pandas as pd
import requests
import json
from utils.schema import normalize_df
from models.local_infer import infer_batch
from utils.highlight import render_html_with_spans

def main():
    st.set_page_config(
        page_title="Before → After: Trustworthy Review Feed", 
        layout="wide"
    )
    st.title("🧹 Before → After: Trustworthy Review Feed")
    st.subtitle("Clean and classify Google reviews with confidence")
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # CSV uploader
        uploaded_file = st.file_uploader(
            "Upload CSV file", 
            type=['csv'],
            help="CSV should contain review text in columns like 'text', 'review', 'content', or 'body'"
        )
        
        # Model connection
        model_type = st.radio(
            "Model connection",
            ["Local Python", "HTTP API"],
            help="Choose between local rule-based model or remote API"
        )
        
        # HTTP API configuration
        api_url = None
        api_headers = {}
        if model_type == "HTTP API":
            api_url = st.text_input(
                "API URL",
                placeholder="https://your-api.com/classify_batch",
                help="URL for the batch classification endpoint"
            )
            
            headers_json = st.text_area(
                "Headers (JSON)",
                placeholder='{"Authorization": "Bearer token"}',
                help="Optional HTTP headers as JSON"
            )
            
            if headers_json.strip():
                try:
                    api_headers = json.loads(headers_json)
                except json.JSONDecodeError:
                    st.error("Invalid JSON format for headers")
        
        # Confidence threshold
        confidence_threshold = st.slider(
            "Min confidence to mark as violation",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.05,
            help="Reviews with confidence above this threshold will be flagged"
        )
        
        # Max rows
        max_rows = st.number_input(
            "Max rows to process",
            min_value=1,
            max_value=10000,
            value=200,
            help="Limit processing to avoid timeouts"
        )
    
    # Main content
    if uploaded_file is not None:
        try:
            # Load and normalize data
            with st.spinner("Loading and normalizing data..."):
                df = pd.read_csv(uploaded_file)
                df = normalize_df(df)
                
                if len(df) > max_rows:
                    df = df.head(max_rows)
                    st.info(f"Truncated to first {max_rows} rows")
                
                st.success(f"Loaded {len(df)} reviews")
            
            # Get predictions
            with st.spinner("Classifying reviews..."):
                texts = df['review_text'].tolist()
                
                if model_type == "HTTP API" and api_url:
                    try:
                        # Call HTTP API
                        payload = {"texts": texts}
                        response = requests.post(
                            api_url, 
                            json=payload, 
                            headers=api_headers,
                            timeout=30
                        )
                        response.raise_for_status()
                        predictions = response.json()
                        
                    except requests.RequestException as e:
                        st.error(f"HTTP API call failed: {str(e)}")
                        st.stop()
                        
                else:
                    # Use local model
                    predictions = infer_batch(texts)
                
                # Merge predictions into dataframe
                df['label'] = [pred['label'] for pred in predictions]
                df['scores'] = [pred['scores'] for pred in predictions]  
                df['violations'] = [pred['violations'] for pred in predictions]
                df['spans'] = [pred['spans'] for pred in predictions]
                df['top_conf'] = [max(pred['scores'].values()) for pred in predictions]
                df['is_violation'] = [
                    pred['label'] in ['ad', 'irrelevant', 'rant'] and 
                    max(pred['scores'].values()) >= confidence_threshold
                    for pred in predictions
                ]
                
                st.success("Classification complete!")
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["📋 Feed", "📊 Metrics", "💾 Export"])
            
            with tab1:
                st.header("Review Feed Comparison")
                
                # Filter options
                show_filter = st.radio(
                    "Show:",
                    ["All", "Valid only", "Violations only"],
                    horizontal=True
                )
                
                # Filter dataframe based on selection
                if show_filter == "Valid only":
                    filtered_df = df[df['label'] == 'valid']
                elif show_filter == "Violations only":
                    filtered_df = df[df['is_violation'] == True]
                else:
                    filtered_df = df
                
                # Two columns layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🔍 Raw Reviews")
                    for idx, row in filtered_df.iterrows():
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
                            st.divider()
                
                with col2:
                    st.subheader("✨ Processed Reviews")
                    for idx, row in filtered_df.iterrows():
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
                st.dataframe(breakdown_df, use_container_width=True)
            
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
                st.dataframe(export_df.head(), use_container_width=True)
                
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
        # Welcome message
        st.info("👆 Upload a CSV file to get started!")
        
        # Show sample data format
        st.subheader("Expected CSV Format")
        sample_df = pd.DataFrame({
            'review_text': [
                "Great service and food!",
                "Visit our website www.promo.com for deals!",
                "Never been here but heard it's bad."
            ],
            'rating': [5, 1, 2],
            'user': ['Alice', 'PromoBot', 'Reviewer'],
            'timestamp': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        st.dataframe(sample_df, use_container_width=True)

if __name__ == "__main__":
    main()
