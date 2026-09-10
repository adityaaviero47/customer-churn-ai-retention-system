-- SQLite
SELECT COUNT(*) AS total_users
FROM users;
SELECT plan_type, COUNT(*) AS user_count
FROM users
GROUP BY plan_type;
SELECT 
    churned,
    COUNT(*) AS user_count
FROM usage
GROUP BY churned;
SELECT 
    COUNT(*) AS total_users,
    SUM(churned) AS churned_users,
    ROUND(SUM(churned) * 100.0 / COUNT(*), 2) AS churn_rate
FROM usage;
SELECT
    u.plan_type,
    COUNT(*) AS total_users,
    SUM(usage.churned) AS churned_users,
    ROUND(
        SUM(usage.churned) * 100.0 / COUNT(*),
        2
    ) AS churn_rate
FROM users u
JOIN usage
    ON u.user_id = usage.user_id
GROUP BY u.plan_type;
SELECT
    churned,
    ROUND(AVG(session_count), 2) AS avg_sessions
FROM usage
GROUP BY churned;
SELECT
    churned,
    ROUND(AVG(last_login_days), 2) AS avg_days_since_login
FROM usage
GROUP BY churned;
SELECT
    churned,
    ROUND(AVG(features_used), 2) AS avg_features_used
FROM usage
GROUP BY churned;
SELECT
    payment_failures,
    COUNT(*) AS total_users,
    SUM(churned) AS churned_users,
    ROUND(
        SUM(churned) * 100.0 / COUNT(*),
        2
    ) AS churn_rate
FROM usage
GROUP BY payment_failures
ORDER BY payment_failures;
SELECT
    user_id,
    COUNT(*) AS ticket_count
FROM tickets
GROUP BY user_id
LIMIT 10;
WITH user_tickets AS (
    SELECT
        u.user_id,
        u.churned,
        COUNT(t.ticket_id) AS ticket_count
    FROM usage u
    LEFT JOIN tickets t
        ON u.user_id = t.user_id
    GROUP BY u.user_id, u.churned
)
SELECT
    CASE
        WHEN ticket_count = 0 THEN '0 tickets'
        WHEN ticket_count = 1 THEN '1 ticket'
        WHEN ticket_count = 2 THEN '2 tickets'
        ELSE '3+ tickets'
    END AS ticket_bucket,
    COUNT(*) AS total_users,
    SUM(churned) AS churned_users,
    ROUND(
        SUM(churned) * 100.0 / COUNT(*),
        2
    ) AS churn_rate
FROM user_tickets
GROUP BY ticket_bucket
ORDER BY
    CASE ticket_bucket
        WHEN '0 tickets' THEN 1
        WHEN '1 ticket' THEN 2
        WHEN '2 tickets' THEN 3
        ELSE 4
    END;
SELECT
    u.churned,
    ROUND(AVG(t.resolution_time), 2) AS avg_resolution_time
FROM usage u
JOIN tickets t
    ON u.user_id = t.user_id
WHERE t.resolution_time IS NOT NULL
GROUP BY u.churned;
SELECT
    u.churned,
    ROUND(AVG(t.response_time), 2) AS avg_response_time
FROM usage u
JOIN tickets t
    ON u.user_id = t.user_id
WHERE t.response_time IS NOT NULL
GROUP BY u.churned;
SELECT
    t.issue_type,
    COUNT(DISTINCT t.user_id) AS users,
    COUNT(DISTINCT CASE WHEN u.churned = 1 THEN t.user_id END) AS churned_users,
    ROUND(
        COUNT(DISTINCT CASE WHEN u.churned = 1 THEN t.user_id END) * 100.0
        / COUNT(DISTINCT t.user_id),
        2
    ) AS churn_rate
FROM tickets t
JOIN usage u
    ON t.user_id = u.user_id
GROUP BY t.issue_type
ORDER BY churn_rate DESC;
SELECT
    u.churned,
    COUNT(*) AS users,
    ROUND(SUM(users.monthly_spend), 2) AS monthly_revenue
FROM usage u
JOIN users
    ON u.user_id = users.user_id
GROUP BY u.churned;
SELECT
    u.plan_type,
    COUNT(*) AS churned_users,
    ROUND(SUM(u.monthly_spend), 2) AS churned_monthly_revenue
FROM users u
JOIN usage us
    ON u.user_id = us.user_id
WHERE us.churned = 1
GROUP BY u.plan_type
ORDER BY churned_monthly_revenue DESC;
SELECT
    u.plan_type,
    COUNT(*) AS churned_users,
    ROUND(SUM(u.monthly_spend), 2) AS churned_monthly_revenue,
    ROUND(AVG(u.monthly_spend), 2) AS avg_revenue_per_churned_user
FROM users u
JOIN usage us
    ON u.user_id = us.user_id
WHERE us.churned = 1
GROUP BY u.plan_type
ORDER BY avg_revenue_per_churned_user DESC;
SELECT
    us.churned,
    COUNT(*) AS users,
    ROUND(AVG(u.monthly_spend), 2) AS avg_monthly_spend
