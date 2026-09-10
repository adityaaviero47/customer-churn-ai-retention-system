import sqlite3
import pandas as pd
import os

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression


# ============================================================
# STEP 1: CONNECT TO DATABASE
# ============================================================

# Get the folder containing this Python file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Locate the existing SQLite database
db_path = os.path.join(script_dir, "..", "SQL", "churn_analysis.db")

# Connect to the database
conn = sqlite3.connect(db_path)


# ============================================================
# STEP 2: LOAD CUSTOMER AND USAGE DATA
# ============================================================

query = """
SELECT
    u.user_id,
    u.plan_type,
    u.monthly_spend,
    us.session_count,
    us.last_login_days,
    us.features_used,
    us.payment_failures,
    us.churned
FROM users u
JOIN usage us
    ON u.user_id = us.user_id
"""

df = pd.read_sql_query(query, conn)

# Close database connection
conn.close()


# ============================================================
# STEP 3: FEATURE ENGINEERING
# ============================================================

# Remove user_id because it is only an identifier
df = df.drop(columns=["user_id"])

# Separate features (X) and target (y)
X = df.drop(columns=["churned"])
y = df["churned"]

# Convert categorical plan_type into numerical columns
X = pd.get_dummies(
    X,
    columns=["plan_type"],
    dtype=int
)


# ============================================================
# STEP 4: TRAIN-TEST SPLIT
# ============================================================

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# STEP 5: LOGISTIC REGRESSION
# ============================================================

# Create a pipeline that scales the features
# and then trains Logistic Regression
logistic_model = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(max_iter=1000))
])

# Train the model using training data
logistic_model.fit(X_train, y_train)


# ============================================================
# STEP 6: MAKE PREDICTIONS
# ============================================================

# Predict churn classes for unseen test customers
predictions = logistic_model.predict(X_test)

# Predict probability of churn for each test customer
probabilities = logistic_model.predict_proba(X_test)[:, 1]


# ============================================================
# STEP 7: DISPLAY RESULTS
# ============================================================

print("Dataset shape:", df.shape)

print("\nML features:")
print(X.columns.tolist())

print("\nTotal customers:", len(X))
print("Training customers:", len(X_train))
print("Testing customers:", len(X_test))

print("\nTraining churn distribution:")
print(y_train.value_counts())

print("\nTesting churn distribution:")
print(y_test.value_counts())

print("\nLogistic Regression trained successfully!")

print("\nFirst 10 predicted churn probabilities:")
print(probabilities[:10])

print("\nFirst 10 predicted classes:")
print(predictions[:10])

# ============================================================
# STEP 8: EVALUATE LOGISTIC REGRESSION
# ============================================================

accuracy = accuracy_score(y_test, predictions)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
f1 = f1_score(y_test, predictions)
roc_auc = roc_auc_score(y_test, probabilities)

print("\nLogistic Regression Performance:")
print(f"Accuracy:  {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall:    {recall:.3f}")
print(f"F1 Score:  {f1:.3f}")
print(f"ROC-AUC:   {roc_auc:.3f}")


# Confusion Matrix
cm = confusion_matrix(y_test, predictions)

print("\nConfusion Matrix:")
print(cm)
# ============================================================
# STEP 9: RANDOM FOREST
# ============================================================

# Create Random Forest model
random_forest_model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced"
)

# Train the model
random_forest_model.fit(X_train, y_train)

print("\nRandom Forest trained successfully!")

# Make predictions
rf_predictions = random_forest_model.predict(X_test)

# Predict churn probabilities
rf_probabilities = random_forest_model.predict_proba(X_test)[:, 1]

print("\nFirst 10 Random Forest churn probabilities:")
print(rf_probabilities[:10])
# ============================================================
# STEP 10: EVALUATE RANDOM FOREST
# ============================================================

rf_accuracy = accuracy_score(y_test, rf_predictions)
rf_precision = precision_score(y_test, rf_predictions)
rf_recall = recall_score(y_test, rf_predictions)
rf_f1 = f1_score(y_test, rf_predictions)
rf_roc_auc = roc_auc_score(y_test, rf_probabilities)

