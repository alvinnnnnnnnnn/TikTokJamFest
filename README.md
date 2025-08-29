# TikTok TechJam

## Problem Statement
Design and implement an ML-based system to evaluate the quality and relevancy of Google location reviews. Our system determines if the review is:
1. High Quality: The review is relevant to the location and provides meaningful feedback
2. Low Quality: The review contains only a rating with little to no text, or consists of very short/uninformative comments 
3. Fake: A fabricated review, such as when the reviewer has not actually visited the location
4. Irrelevant: The review discusses topics unrelated to the location
5. Advertisements: The review includes promotional content or external links unrelated to the business

---

## API Contract

### Batch Classification Endpoint

**POST /classify_batch**

Request:
```json
{"texts": ["review 1", "review 2", "..."]}
```

Response: **200 OK**
```json
[
  {
    "label": "ad",                       // one of: valid|ad|irrelevant|rant
    "scores": {"ad": 0.91, "valid": 0.05, "irrelevant": 0.03, "rant": 0.01},
    "violations": ["No Advertisement"],  // zero or more strings
    "spans": [["promo", 10, 25], ["url", 40, 60]]   // optional highlights (type, start, end)
  }
]
```

**Note:** If HTTP endpoint is unavailable, a local Python function will be used with the same return shape.

---

## Table of Contents
- [API Contract](#api-contract)
- [Quick Start](#quick-start)
- [Datasets Used](#datasets-used)
- [Solution](#solution)
- [Model Metrics](#model-metrics)
- [Member Contributions](#member-contributions)

---

## Quick Start
If you want to find out more about the solution, you can follow these simple steps (Ensure that you have a GPU enabled device):
1. Install anaconda from [here](https://www.anaconda.com/) 
2. Install CUDA Toolkit from [here](https://developer.nvidia.com/cuda-toolkit) 
3. Install Git
4. Run the following lines in your terminal (either IDE or device)
```bash
# Clone the repository
git clone https://github.com/alvinnnnnnnnnn/MentalHealth-LLM.git

# Create a conda environment
conda create -n ENV_NAME python=3.9

# Activate the environment
conda activate ENV_NAME`

# Installing / Upgrading required libraries 
pip install --upgrade -r requirements.txt
```
5. Install [pytorch](https://pytorch.org/) based on your OS

## Datasets Used

## Solution


## Model Metrics
To evaluate the model's performance based on our use case, the following weighted metrics system was used:

|Metrics             |  |||
|--------------------|:---:|:---:|:-----:|


## Member Contributions

# Review Cleaner

A Streamlit web app for cleaning and classifying Google reviews.

## Features

- Upload CSV files containing Google reviews
- Automatic classification (valid | ad | irrelevant | rant)
- Before vs After review comparison
- Text highlighting for URLs, promotional content, and suspicious phrases
- Confidence scores and badges
- Metrics dashboard
- Export cleaned datasets

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## File Structure

```
review-cleaner/
├── app.py                  # Main Streamlit application
├── models/
│   ├── __init__.py
│   └── local_infer.py      # Review classification logic
├── utils/
│   ├── __init__.py
│   ├── highlight.py        # Text highlighting utilities
│   └── schema.py           # Data validation schemas
├── assets/
│   └── sample_reviews.csv  # Sample data for testing
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## CSV Format

Your input CSV should contain these columns:
- `review_id`: Unique identifier
- `review_text`: The review content
- `rating`: Star rating (1-5)
- `user`: Username/reviewer
- `timestamp`: Review date/time

## Deployment

This app can be deployed to:
- Streamlit Cloud
- Hugging Face Spaces
- Any platform supporting Streamlit apps