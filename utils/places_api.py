import googlemaps
import pandas as pd
from datetime import datetime
import streamlit as st

class GooglePlacesClient:
    def __init__(self, api_key):
        self.client = googlemaps.Client(key=api_key)
    
    def search_places(self, query, location_type="restaurant"):
        """Search for places by query (name, address, etc.)"""
        try:
            result = self.client.places(
                query=query,
                type=location_type
            )
            return result.get('results', [])
        except Exception as e:
            st.error(f"Places search failed: {str(e)}")
            return []
    
    def get_place_details(self, place_id):
        """Get detailed information including reviews for a place"""
        try:
            result = self.client.place(
                place_id=place_id,
                fields=['name', 'rating', 'reviews', 'formatted_address', 'place_id']
            )
            return result.get('result', {})
        except Exception as e:
            st.error(f"Place details fetch failed: {str(e)}")
            return {}
    
    def reviews_to_dataframe(self, place_details):
        """Convert Google Places reviews to DataFrame matching CSV schema"""
        reviews = place_details.get('reviews', [])
        if not reviews:
            return pd.DataFrame()
        
        # Transform to match CSV format
        data = []
        for review in reviews:
            data.append({
                'review_text': review.get('text', ''),
                'rating': review.get('rating', 0),
                'user': review.get('author_name', 'Anonymous'),
                'timestamp': datetime.fromtimestamp(
                    review.get('time', 0)
                ).strftime('%Y-%m-%d') if review.get('time') else 'Unknown'
            })
        
        df = pd.DataFrame(data)
        # Filter out empty reviews
        df = df[df['review_text'].str.strip() != '']
        
        return df
    
    def fetch_reviews_for_query(self, query, max_places=3):
        """Complete pipeline: search -> get details -> extract reviews"""
        places = self.search_places(query)
        
        if not places:
            return pd.DataFrame(), []
        
        all_reviews = []
        place_info = []
        
        for place in places[:max_places]:
            place_id = place['place_id']
            details = self.get_place_details(place_id)
            
            if details:
                place_info.append({
                    'name': details.get('name', 'Unknown'),
                    'address': details.get('formatted_address', 'Unknown'),
                    'rating': details.get('rating', 0),
                    'place_id': place_id
                })
                
                reviews_df = self.reviews_to_dataframe(details)
                if not reviews_df.empty:
                    reviews_df['place_name'] = details.get('name', 'Unknown')
                    all_reviews.append(reviews_df)
        
        if all_reviews:
            combined_df = pd.concat(all_reviews, ignore_index=True)
            return combined_df, place_info
        else:
            return pd.DataFrame(), place_info