print("\nRandom Forest Performance:")
print(f"Accuracy:  {rf_accuracy:.3f}")
print(f"Precision: {rf_precision:.3f}")
print(f"Recall:    {rf_recall:.3f}")
print(f"F1 Score:  {rf_f1:.3f}")
print(f"ROC-AUC:   {rf_roc_auc:.3f}")

# Confusion Matrix
rf_cm = confusion_matrix(y_test, rf_predictions)

print("\nRandom Forest Confusion Matrix:")
print(rf_cm)
# ============================================================
# STEP 11: XGBOOST
# ============================================================

# Create XGBoost model
xgb_model = XGBClassifier(
    n_estimators=300,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric="logloss"
)

# Train the model
xgb_model.fit(X_train, y_train)

print("\nXGBoost trained successfully!")

# Make predictions
xgb_predictions = xgb_model.predict(X_test)

# Predict churn probabilities
xgb_probabilities = xgb_model.predict_proba(X_test)[:, 1]

print("\nFirst 10 XGBoost churn probabilities:")
print(xgb_probabilities[:10])

# ============================================================
# STEP 12: EVALUATE XGBOOST
# ============================================================

xgb_accuracy = accuracy_score(y_test, xgb_predictions)
xgb_precision = precision_score(y_test, xgb_predictions)
xgb_recall = recall_score(y_test, xgb_predictions)
xgb_f1 = f1_score(y_test, xgb_predictions)
xgb_roc_auc = roc_auc_score(y_test, xgb_probabilities)

print("\nXGBoost Performance:")
print(f"Accuracy:  {xgb_accuracy:.3f}")
print(f"Precision: {xgb_precision:.3f}")
print(f"Recall:    {xgb_recall:.3f}")
print(f"F1 Score:  {xgb_f1:.3f}")
print(f"ROC-AUC:   {xgb_roc_auc:.3f}")

# Confusion Matrix
xgb_cm = confusion_matrix(y_test, xgb_predictions)

print("\nXGBoost Confusion Matrix:")
print(xgb_cm)
# ============================================================
# STEP 13: XGBOOST THRESHOLD OPTIMIZATION
# ============================================================

thresholds = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

print("\nXGBoost Threshold Analysis:")
print("-" * 75)
print(
    f"{'Threshold':<12}"
    f"{'Precision':<12}"
    f"{'Recall':<12}"
    f"{'F1':<12}"
    f"{'Flagged':<12}"
    f"{'Churners Caught':<18}"
)

for threshold in thresholds:

    # Convert probabilities into predictions using the selected threshold
    threshold_predictions = (
        xgb_probabilities >= threshold
    ).astype(int)

    threshold_precision = precision_score(
        y_test,
        threshold_predictions,
        zero_division=0
    )

    threshold_recall = recall_score(
        y_test,
        threshold_predictions,
        zero_division=0
    )

    threshold_f1 = f1_score(
        y_test,
        threshold_predictions,
        zero_division=0
    )

    customers_flagged = threshold_predictions.sum()

    churners_caught = (
        (threshold_predictions == 1) &
        (y_test == 1)
    ).sum()

    print(
        f"{threshold:<12.0%}"
        f"{threshold_precision:<12.3f}"
        f"{threshold_recall:<12.3f}"
        f"{threshold_f1:<12.3f}"
        f"{customers_flagged:<12}"
        f"{churners_caught:<18}"
    )

# ============================================================
# STEP 14: XGBOOST FEATURE IMPORTANCE
# ============================================================

feature_importance = pd.DataFrame({
    "feature": X_train.columns,
    "importance": xgb_model.feature_importances_
})

feature_importance = feature_importance.sort_values(
    by="importance",
    ascending=False
)

print("\nXGBoost Feature Importance:")
print("-" * 45)

for _, row in feature_importance.iterrows():
    print(
        f"{row['feature']:<25} "
        f"{row['importance']:.4f}"
    )

# ============================================================
# STEP 15: FINAL MODEL COMPARISON
# ============================================================

model_comparison = pd.DataFrame({
    "Model": [
        "Logistic Regression",
        "Random Forest",
        "XGBoost"
    ],
    "Accuracy": [
        0.819,
        0.759,
        0.831
    ],
    "Precision": [
        0.534,
        0.379,
        0.620
    ],
    "Recall": [
        0.210,
        0.462,
        0.237
    ],
    "F1 Score": [
        0.301,
        0.416,
        0.342
    ],
    "ROC-AUC": [
        0.778,
        0.743,
        0.775
    ]
})

