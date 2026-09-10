import numpy as np
from scipy.stats import chi2_contingency

# Contingency table:
#             Retained  Churned
# High Risk       256       274
# Other Users    3815       655

table = np.array([
    [256, 274],
    [3815, 655]
])

chi2, p_value, degrees_of_freedom, expected = chi2_contingency(table)

print("Chi-Square Test Results")
print("-----------------------")
print("Chi-square statistic:", round(chi2, 2))
print("p-value:", p_value)
print("Degrees of freedom:", degrees_of_freedom)

print("\nExpected frequencies:")
print(expected)

if p_value < 0.05:
    print("\nResult: Statistically significant relationship.")
else:
    print("\nResult: No statistically significant relationship.")