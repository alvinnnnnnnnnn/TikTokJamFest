import googlemaps
import pandas as pd
from datetime import datetime
import streamlit as st

class GooglePlacesClient:
    def __init__(self, api_key):
        self.client = googlemaps.Client(key=api_key)
    
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
    
    def fetch_reviews_for_query_and_location(self, query, user_coordinates, place_type="restaurant", max_places=5):
        """Search for places using query near user's location - combines relevance with proximity"""
        try:
            # Search using query with location bias for better results
            result = self.client.places(
                query=f"{query} near me",
                location=user_coordinates,
                radius=5000,
                type=place_type
            )
            places = result.get('results', [])
            
            if not places:
                return [], []
            
            # Fetch reviews for each place (organized by place)
            places_with_reviews = []
            place_info = []
            
            for place in places[:max_places]:
                place_id = place['place_id']
                place_name = place.get('name', 'Unknown')
                
                # Get place details including reviews
                details = self.get_place_details(place_id)
                
                if details:
                    place_info.append({
                        'name': place_name,
                        'address': details.get('formatted_address', 'Unknown'),
                        'rating': details.get('rating', 0),
                        'place_id': place_id
                    })
                    
                    # Get reviews for this specific place
                    reviews_df = self.reviews_to_dataframe(details)
                    if not reviews_df.empty:
                        reviews_df['place_name'] = place_name
                        places_with_reviews.append({
                            'name': place_name,
                            'reviews': reviews_df
                        })
            
            return places_with_reviews, place_info
            
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
            return [], []
