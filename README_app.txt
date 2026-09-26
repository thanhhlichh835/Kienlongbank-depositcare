KIENLONGBANK DEPOSITCARE - APP MỚI

Đặt các file sau cùng một thư mục:
- app.py
- requirements.txt
- du_lieu_cap_CIF_ket_qua.xlsx
- du_lieu_tai_khoan_chi_tiet.xlsx
- logo_KienlongBank.png (không bắt buộc)

Chạy local:
pip install -r requirements.txt
streamlit run app.py

Chức năng:
- Tra cứu khách hàng theo Mã CIF.
- Hiển thị nhóm K-Means K=4 từ file kết quả CIF.
- Hiển thị KPI tiền gửi còn hiệu lực.
- Biểu đồ số dư theo kỳ hạn và từng tài khoản.
- Theo dõi đáo hạn động theo ngày hiện tại với mốc 7/15/30 ngày.
- Xuất danh sách Excel.
