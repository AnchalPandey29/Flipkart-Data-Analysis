import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="📱 Mobile Analytics Dashboard",
    page_icon="📊"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* Main background */
.main {
    background-color: #f5f7fa;
}

/* KPI Cards */
.kpi-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    text-align: center;
}

.kpi-title {
    font-size: 14px;
    color: gray;
}

.kpi-value {
    font-size: 26px;
    font-weight: bold;
    color: #1f77b4;
}

/* Section titles */
.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 20px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #111827;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("Flipkart_Mobiles.csv")

    df['Memory'] = df['Memory'].fillna(df['Memory'].mode()[0])
    df['Storage'] = df['Storage'].fillna(df['Storage'].mode()[0])
    df['Rating'] = df['Rating'].fillna(df['Rating'].mean())

    df['Memory_value'] = df['Memory'].str.extract(r'(\d+)').astype(float)
    df['Memory_GB'] = df['Memory_value']

    df['Storage_value'] = df['Storage'].str.extract(r'(\d+)').astype(float)
    df['Storage_GB'] = df['Storage_value']

    df['discount'] = df['Original Price'] - df['Selling Price']
    df['Discount_Percentage'] = (df['discount'] / df['Original Price']) * 100

    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Filters")
brand = st.sidebar.selectbox("Select Brand", ["All"] + sorted(df['Brand'].unique()))

filtered_df = df if brand == "All" else df[df["Brand"] == brand]

st.sidebar.markdown("---")
st.sidebar.info("Use filters to explore insights dynamically.")

# ---------------- HEADER ----------------
st.title("📱 Mobile Phone Analytics Dashboard")
st.caption("Explore pricing, performance, and trends in mobile data")

# ---------------- KPI CARDS ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Phones</div>
        <div class="kpi-value">{filtered_df.shape[0]}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Avg Price</div>
        <div class="kpi-value">₹{filtered_df['Selling Price'].mean():,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Avg Rating</div>
        <div class="kpi-value">{filtered_df['Rating'].mean():.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", "🏷 Brand Analysis", "💾 Specs", "💰 Pricing"
])

# ---------------- TAB 1 ----------------
with tab1:
    st.markdown('<div class="section-title">Top Discounted Phones</div>', unsafe_allow_html=True)
    st.dataframe(
        filtered_df.sort_values("Discount_Percentage", ascending=False).head(5),
        use_container_width=True
    )

# ---------------- TAB 2 ----------------
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Average Price by Brand")
        fig, ax = plt.subplots()
        data = filtered_df.groupby('Brand')['Selling Price'].mean().sort_values()
        ax.barh(data.index, data.values)
        ax.set_xlabel("Price")
        st.pyplot(fig)

    with col2:
        st.subheader("Brand Share")
        fig, ax = plt.subplots()
        filtered_df['Brand'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
        ax.set_ylabel("")
        st.pyplot(fig)

# ---------------- TAB 3 ----------------
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Price vs RAM")
        fig, ax = plt.subplots()
        sns.scatterplot(
            x=filtered_df["Memory_GB"],
            y=filtered_df["Selling Price"],
            ax=ax
        )
        st.pyplot(fig)

    with col2:
        st.subheader("Best Value Phones")
        st.dataframe(
            filtered_df.sort_values(
                ["Memory_GB", "Selling Price"],
                ascending=[False, True]
            ).head(5),
            use_container_width=True
        )

# ---------------- TAB 4 ----------------
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Price vs Discount")
        fig, ax = plt.subplots()
        sns.scatterplot(
            x=filtered_df["Selling Price"],
            y=filtered_df["Discount_Percentage"],
            ax=ax
        )
        st.pyplot(fig)

    with col2:
        st.subheader("Discount Distribution")
        fig, ax = plt.subplots()
        sns.histplot(filtered_df["Discount_Percentage"], kde=True, ax=ax)
        st.pyplot(fig)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Built By Anchal Pandey • Flipkart Sales Dashboard")
