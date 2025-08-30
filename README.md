# JimJamSlam

## Problem Statement
Design and implement an ML-based system to evaluate the quality and relevancy of Google location reviews. Our system aims to improve the trust in reviews, and ensures that it is a fair representation of the location. 

---

## Table of Contents
- [Quick Start](#quick-start)
- [Datasets Used](#datasets-used)
- [Implementation](#implementation)
- [Model Metrics](#model-metrics)
- [Reflections & Considerations](#reflections--considerations)
- [Member Contributions](#member-contributions)

---

## Quick Start
1. Install Git
2. Clone the repository
```bash
git clone
```
3. Activate python environment
4. Install necessary libraries 
```bash
pip install --upgrade -r requirements.txt
```
5. Install [pytorch](https://pytorch.org/) based on your OS

## Datasets used
This project makes use of datasets obtained via Apify
- [Google Maps Reviews Scraper](https://console.apify.com/actors/Xb8osYTtOjlsgI6k9/input): used to collect user reviews from Google Maps
- [Google Maps Scraper](https://console.apify.com/actors/nwua9Gu5YrADL7ZDj/input): used to gather business details along with their associated reviews

## Implementation
### 1. Feature Engineering
From the raw dataset, additional features were engineered to capture more meaningful signals for classification. The two main features are:

1. **Length of review**
    - Length of each review, in terms of word count.
2. **Relevance between category keyword and review**
    - Each business category was mapped to a set of representative keywords. A cross-encoder model was used to compare the review text with these keywords. The model outputs a score between 0 and 1, where 0 means no similarity and 1 means strong relevance.

### 2. Labelling of data
To establish the ground truth, we first collected a total of **3,800 Google Maps reviews**. These reviews were then passed through ChatGPT-5 to generate initial labels. Each review was categorized into one of the following classes:
1. **High Quality** 
    - Relevant to the location and provides meaningful feedback.
2. **Low Quality**
    - Contains only a rating with little to no text, or very short/uninformative comments.
3. **Fake**
    - Fabricated reviews, such as when the reviewer has not actually visited the location.
4. **Irrelevant**
    - Discusses topics unrelated to the location.
5. **Advertisements**
    - Includes promotional content or external links unrelated to the business.

After the automated labeling, we manually reviewed and validated the dataset to ensure accuracy. This semi-automated approach significantly reduced labeling time while maintaining high-quality training data.

### 3. Model Training

## Model Metrics
To evaluate the model's performance based on our use case, the following weighted metrics system was used:

|Metrics             |Score |
|--------------------|:----:|
|F1-Score            | |
|Precision           | |
|Recall              | |


## Reflections & Considerations
The dataset could be improved with additional information, particularly user metadata (e.g., reviewer history, profile details). Such data would provide stronger signals for identifying the real quality of a review.

There is also a noticeable class imbalance in the dataset, with the majority of reviews categorized as High Quality. This imbalance may have caused a bias model performance.

## Member Contributions
You may find the contributions of each member [here]()