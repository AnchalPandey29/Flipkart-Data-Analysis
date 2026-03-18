import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="📱 Mobile Analytics Dashboard",
    page_icon="📊"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

/* Background */
body {
    background-color: #f4f6f9;
}

/* Header */
.header {
    background: linear-gradient(90deg, #1f77b4, #4facfe);
    padding: 20px;
    border-radius: 12px;
    color: white;
    margin-bottom: 20px;
}

/* KPI Cards */
.kpi-card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.06);
    text-align: center;
    transition: 0.3s;
}
.kpi-card:hover {
    transform: translateY(-5px);
}

.kpi-card h4 {
    color: gray;
    margin-bottom: 5px;
}

.kpi-card h2 {
    color: #1f77b4;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f172a;
    padding-top: 20px;
}

[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* Section spacing */
.section {
    margin-top: 30px;
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background: #e5e7eb;
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
st.sidebar.markdown("## 📊 Mobile Analytics")

st.sidebar.markdown("### 🔍 Filters")

brand = st.sidebar.selectbox(
    "Brand",
    ["All"] + sorted(df['Brand'].unique())
)

price_range = st.sidebar.slider(
    "💰 Price Range",
    int(df['Selling Price'].min()),
    int(df['Selling Price'].max()),
    (int(df['Selling Price'].min()), int(df['Selling Price'].max()))
)

rating_filter = st.sidebar.slider(
    "⭐ Minimum Rating",
    0.0, 5.0, 0.0
)

# Apply filters
filtered_df = df.copy()

if brand != "All":
    filtered_df = filtered_df[filtered_df["Brand"] == brand]

filtered_df = filtered_df[
    (filtered_df["Selling Price"] >= price_range[0]) &
    (filtered_df["Selling Price"] <= price_range[1]) &
    (filtered_df["Rating"] >= rating_filter)
]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 About")
st.sidebar.info("""
Professional mobile analytics dashboard  
Built using Streamlit  

Includes:
- Price insights  
- Brand comparison  
- Feature analysis  
""")

# ---------------- HEADER ----------------
st.markdown("""
<div class="header">
    <h2>📱 Mobile Phone Analytics Dashboard</h2>
    <p>Advanced insights into pricing, performance, and specifications</p>
</div>
""", unsafe_allow_html=True)

# ---------------- KPI CARDS ----------------
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""
<div class="kpi-card">
    <h4>Total Phones</h4>
    <h2>{filtered_df.shape[0]}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card">
    <h4>Avg Price</h4>
    <h2>₹{filtered_df['Selling Price'].mean():,.0f}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card">
    <h4>Avg Rating</h4>
    <h2>{filtered_df['Rating'].mean():.2f}</h2>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="kpi-card">
    <h4>Max Discount</h4>
    <h2>{filtered_df['Discount_Percentage'].max():.1f}%</h2>
</div>
""", unsafe_allow_html=True)

# ---------------- SECTION 1 ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("📊 Brand Analysis")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    data = filtered_df.groupby('Brand')['Selling Price'].mean().sort_values()
    ax.barh(data.index, data.values)
    ax.set_title("Average Price by Brand")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    filtered_df['Brand'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
    ax.set_ylabel("")
    ax.set_title("Brand Distribution")
    st.pyplot(fig)

# ---------------- SECTION 2 ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("💾 Specifications Analysis")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    sns.scatterplot(
        x=filtered_df["Memory_GB"],
        y=filtered_df["Selling Price"],
        ax=ax
    )
    ax.set_title("Price vs RAM")
    st.pyplot(fig)

with col2:
    st.dataframe(
        filtered_df.sort_values(
            ["Memory_GB", "Selling Price"],
            ascending=[False, True]
        ).head(5),
        use_container_width=True
    )

# ---------------- SECTION 3 ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("💰 Pricing & Discounts")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    sns.scatterplot(
        x=filtered_df["Selling Price"],
        y=filtered_df["Discount_Percentage"],
        ax=ax
    )
    ax.set_title("Price vs Discount")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    sns.histplot(filtered_df["Discount_Percentage"], kde=True, ax=ax)
    ax.set_title("Discount Distribution")
    st.pyplot(fig)

# ---------------- SECTION 4 ----------------
st.markdown('<div class="section"></div>', unsafe_allow_html=True)
st.subheader("🏆 Top Discounted Phones")

st.dataframe(
    filtered_df.sort_values("Discount_Percentage", ascending=False).head(5),
    use_container_width=True
)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("📊 Professional Dashboard • Built with Streamlit")
