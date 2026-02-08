import streamlit as st
import pandas as pd
import os

# ===================== CONFIGURATION =====================

HQ_PASSWORD = "benchmark@hq"   # change if needed

COMPANY_OPTIONS = [
    "Reliance Digital",
    "Croma",
    "Vijay Sales",
    "Bajaj Electronics",
    "Other"
]

YEARS = [2024, 2025, 2026]
WEEKS = list(range(1, 53))

EXPECTED_CLUSTERS = [
    "North 1", "North 2", "North 3",
    "West 1", "West 2", "West 3",
    "South 1", "South 2", "South 3", "South 4",
    "East 1", "East 2", "East 3",
    "Central 1", "Central 2"
    # extend to all 52 clusters
]

DATA_FILE = "cluster_inputs.csv"

# ===================== APP SETUP =====================

st.set_page_config(
    page_title="Weekly Cluster Benchmark – Reliance Digital",
    layout="wide"
)

st.title("Weekly Cluster Data Entry – Reliance Digital")

# ===================== LOAD DATA =====================

if os.path.exists(DATA_FILE):
    data = pd.read_csv(DATA_FILE)
else:
    data = pd.DataFrame(columns=[
        "Year",
        "Week",
        "Cluster",
        "Company",
        "Stores",
        "Area_mn_sqft",
        "Revenue_per_store",
        "Margin_per_store",
        "Net_additions",
        "LFL_growth",
        "Bills_per_store",
        "ABV"
    ])

# ===================== INPUT FORM =====================

with st.form("cluster_form"):
    st.subheader("Submit Weekly Cluster Data")

    col1, col2 = st.columns(2)

    with col1:
        year = st.selectbox("Year", YEARS)
        week = st.selectbox("Week number", WEEKS)
        cluster = st.selectbox("Cluster", EXPECTED_CLUSTERS)
        company = st.selectbox("Company", COMPANY_OPTIONS)
        stores = st.number_input("Total number of stores", min_value=0, step=1)
        area = st.number_input("Retail area (mn sq. ft.)", min_value=0.0)
        net_add = st.number_input("Net store additions", step=1)

    with col2:
        rev_store = st.number_input("Revenue per store (Rs. crore)", min_value=0.0)
        margin_store = st.number_input("Margin per store (Rs. crore)", min_value=0.0)
        lfl = st.number_input("LFL growth in revenue (%)", min_value=-100.0, max_value=100.0)
        bills = st.number_input("# of bills per store", min_value=0, step=1)
        abv = st.number_input("Average bill value (Rs.)", min_value=0.0)

    submitted = st.form_submit_button("Submit")

# ===================== SAVE DATA =====================

if submitted:
    new_row = pd.DataFrame([{
        "Year": year,
        "Week": week,
        "Cluster": cluster,
        "Company": company,
        "Stores": stores,
        "Area_mn_sqft": area,
        "Revenue_per_store": rev_store,
        "Margin_per_store": margin_store,
        "Net_additions": net_add,
        "LFL_growth": lfl,
        "Bills_per_store": bills,
        "ABV": abv
    }])

    data = pd.concat([data, new_row], ignore_index=True)
    data.to_csv(DATA_FILE, index=False)

    st.success("Weekly submission recorded successfully")

# ===================== CLUSTER MANAGER VIEW =====================

st.divider()
st.subheader("Your Submissions (Cluster View)")

cluster_data = data[data["Cluster"] == cluster]

if not cluster_data.empty:
    st.dataframe(
        cluster_data.sort_values(["Year", "Week"], ascending=False),
        use_container_width=True
    )
else:
    st.info("No submissions found for this cluster yet.")

# ===================== HQ VIEW =====================

st.divider()
st.subheader("HQ Benchmark View")

hq_access = st.text_input("HQ Access Password", type="password")

if hq_access == HQ_PASSWORD and not data.empty:

    colf1, colf2 = st.columns(2)
    with colf1:
        hq_year = st.selectbox("HQ View – Year", YEARS)
    with colf2:
        hq_week = st.selectbox("HQ View – Week", WEEKS)

    filtered = data[
        (data["Year"] == hq_year) &
        (data["Week"] == hq_week)
    ]

    # ---------- Submission Status ----------
    st.markdown("### Submission Status")

    submitted_clusters = set(filtered["Cluster"].unique())
    expected_clusters = set(EXPECTED_CLUSTERS)
    pending_clusters = sorted(list(expected_clusters - submitted_clusters))

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Clusters Expected", len(expected_clusters))
    col_s2.metric("Clusters Submitted", len(submitted_clusters))
    col_s3.metric("Clusters Pending", len(pending_clusters))

    if pending_clusters:
        st.warning("Pending cluster submissions")
        st.table(pd.DataFrame({"Pending Clusters": pending_clusters}))
    else:
        st.success("All clusters have submitted for this week")

    # ---------- Cluster-Level Detail ----------
    st.markdown("### Cluster-Level Detail")
    st.dataframe(filtered.sort_values(["Cluster", "Company"]), use_container_width=True)

    # ---------- National Summary ----------
    st.markdown("### National Benchmark Summary")

    summary_rows = []

    grouped = filtered.groupby("Company")

    for company, d in grouped:
        total_stores = d["Stores"].sum()
        total_area = d["Area_mn_sqft"].sum()
        total_revenue = (d["Revenue_per_store"] * d["Stores"]).sum()

        summary_rows.append({
            "Company": company,
            "Total number of stores": total_stores,
            "Retail area (mn sq. ft.)": total_area,
            "Revenue per store (Rs. crore)": total_revenue / total_stores if total_stores else 0,
            "Margin per store (Rs. crore)": (
                (d["Margin_per_store"] * d["Stores"]).sum() / total_stores
                if total_stores else 0
            ),
            "Revenue per sq. ft. (Rs.)": (
                (total_revenue * 1e7) / (total_area * 1e6)
                if total_area else 0
            ),
            "Margin per sq. ft. (Rs.)": (
                ((d["Margin_per_store"] * d["Stores"]).sum() * 1e7)
                / (total_area * 1e6)
                if total_area else 0
            ),
            "Net store additions": d["Net_additions"].sum(),
            "LFL growth in revenue (%)": (
                (d["LFL_growth"] * d["Revenue_per_store"] * d["Stores"]).sum()
                / total_revenue
                if total_revenue else 0
            ),
            "# of bills per store": (
                (d["Bills_per_store"] * d["Stores"]).sum() / total_stores
                if total_stores else 0
            ),
            "Average bill value (Rs.)": (
                (d["ABV"] * d["Stores"]).sum() / total_stores
                if total_stores else 0
            )
        })

    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

elif hq_access:
    st.error("Invalid HQ password")
