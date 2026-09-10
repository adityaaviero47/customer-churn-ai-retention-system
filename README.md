# Customer Churn Analytics & AI-Driven Retention System

An end-to-end customer churn analytics and AI-powered retention decision system that identifies at-risk customers, diagnoses churn drivers, prioritizes interventions, and evaluates retention strategies.

## Project Overview

The system follows a product-oriented workflow:

**Detect → Diagnose → Intervene → Measure**

It combines SQL analytics, statistical hypothesis testing, machine learning, customer risk segmentation, and a Streamlit-based retention command center.

## Key Capabilities

- Customer churn analysis using SQL and Python
- Statistical validation of churn drivers
- Machine learning-based churn prediction
- Customer risk scoring and segmentation
- Automated intervention recommendations
- Retention experiment simulation
- Business impact and revenue-at-risk analysis
- Interactive Streamlit prototype

## Dataset

The project uses a synthetic dataset of **5,000 customers** containing customer plans, usage behavior, support interactions, payment information, and churn outcomes.

### Key Findings

- **5,000+ customers** analyzed
- **929 customers** churned
- Overall churn rate: **18.6%**
- Customers with low engagement and prolonged inactivity showed substantially higher churn
- High-risk behavioral users showed approximately **3.5× higher churn**
- More than **₹54K monthly revenue** was associated with churned users within the high-risk behavioral segment

## Machine Learning

Three classification models were evaluated:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 81.9% | 53.4% | 21.0% | 30.1% | 77.8% |
| Random Forest | 75.9% | 37.9% | 46.2% | 41.6% | 74.3% |
| XGBoost | 83.1% | 62.0% | 23.7% | 34.2% | 77.5% |

XGBoost was selected for the operational risk-scoring workflow.

A **20% intervention threshold** was evaluated for retention use cases, capturing **66.7% of historical churners** in the held-out test set.

## Retention Command Center

The Streamlit prototype provides:

1. **Executive Overview** – churn and risk KPIs
2. **Risk Queue** – prioritized customers requiring intervention
3. **Customer Profile** – customer-level risk and recommended action
4. **What-If Simulator** – evaluate different intervention thresholds
5. **Experiments** – retention experiment analysis
6. **Intervention Log** – track launched interventions

## Architecture

```text
Synthetic Customer Data
        ↓
      SQLite
        ↓
 SQL + Statistical Analysis
        ↓
   Machine Learning
     (XGBoost)
        ↓
   Risk Scoring
        ↓
 Risk Segmentation
        ↓
Intervention Engine
        ↓
Retention Command Center
     (Streamlit)
        ↓
   Experimentation
        ↓
 Business Impact
