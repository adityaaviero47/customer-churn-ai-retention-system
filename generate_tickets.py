import pandas as pd
import random
from pathlib import Path
from datetime import datetime, timedelta
project_folder = Path(__file__).parent
NUM_TICKETS = 2000
users_df = pd.read_csv(project_folder.parent / "data" / "users.csv")
user_ids = users_df["user_id"].tolist()
ticket_ids = list(range(1, NUM_TICKETS + 1))
ticket_user_ids = random.choices(user_ids, k=NUM_TICKETS)
start_date = datetime(2026, 5, 1)
end_date = datetime(2026, 7, 31)

ticket_dates = [
    start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days)
    )
    for _ in range(NUM_TICKETS)
]

issue_types = [
    "Payment",
    "Login / Account",
    "Technical / Bug",
    "Feature Issue",
    "Performance",
    "Subscription",
    "Refund",
    "Feature Request",
    "General Query"
]

ticket_issue_types = random.choices(
    issue_types,
    weights=[18, 16, 15, 12, 10, 10, 7, 7, 5],
    k=NUM_TICKETS
)

description_templates = {
    "Payment": [
        "My payment failed when I tried to renew my subscription.",
        "I was unable to complete my payment.",
        "My card was charged but my subscription was not activated.",
        "The payment keeps failing even though my account has sufficient funds."
    ],
    
    "Login / Account": [
        "I am unable to log into my account.",
        "I cannot reset my password.",
        "I am having trouble accessing my account.",
        "My account login is not working."
    ],
    
    "Technical / Bug": [
        "The app keeps crashing when I use it.",
        "I found a bug that is preventing me from using the app.",
        "The application stopped working suddenly.",
        "The app is showing an error whenever I try to continue."
    ],
    
    "Feature Issue": [
        "The feature is not working as expected.",
        "I am unable to use this feature properly.",
        "This feature stopped working after the latest update.",
        "The feature is giving me an unexpected error."
    ],
    
    "Performance": [
        "The app is extremely slow.",
        "Pages are taking too long to load.",
        "The application has become very slow recently.",
        "The dashboard takes a long time to open."
    ],
    
    "Subscription": [
        "I want to change my subscription plan.",
        "I am having an issue with my subscription.",
        "My subscription details are not updating.",
        "I need help managing my subscription."
    ],
    
    "Refund": [
        "I would like to request a refund.",
        "I have not received my refund yet.",
        "I was charged incorrectly and want a refund.",
        "Can you help me with my refund request?"
    ],
    
    "Feature Request": [
        "I would like to suggest a new feature.",
        "It would be useful to have this feature in the app.",
        "Can you add an option to export my data?",
        "I have a suggestion that could improve the product."
    ],
    
    "General Query": [
        "I have a question about the product.",
        "I need some information about how the app works.",
        "Can you help me understand this feature?",
        "I need assistance with using the product."
    ]
}

ticket_descriptions = [
    random.choice(description_templates[issue_type])
    for issue_type in ticket_issue_types
]

response_times = [
    random.randint(5, 240)
    for _ in range(NUM_TICKETS)
]

resolution_ranges = {
    "Payment": (30, 360),
    "Login / Account": (15, 180),
    "Technical / Bug": (60, 720),
    "Feature Issue": (30, 360),
    "Performance": (45, 480),
    "Subscription": (20, 240),
    "Refund": (60, 720),
    "Feature Request": (60, 480),
    "General Query": (10, 120)
}

resolution_times = [
    random.randint(
        resolution_ranges[issue_type][0],
        resolution_ranges[issue_type][1]
    )
    for issue_type in ticket_issue_types
]

resolution_statuses = [
    random.choices(
        ["Resolved", "Pending"],
        weights=[90, 10],
        k=1
    )[0]
    for _ in range(NUM_TICKETS)
]

tickets_df = pd.DataFrame({
    "ticket_id": ticket_ids,
    "user_id": ticket_user_ids,
    "ticket_date": ticket_dates,
    "issue_type": ticket_issue_types,
    "description": ticket_descriptions,
    "response_time": response_times,
    "resolution_time": resolution_times,
    "resolution_status": resolution_statuses
})

print(tickets_df.head())
print(tickets_df.shape)
print(tickets_df["issue_type"].value_counts())
print(tickets_df["resolution_status"].value_counts())
tickets_df.to_csv(project_folder.parent / "data" / "tickets.csv", index=False)