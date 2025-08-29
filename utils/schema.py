from typing import Dict, Any
import pandas as pd

REQUIRED_COL = "review_text"
CANDIDATE_COLS = ["text", "review", "content", "body"]

class ReviewSchema:
    """Schema definitions for review data"""
    
    REQUIRED_COLUMNS = [
        'review_id',
        'review_text', 
        'rating',
        'user',
        'timestamp'
    ]
    
    CLASSIFICATION_CATEGORIES = [
        'valid',
        'ad', 
        'irrelevant',
        'rant'
    ]
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
        """Validate uploaded CSV matches expected schema"""
        validation_result = {
            'is_valid': True,
            'missing_columns': [],
            'extra_columns': [],
            'row_count': len(df)
        }
        
        # Check for missing required columns
        missing_cols = [col for col in ReviewSchema.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            validation_result['is_valid'] = False
            validation_result['missing_columns'] = missing_cols
            
        # Note extra columns (not necessarily invalid)
        extra_cols = [col for col in df.columns if col not in ReviewSchema.REQUIRED_COLUMNS]
        validation_result['extra_columns'] = extra_cols
        
        return validation_result

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize dataframe by lowercasing columns, ensuring review_text exists,
    and dropping NA values in review_text column.
    """
    # Create a copy to avoid modifying original
    normalized_df = df.copy()
    
    # Lowercase all column names
    normalized_df.columns = normalized_df.columns.str.lower()
    
    # Check if review_text already exists
    if REQUIRED_COL not in normalized_df.columns:
        # Try to find a suitable candidate column
        found_col = None
        for candidate in CANDIDATE_COLS:
            if candidate in normalized_df.columns:
                found_col = candidate
                break
        
        if found_col:
            # Rename the found column to review_text
            normalized_df = normalized_df.rename(columns={found_col: REQUIRED_COL})
        else:
            raise ValueError(f"No suitable text column found. Expected one of: {CANDIDATE_COLS}")
    
    # Drop rows where review_text is NA/null
    normalized_df = normalized_df.dropna(subset=[REQUIRED_COL])
    
    return normalized_df
