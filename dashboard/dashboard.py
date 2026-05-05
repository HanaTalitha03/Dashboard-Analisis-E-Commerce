import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="dark")

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_state_df(df):
    state_df = df.groupby("customer_state").agg({
        "order_id": "count",
        "price": "sum"
    })
    state_df = state_df.reset_index()
    state_df.rename(columns={
        "order_id": "total_transaksi",
        "price": "total_revenue"
    }, inplace=True)
    state_df = state_df.sort_values(by="total_revenue", ascending=False)

    return state_df

def create_category_df(df):
    category_df = df.groupby("product_category_name_english").agg({
        "price": "sum",
        "review_score": "mean"
    })
    category_df = category_df.reset_index()
    category_df.rename(columns={
        "price": "total_revenue",
        "review_score": "avg_review_score"
    }, inplace=True)
    category_df = category_df.sort_values(by="total_revenue", ascending=False)

    return category_df

# Load cleaned data
all_df = pd.read_csv("dashboard/main_data.csv")

datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter data
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan header untuk sidebar
    st.header("Filter Data")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Mengambil pilihan state dari multiselect
    state_list = sorted(all_df["customer_state"].unique())
    selected_state = st.multiselect(
        "Pilih State",
        options=state_list,
        default=state_list
    )

# Filter DataFrame
main_df = all_df[
    (all_df["order_purchase_timestamp"] >= pd.Timestamp(start_date)) &
    (all_df["order_purchase_timestamp"] <= pd.Timestamp(end_date)) &
    (all_df["customer_state"].isin(selected_state))
]

# Menyiapkan berbagai dataframe
state_df = create_state_df(main_df)
category_df = create_category_df(main_df)

# Header untuk dashboard
st.header("Dashboard Analisis E-Commerce")

# Ringkasan metrik utama
st.subheader("Ringkasan Data")

col1, col2, col3 = st.columns(3)

with col1:
    total_orders = main_df["order_id"].nunique()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = main_df["price"].sum()
    st.metric("Total Revenue", value=f"R$ {total_revenue:,.2f}")

with col3:
    avg_review_score = main_df["review_score"].mean()
    st.metric("Rata-rata Review Score", value=avg_review_score)

# Pertanyaan 1
st.subheader("State dengan Revenue dan Transaksi Tertinggi (2018)")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(
        data=state_df.head(10), 
        x="total_revenue", 
        y="customer_state", 
        color="#90CAF9",
        ax=ax
        )
    
    ax.set_xlabel("10 State dengan Revenue Tertinggi", fontsize=15)
    ax.set_xlabel("Total Revenue")
    ax.set_ylabel(None)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=10)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(
        data=state_df.head(10), 
        x="total_transaksi", 
        y="customer_state", 
        color="#D3D3D3",
        ax=ax
        )
    ax.set_title("10 State dengan Transaksi Tertinggi", loc="center", fontsize=15)
    ax.set_xlabel("Jumlah Transaksi")
    ax.set_ylabel(None)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=10)
    st.pyplot(fig)


# Tabel kontribusi revenue per state
st.markdown("### Tabel Kontribusi Revenue per State")
total_rev_all = state_df["total_revenue"].sum()
top10_state_df = state_df.head(10).copy()
top10_state_df["kontribusi_revenue"] = (top10_state_df["total_revenue"] / total_rev_all * 100).round(2)
top10_state_df.columns = ["State", "Total Transaksi", "Total Revenue", "Kontribusi Revenue (%)"]
st.dataframe(top10_state_df.reset_index(drop=True))

# Pertanyaan 2
st.subheader("Hubungan Review Score dan Revenue per Kategori (2018)")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(10,5))
    sns.barplot(
        data=category_df.head(10), 
        x="total_revenue", 
        y="product_category_name_english", 
        color="#90CAF9",
        ax=ax
        )
    ax.set_title("10 Kategori dengan Revenue Tertinggi", loc="center", fontsize=15)
    ax.set_xlabel("Total Revenue")
    ax.set_ylabel(None)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=10)
    st.pyplot(fig)

with col2:
    correlation = category_df["avg_review_score"].corr(category_df["total_revenue"])
    fig, ax = plt.subplots(figsize=(10,5))
    sns.scatterplot(
        data=category_df,
        x="avg_review_score",
        y="total_revenue",
        ax=ax
    )
    ax.set_title(f"Review Score vs Total Revenue\n(Korelasi: {correlation:.3f})", loc="center", fontsize=15)
    ax.set_xlabel("Rata-rata Review Score")
    ax.set_ylabel("Total Revenue")
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=10)
    st.pyplot(fig)

st.markdown(
    f"Nilai korelasi sebesar {correlation:.3f} menunjukkan bahwa terdapat hubungan yang {'kuat' if abs(correlation) > 0.7 else 'lemah'} antara rata-rata review score dan total revenue per kategori produk."
    )

st.caption("Dashboard Analisis E-Commerce Public Dataset | Hana Talitha Syahda")