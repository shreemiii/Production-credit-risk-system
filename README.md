# Production Credit Risk System

## Project Overview
This project builds an end-to-end machine learning system to predict loan default risk using the Home Credit Default Risk dataset from Kaggle.

The system will include data processing, model training, evaluation, deployment, monitoring, and retraining.

## Dataset
Source: [Home Credit Default Risk - Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk/data)

We use a fixed sample of 5,000 applicants from the training dataset.

The dataset includes seven main tables containing applicant information, credit history, previous loans, and payment records.

## Week 1: Data Preparation and Baseline Model
- Downloaded and extracted the dataset.
- Created a reproducible 5,000-applicant sample.
- Generated a summary of all seven tables.
- Trained a logistic regression baseline model.
- Evaluated the model using ROC-AUC and accuracy.

## Baseline Results
- ROC-AUC: 0.6745
- Accuracy: 91.4%
- Sample default rate: 8.24%

## Project Files
- `prepare_data.py` - Creates the 5,000-applicant sample.
- `table_summary.py` - Generates the dataset table summary.
- `baseline.py` - Trains and evaluates the logistic regression model.
- `reports/table_summary.csv` - Summary of the seven dataset tables.
- `sample/application_train.csv` - Sampled applicant data (stored locally unless sharing is permitted).

## How to Run
Install dependencies:

```bash
python3 -m pip install pandas scikit-learn
```

Download and extract the Kaggle dataset into the project directory, then run:

```bash
python3 prepare_data.py
python3 table_summary.py
python3 baseline.py
```

## Technologies
Python, Pandas, Scikit-learn, GitHub

Future stages will introduce MLflow, FastAPI, Google Cloud Run, and automated monitoring.
