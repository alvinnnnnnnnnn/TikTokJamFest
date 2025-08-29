# TikTok TechJam

## Problem Statement
Design and implement an ML-based system to evaluate the quality and relevancy of Google location reviews. Our system determines if the review is:
1. High Quality: The review is relevant to the location and provides meaningful feedback
2. Low Quality: The review contains only a rating with little to no text, or consists of very short/uninformative comments 
3. Fake: A fabricated review, such as when the reviewer has not actually visited the location
4. Irrelevant: The review discusses topics unrelated to the location
5. Advertisements: The review includes promotional content or external links unrelated to the business

---

## Table of Contents
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