print("\nFinal Model Comparison:")
print("-" * 80)
print(model_comparison.to_string(index=False))
# ============================================================
# STEP 16: CUSTOMER-LEVEL CHURN RISK TABLE
# ============================================================

# Open a fresh database connection
risk_conn = sqlite3.connect(db_path)

# Load customer information
customer_info = pd.read_sql_query(
    """
    SELECT user_id, plan_type
    FROM users
    """,
    risk_conn
)

# Close the temporary connection
risk_conn.close()

# Create risk dataset from the test features
risk_dataset = X_test.copy()

# Add actual churn outcome
risk_dataset["actual_churn"] = y_test.values

# Add XGBoost churn probability
risk_dataset["churn_probability"] = xgb_probabilities

# Add customer ID
risk_dataset["user_id"] = customer_info.loc[
    X_test.index, "user_id"
].values

# Add plan type
risk_dataset["plan_type"] = customer_info.loc[
    X_test.index, "plan_type"
].values

# Select useful columns
risk_dataset = risk_dataset[
    [
        "user_id",
        "churn_probability",
        "session_count",
        "last_login_days",
        "monthly_spend",
        "features_used",
        "payment_failures",
        "plan_type",
        "actual_churn"
    ]
]

# Sort from highest to lowest predicted churn probability
risk_dataset = risk_dataset.sort_values(
    by="churn_probability",
    ascending=False
)

print("\nTop 20 Customers by Predicted Churn Risk:")
print("-" * 100)

print(
    risk_dataset.head(20).to_string(index=False)
)
# ============================================================
# STEP 17: RISK SEGMENTATION
# ============================================================

def classify_risk(probability):

    if probability >= 0.70:
        return "Critical"

    elif probability >= 0.40:
        return "High"

    elif probability >= 0.20:
        return "Moderate"

    else:
        return "Healthy"


# Apply risk classification
risk_dataset["risk_segment"] = risk_dataset[
    "churn_probability"
].apply(classify_risk)


# Display risk segment distribution
print("\nRisk Segment Distribution:")
print("-" * 60)

segment_summary = (
    risk_dataset
    .groupby("risk_segment")
    .agg(
        customers=("user_id", "count"),
        avg_churn_probability=("churn_probability", "mean"),
        actual_churns=("actual_churn", "sum")
    )
    .sort_values(
        by="avg_churn_probability",
        ascending=False
    )
)

print(segment_summary)


# Display top customers with risk segments
print("\nTop 20 Customers with Risk Segments:")
print("-" * 120)

print(
    risk_dataset[
        [
            "user_id",
            "churn_probability",
            "risk_segment",
            "session_count",
            "last_login_days",
            "monthly_spend",
            "plan_type",
            "actual_churn"
        ]
    ]
    .head(20)
    .to_string(index=False)
)
# ============================================================
# STEP 18: RETENTION INTERVENTION ENGINE
# ============================================================

def recommend_intervention(row):

    risk = row["risk_segment"]
    sessions = row["session_count"]
    last_login = row["last_login_days"]
    plan = row["plan_type"]

    # Critical-risk customers
    if risk == "Critical":

        if plan == "Premium":
            return "Priority personal re-engagement"

        elif plan == "Basic":
            return "Personalized re-engagement campaign"

        else:
            return "Re-engagement campaign"

    # High-risk customers
    elif risk == "High":

        if sessions <= 5:
            return "Early engagement campaign"

        else:
            return "Product engagement campaign"

    # Moderate-risk customers
    elif risk == "Moderate":

        if last_login >= 14:
            return "Feature discovery campaign"

        else:
            return "Product education campaign"

    # Healthy customers
    else:

        if plan == "Premium":
            return "Loyalty / upsell opportunity"

        else:
            return "Monitor engagement"


# Apply intervention recommendation
risk_dataset["recommended_action"] = risk_dataset.apply(
    recommend_intervention,
    axis=1
)


# Assign intervention priority
def assign_priority(risk):

    if risk == "Critical":
        return "P1 - Immediate"

    elif risk == "High":
        return "P2 - High"

    elif risk == "Moderate":
        return "P3 - Medium"

    else:
        return "P4 - Monitor"


