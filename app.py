import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Bảng điều khiển Phân tích Superstore", layout="wide")

# --- HÀM LOAD DỮ LIỆU ---
@st.cache_data
def load_data():
    file_name = "SampleSuperstore.csv"
    if not os.path.exists(file_name):
        return None
    
    # Đọc file với encoding chuẩn
    df = pd.read_csv(file_name, encoding='windows-1252')
    
    # 1. Làm sạch: Xóa khoảng trắng tên cột
    df.columns = df.columns.str.strip()
    
    # 2. Xử lý dữ liệu thiếu/sai định dạng
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
    df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce').fillna(0)
    
    return df

df = load_data()

if df is None:
    st.error("❌ Không tìm thấy file 'SampleSuperstore.csv'. Hãy kiểm tra tên file!")
else:
    # --- GIAO DIỆN DASHBOARD ---
    st.title("🏬 BẢNG ĐIỀU KHIỂN KINH DOANH SUPERSTORE")
    st.markdown("### Báo cáo: Phân tích & Trực quan hóa dữ liệu bán hàng")

    # SIDEBAR: BỔ SUNG BỘ LỌC CATEGORY
    st.sidebar.header("🕹️ Bộ lọc tùy chỉnh")
    regions = st.sidebar.multiselect("Chọn Khu vực:", options=df["Region"].unique(), default=df["Region"].unique())
    segments = st.sidebar.multiselect("Chọn Phân khúc:", options=df["Segment"].unique(), default=df["Segment"].unique())
    # Thêm bộ lọc Danh mục sản phẩm
    categories = st.sidebar.multiselect("Chọn Danh mục sản phẩm:", options=df["Category"].unique(), default=df["Category"].unique())

    # Lọc dữ liệu theo tương tác người dùng (đã thêm categories)
    df_filtered = df[
        df["Region"].isin(regions) & 
        df["Segment"].isin(segments) & 
        df["Category"].isin(categories)
    ]

    # CHỈ SỐ TỔNG QUAN (KPIs)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_sales = df_filtered['Sales'].sum()
    total_profit = df_filtered['Profit'].sum()
    
    kpi1.metric("Tổng Doanh thu", f"${total_sales:,.0f}")
    kpi2.metric("Tổng Lợi nhuận", f"${total_profit:,.0f}")
    kpi3.metric("Số lượng bán ra", f"{df_filtered['Quantity'].sum():,.0f}")
    kpi4.metric("Tỷ suất Lợi nhuận", f"{(total_profit/total_sales*100 if total_sales != 0 else 0):.1f}%")

    st.divider()

    # --- PHẦN 1: HỆ THỐNG BIỂU ĐỒ CƠ BẢN ---
    st.header("1️⃣ HỆ THỐNG BIỂU ĐỒ CƠ BẢN")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("2.1 Top 10 Bang doanh thu cao nhất")
        state_sales = df_filtered.groupby("State")["Sales"].sum().reset_index().sort_values("Sales", ascending=False).head(10)
        fig1 = px.line(state_sales, x="State", y="Sales", markers=True, labels={"Sales": "Doanh thu ($)"})
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("2.2 Tỷ trọng Doanh thu theo Phân khúc")
        fig2 = px.pie(df_filtered, values='Sales', names='Segment', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("2.3 Doanh thu theo Vùng & Ngành hàng")
        fig3 = px.bar(df_filtered, x='Region', y='Sales', color='Category', barmode='group')
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("2.4 Doanh thu vs Lợi nhuận")
        fig4 = px.scatter(df_filtered, x='Sales', y='Profit', color='Category', size='Discount', hover_data=['Sub-Category'])
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # --- PHẦN 2: GIẢI PHÁP NÂNG CAO (ĐÃ SỬA LỖI) ---
    st.header("2️⃣ GIẢI PHÁP TRỰC QUAN HÓA NÂNG CAO")
    tab1, tab2 = st.tabs(["📌 Phương án 1: Biểu đồ nhiệt (Heatmap)", "📌 Phương án 2: Treemap (Cây phân cấp)"])

    with tab1:
        st.subheader("Biểu đồ nhiệt: Tổng Lợi nhuận theo Vùng & Ngành hàng")
        # SỬA LỖI: Chuyển từ .mean() sang .sum() để phản ánh đúng thực tế kinh doanh
        heat_data = df_filtered.groupby(['Category', 'Region'])['Profit'].sum().reset_index()
        fig_heat = px.density_heatmap(
            heat_data, x='Region', y='Category', z='Profit', 
            color_continuous_scale='RdYlGn', 
            text_auto='.0f', # Hiển thị số nguyên cho rõ ràng
            color_continuous_midpoint=0 # Đảm bảo số 0 là màu trung tính
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        st.write("**Giải pháp:** Đã chuyển sang hiển thị **Tổng lợi nhuận** để tránh nhầm lẫn với giá trị trung bình.")

    with tab2:
        st.subheader("Biểu đồ Treemap: Cơ cấu Doanh thu & Lợi nhuận đa tầng")
        
        # SỬA LỖI MÀU SẮC: Thiết lập midpoint=0 để màu đỏ chỉ dành cho lợi nhuận âm
        fig_tree = px.treemap(
            df_filtered, 
            path=[px.Constant("Tất cả Sản phẩm"), 'Category', 'Sub-Category'], 
            values='Sales', 
            color='Profit', 
            color_continuous_scale='RdYlGn',
            color_continuous_midpoint=0 # CỰC KỲ QUAN TRỌNG: Để 0 là mốc trắng/vàng, tránh "nhuộm đỏ" cả các nhóm lãi ít
        )
        
        fig_tree.update_traces(
            textinfo="label+value",
            texttemplate="%{label}<br>Doanh thu: $%{value:,.0f}",
            hovertemplate='<b>%{label}</b><br>Doanh thu: $%{value:,.0f}<br>Lợi nhuận: $%{color:,.0f}'
        )
        
        st.plotly_chart(fig_tree, use_container_width=True)
        st.success("✅ **Cải tiến:** Thang màu Treemap đã được căn chỉnh mốc 0. Giờ đây chỉ những nhóm thực sự lỗ (như Tables) mới hiển thị màu đỏ.")
