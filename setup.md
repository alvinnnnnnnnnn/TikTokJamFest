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

## Smoke Tests

Run these acceptance tests to verify the app works correctly:

### Test 1: Local Mode Functionality
1. Run `streamlit run app.py`
2. Upload `assets/sample_reviews.csv`
3. Ensure "Local Python" is selected in sidebar
4. **Expected**: See classified labels (Valid/Ad/Rant) and colored highlights on the right column
5. **Pass criteria**: All 10 reviews processed with badges and highlighting

### Test 2: Model Performance & Accuracy
Verify the local model produces expected classifications:

1. Upload `assets/sample_reviews.csv`
2. Check specific expected results:
   - **Sarah_M review** → Valid (confidence >0.6)
   - **PromoBot_123 review** → Ad (contains www.bestdeals.com)
   - **AngryCustomer review** → Rant (ALL CAPS, multiple !!!!)
   - **RandomReviewer review** → Rant (contains "never been")
3. **Expected**: Classifications match the rule-based logic
4. **Pass criteria**: At least 8/10 reviews classified as expected

### Test 3: Local Model Integration
Test the model can be easily replaced:

1. Note current `models/local_infer.py` uses rule-based logic
2. Verify `infer_batch()` function returns correct API format
3. **Expected**: Function returns list of dicts with `label`, `scores`, `violations`, `spans`
4. **Pass criteria**: Model replacement would only require updating `infer_batch()` function

### Test 4: Confidence Threshold Toggle
1. Upload sample CSV with default settings
2. Note initial violation count in Metrics tab
3. Set "Min confidence to mark as violation" to 0.95
4. **Expected**: Fewer violations flagged (higher threshold = stricter filtering)
5. **Pass criteria**: Violation count decreases, "Valid only" filter shows more reviews

### Test 5: CSV Export Functionality
1. Process sample CSV with any settings
2. Go to Export tab
3. Click "📥 Download cleaned_reviews.csv"
4. Open downloaded file
5. **Expected**: Only valid reviews present, with confidence scores
6. **Pass criteria**: CSV contains only reviews with `label="valid"`, has `reason` column

### Test 6: Large Dataset Performance
Create a larger test file:

```bash
# Generate larger CSV for testing
python -c "
import pandas as pd
import random

# Base reviews to replicate
base_reviews = [
    'Great food and amazing service!',
    'Visit our website www.deals.com for offers!',
    'TERRIBLE PLACE!!!! WORST EVER!!!!',
    'Never been here but heard bad things.',
    'Nice atmosphere, good food.',
    'Check out our promo at https://sale.com',
    'Lovely place for dinner.',
    'Bad service.',
    'Outstanding quality.',
    'Haven\'t been myself but friend said no good.'
]

# Generate 1000 rows
data = []
for i in range(1000):
    review = random.choice(base_reviews)
    data.append({
        'review_text': f'{review} #{i}',
        'rating': random.randint(1, 5),
        'user': f'User_{i}',
        'timestamp': f'2024-01-{(i%30)+1:02d}'
    })

df = pd.DataFrame(data)
df.to_csv('large_test.csv', index=False)
print('Generated large_test.csv with 1000 rows')
"
```

Test:
1. Upload `large_test.csv`
2. Set "Max rows to process" to 200
3. **Expected**: App processes only first 200 rows, remains responsive
4. Try increasing to 500, then 1000
5. **Pass criteria**: UI stays responsive, processing completes within reasonable time

### Test 7: Column Mapping
Test CSV normalization:

```bash
# Create CSV with different column names
cat > different_columns.csv << 'EOF'
id,text,score,reviewer,date
1,"Great place!",5,"Alice","2024-01-01"
2,"Visit www.promo.com for deals!",1,"Bot","2024-01-02"
3,"Never been but heard it's bad.",2,"Bob","2024-01-03"
EOF
```

Test:
1. Upload `different_columns.csv`
2. **Expected**: App automatically maps `text` column to `review_text`
3. **Pass criteria**: Reviews process normally despite different column names

## Pass/Fail Criteria

All tests should pass for the app to be considered ready for deployment:
- ✅ Local classification works with visual feedback
- ✅ Model performance and accuracy meet expectations
- ✅ Local model integration is seamless
- ✅ Threshold adjustment affects violation detection
- ✅ Export produces valid-only CSV files
- ✅ Large datasets are handled with performance controls
- ✅ Column mapping works for different CSV formats

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
3. Try the local model with different datasets
4. Deploy to Streamlit Cloud or Hugging Face Spaces
