import streamlit as st
import pandas as pd
import plotly.express as px

# Tiêu đề chính
st.title("🚀 Supermarket Data Analysis Dashboard")
st.markdown("Đây là bài kiểm tra giữa kỳ của nhóm [Tên Nhóm]")

# Đọc dữ liệu
df = pd.read_csv("supermarket_data.csv")

# --- BIỂU ĐỒ LINE (PHẦN 2.1) ---
st.header("1. Xu hướng Doanh thu")
# Code vẽ biểu đồ line...
st.plotly_chart(fig_line)
st.info("**Insight:** Doanh thu đạt đỉnh vào tháng 12 do mùa mua sắm lễ hội. **Hạn chế:** Biểu đồ chưa thể hiện được biến động theo từng ngày.")

# --- BIỂU ĐỒ HEATMAP (PHẦN 4 - NÂNG CAO) ---
st.header("2. Phân tích Lợi nhuận (Advanced)")
# Code vẽ heatmap...
st.plotly_chart(fig_heat)
st.success("**Insight:** Vùng phía Tây có lợi nhuận ổn định nhất nhờ danh mục Technology.")
