import streamlit as st
import pandas as pd
from utils.schema import ReviewSchema
from models.local_infer import ReviewClassifier
from utils.highlight import TextHighlighter

def main():
    st.set_page_config(page_title="Review Cleaner", layout="wide")
    st.title("🧹 Review Cleaner")
    st.subtitle("Clean and classify Google reviews")
    
    # Placeholder for main app logic
    st.info("App skeleton created. Ready for implementation!")

if __name__ == "__main__":
    main()
