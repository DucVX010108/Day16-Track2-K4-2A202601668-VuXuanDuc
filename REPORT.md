**Báo cáo đánh giá hạ tầng & hiệu năng mô hình LightGBM trên GCP**
1. **Thời gian triển khai & Khởi tạo (Deployment & Bootstrap)**: Quá trình chạy terraform apply hạ tầng (VPC, Cloud NAT, Global Forwarding Rule) hoàn tất trong khoảng **4 phút 30 giây**, và mất thêm khoảng **2–3 phút** để kết nối SSH qua IAP cài đặt môi trường thư viện ML.

2. **Thời gian huấn luyện & Chất lượng mô hình****: Quá trình tải dữ liệu mất **1.83s**; thời gian huấn luyện mô hình LightGBM trên 2 vCPU của node e2-medium diễn ra nhanh chóng trong **2.12s**, đạt chỉ số phân tách **AUC-ROC = 0.9367**.

3. **Đánh giá Bỏ sót & Cảnh báo nhầm (Precision & Recall)**: Mô hình đạt **Recall = 0.8673** (bắt trúng ~86.7% các vụ gian lận, tỷ lệ bỏ sót thấp) và **Precision = 0.6250** (trong số các ca bị gắn cờ gian lận thì có 62.5% là chính xác, còn lại ~37.5% là cảnh báo nhầm ở mức chấp nhận được).

4. **Độ trễ đơn bản ghi & Thông lượng hàng loạt (Latency vs Throughput)**: Độ trễ suy luận cho từng giao dịch đơn lẻ (single-row) đạt **0.4366 ms/row** (phù hợp real-time scoring); khi chuyển sang xử lý hàng loạt 1,000 bản ghi, thông lượng (throughput) tăng vọt lên **1,484,787 QPS** nhờ tính năng vector hóa song song trên CPU.

5. **Đánh giá tải phần cứng (CPU & RAM Bottleneck)**: CPU và RAM không phải là bottleneck; lệnh top và free -h cho thấy CPU ở trạng thái nhàn rỗi (idle 100%) sau huấn luyện, RAM hệ thống chỉ dùng **~498 MiB / 3.8 GiB (~13%)** và còn dư hơn **3.3 GiB** bộ nhớ khả dụng.

6. **Thành phần đóng góp chi phí (Cost Drivers)**: Theo GCP Billing Reports, các dịch vụ đóng góp chi phí chính theo giờ gồm **Compute Engine (₫606)**, **Cloud NAT (₫539)** để kết nối ra Internet và **Cloud Load Balancing (₫395)**; toàn bộ chi phí thực tế (~1.903 VNĐ cho ~45 phút chạy) được bù trừ hoàn toàn bởi gói $300 Free Trial Credit.
