import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

NUM_USERS = 5000
user_ids = list(range(1, NUM_USERS + 1))
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 8, 1)

signup_dates = [
    start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days)
    )
    for _ in range(NUM_USERS)
]

plan_types = random.choices(
    ["Free", "Basic", "Premium"],
    weights=[50, 30, 20],
    k=NUM_USERS
)

monthly_spend = []

for plan in plan_types:
    if plan == "Free":
        monthly_spend.append(0)
    elif plan == "Basic":
        monthly_spend.append(299)
    else:
        monthly_spend.append(499)

users_df = pd.DataFrame({
    "user_id": user_ids,
    "signup_date": signup_dates,
    "plan_type": plan_types,
    "monthly_spend": monthly_spend
})

print(users_df.head())
print(users_df.shape)
project_folder = Path(__file__).resolve().parent.parent
users_df.to_csv(project_folder / "data" / "users.csv", index=False)

session_counts = []

for _ in range(NUM_USERS):
    sessions = random.randint(1, 40)
    session_counts.append(sessions)

last_login_days = []

for sessions in session_counts:
    if sessions <= 5:
        days = random.randint(10, 30)
    elif sessions <= 20:
        days = random.randint(3, 15)
    else:
        days = random.randint(0, 7)

    last_login_days.append(days)

churned = []

for sessions, days in zip(session_counts, last_login_days):
    churn_probability = 0.05

    if sessions <= 5:
        churn_probability += 0.25
    elif sessions <= 20:
        churn_probability += 0.10

    if days >= 20:
        churn_probability += 0.30
    elif days >= 10:
        churn_probability += 0.15

    churn_probability = min(churn_probability, 0.90)

    churn = 1 if random.random() < churn_probability else 0
    churned.append(churn)

features_used = []
for _ in range(NUM_USERS):
    features = random.choices(
        range(1, 9),
        weights=[20, 20, 15, 15, 10, 8, 7, 5],
        k=1
    )[0]

    features_used.append(features)

print(pd.Series(features_used).value_counts().sort_index())

payment_failures = []
payment_failures = random.choices(
    [0, 1, 2, 3, 4],
    weights=[75, 17, 5, 2, 1],
    k=NUM_USERS
)
print(pd.Series(payment_failures).value_counts().sort_index())

usage_df = pd.DataFrame({
    "user_id": user_ids,
    "session_count": session_counts,
    "last_login_days": last_login_days,
    "features_used": features_used,
    "payment_failures": payment_failures,
    "churned": churned
})

print(usage_df.head())
print(usage_df["churned"].value_counts())

print(usage_df.groupby("churned")["session_count"].mean())
print(usage_df.groupby("churned")["last_login_days"].mean())
usage_df.to_csv(project_folder / "data" / "usage.csv", index=False)
