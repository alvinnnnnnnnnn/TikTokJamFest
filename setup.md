# Setup Guide

This guide will help you set up the development environment and run the Review Cleaner app locally.

## Prerequisites

- Python 3.8 or higher
- Git (optional, for cloning)

## Environment Setup

### Option 1: Python Virtual Environment (Recommended)

1. **Navigate to project directory**
   ```bash
   cd /path/to/TikTokJamFest
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # macOS/Linux
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```
   Your terminal prompt should now show `(venv)` at the beginning.

4. **Upgrade pip**
   ```bash
   pip install --upgrade pip
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Conda Environment

1. **Create conda environment**
   ```bash
   conda create -n review-cleaner python=3.9
   ```

2. **Activate environment**
   ```bash
   conda activate review-cleaner
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

2. **Open in browser**
   - The app will automatically open at `http://localhost:8501`
   - If it doesn't open automatically, navigate to the URL manually

## Testing the App

1. **Upload sample data**
   - Use the sidebar file uploader
   - Upload `assets/sample_reviews.csv` for testing

2. **Configure settings**
   - Keep "Local Python" selected for initial testing
   - Adjust confidence threshold as needed (default: 0.6)

3. **Explore features**
   - **Feed Tab**: Compare raw vs processed reviews
   - **Metrics Tab**: View classification statistics
   - **Export Tab**: Download cleaned dataset

## Expected Test Results

With the sample data, you should see:
- **4 Valid reviews** (Sarah_M, John_D, CoupleGoals, FoodieExpert)
- **2 Ad reviews** (PromoBot_123, FakeAccount_99) 
- **2 Rant reviews** (AngryCustomer, LazyReviewer)
- **2 Irrelevant reviews** (RandomReviewer, SecondHand_Info)

## Troubleshooting

### Command Not Found Error
If you get "streamlit: command not found":
1. Ensure your virtual environment is activated
2. Re-run `pip install -r requirements.txt`
3. Verify installation: `streamlit --version`

### Import Errors
If you get module import errors:
1. Check that you're in the project root directory
2. Ensure all files were created correctly
3. Verify Python path includes the project directory

### Port Already in Use
If port 8501 is busy:
```bash
streamlit run app.py --server.port 8502
```

## Deactivating Environment

When you're done working:
```bash
# For venv
deactivate

# For conda
conda deactivate
```

## File Structure

```
TikTokJamFest/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── setup.md                  # This setup guide
├── README.md                 # Project documentation
├── models/
│   ├── __init__.py
│   └── local_infer.py        # Local classification model
├── utils/
│   ├── __init__.py
│   ├── highlight.py          # Text highlighting utilities  
│   └── schema.py             # Data validation and normalization
├── assets/
│   └── sample_reviews.csv    # Sample data for testing
└── venv/                     # Virtual environment (created after setup)
```

## Next Steps

Once the app is running successfully:
1. Test with your own CSV data
2. Experiment with different confidence thresholds
3. Try the HTTP API mode (when you have an endpoint available)
4. Deploy to Streamlit Cloud or Hugging Face Spaces
