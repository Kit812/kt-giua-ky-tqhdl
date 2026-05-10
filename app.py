import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Supermarket Analysis Dashboard", layout="wide")

# --- HÀM ĐỌC DỮ LIỆU (Tối ưu tránh lỗi FileNotFoundError) ---
@st.cache_data
def load_data():
    # Danh sách các tên file có khả năng xảy ra (phòng trường hợp viết hoa/thường)
    possible_names = ["SampleSuperstore.csv", "Supermarket_Data.csv", "supermarket_data.CSV"]
    df = None
    
    for name in possible_names:
        if os.path.exists(name):
            df = pd.read_csv(name)
            break
            
    if df is None:
        return None

    # LÀM SẠCH DỮ LIỆU (Phần 1)
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # Xử lý dữ liệu thiếu: Điền giá trị trung vị cho Sales và Profit
    if 'Sales' in df.columns:
        df['Sales'] = df['Sales'].fillna(df['Sales'].median())
    if 'Profit' in df.columns:
        df['Profit'] = df['Profit'].fillna(df['Profit'].median())
        
    return df

# Chạy hàm load dữ liệu
df = load_data()

# --- GIAO DIỆN CHÍNH ---
if df is None:
    st.error("❌ KHÔNG TÌM THẤY FILE DỮ LIỆU!")
    st.markdown("""
    **Cách sửa lỗi:**
    1. Kiểm tra file trên GitHub có đúng tên là `supermarket_data.csv` không.
    2. Đảm bảo file nằm cùng thư mục với file `app.py` (không nằm trong folder con).
    """)
else:
    # --- SIDEBAR (PHẦN TƯƠNG TÁC) ---
    st.sidebar.header("🔍 Bộ lọc dữ liệu")
    region = st.sidebar.multiselect("Chọn Vùng (Region):", options=df["Region"].unique(), default=df["Region"].unique())
    segment = st.sidebar.multiselect("Chọn Phân khúc (Segment):", options=df["Segment"].unique(), default=df["Segment"].unique())

    # Lọc dữ liệu theo lựa chọn
    mask = df["Region"].isin(region) & df["Segment"].isin(segment)
    df_sub = df[mask]

    # --- TIÊU ĐỀ BÀI GIỮA KỲ ---
    st.title("📊 Báo cáo Phân tích Siêu thị")
    st.info("Bài kiểm tra giữa kỳ - Nhóm thực hiện: [Tên nhóm của bạn]")

    # Chỉ số chính (KPIs)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Tổng Doanh thu", f"${df_sub['Sales'].sum():,.0f}")
    kpi2.metric("Tổng Lợi nhuận", f"${df_sub['Profit'].sum():,.0f}")
    kpi3.metric("Số đơn hàng", len(df_sub))

    st.divider()

    # --- PHẦN 2: BIỂU ĐỒ CƠ BẢN (40%) ---
    st.header("I. Bộ biểu đồ cơ bản")
    
    c1, c2 = st.columns(2)

    with c1:
        # 1. Line Graph
        st.subheader("1. Xu hướng doanh thu")
        line_df = df_sub.groupby(df_sub['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
        line_df['Order Date'] = line_df['Order Date'].astype(str)
        fig1 = px.line(line_df, x='Order Date', y='Sales', title="Doanh thu theo tháng", markers=True)
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("**Insight:** Doanh thu biến động theo mùa. **Hạn chế:** Chưa lọc được theo từng ngày cụ thể.")

        # 2. Pie Chart
        st.subheader("2. Tỷ trọng doanh thu theo Category")
        fig2 = px.pie(df_sub, values='Sales', names='Category', hole=0.4, title="Cơ cấu ngành hàng")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("**Insight:** Office Supplies thường chiếm số lượng đơn cao nhất. **Hạn chế:** Khó nhìn nếu có quá nhiều nhóm.")

    with c2:
        # 3. Stacked Bar Chart
        st.subheader("3. Lợi nhuận theo Vùng & Phân khúc")
        fig3 = px.bar(df_sub, x='Region', y='Profit', color='Segment', title="Lợi nhuận theo vùng (Chồng)")
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("**Insight:** Vùng West đóng góp lợi nhuận ổn định nhất. **Hạn chế:** Các cột chồng khó so sánh giá trị lẻ.")

        # 4. Scatter Plot
        st.subheader("4. Tương quan Sales & Profit")
        fig4 = px.scatter(df_sub, x='Sales', y='Profit', color='Category', size='Quantity', title="Sales vs Profit")
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("**Insight:** Đơn hàng lớn không phải lúc nào cũng lãi cao. **Hạn chế:** Dữ liệu quá dày gây rối mắt.")

    st.divider()

    # --- PHẦN 3 & 4: NÂNG CAO (40%) ---
    st.header("II. Giải pháp trực quan hóa nâng cao")
    
    tab1, tab2 = st.tabs(["Phương án 1: Heatmap", "Phương án 2: Treemap (Lựa chọn)"])

    with tab1:
        st.subheader("Heatmap: Hiệu quả lợi nhuận trung bình")
        pivot_heat = df_sub.pivot_table(index='Category', columns='Region', values='Profit', aggfunc='mean')
        fig_h, ax = plt.subplots()
        sns.heatmap(pivot_heat, annot=True, cmap="YlGnBu", ax=ax)
        st.pyplot(fig_h)
        st.write("**Lý do:** Giúp soi chiếu nhanh vùng nào đang kinh doanh lỗ/lãi theo loại hàng.")

    with tab2:
        st.subheader("Treemap: Phân cấp doanh thu chi tiết")
        fig_tree = px.treemap(df_sub, path=['Category', 'Sub-Category'], values='Sales',
                              color='Profit', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_tree, use_container_width=True)
        
        st.success("""
        **Đánh giá thiết kế (Phần 4):**
        - **Bố cục:** Tận dụng diện tích màn hình để so sánh quy mô (size) và hiệu quả (màu sắc).
        - **Màu sắc:** Thang Đỏ-Xanh giúp nhận diện nhanh mặt hàng thua lỗ (màu đỏ).
        - **Tương tác:** Cho phép nhấn vào từng nhóm để xem chi tiết bên trong (Drill-down).
        """)

    st.balloons()
