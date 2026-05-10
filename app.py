import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Cấu hình giao diện rộng để chứa được nhiều thông tin
st.set_page_config(page_title="Báo cáo Giữa kỳ - Phân tích Siêu thị", layout="wide")

# --- HÀM HỖ TRỢ ĐỌC DỮ LIỆU ---
@st.cache_data
def load_and_clean_data():
    file_path = "supermarket_data.csv"
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_csv(file_path)
    # Phần 1: Làm sạch dữ liệu
    df.columns = df.columns.str.strip()
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
    
    # Xử lý missing values
    for col in ['Sales', 'Profit']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].median())
    return df

df = load_and_clean_data()

# --- NỘI DUNG CHÍNH ---
if df is None:
    st.error("❌ Không tìm thấy file dữ liệu. Vui lòng kiểm tra lại GitHub.")
else:
    st.title("🚀 ĐỒ ÁN GIỮA KỲ: PHÂN TÍCH DỮ LIỆU SIÊU THỊ")
    st.sidebar.markdown("### Thành viên nhóm:\n1. [Tên 1]\n2. [Tên 2]\n3. [Tên 3]")

    # --- PHẦN 1: LÀM SẠCH VÀ HIỂU DỮ LIỆU (10%) ---
    with st.expander("📂 PHẦN 1: LÀM SẠCH VÀ HIỂU DỮ LIỆU", expanded=True):
        col_desc1, col_desc2 = st.columns(2)
        with col_desc1:
            st.write("**Mô tả dữ liệu:** Bộ dữ liệu gồm các giao dịch bán hàng, bao gồm thông tin khách hàng, sản phẩm và lợi nhuận.")
            st.write(f"- Tổng số dòng: {df.shape[0]}")
            st.write(f"- Các biến chính: `Order Date`, `Category`, `Region`, `Sales`, `Profit`, `Discount`.")
        with col_desc2:
            st.write("**Câu hỏi phân tích:**")
            st.write("1. Xu hướng doanh thu thay đổi thế nào theo tháng?")
            st.write("2. Vùng nào có lợi nhuận cao nhất?")
            st.write("3. Mối quan hệ giữa giảm giá và lợi nhuận thực tế?")

    # --- PHẦN 2: BỘ BIỂU ĐỒ CƠ BẢN BẮT BUỘC (40%) ---
    st.header("📊 PHẦN 2: BỘ BIỂU ĐỒ CƠ BẢN")
    
    # 1. Line Graph & 2. Pie Chart
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Line Graph: Xu hướng Doanh thu")
        line_df = df.copy()
        line_df['Month'] = line_df['Order Date'].dt.to_period('M').astype(str)
        line_data = line_df.groupby('Month')['Sales'].sum().reset_index()
        fig1 = px.line(line_data, x='Month', y='Sales', markers=True)
        st.plotly_chart(fig1, use_container_width=True)
        st.info("**Insight:** Doanh thu tăng trưởng mạnh vào các tháng cuối năm. \n\n **Hạn chế:** Chưa thể hiện được nguyên nhân cụ thể gây biến động.")

    with col2:
        st.subheader("2. Pie Chart: Tỷ trọng theo Phân khúc")
        fig2 = px.pie(df, values='Sales', names='Segment', hole=0.3)
        st.plotly_chart(fig2, use_container_width=True)
        st.info("**Insight:** Khách hàng cá nhân (Consumer) chiếm ưu thế tuyệt đối. \n\n **Hạn chế:** Khó so sánh nếu các phần có tỷ lệ gần bằng nhau.")

    # 3. Stacked Bar & 4. Scatter Plot
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("3. Stacked Bar: Doanh thu theo Vùng & Ngành hàng")
        fig3 = px.bar(df, x='Region', y='Sales', color='Category')
        st.plotly_chart(fig3, use_container_width=True)
        st.info("**Insight:** Vùng West dẫn đầu doanh thu ở mọi ngành hàng. \n\n **Hạn chế:** Khó xác định giá trị chính xác của các cột ở giữa.")

    with col4:
        st.subheader("4. Scatter Plot: Sales vs Profit")
        fig4 = px.scatter(df, x='Sales', y='Profit', color='Discount', size='Quantity')
        st.plotly_chart(fig4, use_container_width=True)
        st.info("**Insight:** Đơn hàng giảm giá cao (>20%) thường dẫn đến lỗ vốn. \n\n **Hạn chế:** Các điểm dữ liệu quá dày gây khó nhìn.")

    # --- PHẦN 3 & 4: NÂNG CAO (40%) ---
    st.markdown("---")
    st.header("🌟 PHẦN 3 & 4: TRỰC QUAN HÓA NÂNG CAO")
    
    st.subheader("Đề xuất 2 phương án nâng cao:")
    st.write("- **Phương án 1: Heatmap** (Để soi lợi nhuận theo vùng và danh mục).")
    st.write("- **Phương án 2: Treemap** (Để xem phân cấp sản phẩm).")

    # Triển khai phương án nâng cao chọn lọc (Phần 4)
    st.subheader("Thiết kế chi tiết Phương án: Treemap")
    fig_tree = px.treemap(df, path=[px.Constant("Siêu thị"), 'Category', 'Sub-Category'], 
                          values='Sales', color='Profit', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_tree, use_container_width=True)
    
    # Giải thích thiết kế theo yêu cầu Phần 4
    with st.expander("🎨 Giải thích thiết kế & Đánh giá (Phần 4)"):
        st.write("- **Bố cục:** Sử dụng sơ đồ cây để thể hiện cấu trúc phân cấp.")
        st.write("- **Màu sắc:** Thang màu Đỏ-Xanh (Diverging) để phân biệt lỗ/lãi.")
        st.write("- **Tương tác:** Cho phép click vào từng ô để xem chi tiết danh mục con.")
        st.write("- **So sánh:** Hiệu quả hơn biểu đồ cơ bản vì hiển thị được 3 chiều dữ liệu (Phân cấp, Doanh thu, Lợi nhuận) cùng lúc.")

    # --- PHẦN 5: THUYẾT TRÌNH ---
    st.sidebar.success("✅ App đã sẵn sàng cho buổi thuyết trình 10 phút!")