FROM usage us
JOIN users u
    ON us.user_id = u.user_id
GROUP BY us.churned;
SELECT
    u.plan_type,
    us.churned,
    COUNT(*) AS users,
    ROUND(AVG(us.session_count), 2) AS avg_sessions
FROM users u
JOIN usage us
    ON u.user_id = us.user_id
GROUP BY u.plan_type, us.churned
ORDER BY u.plan_type, us.churned;
SELECT
    u.plan_type,
    us.churned,
    COUNT(*) AS users,
    ROUND(AVG(us.last_login_days), 2) AS avg_days_since_login
FROM users u
JOIN usage us
    ON u.user_id = us.user_id
GROUP BY u.plan_type, us.churned
ORDER BY u.plan_type, us.churned;
SELECT
    CASE
        WHEN session_count <= 10 THEN '0-10 sessions'
        WHEN session_count <= 20 THEN '11-20 sessions'
        WHEN session_count <= 30 THEN '21-30 sessions'
        ELSE '31+ sessions'
    END AS session_bucket,
    COUNT(*) AS total_users,
    SUM(churned) AS churned_users,
    ROUND(
        SUM(churned) * 100.0 / COUNT(*),
        2
    ) AS churn_rate
FROM usage
GROUP BY session_bucket
ORDER BY
    CASE
        WHEN session_bucket = '0-10 sessions' THEN 1
        WHEN session_bucket = '11-20 sessions' THEN 2
        WHEN session_bucket = '21-30 sessions' THEN 3
        ELSE 4
    END;
SELECT
    CASE
        WHEN session_count <= 10 THEN '0-10 sessions'
        WHEN session_count <= 20 THEN '11-20 sessions'
        WHEN session_count <= 30 THEN '21-30 sessions'
        ELSE '31+ sessions'
    END AS session_bucket,

    CASE
        WHEN last_login_days <= 7 THEN '0-7 days'
        WHEN last_login_days <= 14 THEN '8-14 days'
        ELSE '15+ days'
    END AS login_recency,

    COUNT(*) AS total_users,
    SUM(churned) AS churned_users,

    ROUND(
        SUM(churned) * 100.0 / COUNT(*),
        2
    ) AS churn_rate

FROM usage

GROUP BY session_bucket, login_recency

ORDER BY session_bucket, login_recency;
SELECT
    COUNT(*) AS total_users,
    SUM(us.churned) AS churned_users,
    ROUND(SUM(u.monthly_spend), 2) AS monthly_revenue,
    ROUND(
        SUM(CASE WHEN us.churned = 1 THEN u.monthly_spend ELSE 0 END),
        2
    ) AS churned_monthly_revenue
FROM users u
JOIN usage us
    ON u.user_id = us.user_id
WHERE us.session_count <= 10
  AND us.last_login_days > 14;
SELECT
    u.plan_type,
    COUNT(*) AS high_risk_users,
    SUM(us.churned) AS churned_users,
    ROUND(SUM(u.monthly_spend), 2) AS monthly_revenue,
    ROUND(
        SUM(CASE WHEN us.churned = 1 THEN u.monthly_spend ELSE 0 END),
        2
    ) AS churned_monthly_revenue
FROM users u
JOIN usage us
    ON u.user_id = us.user_id
WHERE us.session_count <= 10
  AND us.last_login_days > 14
GROUP BY u.plan_type
ORDER BY churned_monthly_revenue DESC;
SELECT
    CASE
        WHEN session_count <= 10
             AND last_login_days > 14
        THEN 'High Risk'
        ELSE 'Other Users'
    END AS risk_group,

    COUNT(*) AS total_users,

    SUM(churned) AS churned_users,

    ROUND(
        SUM(churned) * 100.0 / COUNT(*),
        2
    ) AS churn_rate

FROM usage

GROUP BY risk_group;
SELECT
    SUM(CASE WHEN us.churned = 1 THEN u.monthly_spend ELSE 0 END) AS churned_revenue,
    
    ROUND(
        SUM(CASE WHEN us.churned = 1 THEN u.monthly_spend ELSE 0 END) * 0.10,
        2
    ) AS revenue_if_10pct_retained,

    ROUND(
        SUM(CASE WHEN us.churned = 1 THEN u.monthly_spend ELSE 0 END) * 0.20,
        2
    ) AS revenue_if_20pct_retained,

    ROUND(
        SUM(CASE WHEN us.churned = 1 THEN u.monthly_spend ELSE 0 END) * 0.30,
        2
    ) AS revenue_if_30pct_retained

FROM users u
JOIN usage us
    ON u.user_id = us.user_id

WHERE us.session_count <= 10
  AND us.last_login_days > 14
  AND us.churned = 1;
SELECT
    CASE
        WHEN session_count <= 10
             AND last_login_days > 14
        THEN 'High Risk'
        ELSE 'Other Users'
    END AS risk_group,
    churned,
    COUNT(*) AS users
FROM usage
GROUP BY risk_group, churned
ORDER BY risk_group, churned;