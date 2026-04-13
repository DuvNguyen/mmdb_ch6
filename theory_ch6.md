# Chương 6: Chỉ mục nghịch đảo (Inverted Index)
## Xây dựng và Truy vấn văn bản

### 1. Bài toán chi tiết
Chỉ mục nghịch đảo (Inverted Index) là cấu trúc dữ liệu cốt lõi trong các hệ thống tìm kiếm thông tin (Information Retrieval). Thay vì tìm kiếm tuần tự từng file, ta xây dựng một bảng tra cứu từ **Từ (Term)** sang **Danh sách tài liệu (Posting List)** chứa từ đó.

Yêu cầu bài tập:
- Xây dựng chỉ mục từ một thư mục tài liệu.
- Chỉ lưu các từ bắt đầu bằng chữ 'C' (không phân biệt hoa thường).
- Thực hiện tìm kiếm Top-N tài liệu phù hợp nhất.

### 2. Các thành phần chính

#### a. DocTable
Lưu trữ danh sách các tài liệu trong hệ thống.
- **Key**: ID tài liệu (số nguyên).
- **Value**: Tên file tài liệu.

#### b. TermTable (Chỉ mục nghịch đảo)
Lưu trữ ánh xạ từ từ khóa đến các tài liệu chứa nó.
- **Key**: Từ khóa (Token) - Chỉ các từ bắt đầu bằng 'c'.
- **Value**: Một dictionary chứa `{doc_id: count}`, trong đó `count` là số lần từ xuất hiện trong tài liệu đó.

#### c. Hàm tìm kiếm
- **Find(Word, Weight, N)**: Tìm N tài liệu có trọng số (số lần xuất hiện * weight) cao nhất cho một từ.
- **Find(WordFile, N)**: Đọc danh sách nhiều từ từ một file và tìm N tài liệu khớp tốt nhất với toàn bộ tập từ khóa đó.

### 3. Quy trình thực hiện
1. **Tiền xử lý**: Đọc từng file trong thư mục, loại bỏ các từ trong `StopList`.
2. **Lọc nội dung**: Chỉ tách các từ bắt đầu bằng 'C'.
3. **Xây dựng chỉ mục**: Đếm tần suất xuất hiện và lưu vào `TermTable`.
4. **Truy vấn**: Sử dụng `TermTable` để tính điểm cho các tài liệu và sắp xếp lấy Top N.

### 4. Hướng dẫn chạy Demo
1. Mở thư mục `inverted_index`.
2. Chạy lệnh: `python main.py`.
3. Giao diện hiện ra cho phép:
   - Chọn thư mục tài liệu và file StopList.
   - Nhấn "Xây dựng chỉ mục" để tạo `DocTable` và `TermTable`.
   - Nhập từ khóa hoặc chọn WordFile để tìm kiếm tài liệu.
   - Xem danh sách Top-N kết quả trực quan.
