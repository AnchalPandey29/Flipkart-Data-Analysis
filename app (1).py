
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.set_page_config(layout="wide", page_title="Mobile Phone Data Analysis")

# --- Load and Preprocess Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("Flipkart_Mobiles.csv")
    
    # Handle missing values
    df['Memory'] = df['Memory'].fillna(df['Memory'].mode()[0])
    df['Storage'] = df['Storage'].fillna(df['Storage'].mode()[0])
    df['Rating'] = df['Rating'].fillna(df['Rating'].mean())
    
    # Process Memory column
    df['Memory_raw'] = df['Memory']
    df['Memory_value'] = df['Memory_raw'].str.extract(r'(\d+)').astype(float)
    df['is_MB_mem'] = df['Memory_raw'].str.contains("MB", case=False)
    df['Memory_GB'] = df['Memory_value']
    df.loc[df['is_MB_mem'], 'Memory_GB'] = df['Memory_value'] / 1024
    
    # Process Storage column
    df['Storage_raw'] = df['Storage']
    df['Storage_value'] = df['Storage_raw'].str.extract(r'(\d+)').astype(float)
    df['is_MB_storage'] = df['Storage_raw'].str.contains('MB', case=False)
    df['is_GB_storage'] = df['Storage_raw'].str.contains('GB', case=False)
    df['is_TB_storage'] = df['Storage_raw'].str.contains('TB', case=False)
    df['is_expandable'] = df['Storage_raw'].str.contains('Expandable', case=False)
    
    df['Storage_GB'] = df['Storage_value']
    df.loc[df['is_MB_storage'], 'Storage_GB'] = df['Storage_value'] / 1024
    df.loc[df['is_TB_storage'], 'Storage_GB'] = df['Storage_value'] * 1024
    df['Expandable_Storage_GB'] = None
    df.loc[df['is_expandable'], 'Expandable_Storage_GB'] = df['Storage_value']
    df.loc[df['is_expandable'], 'Storage_GB'] = None

    # Calculate discounts
    df['discount'] = df['Original Price'] - df['Selling Price']
    df['Discount_Percentage'] = (df['discount'] / df['Original Price']) * 100
    
    return df

df = load_data()

# --- Streamlit App Layout ---
st.title("📱 Mobile Phone Data Analysis Dashboard")
st.markdown("### Exploring Flipkart Mobile Data for Comprehensive Insights")

# Sidebar for filters
st.sidebar.header("Filter Options")
selected_brand = st.sidebar.selectbox('Select Brand', ['All'] + sorted(df['Brand'].unique().tolist()))

filtered_df = df.copy()
if selected_brand != 'All':
    filtered_df = df[df['Brand'] == selected_brand]

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Brand Analysis", "Memory & Storage", "Price & Discount", "Ratings Distribution"])

with tab1:
    st.header("Key Data Insights")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Phones Analyzed", value=filtered_df.shape[0])
    with col2:
        st.metric(label="Average Selling Price", value=f"₹{filtered_df['Selling Price'].mean():,.2f}")
    with col3:
        st.metric(label="Average Rating", value=f"{filtered_df['Rating'].mean():.2f}")
    
    st.subheader("Top 5 Most Discounted Phones")
    st.dataframe(filtered_df.sort_values('Discount_Percentage', ascending=False).head(5))

with tab2:
    st.header("Brand Performance Analysis")

    st.subheader("Average Selling Price by Brand")
    brand_price_chart = filtered_df.groupby('Brand')['Selling Price'].mean().sort_values()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(brand_price_chart.index, brand_price_chart.values, color='skyblue')
    ax.set_xlabel('Brand')
    ax.set_ylabel('Average Selling Price')
    ax.set_title('Average Selling Price by Brand')
    plt.xticks(rotation=90)
    st.pyplot(fig)

    st.subheader("Brand Distribution")
    brand_count_chart = filtered_df['Brand'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(brand_count_chart.values, labels=brand_count_chart.index, autopct='%1.1f%%', startangle=140)
    ax.set_title('Brand Distribution')
    st.pyplot(fig)

with tab3:
    st.header("Memory & Storage Analysis")

    st.subheader("Average Price by RAM (Memory_GB)")
    ram_price = filtered_df.groupby('Memory_GB')['Selling Price'].mean().sort_values()
    st.bar_chart(ram_price)

    st.subheader("Best Value RAM Phone (Highest RAM for Lowest Price)")
    st.dataframe(filtered_df.sort_values(['Memory_GB', 'Selling Price'], ascending=[False, True]).head(5))

    st.subheader("Best Value Storage Phone (Highest Storage for Lowest Price)")
    st.dataframe(filtered_df.sort_values(['Storage_GB', 'Selling Price'], ascending=[False, True]).head(5))

with tab4:
    st.header("Price and Discount Analysis")

    st.subheader("Selling Price vs. Discount Percentage")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x=filtered_df['Selling Price'], y=filtered_df['Discount_Percentage'], ax=ax, alpha=0.6)
    ax.set_xlabel('Selling Price')
    ax.set_ylabel('Discount Percentage')
    ax.set_title('Selling Price vs. Discount Percentage')
    st.pyplot(fig)

    st.subheader("Distribution of Discounts")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(filtered_df['Discount_Percentage'].dropna(), bins=20, kde=True, ax=ax)
    ax.set_xlabel('Discount Percentage')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Discount Percentages')
    st.pyplot(fig)

with tab5:
    st.header("Ratings Distribution")
    st.subheader("Distribution of Ratings")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(filtered_df['Rating'], bins=10, kde=True, ax=ax)
    ax.set_xlabel('Rating')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Ratings')
    st.pyplot(fig)

# --- Conclusion ---
st.sidebar.header("About")
st.sidebar.markdown("""
This interactive dashboard provides a detailed analysis of mobile phone data, offering insights into pricing, brand performance, memory/storage value, and discount trends. Use the filters and tabs to explore the data.

**Key Features:**
- Dynamic data filtering by brand.
- Tab-based navigation for organized insights.
- Visualizations for key metrics and distributions.
""")
