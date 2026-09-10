
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Retention Command Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "Outputs"
RISK_FILE = OUTPUT_DIR / "customer_risk_scores.csv"
QUEUE_FILE = OUTPUT_DIR / "intervention_queue.csv"
AB_FILE = OUTPUT_DIR / "ab_test_results.csv"
KPI_FILE = OUTPUT_DIR / "retention_kpis.csv"
LOG_DB = OUTPUT_DIR / "intervention_log.db"

# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }

    .subtitle {
        color: #666;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Explicit dark text for all custom white cards */
    .kpi-card {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 18px;
        background: #ffffff;
        min-height: 115px;
        color: #111827 !important;
    }

    .kpi-card .kpi-label {
        font-size: 0.82rem;
        color: #4b5563 !important;
        margin-bottom: 8px;
    }

    .kpi-card .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #111827 !important;
    }

    /* Keep normal Streamlit metrics readable on the dark app background */
    [data-testid="stMetricLabel"] {
        color: #9ca3af !important;
    }

    [data-testid="stMetricValue"] {
        color: #f9fafb !important;
    }

    [data-testid="stMetricDelta"] {
        color: #d1d5db !important;
    }

    /* Streamlit warning/info boxes use dark backgrounds in the current theme */
    [data-testid="stAlert"] {
        color: #ffffff !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div,
    [data-testid="stAlert"] span {
        color: #ffffff !important;
    }

    /* Text inside light containers */
    .stDataFrame, .stTable {
        color: #111827;
    }

    .risk-critical {
        color: #b91c1c;
        font-weight: 700;
    }

    .risk-high {
        color: #c2410c;
        font-weight: 700;
    }

    .risk-moderate {
        color: #a16207;
        font-weight: 700;
    }

    .risk-healthy {
        color: #15803d;
        font-weight: 700;
    }

    .info-box {
        border-left: 4px solid #6b7280;
        background: #f8fafc;
        color: #111827 !important;
        padding: 12px 15px;
        border-radius: 6px;
        margin: 8px 0;
    }

    .info-box,
    .info-box p,
    .info-box strong,
    .info-box b {
        color: #111827 !important;
    }

    /* Force readable text in Streamlit alert/info containers */
    [data-testid="stAlert"] {
        color: #111827 !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div,
    [data-testid="stAlert"] span {
        color: #111827 !important;
    }
    
    /* Custom alert boxes with explicit text colors */
    .warning-box {
        background: #3f4512;
        color: #ffffff !important;
        padding: 14px 18px;
        border-radius: 9px;
        margin: 10px 0;
    }

    .warning-box p,
    .warning-box strong,
    .warning-box b {
        color: #ffffff !important;
        margin: 0;
    }

    .action-box {
        background: #1d3a56;
        color: #ffffff !important;
        padding: 16px 20px;
        border-radius: 9px;
        margin: 10px 0;
    }

    .action-box p,
    .action-box strong,
    .action-box b {
        color: #ffffff !important;
    }

    .empty-log-box {
        background: #1d3a56;
        color: #ffffff !important;
        padding: 16px 20px;
        border-radius: 9px;
        margin: 10px 0;
    }

    .empty-log-box p {
        color: #ffffff !important;
        margin: 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data():
    risk = pd.read_csv(RISK_FILE)
    queue = pd.read_csv(QUEUE_FILE)
    ab = pd.read_csv(AB_FILE)
    kpi = pd.read_csv(KPI_FILE)

    # Normalize expected numeric fields
    for df in [risk, queue]:
        for col in ["churn_probability", "monthly_spend", "session_count",
                    "last_login_days", "actual_churn"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    return risk, queue, ab, kpi


def init_log_db():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(LOG_DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS intervention_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            risk_segment TEXT,
            churn_probability REAL,
            recommended_action TEXT,
            priority TEXT,
            plan_type TEXT,
            monthly_spend REAL,
            session_count REAL,
            last_login_days REAL,
            intervention_time TEXT,
            status TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log_intervention(row):
    init_log_db()

    conn = sqlite3.connect(LOG_DB)
    conn.execute(
        """
        INSERT INTO intervention_log (
            user_id, risk_segment, churn_probability,
            recommended_action, priority, plan_type,
            monthly_spend, session_count, last_login_days,
            intervention_time, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(row["user_id"]),
            str(row["risk_segment"]),
            float(row["churn_probability"]),
            str(row["recommended_action"]),
            str(row["priority"]),
            str(row["plan_type"]),
            float(row["monthly_spend"]),
            float(row["session_count"]),
            float(row["last_login_days"]),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Launched - Simulated",
        ),
    )
    conn.commit()
    conn.close()


def load_intervention_log():
    init_log_db()
    conn = sqlite3.connect(LOG_DB)
    df = pd.read_sql_query(
        """
        SELECT *
        FROM intervention_log
        ORDER BY intervention_time DESC
        """,
        conn,
    )
    conn.close()
    return df


risk_df, queue_df, ab_df, kpi_df = load_data()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## Retention Command Center")
st.sidebar.caption("Customer churn decision-support prototype")

page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "Risk Queue",
        "Customer Profile",
        "What-If Simulator",
        "Experiments",
        "Intervention Log",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Prototype architecture")
st.sidebar.markdown(
    """
    **Data → Prediction → Risk → Intervention → Measurement**

    Python + XGBoost + SQLite + Streamlit
    """
)

# ============================================================
# HELPERS
# ============================================================

def money(value):
    return f"₹{value:,.0f}"


def pct(value):
    return f"{value:.1f}%"


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.markdown(
        '<div class="main-title">Retention Command Center</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="subtitle">Turn churn predictions into prioritized retention decisions.</div>',
        unsafe_allow_html=True,
    )

    total_customers = len(risk_df)
    at_risk = int((risk_df["churn_probability"] >= 0.20).sum())
    critical = int((risk_df["risk_segment"] == "Critical").sum())

    revenue_at_risk = risk_df.loc[
        risk_df["churn_probability"] >= 0.20,
        "monthly_spend"
    ].sum()

    cols = st.columns(4)

    metrics = [
        ("Customers analyzed", f"{total_customers:,}"),
        ("Customers needing intervention", f"{at_risk:,}"),
        ("Critical risk customers", f"{critical:,}"),
        ("Monthly revenue represented", money(revenue_at_risk)),
    ]

    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    left, right = st.columns(2)

    with left:
        st.subheader("Risk distribution")

        risk_order = ["Critical", "High", "Moderate", "Healthy"]
        risk_counts = (
            risk_df["risk_segment"]
            .value_counts()
            .reindex(risk_order, fill_value=0)
        )

        chart_df = pd.DataFrame(
            {"Customers": risk_counts}
        )
        st.bar_chart(chart_df)

        st.caption(
            "Operational thresholds: Critical ≥70%, High 40–69.9%, "
            "Moderate 20–39.9%, Healthy <20%."
        )

    with right:
        st.subheader("Revenue exposure by risk")

        revenue_by_risk = (
            risk_df.groupby("risk_segment")["monthly_spend"]
            .sum()
            .reindex(risk_order, fill_value=0)
        )

        revenue_chart = pd.DataFrame(
            {"Monthly revenue represented": revenue_by_risk}
        )
        st.bar_chart(revenue_chart)

    st.divider()

    st.subheader("Highest-priority customers")

    top = (
        risk_df[risk_df["churn_probability"] >= 0.20]
        .sort_values("churn_probability", ascending=False)
        .head(10)
        [
            [
                "user_id",
                "risk_segment",
                "churn_probability",
                "plan_type",
                "session_count",
                "last_login_days",
                "monthly_spend",
                "recommended_action",
                "priority",
            ]
        ]
        .copy()
    )

    top["churn_probability"] = top["churn_probability"].map(lambda x: f"{x:.1%}")
    top["monthly_spend"] = top["monthly_spend"].map(money)

    st.dataframe(
        top,
        width="stretch",
        hide_index=True,
        column_config={
            "user_id": "Customer",
            "risk_segment": "Risk",
            "churn_probability": "Churn Probability",
            "plan_type": "Plan",
            "session_count": "Sessions",
            "last_login_days": "Days Since Login",
            "monthly_spend": "Monthly Spend",
            "recommended_action": "Recommended Action",
            "priority": "Priority",
        },
    )

    st.markdown(
        """
        <div class="info-box">
        <b>Product interpretation:</b> the system is designed to focus limited
        retention capacity on customers most likely to churn, rather than treating
        every customer equally.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# RISK QUEUE
# ============================================================

elif page == "Risk Queue":

    st.title("Risk Queue")
    st.caption("Prioritized customer list generated by the retention decision system.")

    c1, c2, c3 = st.columns(3)

    with c1:
        segment_options = ["All"] + [
            x for x in ["Critical", "High", "Moderate", "Healthy"]
            if x in queue_df["risk_segment"].unique()
        ]
        selected_segment = st.selectbox("Risk segment", segment_options)

    with c2:
        plan_options = ["All"] + sorted(queue_df["plan_type"].dropna().unique().tolist())
        selected_plan = st.selectbox("Plan", plan_options)

    with c3:
        min_probability = st.slider(
            "Minimum churn probability",
            min_value=0.0,
            max_value=1.0,
            value=0.20,
            step=0.05,
        )

    filtered = queue_df.copy()

    filtered = filtered[
        filtered["churn_probability"] >= min_probability
    ]

    if selected_segment != "All":
        filtered = filtered[
            filtered["risk_segment"] == selected_segment
        ]

    if selected_plan != "All":
        filtered = filtered[
            filtered["plan_type"] == selected_plan
        ]

    st.write(f"**{len(filtered):,} customers** match the current filters.")

    display = filtered.sort_values(
        "churn_probability",
        ascending=False
    ).copy()

    display["churn_probability"] = display["churn_probability"].map(
        lambda x: f"{x:.1%}"
    )
    display["monthly_spend"] = display["monthly_spend"].map(money)

    st.dataframe(
        display[
            [
                "user_id",
                "risk_segment",
                "churn_probability",
                "plan_type",
                "session_count",
                "last_login_days",
                "monthly_spend",
                "recommended_action",
                "priority",
            ]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "user_id": "Customer",
            "risk_segment": "Risk",
            "churn_probability": "Churn Probability",
            "plan_type": "Plan",
            "session_count": "Sessions",
            "last_login_days": "Days Since Login",
            "monthly_spend": "Monthly Spend",
            "recommended_action": "Recommended Action",
            "priority": "Priority",
        },
    )

# ============================================================
# CUSTOMER PROFILE
# ============================================================

elif page == "Customer Profile":

    st.title("Customer Profile")
    st.caption("Inspect the model output and recommended retention action for one customer.")

    customers = (
        risk_df.sort_values("churn_probability", ascending=False)["user_id"]
        .astype(str)
        .tolist()
    )

    selected_customer = st.selectbox(
        "Select customer",
        customers,
    )

    customer = risk_df[
        risk_df["user_id"].astype(str) == str(selected_customer)
    ].iloc[0]

    st.divider()

    cols = st.columns(4)

    with cols[0]:
        st.metric(
            "Churn probability",
            f"{customer['churn_probability']:.1%}"
        )

    with cols[1]:
        st.metric(
            "Risk segment",
            customer["risk_segment"]
        )

    with cols[2]:
        st.metric(
            "Monthly spend",
            money(customer["monthly_spend"])
        )

    with cols[3]:
        st.metric(
            "Plan",
            customer["plan_type"]
        )

    st.subheader("Behavior")

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        st.metric("Sessions", f"{int(customer['session_count'])}")

    with b2:
        st.metric("Days since login", f"{int(customer['last_login_days'])}")

    with b3:
        st.metric("Features used", f"{int(customer['features_used'])}")

    with b4:
        st.metric("Payment failures", f"{int(customer['payment_failures'])}")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Risk diagnosis")

        if customer["last_login_days"] > 14:
            st.markdown(
                '<div class="warning-box">Extended inactivity detected.</div>',
                unsafe_allow_html=True,
            )

        if customer["session_count"] <= 10:
            st.markdown(
                '<div class="warning-box">Low product engagement detected.</div>',
                unsafe_allow_html=True,
            )

        if (
            customer["last_login_days"] <= 14
            and customer["session_count"] > 10
        ):
            st.success("No major inactivity/low-session warning triggered.")

    with right:
        st.subheader("Recommended intervention")

        st.info(
            f"**{customer['recommended_action']}**\n\n"
            f"Priority: **{customer['priority']}**"
        )

        if st.button(
            "Launch Intervention",
            type="primary",
            width="stretch",
        ):
            log_intervention(customer)
            st.success(
                f"Intervention launched for customer {selected_customer} "
                "(simulated prototype action)."
            )

# ============================================================
# WHAT-IF SIMULATOR
# ============================================================

elif page == "What-If Simulator":

    st.title("What-If Intervention Simulator")
    st.caption(
        "Explore how changing the intervention threshold changes workload and churn capture."
    )

    threshold = st.slider(
        "Intervention threshold",
        min_value=0.05,
        max_value=0.50,
        value=0.20,
        step=0.05,
        format="%.0f%%",
    )

    eligible = risk_df[
        risk_df["churn_probability"] >= threshold
    ].copy()

    total_flagged = len(eligible)

    if "actual_churn" in eligible.columns:
        churners_captured = int(eligible["actual_churn"].sum())
        total_churners = int(risk_df["actual_churn"].sum())
        capture_rate = (
            churners_captured / total_churners
            if total_churners > 0 else 0
        )
    else:
        churners_captured = np.nan
        capture_rate = np.nan

    revenue = eligible["monthly_spend"].sum()

    a, b, c, d = st.columns(4)

    with a:
        st.metric("Customers targeted", f"{total_flagged:,}")

    with b:
        st.metric(
            "Intervention coverage",
            f"{total_flagged / len(risk_df):.1%}"
        )

    with c:
        st.metric(
            "Historical churners captured",
            f"{churners_captured:,}"
            if not pd.isna(churners_captured) else "N/A"
        )

    with d:
        st.metric(
            "Revenue represented",
            money(revenue)
        )

    st.divider()

    thresholds = np.arange(0.05, 0.51, 0.05)
    rows = []

    total_churners_all = (
        int(risk_df["actual_churn"].sum())
        if "actual_churn" in risk_df.columns else np.nan
    )

    for t in thresholds:
        subset = risk_df[risk_df["churn_probability"] >= t]

        if "actual_churn" in subset.columns:
            caught = int(subset["actual_churn"].sum())
            capture = caught / total_churners_all if total_churners_all else np.nan
        else:
            caught = np.nan
            capture = np.nan

        rows.append(
            {
                "Threshold": f"{t:.0%}",
                "Customers Targeted": len(subset),
                "Coverage": len(subset) / len(risk_df),
                "Historical Churners Captured": caught,
                "Capture Rate": capture,
                "Revenue Represented": subset["monthly_spend"].sum(),
            }
        )

    scenario_df = pd.DataFrame(rows)

    scenario_display = scenario_df.copy()
    scenario_display["Coverage"] = scenario_display["Coverage"].map(
        lambda x: f"{x:.1%}"
    )
    scenario_display["Capture Rate"] = scenario_display["Capture Rate"].map(
        lambda x: f"{x:.1%}" if not pd.isna(x) else "N/A"
    )
    scenario_display["Revenue Represented"] = scenario_display[
        "Revenue Represented"
    ].map(money)

    st.subheader("Threshold scenarios")

    st.dataframe(
        scenario_display,
        width="stretch",
        hide_index=True,
    )

    st.markdown(
        """
        <div class="info-box">
        <b>Decision principle:</b> a lower threshold catches more potential churners
        but increases intervention workload. A higher threshold reduces workload
        but risks missing customers who may churn.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "Historical simulation only: these results use known historical outcomes. "
        "They do not establish causal retention impact."
    )

# ============================================================
# EXPERIMENTS
# ============================================================

elif page == "Experiments":

    st.title("Retention Experiments")
    st.caption("A/B testing framework for evaluating intervention effectiveness.")

    ab = ab_df.copy()

    if len(ab.columns) > 0:
        st.dataframe(
            ab,
            width="stretch",
            hide_index=True,
        )

    # Try to surface the known experiment values from the exported file.
    numeric_values = {}
    for col in ab.columns:
        try:
            numeric_values[col] = pd.to_numeric(ab[col], errors="coerce")
        except Exception:
            pass

    st.divider()

    st.subheader("Experiment interpretation")

    st.markdown(
        """
        **Purpose:** compare retention between customers receiving a treatment
        intervention and a control group.

        **Important:** the current experiment is a historical simulation using
        observed outcomes. It should be presented as an experiment framework /
        retrospective simulation, not as proof that the intervention caused the
        observed difference.

        A production version would:
        1. Generate the risk score.
        2. Randomly assign eligible customers to control or treatment.
        3. Deliver the intervention.
        4. Observe retention over a predefined period.
        5. Run a statistical significance test.
        6. Roll out the intervention only if the evidence supports it.
        """
    )

# ============================================================
# INTERVENTION LOG
# ============================================================

elif page == "Intervention Log":

    st.title("Intervention Log")
    st.caption("Persistent record of interventions launched from the prototype.")

    log_df = load_intervention_log()

    if log_df.empty:
        st.markdown(
            '''
            <div class="empty-log-box">
                No interventions have been launched yet.
                This is expected until you launch one from Customer Profile.
            </div>
            ''',
            unsafe_allow_html=True,
        )
    else:
        total = len(log_df)
        unique_customers = log_df["user_id"].nunique()

        c1, c2 = st.columns(2)

        with c1:
            st.metric("Interventions launched", f"{total:,}")

        with c2:
            st.metric("Unique customers", f"{unique_customers:,}")

        st.dataframe(
            log_df,
            width="stretch",
            hide_index=True,
        )

        st.caption(
            "These are simulated prototype actions; no real customer communication is sent."
        )
