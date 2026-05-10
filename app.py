import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Supermarket Analysis Dashboard", layout="wide")

# --- HÀM ĐỌC DỮ LIỆU ---
@st.cache_data
def load_data():
    # Kiểm tra file có tồn tại không để tránh lỗi FileNotFoundError
    file_name = "SampleSuperstore.csv"
    if not os.path.exists(file_name):
        st.error(f"Không tìm thấy file {file_name}. Hãy đảm bảo bạn đã upload file lên GitHub cùng thư mục với app.py")
        return None
    
    df = pd.read_csv(file_name)
    # Chuyển đổi ngày tháng
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
    # Xử lý dữ liệu thiếu (Phần 1)
    if 'Sales' in df.columns:
        df['Sales'] = df['Sales'].fillna(df['Sales'].median())
    if 'Profit' in df.columns:
        df['Profit'] = df['Profit'].fillna(df['Profit'].median())
    return df

df = load_data()

if df is not None:
    # --- SIDEBAR (TƯƠNG TÁC) ---
    st.sidebar.header("Bộ lọc tìm kiếm")
    region = st.sidebar.multiselect("Chọn Vùng:", options=df["Region"].unique(), default=df["Region"].unique())
    category = st.sidebar.multiselect("Chọn Danh mục:", options=df["Category"].unique(), default=df["Category"].unique())

    # Lọc dữ liệu theo sidebar
    df_selection = df.query("Region == @region & Category == @category")

    # --- TIÊU ĐỀ ---
    st.title("📊 Báo cáo Phân tích Dữ liệu Siêu thị")
    st.markdown("## Bài kiểm tra giữa kỳ - Nhóm: [Tên nhóm của bạn]")
    
    # Chỉ số KPI nhanh
    total_sales = df_selection['Sales'].sum()
    total_profit = df_selection['Profit'].sum()
    st.columns(2)[0].metric("Tổng Doanh thu", f"${total_sales:,.2f}")
    st.columns(2)[1].metric("Tổng Lợi nhuận", f"${total_profit:,.2f}")
    
    st.divider()

    # --- PHẦN 2: BIỂU ĐỒ CƠ BẢN (40%) ---
    st.header("I. Bộ biểu đồ cơ bản")
    
    col1, col2 = st.columns(2)

    with col1:
        # 1. Line Graph (Xu hướng)
        st.subheader("1. Xu hướng doanh thu theo tháng")
        df_line = df_selection.set_index('Order Date').resample('M')['Sales'].sum().reset_index()
        fig1 = px.line(df_line, x='Order Date', y='Sales', markers=True, title="Doanh thu theo thời gian")
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("**Insight:** Theo dõi các điểm đỉnh doanh thu vào cuối năm. **Hạn chế:** Chưa thể hiện được yếu tố mùa vụ chi tiết theo ngày.")

        # 2. Pie Chart (Tỷ trọng)
        st.subheader("2. Tỷ trọng doanh thu theo Phân khúc")
        fig2 = px.pie(df_selection, values='Sales', names='Segment', hole=0.3, title="Doanh thu theo Segment")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("**Insight:** Khách hàng lẻ (Consumer) chiếm tỷ trọng lớn nhất. **Hạn chế:** Khó so sánh nếu có quá nhiều phân khúc nhỏ.")

    with col2:
        # 3. Stacked Column Chart
        st.subheader("3. Doanh thu theo Vùng và Danh mục")
        fig3 = px.bar(df_selection, x='Region', y='Sales', color='Category', title="Doanh thu chồng theo Region")
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("**Insight:** Vùng West thường dẫn đầu về doanh thu Technology. **Hạn chế:** Các cột chồng khó so sánh giá trị tuyệt đối của nhóm nằm giữa.")

        # 4. Scatter Plot (Mối quan hệ)
        st.subheader("4. Mối quan hệ Doanh thu vs Lợi nhuận")
        fig4 = px.scatter(df_selection, x='Sales', y='Profit', color='Discount', hover_data=['Sub-Category'], title="Sales vs Profit")
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("**Insight:** Chiết khấu cao (Discount > 0.2) thường gây lỗ vốn. **Hạn chế:** Các điểm dữ liệu dễ bị chồng lấp khi dữ liệu lớn.")

    st.divider()

    # --- PHẦN 3 & 4: PHƯƠNG ÁN NÂNG CAO (40%) ---
    st.header("II. Trực quan hóa nâng cao (Đề xuất & Thiết kế)")
    
    tab1, tab2 = st.tabs(["Phương án 1: Heatmap", "Phương án 2: Treemap (Lựa chọn thiết kế)"])

    with tab1:
        st.subheader("Bản đồ nhiệt Lợi nhuận trung bình")
        pivot_df = df_selection.pivot_table(index='Category', columns='Region', values='Profit', aggfunc='mean')
        fig_heat, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(pivot_df, annot=True, cmap="RdYlGn", fmt=".1f", ax=ax)
        st.pyplot(fig_heat)
        st.write("**Ưu điểm:** Nhận diện nhanh các vùng kinh doanh không hiệu quả (màu đỏ).")

    with tab2:
        st.subheader("Cơ cấu danh mục sản phẩm (Treemap)")
        # Đây là phương án nâng cao chọn để đánh giá
        fig_tree = px.treemap(df_selection, path=[px.Constant("Tất cả"), 'Category', 'Sub-Category'], 
                              values='Sales', color='Profit',
                              color_continuous_scale='RdYlGn',
                              title="Treemap: Doanh thu & Lợi nhuận theo Phân cấp")
        st.plotly_chart(fig_tree, use_container_width=True)
        
        st.info("""
        **Đánh giá thiết kế (Phần 4):**
        - **Bố cục:** Sử dụng không gian hình chữ nhật để thể hiện phân cấp từ Category xuống Sub-Category.
        - **Màu sắc:** Thang màu Đỏ - Vàng - Xanh thể hiện trực quan mức độ sinh lời (Profit).
        - **Tương tác:** Người dùng có thể nhấn vào từng ô để 'Drill-down' xem chi tiết.
        - **So sánh:** Hiệu quả hơn biểu đồ tròn khi muốn xem nhiều cấp độ sản phẩm cùng lúc.
        """)

else:
    st.warning("Vui lòng kiểm tra lại file dữ liệu trên GitHub của bạn.")