risk_dataset["priority"] = risk_dataset[
    "risk_segment"
].apply(assign_priority)


# Display intervention recommendations
print("\nTop 20 Customers with Recommended Interventions:")
print("-" * 150)

print(
    risk_dataset[
        [
            "user_id",
            "churn_probability",
            "risk_segment",
            "session_count",
            "last_login_days",
            "monthly_spend",
            "plan_type",
            "recommended_action",
            "priority"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# Intervention summary
print("\nIntervention Summary:")
print("-" * 80)

intervention_summary = (
    risk_dataset
    .groupby(
        ["risk_segment", "recommended_action"]
    )
    .agg(
        customers=("user_id", "count"),
        avg_churn_probability=("churn_probability", "mean")
    )
    .reset_index()
)

print(intervention_summary.to_string(index=False))
# ============================================================
# STEP 19: INTERVENTION TRACKING
# ============================================================

import numpy as np


# Create intervention tracking dataset
intervention_data = risk_dataset[
    [
        "user_id",
        "risk_segment",
        "churn_probability",
        "recommended_action",
        "priority",
        "monthly_spend",
        "plan_type",
        "session_count",
        "last_login_days",
        "actual_churn"
    ]
].copy()


# Only customers above the intervention threshold
intervention_data = intervention_data[
    intervention_data["churn_probability"] >= 0.20
].copy()


# Create simulated intervention status
intervention_data["intervention_status"] = "Simulated - Pending"


# Create a simulated intervention date
intervention_data["intervention_date"] = "2026-09-07"


# Create response status
intervention_data["response_status"] = "Not Yet Measured"


# Create outcome field
intervention_data["retained_after_intervention"] = np.nan


# Display intervention tracking table
print("\nIntervention Tracking Table:")
print("-" * 150)

print(
    intervention_data[
        [
            "user_id",
            "risk_segment",
            "churn_probability",
            "recommended_action",
            "priority",
            "intervention_status",
            "intervention_date",
            "response_status"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# Intervention workload summary
print("\nIntervention Workload:")
print("-" * 80)

workload_summary = (
    intervention_data
    .groupby(["risk_segment", "priority"])
    .agg(
        customers=("user_id", "count"),
        avg_churn_probability=("churn_probability", "mean")
    )
    .reset_index()
)

print(
    workload_summary.to_string(index=False)
)

print(
    f"\nTotal customers eligible for intervention: "
    f"{len(intervention_data)}"
)
# ============================================================
# STEP 20: A/B TESTING FRAMEWORK
# ============================================================

# Create a copy of intervention-eligible customers
ab_test = intervention_data.copy()


# Set a reproducible random seed
np.random.seed(42)


# Randomly assign customers to Control or Treatment
ab_test["experiment_group"] = np.random.choice(
    ["Control", "Treatment"],
    size=len(ab_test),
    p=[0.5, 0.5]
)


# Control group receives no intervention
ab_test.loc[
    ab_test["experiment_group"] == "Control",
    "intervention_status"
] = "Control - No Intervention"


# Treatment group receives recommended intervention
ab_test.loc[
    ab_test["experiment_group"] == "Treatment",
    "intervention_status"
] = "Treatment - Intervention Sent"


# For this historical dataset:
# actual_churn = 0 means retained
# actual_churn = 1 means churned

ab_test["retained"] = (
    ab_test["actual_churn"] == 0
).astype(int)


# Calculate experiment summary
experiment_summary = (
    ab_test
    .groupby("experiment_group")
    .agg(
        customers=("user_id", "count"),
        churned=("actual_churn", "sum"),
        retained=("retained", "sum")
    )
)


# Calculate churn rate
experiment_summary["churn_rate"] = (
    experiment_summary["churned"]
    / experiment_summary["customers"]
)


# Calculate retention rate
experiment_summary["retention_rate"] = (
    experiment_summary["retained"]
    / experiment_summary["customers"]
)


# Display experiment results
print("\nA/B Test Framework:")
print("-" * 80)

print(
    experiment_summary
)


# Calculate observed difference
control_retention = experiment_summary.loc[
    "Control",
    "retention_rate"
]

treatment_retention = experiment_summary.loc[
    "Treatment",
    "retention_rate"
]


retention_difference = (
    treatment_retention
    - control_retention
)


print(
    f"\nObserved retention difference: "
    f"{retention_difference:.2%}"
)


print(
    "\nIMPORTANT:"
)

print(
    "This is a simulated experiment framework using "
    "historical outcomes."
)

print(
    "The observed difference must NOT be interpreted "
    "as causal intervention impact."
)
# ============================================================
# STEP 21: A/B TEST STATISTICAL SIGNIFICANCE
# ============================================================

from statsmodels.stats.proportion import proportions_ztest


# Number of retained customers
retained_counts = np.array([
    experiment_summary.loc["Control", "retained"],
    experiment_summary.loc["Treatment", "retained"]
])


# Total customers in each group
group_sizes = np.array([
    experiment_summary.loc["Control", "customers"],
    experiment_summary.loc["Treatment", "customers"]
])


# Two-proportion z-test
z_stat, p_value = proportions_ztest(
    retained_counts,
    group_sizes
)


print("\nA/B Test Statistical Significance:")
print("-" * 80)

print(f"Control retention:    {control_retention:.2%}")
print(f"Treatment retention:  {treatment_retention:.2%}")
print(f"Observed difference:  {retention_difference:.2%}")
print(f"Z-statistic:          {z_stat:.4f}")
print(f"P-value:              {p_value:.6f}")


# Statistical decision
alpha = 0.05

if p_value < alpha:

    print(
        "\nResult: Statistically significant difference "
        "between the groups."
    )

else:

    print(
        "\nResult: No statistically significant difference "
        "between the groups."
    )


print(
    "\nIMPORTANT: This test evaluates the historical "
    "simulation and does not establish causal intervention impact."
)
# ============================================================
# STEP 21: A/B TEST STATISTICAL SIGNIFICANCE
# ============================================================

from statsmodels.stats.proportion import proportions_ztest


# Number of retained customers
retained_counts = np.array([
    experiment_summary.loc["Control", "retained"],
    experiment_summary.loc["Treatment", "retained"]
])


# Total customers in each group
group_sizes = np.array([
    experiment_summary.loc["Control", "customers"],
    experiment_summary.loc["Treatment", "customers"]
])


# Two-proportion z-test
z_stat, p_value = proportions_ztest(
    retained_counts,
    group_sizes
)


print("\nA/B Test Statistical Significance:")
print("-" * 80)

print(f"Control retention:    {control_retention:.2%}")
print(f"Treatment retention:  {treatment_retention:.2%}")
print(f"Observed difference:  {retention_difference:.2%}")
print(f"Z-statistic:          {z_stat:.4f}")
print(f"P-value:              {p_value:.6f}")


# Statistical decision
alpha = 0.05

if p_value < alpha:

    print(
        "\nResult: Statistically significant difference "
        "between the groups."
    )

else:

    print(
        "\nResult: No statistically significant difference "
        "between the groups."
    )


print(
    "\nIMPORTANT: This test evaluates the historical "
    "simulation and does not establish causal intervention impact."
)
# ============================================================
# STEP 22: RETENTION KPI & BUSINESS IMPACT
# ============================================================

# ------------------------------------------------------------
# KPI 1: At-risk customers
# ------------------------------------------------------------

at_risk_customers = len(intervention_data)


# ------------------------------------------------------------
# KPI 2: Risk segment counts
# ------------------------------------------------------------

risk_counts = (
    intervention_data
    .groupby("risk_segment")
    .size()
)


critical_customers = risk_counts.get("Critical", 0)
high_customers = risk_counts.get("High", 0)
moderate_customers = risk_counts.get("Moderate", 0)


# ------------------------------------------------------------
# KPI 3: Intervention coverage
# ------------------------------------------------------------

intervention_coverage = (
    len(intervention_data)
    / len(risk_dataset)
)


# ------------------------------------------------------------
# KPI 4: Revenue associated with at-risk customers
# ------------------------------------------------------------

at_risk_revenue = intervention_data[
    "monthly_spend"
].sum()


# ------------------------------------------------------------
# KPI 5: Revenue associated with churned at-risk users
# ------------------------------------------------------------

churned_at_risk_revenue = intervention_data.loc[
    intervention_data["actual_churn"] == 1,
    "monthly_spend"
].sum()


# ------------------------------------------------------------
# KPI 6: Hypothetical revenue recovery scenarios
# ------------------------------------------------------------

recovery_10 = churned_at_risk_revenue * 0.10
recovery_20 = churned_at_risk_revenue * 0.20
recovery_30 = churned_at_risk_revenue * 0.30


# ------------------------------------------------------------
# Display KPI dashboard
# ------------------------------------------------------------

print("\nRETENTION KPI & BUSINESS IMPACT:")
print("=" * 80)

print(
    f"At-risk customers:              {at_risk_customers}"
)

print(
    f"Critical customers:             {critical_customers}"
)

print(
    f"High-risk customers:            {high_customers}"
)

print(
    f"Moderate-risk customers:        {moderate_customers}"
)

print(
    f"Intervention coverage:          {intervention_coverage:.2%}"
)

print(
    f"Monthly revenue of at-risk users: "
    f"₹{at_risk_revenue:,.0f}"
)

print(
    f"Monthly revenue associated with "
    f"churned at-risk users: ₹{churned_at_risk_revenue:,.0f}"
)

print("\nHypothetical Revenue Recovery Scenarios:")
print("-" * 80)

print(
    f"10% recovery: ₹{recovery_10:,.0f} / month"
)

print(
    f"20% recovery: ₹{recovery_20:,.0f} / month"
)

print(
    f"30% recovery: ₹{recovery_30:,.0f} / month"
)

print(
    "\nNOTE: Revenue recovery figures are hypothetical "
    "scenarios, not observed business impact."
)
# ============================================================
# STEP 23: EXPORT RETENTION SYSTEM OUTPUTS
# ============================================================

import os


# Create Outputs folder
output_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "Outputs"
)

os.makedirs(output_dir, exist_ok=True)


# ------------------------------------------------------------
# 1. Customer risk scores
# ------------------------------------------------------------

risk_output = risk_dataset[
    [
        "user_id",
        "churn_probability",
        "risk_segment",
        "session_count",
        "last_login_days",
        "monthly_spend",
        "features_used",
        "payment_failures",
        "plan_type",
        "actual_churn",
        "recommended_action",
        "priority"
    ]
].copy()


risk_output.to_csv(
    os.path.join(
        output_dir,
        "customer_risk_scores.csv"
    ),
    index=False
)


# ------------------------------------------------------------
# 2. Intervention queue
# ------------------------------------------------------------

intervention_output = intervention_data.copy()


intervention_output.to_csv(
    os.path.join(
        output_dir,
        "intervention_queue.csv"
    ),
    index=False
)


# ------------------------------------------------------------
# 3. A/B test results
# ------------------------------------------------------------

ab_output = experiment_summary.reset_index()


ab_output.to_csv(
    os.path.join(
        output_dir,
        "ab_test_results.csv"
    ),
    index=False
)


# ------------------------------------------------------------
# 4. Retention KPIs
# ------------------------------------------------------------

kpi_output = pd.DataFrame({
    "KPI": [
        "At-risk customers",
        "Critical customers",
        "High-risk customers",
        "Moderate-risk customers",
        "Intervention coverage",
        "Monthly revenue of at-risk users",
        "Monthly revenue associated with churned at-risk users",
        "Hypothetical 10% revenue recovery",
        "Hypothetical 20% revenue recovery",
        "Hypothetical 30% revenue recovery"
    ],

    "Value": [
        at_risk_customers,
        critical_customers,
        high_customers,
        moderate_customers,
        intervention_coverage,
        at_risk_revenue,
        churned_at_risk_revenue,
        recovery_10,
        recovery_20,
        recovery_30
    ]
})


kpi_output.to_csv(
    os.path.join(
        output_dir,
        "retention_kpis.csv"
    ),
    index=False
)


# ------------------------------------------------------------
# Confirmation
# ------------------------------------------------------------

print("\nOUTPUT FILES CREATED:")
print("-" * 80)

print(
    f"Customer risk scores: "
    f"{os.path.join(output_dir, 'customer_risk_scores.csv')}"
)

print(
    f"Intervention queue: "
    f"{os.path.join(output_dir, 'intervention_queue.csv')}"
)

print(
    f"A/B test results: "
    f"{os.path.join(output_dir, 'ab_test_results.csv')}"
)

print(
    f"Retention KPIs: "
    f"{os.path.join(output_dir, 'retention_kpis.csv')}"
)