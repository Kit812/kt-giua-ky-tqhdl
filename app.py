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

    # SIDEBAR: DASHBOARD TƯƠNG TÁC
    st.sidebar.header("🕹️ Bộ lọc tùy chỉnh")
    regions = st.sidebar.multiselect("Chọn Khu vực:", options=df["Region"].unique(), default=df["Region"].unique())
    segments = st.sidebar.multiselect("Chọn Phân khúc khách hàng:", options=df["Segment"].unique(), default=df["Segment"].unique())

    # Lọc dữ liệu theo tương tác người dùng
    df_filtered = df[df["Region"].isin(regions) & df["Segment"].isin(segments)]

    # CHỈ SỐ TỔNG QUAN (KPIs)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Tổng Doanh thu", f"${df_filtered['Sales'].sum():,.0f}")
    kpi2.metric("Tổng Lợi nhuận", f"${df_filtered['Profit'].sum():,.0f}")
    kpi3.metric("Số lượng bán ra", f"{df_filtered['Quantity'].sum():,.0f}")
    kpi4.metric("Tỷ suất Lợi nhuận", f"{(df_filtered['Profit'].sum()/df_filtered['Sales'].sum()*100):.1f}%")

    st.divider()

    # --- PHẦN 1: HỆ THỐNG BIỂU ĐỒ CƠ BẢN ---
    st.header("1️⃣ HỆ THỐNG BIỂU ĐỒ CƠ BẢN")
    
    col1, col2 = st.columns(2)

    with col1:
        # 2.1 Biểu đồ đường (Line Graph)
        st.subheader("2.1 Biểu đồ đường: Top 10 Bang doanh thu cao nhất")
        state_sales = df_filtered.groupby("State")["Sales"].sum().reset_index().sort_values("Sales", ascending=False).head(10)
        fig1 = px.line(state_sales, x="State", y="Sales", markers=True, 
                       title="Top 10 Bang theo Doanh thu",
                       labels={"State": "Bang", "Sales": "Doanh thu ($)"})
        st.plotly_chart(fig1, use_container_width=True)
        st.info("**Nhận xét:** California dẫn đầu thị trường. **Hạn chế:** Chỉ quan sát được nhóm đầu bảng.")

        # 2.2 Biểu đồ tròn (Pie Chart)
        st.subheader("2.2 Biểu đồ tròn: Tỷ trọng Doanh thu theo Phân khúc")
        fig2 = px.pie(df_filtered, values='Sales', names='Segment', hole=0.4, 
                      title="Phân bổ Doanh thu theo Khách hàng",
                      labels={"Segment": "Phân khúc", "Sales": "Doanh thu"})
        st.plotly_chart(fig2, use_container_width=True)
        st.info("**Nhận xét:** Nhóm Consumer (Cá nhân) chiếm tỷ trọng lớn nhất. **Hạn chế:** Khó so sánh chính xác sự chênh lệch nhỏ.")

    with col2:
        # 2.3 Biểu đồ cột chồng (Stacked Bar Chart)
        st.subheader("2.3 Biểu đồ cột: Doanh thu theo Vùng & Ngành hàng")
        fig3 = px.bar(df_filtered, x='Region', y='Sales', color='Category', 
                      title="Doanh thu các Vùng theo Danh mục",
                      labels={"Region": "Khu vực", "Sales": "Doanh thu ($)", "Category": "Ngành hàng"})
        st.plotly_chart(fig3, use_container_width=True)
        st.info("**Nhận xét:** Khu vực phía Tây (West) có doanh số Công nghệ vượt trội. **Hạn chế:** Khó đọc giá trị chi tiết của các phần ở giữa cột.")

        # 2.4 Biểu đồ phân tán (Scatter Plot)
        st.subheader("2.4 Biểu đồ phân tán: Doanh thu vs Lợi nhuận")
        fig4 = px.scatter(df_filtered, x='Sales', y='Profit', color='Category', size='Discount', 
                          hover_data=['Sub-Category'],
                          title="Tương quan Doanh thu - Lợi nhuận và Chiết khấu",
                          labels={"Sales": "Doanh thu", "Profit": "Lợi nhuận", "Category": "Ngành hàng", "Discount": "Chiết khấu"})
        st.plotly_chart(fig4, use_container_width=True)
        st.info("**Nhận xét:** Chiết khấu cao (kích thước điểm lớn) thường gây lỗ nặng. **Hạn chế:** Dữ liệu bị chồng lấp khi quá nhiều đơn hàng.")

    st.divider()

    # --- PHẦN 2: GIẢI PHÁP NÂNG CAO ---
    st.header("2️⃣ GIẢI PHÁP TRỰC QUAN HÓA NÂNG CAO")
    
    tab1, tab2 = st.tabs(["📌 Phương án 1: Biểu đồ nhiệt (Heatmap)", "📌 Phương án 2: Treemap (Cây phân cấp)"])

    with tab1:
        st.subheader("Biểu đồ nhiệt: Lợi nhuận trung bình theo Vùng & Ngành hàng")
        heat_data = df_filtered.groupby(['Category', 'Region'])['Profit'].mean().reset_index()
        fig_heat = px.density_heatmap(heat_data, x='Region', y='Category', z='Profit', 
                                      color_continuous_scale='RdYlGn', text_auto='.1f',
                                      title="Bản đồ nhiệt Lợi nhuận",
                                      labels={"Region": "Vùng", "Category": "Ngành hàng", "Profit": "LN Trung bình"})
        st.plotly_chart(fig_heat, use_container_width=True)
        st.write("**Ưu điểm:** Giúp bộ phận quản lý nhận diện ngay lập tức các vùng/ngành hàng đang thua lỗ qua màu đỏ.")

    with tab2:
        st.subheader("Biểu đồ Treemap: Cơ cấu Doanh thu & Lợi nhuận đa tầng")
        
        fig_tree = px.treemap(
            df_filtered, 
            path=[px.Constant("Tất cả Sản phẩm"), 'Category', 'Sub-Category'], 
            values='Sales', 
            color='Profit', 
            color_continuous_scale='RdYlGn',
            title="Kích thước ô = Doanh thu | Màu sắc = Lợi nhuận (Nhấn vào ô để xem chi tiết)"
        )
        
        # Cấu hình tiếng Việt cho nội dung hiển thị trong ô
        fig_tree.update_traces(
            textinfo="label+value",
            textfont_size=15, 
            texttemplate="%{label}<br>Doanh thu: $%{value:,.0f}",
            hovertemplate='<b>%{label}</b><br>Doanh thu: $%{value:,.0f}<br>Lợi nhuận: $%{color:,.0f}'
        )
        
        fig_tree.update_layout(margin=dict(t=50, l=10, r=10, b=10))
        st.plotly_chart(fig_tree, use_container_width=True)
        
        st.success("""
        **Phân tích thiết kế chuyên sâu:**
        - **Cấu trúc:** Sử dụng phân cấp Ngành hàng -> Nhóm hàng giúp tối ưu không gian hiển thị.
        - **Màu sắc:** Sử dụng thang màu Đỏ - Xanh giúp phát hiện nhóm hàng 'Bàn' (Tables) đang lỗ vốn cực nhanh.
        - **Tính tương tác:** Tính năng 'Drill-down' cho phép người dùng đào sâu vào từng ngách nhỏ mà không bị rối mắt.
        """)

    st.sidebar.markdown("---")
