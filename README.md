# MCP Server - Quản lý Full Stack & Database

MCP Server toàn diện để quản lý website full stack và cơ sở dữ liệu MySQL, tích hợp thêm khả năng rà soát bảo mật.

## Tính năng chính

### 🗄️ Quản lý Database
- **db_query**: Thực thi câu lệnh SELECT và trả về kết quả
- **db_execute**: Thực thi INSERT, UPDATE, DELETE
- **db_get_tables**: Liệt kê tất cả các bảng trong database
- **db_get_table_schema**: Xem cấu trúc của một bảng
- **db_get_table_data**: Lấy dữ liệu từ bảng với giới hạn
- **db_backup_table**: Tạo file SQL backup cho bảng

### 📁 Quản lý File
- **file_read**: Đọc nội dung file
- **file_write**: Ghi hoặc cập nhật nội dung file
- **file_list**: Liệt kê file và thư mục
- **file_search**: Tìm kiếm pattern trong các file

### 🔍 Phân tích Web Stack
- **analyze_project_structure**: Phân tích cấu trúc dự án
- **analyze_php_files**: Phân tích các file PHP (functions, classes, dependencies)
- **analyze_dependencies**: Phân tích các dependency giữa các file
- **generate_api_docs**: Tạo tài liệu API từ code PHP
- **check_security**: Kiểm tra bảo mật cơ bản

## Cài đặt

### Bước 1: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 2: Cấu hình Database
Tạo file .env và cấu hình.

```python
# Database Configuration
DB_HOST=...
DB_USER=...
DB_PASSWORD=...
DB_NAME=...

# Workspace Configuration
WORKSPACE_ROOT=path/to/webroot
```

### Bước 3: Cấu hình trong Claude Desktop
Mở file cấu hình Claude Desktop và thêm:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "web-management-mcp": {
      "command": "path\\.venv\\Scripts\\python.exe",
      "args": [
        "path\\web-management\\web_management_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "path\\web-management"
      }
    }
}
```
Thay đổi *path*.
### Bước 4: Khởi động lại Claude Desktop

# Reference
ZilongXue - claude-post: https://github.com/ZilongXue/claude-post
RichardHan - mssql_mcp_server: https://github.com/RichardHan/mssql_mcp_server
GongRzhe - Gmail-MCP-Server: https://github.com/GongRzhe/Gmail-MCP-Server

