import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Superstore Analytics Dashboard", layout="wide")

# --- HÀM LOAD DỮ LIỆU (PHẦN 1: 10%) ---
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
    st.error("❌ Không tìm thấy file 'SampleSuperstore.csv'. Hãy kiểm tra tên file trên GitHub!")
else:
    # --- GIAO DIỆN DASHBOARD ---
    st.title("🏬 SUPERSTORE BUSINESS DASHBOARD")
    st.markdown("### Đồ án Giữa kỳ: Phân tích & Trực quan hóa dữ liệu")

    # SIDEBAR: DASHBOARD TƯƠNG TÁC (PHẦN 4)
    st.sidebar.header("🕹️ Bộ lọc tương tác")
    regions = st.sidebar.multiselect("Chọn Vùng (Region):", options=df["Region"].unique(), default=df["Region"].unique())
    segments = st.sidebar.multiselect("Chọn Phân khúc (Segment):", options=df["Segment"].unique(), default=df["Segment"].unique())

    # Lọc dữ liệu theo tương tác người dùng
    df_filtered = df[df["Region"].isin(regions) & df["Segment"].isin(segments)]

    # CHỈ SỐ TỔNG QUAN (KPIs)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Tổng Doanh thu", f"${df_filtered['Sales'].sum():,.0f}")
    kpi2.metric("Tổng Lợi nhuận", f"${df_filtered['Profit'].sum():,.0f}")
    kpi3.metric("Số lượng bán", f"{df_filtered['Quantity'].sum():,.0f}")
    kpi4.metric("Tỷ lệ LN", f"{(df_filtered['Profit'].sum()/df_filtered['Sales'].sum()*100):.1f}%")

    st.divider()

    # --- PHẦN 2: 4 BIỂU ĐỒ CƠ BẢN (40%) ---
    st.header("1️⃣ HỆ THỐNG BIỂU ĐỒ CƠ BẢN")
    
    col1, col2 = st.columns(2)

    with col1:
        # 2.1 Line Graph
        st.subheader("2.1 Line Graph: Top 10 Bang Doanh thu")
        state_sales = df_filtered.groupby("State")["Sales"].sum().reset_index().sort_values("Sales", ascending=False).head(10)
        fig1 = px.line(state_sales, x="State", y="Sales", markers=True, title="Top 10 States by Sales")
        st.plotly_chart(fig1, use_container_width=True)
        st.info("**Insight:** California dẫn đầu thị trường. **Hạn chế:** Chỉ nhìn thấy nhóm đứng đầu.")

        # 2.2 Pie Chart
        st.subheader("2.2 Pie Chart: Tỷ trọng Sales theo Segment")
        fig2 = px.pie(df_filtered, values='Sales', names='Segment', hole=0.4, title="Sales Distribution")
        st.plotly_chart(fig2, use_container_width=True)
        st.info("**Insight:** Consumer chiếm tỷ trọng chính. **Hạn chế:** Khó so sánh chính xác diện tích.")

    with col2:
        # 2.3 Stacked Bar Chart
        st.subheader("2.3 Stacked Bar: Doanh thu theo Vùng & Ngành hàng")
        fig3 = px.bar(df_filtered, x='Region', y='Sales', color='Category', title="Regional Sales by Category")
        st.plotly_chart(fig3, use_container_width=True)
        st.info("**Insight:** West có doanh số Technology cao nhất. **Hạn chế:** Khó xem giá trị nhóm giữa.")

        # 2.4 Scatter Plot
        st.subheader("2.4 Scatter Plot: Sales vs Profit")
        fig4 = px.scatter(df_filtered, x='Sales', y='Profit', color='Category', size='Discount', hover_data=['Sub-Category'])
        st.plotly_chart(fig4, use_container_width=True)
        st.info("**Insight:** Discount cao gây lỗ vốn. **Hạn chế:** Các điểm dữ liệu bị chồng lấp.")

    st.divider()

    # --- PHẦN 3 & 4: NÂNG CAO & THIẾT KẾ (40%) ---
    st.header("2️⃣ GIẢI PHÁP TRỰC QUAN HÓA NÂNG CAO")
    
    tab1, tab2 = st.tabs(["📌 Phương án 1: Heatmap", "📌 Phương án 2: Treemap (Triển khai & Đánh giá)"])

    with tab1:
        st.subheader("Heatmap: Lợi nhuận trung bình theo Vùng & Ngành hàng")
        heat_data = df_filtered.groupby(['Category', 'Region'])['Profit'].mean().reset_index()
        fig_heat = px.density_heatmap(heat_data, x='Region', y='Category', z='Profit', 
                                      color_continuous_scale='RdYlGn', text_auto='.1f', title="Profit Heatmap")
        st.plotly_chart(fig_heat, use_container_width=True)
        st.write("**Ưu điểm:** Nhận diện vùng thua lỗ cực nhanh qua màu sắc.")

    with tab2:
        st.subheader("Treemap: Phân cấp Cơ cấu Doanh thu & Lợi nhuận")
        
        # TỐI ƯU TREEMAP ĐỂ CHỮ RÕ HƠN
        fig_tree = px.treemap(
            df_filtered, 
            path=[px.Constant("Siêu thị"), 'Category', 'Sub-Category'], 
            values='Sales', 
            color='Profit', 
            color_continuous_scale='RdYlGn',
            title="Kích cỡ = Doanh thu | Màu sắc = Lợi nhuận (Click vào ô để phóng to)"
        )
        
        # Cấu hình font chữ và hiển thị nội dung ô
        fig_tree.update_traces(
            textinfo="label+value",
            textfont_size=15, 
            texttemplate="%{label}<br>$%{value:,.0f}",
            hovertemplate='<b>%{label}</b><br>Sales: $%{value:,.0f}<br>Profit: $%{color:,.0f}'
        )
        
        fig_tree.update_layout(margin=dict(t=50, l=10, r=10, b=10))
        
        st.plotly_chart(fig_tree, use_container_width=True)
        
        st.success("""
        **Đánh giá thiết kế (Phần 4):**
        - **Bố cục:** Sử dụng phân cấp Category lồng Sub-Category để tiết kiệm diện tích màn hình.
        - **Màu sắc:** Thang Đỏ - Xanh (Diverging) giúp nhận diện rủi ro 'Tables' lỗ ngay lập tức.
        - **Tương tác:** Tính năng 'Drill-down' (nhấn vào ô) giúp giải quyết vấn đề chữ nhỏ, người dùng có thể xem chi tiết từng cấp độ.
        """)

    st.sidebar.markdown("---")
