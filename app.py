import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Superstore Analytics Dashboard", layout="wide")

# --- HÀM LOAD DỮ LIỆU ---
@st.cache_data
def load_data():
    file_name = "SampleSuperstore.csv"
    if not os.path.exists(file_name):
        return None
    
    # Đọc file với encoding chuẩn để tránh lỗi font
    df = pd.read_csv(file_name, encoding='windows-1252')
    
    # Làm sạch tên cột và định dạng số
    df.columns = df.columns.str.strip()
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
    df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce').fillna(0)
    df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce').fillna(0)
    
    return df

df = load_data()

if df is None:
    st.error("❌ Không tìm thấy file 'SampleSuperstore.csv'. Hãy kiểm tra lại tệp nguồn!")
else:
    # --- SIDEBAR: BỘ LỌC TƯƠNG TÁC ---
    st.sidebar.header("🕹️ Bộ lọc tùy chỉnh")
    
    regions = st.sidebar.multiselect("Chọn Khu vực:", options=df["Region"].unique(), default=df["Region"].unique())
    segments = st.sidebar.multiselect("Chọn Phân khúc:", options=df["Segment"].unique(), default=df["Segment"].unique())
    categories = st.sidebar.multiselect("Chọn Danh mục:", options=df["Category"].unique(), default=df["Category"].unique())

    # Lọc dữ liệu
    df_filtered = df[
        df["Region"].isin(regions) & 
        df["Segment"].isin(segments) & 
        df["Category"].isin(categories)
    ]

    # --- TIÊU ĐỀ & KPIs ---
    st.title("🏬 BẢNG ĐIỀU KHIỂN KINH DOANH SUPERSTORE")
    
    k1, k2, k3, k4 = st.columns(4)
    total_sales = df_filtered['Sales'].sum()
    total_profit = df_filtered['Profit'].sum()
    
    k1.metric("Tổng Doanh thu", f"${total_sales:,.0f}")
    k2.metric("Tổng Lợi nhuận", f"${total_profit:,.0f}")
    k3.metric("Số lượng bán", f"{df_filtered['Quantity'].sum():,.0f}")
    
    margin = (total_profit / total_sales * 100) if total_sales != 0 else 0
    k4.metric("Tỷ suất lợi nhuận", f"{margin:.1f}%")

    st.divider()

    # --- PHẦN 1: HỆ THỐNG BIỂU ĐỒ CƠ BẢN (CHIA 2 CỘT) ---
    st.header("1️⃣ HỆ THỐNG BIỂU ĐỒ CƠ BẢN")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("2.1 Top 10 Bang doanh thu cao nhất")
        state_sales = df_filtered.groupby("State")["Sales"].sum().reset_index().sort_values("Sales", ascending=False).head(10)
        fig1 = px.line(state_sales, x="State", y="Sales", markers=True)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("2.2 Tỷ trọng Doanh thu theo Phân khúc")
        fig2 = px.pie(df_filtered, values='Sales', names='Segment', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("2.3 Doanh thu theo Vùng & Ngành hàng")
        fig3 = px.bar(df_filtered, x='Region', y='Sales', color='Category', barmode='group')
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("2.4 Tương quan Doanh thu - Lợi nhuận")
        fig4 = px.scatter(df_filtered, x='Sales', y='Profit', color='Category', size='Discount', hover_data=['Sub-Category'])
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # --- PHẦN 2: GIẢI PHÁP NÂNG CAO (GIAO DIỆN RỘNG ĐỂ CHỤP ẢNH) ---
    st.header("2️⃣ GIẢI PHÁP TRỰC QUAN HÓA NÂNG CAO")
    st.write("Dưới đây là các biểu đồ được thiết kế khổ rộng để tối ưu việc đưa vào báo cáo Word.")

    # 2.1 HEATMAP FULL-WIDTH
    st.subheader("📌 Phương án 1: Heatmap - Tổng Lợi nhuận theo Vùng & Ngành hàng")
    # SỬA LỖI: Gom nhóm theo SUM thay vì MEAN
    heat_data = df_filtered.groupby(['Category', 'Region'])['Profit'].sum().reset_index()
    fig_heat = px.density_heatmap(
        heat_data, x='Region', y='Category', z='Profit', 
        color_continuous_scale='RdYlGn', 
        text_auto='.0f', 
        color_continuous_midpoint=0, # Số 0 là màu trung tính, tránh nhầm lãi/lỗ
        height=500
    )
    fig_heat.update_layout(margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.write("---")

    # 2.2 TREEMAP FULL-WIDTH
    st.subheader("📌 Phương án 2: Treemap - Cơ cấu Doanh thu & Lợi nhuận đa tầng")
    # SỬA LỖI: Tính toán tổng trước khi vẽ để tránh lấy giá trị đơn lẻ
    df_tree_data = df_filtered.groupby(['Category', 'Sub-Category'])[['Sales', 'Profit']].sum().reset_index()
    
    fig_tree = px.treemap(
        df_tree_data, 
        path=['Category', 'Sub-Category'], 
        values='Sales', 
        color='Profit', 
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0, # Mốc ranh giới Đỏ - Xanh
        height=650
    )
    
    fig_tree.update_traces(
        textinfo="label+value",
        texttemplate="<b>%{label}</b><br>Doanh thu: $%{value:,.0f}",
        hovertemplate='<b>%{label}</b><br>Tổng Doanh thu: $%{value:,.0f}<br>Tổng Lợi nhuận: $%{color:,.0f}'
    )
    
    fig_tree.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_tree, use_container_width=True)
