import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Cấu hình Dashboard
st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide")

# --- HÀM LOAD DỮ LIỆU ---
@st.cache_data
def load_data():
    file_name = "SampleSuperstore.csv"  # Đã đổi tên theo yêu cầu của bạn
    if not os.path.exists(file_name):
        return None
    
    # Đọc dữ liệu
    df = pd.read_csv(file_name, encoding='windows-1252') # Thêm encoding phổ biến cho file này
    
    # PHẦN 1: LÀM SẠCH DỮ LIỆU
    df.columns = df.columns.str.strip() # Xóa khoảng trắng tên cột
    
    # Chuyển đổi ngày tháng nếu có (Bộ Superstore thường có Order Date)
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # Xử lý dữ liệu thiếu/sai
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
    df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce').fillna(0)
    
    return df

df = load_data()

if df is None:
    st.error("❌ Không tìm thấy file 'SampleSuperstore.csv'. Vui lòng kiểm tra lại tên file trên GitHub!")
else:
    # --- GIAO DIỆN DASHBOARD ---
    st.title("🏬 SUPERSTORE ANALYTICS DASHBOARD")
    st.markdown("### BÀI KIỂM TRA GIỮA KỲ - PHÂN TÍCH VÀ TRỰC QUAN HÓA")

    # SIDEBAR TƯƠNG TÁC
    st.sidebar.header("🕹️ Bộ lọc Dashboard")
    region = st.sidebar.multiselect("Chọn Vùng (Region):", options=df["Region"].unique(), default=df["Region"].unique())
    category = st.sidebar.multiselect("Chọn Danh mục (Category):", options=df["Category"].unique(), default=df["Category"].unique())

    # Lọc dữ liệu
    df_filtered = df[df["Region"].isin(region) & df["Category"].isin(category)]

    # CHỈ SỐ TỔNG QUAN (KPIs)
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    col_kpi1.metric("Tổng Doanh thu", f"${df_filtered['Sales'].sum():,.0f}")
    col_kpi2.metric("Tổng Lợi nhuận", f"${df_filtered['Profit'].sum():,.0f}")
    col_kpi3.metric("Số lượng đã bán", f"{df_filtered['Quantity'].sum():,.0f}")
    col_kpi4.metric("Tỷ lệ lợi nhuận", f"{(df_filtered['Profit'].sum()/df_filtered['Sales'].sum()*100):.1f}%")

    st.divider()

    # --- PHẦN 2: 4 BIỂU ĐỒ CƠ BẢN BẮT BUỘC (40%) ---
    st.header("1️⃣ BỘ BIỂU ĐỒ CƠ BẢN")
    
    row1_1, row1_2 = st.columns(2)
    with row1_1:
        st.subheader("Line Graph: Doanh thu theo Bang (State)")
        state_sales = df_filtered.groupby("State")["Sales"].sum().reset_index().sort_values("Sales", ascending=False).head(10)
        fig1 = px.line(state_sales, x="State", y="Sales", markers=True, title="Top 10 Bang có doanh thu cao nhất")
        st.plotly_chart(fig1, use_container_width=True)
        st.info("**Insight:** California và New York là thị trường trọng điểm. **Hạn chế:** Chỉ xem được top đầu, chưa thấy được sự phân bổ toàn quốc.")

    with row1_2:
        st.subheader("Pie Chart: Tỷ trọng Doanh thu theo Phân khúc")
        fig2 = px.pie(df_filtered, values='Sales', names='Segment', title="Cơ cấu khách hàng", hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
        st.info("**Insight:** Phân khúc Consumer chiếm hơn 50%. **Hạn chế:** Không thể hiện được giá trị lợi nhuận đi kèm.")

    row2_1, row2_2 = st.columns(2)
    with row2_1:
        st.subheader("Stacked Bar: Doanh thu theo Vùng & Ngành hàng")
        fig3 = px.bar(df_filtered, x='Region', y='Sales', color='Category', title="Doanh thu chồng")
        st.plotly_chart(fig3, use_container_width=True)
        st.info("**Insight:** Technology đóng góp giá trị cao nhất tại phía Tây. **Hạn chế:** Khó so sánh chính xác các phần ở giữa cột.")

    with row2_2:
        st.subheader("Scatter Plot: Sales vs Profit")
        fig4 = px.scatter(df_filtered, x='Sales', y='Profit', color='Category', size='Discount', hover_data=['Sub-Category'])
        st.plotly_chart(fig4, use_container_width=True)
        st.info("**Insight:** Nhiều đơn hàng doanh thu cao nhưng lỗ do Discount quá lớn. **Hạn chế:** Dữ liệu bị chồng lấp tại các điểm giá trị thấp.")

    st.divider()

    # --- PHẦN 3 & 4: PHƯƠNG ÁN NÂNG CAO (40%) ---
    st.header("2️⃣ TRỰC QUAN HÓA NÂNG CAO")
    
    tab_adv1, tab_adv2 = st.tabs(["Heatmap (Đề xuất)", "Treemap (Triển khai & Đánh giá)"])

    with tab_adv1:
        st.subheader("Heatmap: Lợi nhuận trung bình theo Sub-Category & Region")
        pivot_heat = df_filtered.pivot_table(index='Sub-Category', columns='Region', values='Profit', aggfunc='mean')
        fig_h, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot_heat, annot=True, cmap="RdYlGn", fmt=".1f", ax=ax)
        st.pyplot(fig_h)
        st.write("**Câu hỏi phân tích:** Những mặt hàng nào đang gây lỗ ở vùng cụ thể?")
        st.write("**Ưu điểm:** Nhận diện vùng đỏ (lỗ) ngay lập tức mà biểu đồ cột không làm được.")

    with tab_adv2:
    st.subheader("Treemap: Phân cấp Cơ cấu Doanh thu & Lợi nhuận")
    
    # SỬA ĐỔI: Sử dụng maxdepth để tránh hiển thị quá nhiều chữ cùng lúc
    fig_tree = px.treemap(
        df_filtered, 
        path=[px.Constant("Tất cả"), 'Category', 'Sub-Category'], # Thêm gốc để dễ nhìn
        values='Sales', 
        color='Profit', 
        color_continuous_scale='RdYlGn',
        title="Toàn cảnh Sản phẩm: Kích cỡ = Doanh thu, Màu sắc = Lợi nhuận"
    )

    # TỐI ƯU HIỂN THỊ CHỮ (LAYOUT)
    fig_tree.update_traces(
        textinfo="label+value",             # Chỉ hiện tên và giá trị (giảm tải chữ)
        hoverinfo="label+value+percent parent",
        textfont_size=14,                   # Tăng kích thước font chữ cơ bản
        insidetextfont_size=12,             # Tăng kích thước font chữ bên trong ô
        texttemplate="%{label}<br>$%{value:,.0f}" # Định dạng chữ hiển thị rõ ràng hơn
    )

    # CẤU HÌNH ĐỂ CHỮ TỰ ĐỘNG CĂN CHỈNH TỐT HƠN
    fig_tree.update_layout(
        margin=dict(t=50, l=25, r=25, b=25), # Nới rộng lề
        font=dict(size=14)
    )

    st.plotly_chart(fig_tree, use_container_width=True)
        
        # Phần đánh giá thiết kế
        st.success("""
        **Phân tích Quyết định Thiết kế (Phần 4):**
        - **Bố cục:** Sử dụng diện tích để thể hiện quy mô doanh thu, giúp so sánh nhanh các ngành hàng.
        - **Màu sắc:** Thang màu xanh (lãi) - đỏ (lỗ) giúp quản lý tập trung vào các nhóm sản phẩm yếu kém (như Tables).
        - **Tương tác:** Cho phép người dùng click vào từng Category để xem chi tiết bên trong.
        - **Đánh giá:** So với biểu đồ cơ bản, Treemap hiển thị được 3 chiều dữ liệu đồng thời, giúp tiết kiệm không gian Dashboard.
        """)

    st.sidebar.markdown("---")
    st.sidebar.info("Phần 5: Sẵn sàng thuyết trình trong 10 phút.")
