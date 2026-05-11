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
    
    # Đọc file với encoding windows-1252 để tránh lỗi ký tự
    df = pd.read_csv(file_name, encoding='windows-1252')
    
    # 1. Làm sạch: Xóa khoảng trắng thừa trong tên cột [cite: 14]
    df.columns = df.columns.str.strip()
    
    # 2. Định dạng dữ liệu: Đảm bảo các cột định lượng là số [cite: 15]
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
    df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce').fillna(0)
    df['Discount'] = pd.to_numeric(df['Discount'], errors='coerce').fillna(0)
    
    return df

df = load_data()

if df is None:
    st.error("❌ Không tìm thấy file 'SampleSuperstore.csv'. Vui lòng kiểm tra lại tệp nguồn!")
else:
    # --- GIAO DIỆN SIDEBAR ---
    st.sidebar.header("🕹️ Bộ lọc tùy chỉnh")
    
    # Lấy danh sách các giá trị duy nhất để làm tùy chọn lọc
    all_regions = df["Region"].unique()
    all_segments = df["Segment"].unique()
    all_categories = df["Category"].unique()

    # Bộ lọc Khu vực [cite: 56]
    regions = st.sidebar.multiselect("Chọn Khu vực:", options=all_regions, default=all_regions)
    
    # Bộ lọc Phân khúc khách hàng [cite: 56]
    segments = st.sidebar.multiselect("Chọn Phân khúc:", options=all_segments, default=all_segments)
    
    # BỔ SUNG: Bộ lọc Danh mục sản phẩm theo yêu cầu
    categories = st.sidebar.multiselect("Chọn Danh mục sản phẩm:", options=all_categories, default=all_categories)

    # Lọc dữ liệu dựa trên lựa chọn của người dùng [cite: 57]
    df_filtered = df[
        df["Region"].isin(regions) & 
        df["Segment"].isin(segments) & 
        df["Category"].isin(categories)
    ]

    # --- TIÊU ĐỀ & KPIs ---
    st.title("🏬 BẢNG ĐIỀU KHIỂN KINH DOANH SUPERSTORE")
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    total_sales = df_filtered['Sales'].sum()
    total_profit = df_filtered['Profit'].sum()
    
    col_kpi1.metric("Tổng Doanh thu", f"${total_sales:,.0f}")
    col_kpi2.metric("Tổng Lợi nhuận", f"${total_profit:,.0f}")
    col_kpi3.metric("Số lượng bán", f"{df_filtered['Quantity'].sum():,.0f}")
    
    margin = (total_profit / total_sales * 100) if total_sales != 0 else 0
    col_kpi4.metric("Tỷ suất lợi nhuận", f"{margin:.1f}%")

    st.divider()

    # --- PHẦN 1: CÁC BIỂU ĐỒ CƠ BẢN ---
    st.header("1️⃣ HỆ THỐNG BIỂU ĐỒ CƠ BẢN")
    c1, c2 = st.columns(2)

    with c1:
        # 2.1 Biểu đồ đường (Line Graph) [cite: 22]
        st.subheader("2.1 Top 10 Bang doanh thu cao nhất")
        state_sales = df_filtered.groupby("State")["Sales"].sum().reset_index().sort_values("Sales", ascending=False).head(10)
        fig1 = px.line(state_sales, x="State", y="Sales", markers=True, labels={"Sales": "Doanh thu ($)"})
        st.plotly_chart(fig1, use_container_width=True)

        # 2.2 Biểu đồ tròn (Pie Chart) [cite: 26]
        st.subheader("2.2 Tỷ trọng Doanh thu theo Phân khúc")
        fig2 = px.pie(df_filtered, values='Sales', names='Segment', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        # 2.3 Biểu đồ cột (Bar Chart) [cite: 30]
        st.subheader("2.3 Doanh thu theo Vùng & Ngành hàng")
        fig3 = px.bar(df_filtered, x='Region', y='Sales', color='Category', barmode='group')
        st.plotly_chart(fig3, use_container_width=True)

        # 2.4 Biểu đồ phân tán (Scatter Plot) [cite: 34]
        st.subheader("2.4 Tương quan Doanh thu - Lợi nhuận")
        fig4 = px.scatter(df_filtered, x='Sales', y='Profit', color='Category', size='Discount', 
                          hover_data=['Sub-Category'], opacity=0.7)
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # --- PHẦN 2: PHƯƠNG ÁN NÂNG CAO (ĐÃ SỬA LỖI HIỂN THỊ) ---
    st.header("2️⃣ GIẢI PHÁP TRỰC QUAN HÓA NÂNG CAO")
    t1, t2 = st.tabs(["📌 Phương án 1: Heatmap", "📌 Phương án 2: Treemap"])

    with t1:
        st.subheader("Biểu đồ nhiệt: Tổng Lợi nhuận theo Vùng & Ngành hàng")
        # SỬA LỖI: Sử dụng .sum() để phản ánh đúng quy mô tài chính thay vì .mean() [cite: 40]
        heat_data = df_filtered.groupby(['Category', 'Region'])['Profit'].sum().reset_index()
        fig_heat = px.density_heatmap(
            heat_data, x='Region', y='Category', z='Profit', 
            color_continuous_scale='RdYlGn', 
            text_auto='.0f', 
            color_continuous_midpoint=0 # Đảm bảo mốc 0 là màu trung tính (vàng/trắng) [cite: 43, 54]
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with t2:
        st.subheader("Biểu đồ Treemap: Cơ cấu Doanh thu & Lợi nhuận")
        
        # SỬA LỖI: Gom nhóm dữ liệu trước khi vẽ để đảm bảo tính TOÀN BỘ lợi nhuận của Sub-Category
        df_tree_data = df_filtered.groupby(['Category', 'Sub-Category'])[['Sales', 'Profit']].sum().reset_index()
        
        fig_tree = px.treemap(
            df_tree_data, 
            path=['Category', 'Sub-Category'], 
            values='Sales', 
            color='Profit', 
            color_continuous_scale='RdYlGn',
            # ĐIỂM QUAN TRỌNG NHẤT:
            color_continuous_midpoint=0 
        )
        
        fig_tree.update_traces(
            textinfo="label+value",
            texttemplate="<b>%{label}</b><br>Doanh thu: $%{value:,.0f}",
            hovertemplate='<b>%{label}</b><br>Tổng Doanh thu: $%{value:,.0f}<br>Tổng Lợi nhuận: $%{color:,.0f}'
        )
        
        st.plotly_chart(fig_tree, use_container_width=True)
        st.info("💡 **Ghi chú:** Màu đỏ hiện nay chỉ đại diện cho các mặt hàng thực sự âm vốn (Lợi nhuận < 0).")
