# NL ERP System - Intelligent Logistics Management
NL ERP là giải pháp quản lý chuỗi cung ứng (All-in-one) được xây dựng hoàn toàn bằng **Python**. Dự án tập trung vào việc tự động hóa quy trình vận hành và áp dụng **Data Science** để hỗ trợ ra quyết định kinh doanh.

## Tính năng chính (Key Features)

### 1. Quản trị Kho hàng (Inventory Management)
* Theo dõi tồn kho thời gian thực (Real-time Tracking).
* Cảnh báo tự động khi hàng sắp hết hoặc tồn đọng.
* Hỗ trợ nhập liệu hàng loạt từ file Excel (Bulk Import).

### 2. Bán hàng & POS (Point of Sale)
* Tự động tính toán giá bán theo đa tiền tệ (VND, USD, CNY, EUR).
* Xuất hóa đơn PDF chuyên nghiệp, tự động xử lý lỗi font tiếng Việt.
* Cơ chế kiểm soát tồn kho chặt chẽ khi xuất hàng.

### 3. AI & Phân tích dữ liệu (Advanced Analytics)
* **Dự báo doanh thu:** Sử dụng Machine Learning (`Scikit-learn`) để dự đoán xu hướng bán hàng trong 7 ngày tới.
* **Smart Replenishment:** Tự động tính toán số lượng hàng cần nhập dựa trên sức mua thực tế.
* **Phân tích đa chiều:** Biểu đồ Sunburst cho danh mục, Phân tích ABC cho sản phẩm chủ lực.

### 4. Tối ưu hóa Vận chuyển (Transport Optimization)
* Tự động chuyển đổi địa chỉ đơn hàng thành tọa độ (Geocoding).
* Sử dụng thuật toán tìm đường tối ưu để vẽ lộ trình giao hàng ngắn nhất trên bản đồ (`Folium`).

### 5. Bảo mật & Quản trị
* Hệ thống đăng nhập phân quyền (Admin/Staff).
* Ghi nhật ký giao dịch (Audit Log) chi tiết.

## Công nghệ sử dụng (Tech Stack)
* Language: Python 3.9+
* Frontend: Streamlit, Streamlit-Option-Menu
* Backend/Database: SQLite3
* Data Analysis: Pandas, NumPy, Plotly
* AI/ML: Scikit-learn (Linear Regression)
* Logistics Utils: Geopy, Folium, FPDF

## Tác giả
* Email: linhbuingoc11@gmail.com
* LinkedIn: https://www.linkedin.com/in/linh-b%C3%B9i-ng%E1%BB%8Dc-538592395/