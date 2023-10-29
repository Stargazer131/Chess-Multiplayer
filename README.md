# Chủ đề
Ứng dụng chơi cờ vua - Chess.io

# Thông tin nhóm
1. Vũ Ngọc Hảo - B20DCCN228
2. Nguyễn Xuân Hưng - B20DCCN344
3. Nguyễn Văn Đức - B20DCCN199

# Công nghệ sử dụng/ Ngôn ngữ
1. Python
2. TCP Socket
3. Multi Threading

# Mô tả
### Kiến trúc
+ Client - Server
### Giao tiếp
+ Lần đầu kết nối: client gửi thông điệp (người chơi hoặc người xem) đến server
+ Server gửi lại client id
+ Nếu là người chơi:
  + Client tiến vào hàng đợi
  + Serer ghép cặp 2 người chơi, server gửi thông báo sẵn sàng đến 2 client
  + Client thực hiện xong một bước đi -> gửi dữ liệu đến server
  + Server -> gửi dữ liệu đến client còn lại
  + Liên tục cho đến khi: có người thoát hoặc kết thúc game
  + Đóng kết nối
+ Nếu là người xem:
  + Server gửi đến client danh sách các phòng (bất cứ khi nào yêu cầu)
  + Server đợi Client gửi mã game
  + Client gửi mã game đến Server
  + Server nhận mã game và liên tục gửi dữ liệu game đến Client
  + Kết thúc khi: Client tự thoát hoặc game kết thúc -> Server tiếp tục đợi Client gửi mã game
  + Đóng kết nối: khi client thoát khỏi giao diện chọn game để xem
### Thư viện xử lý
1. Socket - truyền dữ liệu
2. Pickle - mã hóa dữ liệu gửi và giải mã dữ liệu nhận
3. Threading - đa luồng xử lý đồng thời
4. Pygame - hiển thị game
5. Python-Chess - xử lý logic game
6. Tkinter - hiển thị giao diện
### Chức năng chính
1. Chơi game cờ vua - 2 người
2. Xem game cờ vua - đang chơi
3. Xem replay (đang phát triển)

# Preview giao diện
### Màn hình chính
![Screenshot 2023-10-29 212754.png](demo_img%2FScreenshot%202023-10-29%20212754.png)
### Đợi người khác
![Screenshot 2023-10-29 212810.png](demo_img%2FScreenshot%202023-10-29%20212810.png)
### Đang chơi
![Screenshot 2023-10-29 212904.png](demo_img%2FScreenshot%202023-10-29%20212904.png)
### Kết thúc
![Screenshot 2023-10-29 213249.png](demo_img%2FScreenshot%202023-10-29%20213249.png)
### Danh sách phòng
![Screenshot 2023-10-29 213009.png](demo_img%2FScreenshot%202023-10-29%20213009.png)
### Xem game
![Screenshot 2023-10-29 213122.png](demo_img%2FScreenshot%202023-10-29%20213122.png)