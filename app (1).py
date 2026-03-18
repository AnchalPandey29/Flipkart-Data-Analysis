import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    layout="wide",
    page_title="📱 Mobile Analytics Pro",
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
    padding: 25px;
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

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f172a;
}

[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* Section spacing */
.section {
    margin-top: 30px;
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

    df['Memory_GB'] = df['Memory'].str.extract(r'(\d+)').astype(float)
    df['Storage_GB'] = df['Storage'].str.extract(r'(\d+)').astype(float)

    df['discount'] = df['Original Price'] - df['Selling Price']
    df['Discount_Percentage'] = (df['discount'] / df['Original Price']) * 100

    return df

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Filters")

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

rating = st.sidebar.slider("⭐ Min Rating", 0.0, 5.0, 0.0)

# Apply filters
filtered_df = df.copy()

if brand != "All":
    filtered_df = filtered_df[filtered_df["Brand"] == brand]

filtered_df = filtered_df[
    (filtered_df["Selling Price"].between(price_range[0], price_range[1])) &
    (filtered_df["Rating"] >= rating)
]

# ---------------- HEADER ----------------
st.markdown("""
<div class="header">
    <h2>📱 Mobile Analytics Dashboard</h2>
    <p>Interactive insights on pricing, brands, and features</p>
</div>
""", unsafe_allow_html=True)

# ---------------- KPI CARDS ----------------
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"""<div class="kpi-card"><h4>Total Phones</h4><h2>{filtered_df.shape[0]}</h2></div>""", unsafe_allow_html=True)
col2.markdown(f"""<div class="kpi-card"><h4>Avg Price</h4><h2>₹{filtered_df['Selling Price'].mean():,.0f}</h2></div>""", unsafe_allow_html=True)
col3.markdown(f"""<div class="kpi-card"><h4>Avg Rating</h4><h2>{filtered_df['Rating'].mean():.2f}</h2></div>""", unsafe_allow_html=True)
col4.markdown(f"""<div class="kpi-card"><h4>Max Discount</h4><h2>{filtered_df['Discount_Percentage'].max():.1f}%</h2></div>""", unsafe_allow_html=True)

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🏷 Brand Analysis",
    "💾 Specs",
    "💰 Pricing"
])

# ---------------- TAB 1 ----------------
with tab1:
    st.subheader("Top Discounted Phones")
    st.dataframe(
        filtered_df.sort_values("Discount_Percentage", ascending=False).head(10),
        use_container_width=True
    )

# ---------------- TAB 2 ----------------
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            filtered_df.groupby('Brand')['Selling Price'].mean().sort_values().reset_index(),
            x='Selling Price',
            y='Brand',
            orientation='h',
            title="Average Price by Brand"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            filtered_df,
            names='Brand',
            title="Brand Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 3 ----------------
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.scatter(
            filtered_df,
            x="Memory_GB",
            y="Selling Price",
            color="Brand",
            title="Price vs RAM"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Best Value Phones")
        st.dataframe(
            filtered_df.sort_values(
                ["Memory_GB", "Selling Price"],
                ascending=[False, True]
            ).head(10),
            use_container_width=True
        )

# ---------------- TAB 4 ----------------
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        fig = px.scatter(
            filtered_df,
            x="Selling Price",
            y="Discount_Percentage",
            color="Brand",
            title="Price vs Discount"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            filtered_df,
            x="Discount_Percentage",
            nbins=20,
            title="Discount Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption(" Flipkart Sales Analysis • Built By Anchal Pandey")
