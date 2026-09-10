import sqlite3
from scipy.stats import mannwhitneyu

# Connect to our database
db_path = r"C:\Users\Aditya\Desktop\Project\SQL\churn_analysis.db"
conn = sqlite3.connect(db_path)

# Get session counts for retained users
retained = conn.execute("""
    SELECT session_count
    FROM usage
    WHERE churned = 0
""").fetchall()

# Get session counts for churned users
churned = conn.execute("""
    SELECT session_count
    FROM usage
    WHERE churned = 1
""").fetchall()

conn.close()

# Convert database results into simple lists
retained_sessions = [row[0] for row in retained]
churned_sessions = [row[0] for row in churned]

# Mann-Whitney U test
statistic, p_value = mannwhitneyu(
    retained_sessions,
    churned_sessions,
    alternative="two-sided"
)

print("Session Count Statistical Test")
print("--------------------------------")
print("Retained users:", len(retained_sessions))
print("Churned users:", len(churned_sessions))
print("Average sessions - retained:",
      round(sum(retained_sessions) / len(retained_sessions), 2))
print("Average sessions - churned:",
      round(sum(churned_sessions) / len(churned_sessions), 2))
print("Mann-Whitney U statistic:", round(statistic, 2))
print("p-value:", p_value)

if p_value < 0.05:
    print("\nResult: Session count has a statistically significant relationship with churn.")
else:
    print("\nResult: No statistically significant relationship found.")