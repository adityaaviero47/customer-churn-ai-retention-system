import sqlite3
from scipy.stats import mannwhitneyu

# Connect to our database
db_path = r"C:\Users\Aditya\Desktop\Project\SQL\churn_analysis.db"
conn = sqlite3.connect(db_path)

# Get login recency for retained users
retained = conn.execute("""
    SELECT last_login_days
    FROM usage
    WHERE churned = 0
""").fetchall()

# Get login recency for churned users
churned = conn.execute("""
    SELECT last_login_days
    FROM usage
    WHERE churned = 1
""").fetchall()

conn.close()

# Convert database results into lists
retained_recency = [row[0] for row in retained]
churned_recency = [row[0] for row in churned]

# Mann-Whitney U test
statistic, p_value = mannwhitneyu(
    retained_recency,
    churned_recency,
    alternative="two-sided"
)

print("Last-Login Recency Statistical Test")
print("------------------------------------")
print("Retained users:", len(retained_recency))
print("Churned users:", len(churned_recency))

print("Average days since login - retained:",
      round(sum(retained_recency) / len(retained_recency), 2))

print("Average days since login - churned:",
      round(sum(churned_recency) / len(churned_recency), 2))

print("Mann-Whitney U statistic:", round(statistic, 2))
print("p-value:", p_value)

if p_value < 0.05:
    print("\nResult: Last-login recency has a statistically significant relationship with churn.")
else:
    print("\nResult: No statistically significant relationship found.")