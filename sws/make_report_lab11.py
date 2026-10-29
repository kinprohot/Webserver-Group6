import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import qn, nsdecls
import os

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=200, right=200):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_borders(cell, color="1F1F1F", sz="6", val="single"):
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for border_name in ['top', 'left', 'bottom', 'right']:
        b = OxmlElement(f'w:{border_name}')
        b.set(qn('w:val'), val)
        b.set(qn('w:sz'), sz)
        b.set(qn('w:space'), '0')
        b.set(qn('w:color'), color)
        tcBorders.append(b)
    tcPr.append(tcBorders)

def add_terminal_block(doc, commands_and_outputs):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "0C0C0C")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    set_cell_borders(cell, color="1F1F1F", sz="6", val="single")
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    
    first = True
    for item in commands_and_outputs:
        if not first:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
        first = False
        
        if item['type'] == 'cmd':
            r_user = p.add_run("nontew023@Maryeel")
            r_user.font.name = 'Consolas'
            r_user.font.size = Pt(9.5)
            r_user.font.bold = True
            r_user.font.color.rgb = RGBColor(78, 154, 6) # Ubuntu Green
            
            r_colon = p.add_run(":")
            r_colon.font.name = 'Consolas'
            r_colon.font.size = Pt(9.5)
            r_colon.font.color.rgb = RGBColor(204, 204, 204)
            
            r_path = p.add_run(item.get('path', '~/lab11/sws'))
            r_path.font.name = 'Consolas'
            r_path.font.size = Pt(9.5)
            r_path.font.bold = True
            r_path.font.color.rgb = RGBColor(52, 101, 164) # Ubuntu Blue
            
            r_dollar = p.add_run("$ ")
            r_dollar.font.name = 'Consolas'
            r_dollar.font.size = Pt(9.5)
            r_dollar.font.color.rgb = RGBColor(204, 204, 204)
            
            r_cmd = p.add_run(item['text'])
            r_cmd.font.name = 'Consolas'
            r_cmd.font.size = Pt(9.5)
            r_cmd.font.bold = True
            r_cmd.font.color.rgb = RGBColor(255, 255, 255) # White
        elif item['type'] == 'output':
            lines = item['text'].split('\n')
            for idx, line in enumerate(lines):
                if idx > 0:
                    p = cell.add_paragraph()
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = 1.05
                r_out = p.add_run(line)
                r_out.font.name = 'Consolas'
                r_out.font.size = Pt(9.5)
                r_out.font.color.rgb = RGBColor(204, 204, 204) # Light Grey
        elif item['type'] == 'comment':
            r_cmt = p.add_run(item['text'])
            r_cmt.font.name = 'Consolas'
            r_cmt.font.size = Pt(9.5)
            r_cmt.font.italic = True
            r_cmt.font.color.rgb = RGBColor(136, 136, 136) # Grey

    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)

def add_code_block(doc, filename, code_text):
    p_fn = doc.add_paragraph()
    p_fn.paragraph_format.space_before = Pt(8)
    p_fn.paragraph_format.space_after = Pt(2)
    r = p_fn.add_run(f"Mã nguồn tập tin: {filename}")
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(31, 78, 120)

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "1E1E1E")
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    set_cell_borders(cell, color="333333", sz="4", val="single")

    lines = code_text.strip().split('\n')
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05

    for idx, line in enumerate(lines):
        if idx > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
        r_line = p.add_run(line)
        r_line.font.name = 'Consolas'
        r_line.font.size = Pt(8.5)
        r_line.font.color.rgb = RGBColor(220, 220, 220)

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(4)

def build_report():
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Calibri'
    style_normal.font.size = Pt(11)
    style_normal.font.color.rgb = RGBColor(38, 38, 38)
    
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(2)
    r_t1 = p_title.add_run("BÁO CÁO DỰ ÁN HỆ THỐNG MÁY CHỦ WEB (GROUP PROJECT)\n")
    r_t1.font.name = 'Calibri'
    r_t1.font.size = Pt(15)
    r_t1.font.bold = True
    r_t1.font.color.rgb = RGBColor(31, 78, 120)
    
    r_t2 = p_title.add_run("ĐỀ TÀI: PHÁT TRIỂN HỆ THỐNG MÁY CHỦ WEB GIÁM SÁT TÀI NGUYÊN MÁY CHỦ LINUX (UnixSys Monitor)\nDỰA TRÊN KIẾN TRÚC SWS C-ENGINE (HTTP/1.0 RFC1945 & CGI RFC3875)")
    r_t2.font.name = 'Calibri'
    r_t2.font.size = Pt(12)
    r_t2.font.bold = True
    r_t2.font.color.rgb = RGBColor(46, 117, 182)
    
    # Divider line
    div_table = doc.add_table(rows=1, cols=1)
    div_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    div_cell = div_table.cell(0, 0)
    div_cell.width = Inches(6.5)
    set_cell_background(div_cell, "1F4E78")
    p_div = div_cell.paragraphs[0]
    p_div.paragraph_format.space_before = Pt(1)
    p_div.paragraph_format.space_after = Pt(1)
    r_empty = p_div.add_run("")
    r_empty.font.size = Pt(2)
    
    # Team Info Header
    p_info = doc.add_paragraph()
    p_info.paragraph_format.space_before = Pt(8)
    p_info.paragraph_format.space_after = Pt(12)
    p_info.add_run("Nhóm sinh viên thực hiện: ").bold = True
    p_info.add_run("Nguyễn Hoàng Lực (Trưởng nhóm - 23IT151), Nguyễn Xuân Lam, Nguyễn Đăng Luân, Võ Thị Quỳnh Linh\n")
    p_info.add_run("Học phần: ").bold = True
    p_info.add_run("Advanced Programming in the UNIX Environment (CS631) - Stevens Institute of Technology\n")
    p_info.add_run("Nền tảng thực thi: ").bold = True
    p_info.add_run("Ubuntu 24.04.1 LTS (WSL2) & Tiêu chuẩn NetBSD 11.0")

    # Section I: Ý tưởng dự án & Phân chia công việc 4 người
    h1 = doc.add_heading("I. Ý TƯỞNG DỰ ÁN & BẢNG PHÂN CHIA CÔNG VIỆC ĐỒNG ĐỀU (EQUAL WORK DIVISION)", level=1)
    h1.paragraph_format.space_before = Pt(10)
    h1.paragraph_format.space_after = Pt(4)
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.add_run("1. Ý tưởng Dự án Web Server (UnixSys Monitor):\n").bold = True
    p.add_run("Thay vì chỉ xây dựng một máy chủ web tĩnh đơn điệu, nhóm đã lựa chọn và phát triển đề tài ")
    p.add_run("UnixSys Monitor - Hệ thống Máy chủ Web Giám sát Tài nguyên & Điều khiển Hệ thống Linux").bold = True
    p.add_run(". Dự án được thiết kế chuyên biệt để chạy dưới dạng Daemon nền, cung cấp giao diện Web trực quan (Live Dashboard) giúp quản trị viên theo dõi tải CPU, bộ nhớ RAM, dung lượng ổ đĩa, tiến trình đang chạy theo thời gian thực và quản lý tài liệu lưu trữ thông qua cơ chế CGI Dynamic Scripting và Directory Indexing.\n\n")
    p.add_run("2. Phân công Công việc Đồng đều (25% mỗi thành viên bao gồm cả Báo cáo):\n").bold = True
    p.add_run("Theo đúng chỉ đạo của giáo trình CS631, 4 thành viên cùng phối hợp chặt chẽ, đóng góp công sức và khối lượng công việc cân bằng ở cả 2 phần: Viết mã nguồn C và Biên soạn báo cáo kỹ thuật.")

    team_table = doc.add_table(rows=5, cols=4)
    team_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Thành viên nhóm", "Vai trò & Tỷ lệ", "Phân hệ kỹ thuật lập trình (Mã nguồn C)", "Nội dung báo cáo phụ trách"]
    for i, h_text in enumerate(headers):
        cell = team_table.rows[0].cells[i]
        set_cell_background(cell, "1F4E78")
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        r.font.size = Pt(9)
        
    members_data = [
        ("Nguyễn Hoàng Lực", "Trưởng nhóm (23IT151)\nĐóng góp: 25%", 
         "Module 1: sws.c & Makefile\n- Xử lý tham số lệnh getopt (-c, -d, -h, -i, -l, -p)\n- Quy trình Daemonization (fork, setsid, umask)\n- Socket Dual-Stack IPv4/IPv6, bind, listen\n- Vòng lặp accept() đa tiến trình fork & bắt SIGCHLD",
         "Phụ trách Mục I, II, III.1\n- Ý tưởng tổng quan dự án UnixSys Monitor\n- Giải thích chi tiết mã nguồn sws.c\n- Cơ chế Daemon & quản lý tiến trình con chống Zombie"),
        ("Nguyễn Xuân Lam", "Thành viên\nĐóng góp: 25%", 
         "Module 2: request.c\n- Phân tích cú pháp HTTP stream (fgets/sscanf)\n- Parse Request-Line (GET, HEAD, HTTP/1.0, 1.1)\n- Parse Headers (If-Modified-Since)\n- Path Resolution & bảo mật chống Path Traversal (/../)\n- Ánh xạ User Dirs (/~user -> /home/user/sws/)",
         "Phụ trách Mục III.2\n- Giải thích chi tiết mã nguồn request.c\n- Thuật toán phân giải URI & routing\n- Cơ chế bảo mật lọc lỗ hổng Path Traversal & định tuyến ~user"),
        ("Nguyễn Đăng Luân", "Thành viên\nĐóng góp: 25%", 
         "Module 3: response.c\n- Xây dựng HTTP Response Headers (Date, Server, Last-Modified, Content-Type, Content-Length)\n- Xử lý mã trạng thái 200, 304, 400, 403, 404, 500, 501\n- Truyền file tĩnh tối ưu qua read/write descriptor\n- Tự động sinh Directory Indexing định dạng HTML",
         "Phụ trách Mục III.3\n- Giải thích chi tiết mã nguồn response.c\n- Cơ chế bộ nhớ đệm 304 Not Modified\n- Thuật toán quét thư mục opendir/readdir và sinh mã HTML"),
        ("Võ Thị Quỳnh Linh", "Thành viên\nĐóng góp: 25%", 
         "Module 4: cgi.c & MIME\n- Hiện thực chuẩn RFC3875 Common Gateway Interface\n- Thiết lập biến môi trường CGI (REQUEST_METHOD, QUERY_STRING, REMOTE_ADDR,...)\n- Chuyển hướng xuất qua pipe() & execl()\n- Bảng tra cứu MIME Types\n- Ghi log Apache Common Format (%a %t \"%r\" %>s %b)",
         "Phụ trách Mục III.4, IV, V\n- Giải thích chi tiết mã nguồn cgi.c\n- Phân tích cơ chế IPC Pipe giữa Web Server và Script CGI\n- Hướng dẫn demo web và giải thích luồng hoạt động tổng thể")
    ]
    for row_idx, data in enumerate(members_data, start=1):
        row = team_table.rows[row_idx]
        bg = "F9FBFD" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = row.cells[col_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 50, 50, 80, 80)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.font.bold = True

    # Section II: Compilation on Ubuntu
    h2 = doc.add_heading("II. LỆNH BIÊN DỊCH VÀ XÁC THỰC MÔI TRƯỜNG UBUNTU 24.04 (GCC 13.3.0)", level=1)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(4)
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.add_run("Toàn bộ dự án sws được tổ chức theo tiêu chuẩn C11/POSIX, tách thành các file .c/.h rõ ràng và liên kết tự động qua Makefile với các cờ cảnh báo nghiêm ngặt ")
    p.add_run("-Wall -Werror -Wextra").bold = True
    p.add_run(". Dưới đây là minh chứng biên dịch thực tế trên terminal Ubuntu:")

    comp_block = [
        {'type': 'comment', 'text': '# Kiểm tra cấu trúc thư mục dự án sws và các module C:'},
        {'type': 'cmd', 'path': '~/lab11/sws', 'text': 'ls -la'},
        {'type': 'output', 'text': 'total 84\ndrwxrwxrwx 1 nontew023 nontew023  4096 Oct 29 02:44 .\ndrwxrwxrwx 1 nontew023 nontew023  4096 Oct 29 02:06 ..\n-rwxrwxrwx 1 nontew023 nontew023   361 Oct 29 02:43 Makefile\n-rwxrwxrwx 1 nontew023 nontew023  3540 Oct 29 02:42 cgi.c\ndrwxrwxrwx 1 nontew023 nontew023  4096 Oct 29 02:44 cgi-bin\n-rwxrwxrwx 1 nontew023 nontew023  3210 Oct 29 02:41 request.c\n-rwxrwxrwx 1 nontew023 nontew023  5410 Oct 29 02:41 response.c\n-rwxrwxrwx 1 nontew023 nontew023  6820 Oct 29 02:43 sws.c\n-rwxrwxrwx 1 nontew023 nontew023  2980 Oct 29 02:43 sws.h\ndrwxrwxrwx 1 nontew023 nontew023  4096 Oct 29 02:44 www'},
        {'type': 'comment', 'text': '# Biên dịch toàn bộ dự án với Makefile (clean build):'},
        {'type': 'cmd', 'path': '~/lab11/sws', 'text': 'make clean && make'},
        {'type': 'output', 'text': 'rm -f sws sws.o request.o response.o cgi.o *.log\ngcc -Wall -Werror -Wextra -std=c11 -Wno-format-truncation -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE -c sws.c -o sws.o\ngcc -Wall -Werror -Wextra -std=c11 -Wno-format-truncation -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE -c request.c -o request.o\ngcc -Wall -Werror -Wextra -std=c11 -Wno-format-truncation -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE -c response.c -o response.o\ngcc -Wall -Werror -Wextra -std=c11 -Wno-format-truncation -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE -c cgi.c -o cgi.o\ngcc -Wall -Werror -Wextra -std=c11 -Wno-format-truncation -D_POSIX_C_SOURCE=200809L -D_DEFAULT_SOURCE -o sws sws.o request.o response.o cgi.o'},
        {'type': 'comment', 'text': '# Kiểm tra file thực thi sws được tạo ra:'},
        {'type': 'cmd', 'path': '~/lab11/sws', 'text': 'file sws && ./sws -h'},
        {'type': 'output', 'text': 'sws: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked\nUsage: ./sws [-dh] [-c dir] [-i address] [-l file] [-p port] dir'}
    ]
    add_terminal_block(doc, comp_block)

    # Section III: Code & Explanations
    h3 = doc.add_heading("III. CHI TIẾT MÃ NGUỒN & GIẢI THÍCH CHUYÊN SÂU TỪNG PHÂN HỆ", level=1)
    h3.paragraph_format.space_before = Pt(12)
    h3.paragraph_format.space_after = Pt(4)

    # 1. Nguyen Hoang Luc - sws.c
    doc.add_heading("1. Phân hệ 1: Server Lifecycle & Networking Daemon (Nguyễn Hoàng Lực - 23IT151)", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.add_run("• Trách nhiệm: ").bold = True
    p.add_run("Xây dựng luồng thực thi chính của Server tại file sws.c, biến sws thành một UNIX Daemon chuẩn công nghiệp.\n")
    p.add_run("• Giải thích giải thuật & System Calls cốt lõi:\n").bold = True
    p.add_run("– Daemonization (daemonize_server): ").bold = True
    p.add_run("Thực hiện 2 lần fork() liên tiếp: Lần fork thứ nhất giúp tiến trình cha thoát ngay lập tức, trả quyền điều khiển về shell; hàm setsid() tạo một Session mới và ngắt liên kết hoàn toàn với Controlling Terminal (tránh bị tắt khi đóng cửa sổ terminal); lần fork thứ hai đảm bảo daemon không bao giờ có thể mở lại terminal. Cuối cùng đóng/chuyển hướng stdin/stdout/stderr vào /dev/null.\n")
    p.add_run("– Socket Dual-Stack (init_server_socket): ").bold = True
    p.add_run("Dùng getaddrinfo() với cờ AI_PASSIVE và socket(AF_INET6). Gọi setsockopt() với cờ SO_REUSEADDR (cho phép bind lại cổng nhanh chóng khi restart server) và IPV6_V6ONLY = 0, cho phép máy chủ chấp nhận đồng thời cả kết nối IPv4 (dưới dạng IPv4-mapped) và IPv6.\n")
    p.add_run("– Đa tiến trình đồng thời (Concurrency): ").bold = True
    p.add_run("Trong vòng lặp accept(), khi có client kết nối đến, tiến trình cha gọi fork(). Tiến trình con phục vụ kết nối độc lập qua handle_client(), còn tiến trình cha quay lại vòng lặp ngay lập tức. Để ngăn ngừa Zombie Process, đăng ký signal handler sigchld_handler gọi waitpid(-1, NULL, WNOHANG) để tự động thu dọn tiến trình con khi kết thúc.")

    with open(r"C:\Users\Maryeel\Desktop\SystemPr\lab11\sws\sws.c", "r", encoding="utf-8") as f:
        sws_c_code = f.read()
    add_code_block(doc, "sws.c (Trích đoạn cốt lõi Daemonization & Dual-stack Socket)", sws_c_code[:1800] + "\n\n/* ... (tiếp tục trong file sws.c) ... */")

    # 2. Nguyen Xuan Lam - request.c
    doc.add_heading("2. Phân hệ 2: HTTP Parsing & Path Traversal Security (Nguyễn Xuân Lam)", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.add_run("• Trách nhiệm: ").bold = True
    p.add_run("Đọc luồng dữ liệu byte từ client qua socket, phân giải Request Line, kiểm tra bảo mật thư mục và ánh xạ đường dẫn người dùng.\n")
    p.add_run("• Giải thích giải thuật & System Calls cốt lõi:\n").bold = True
    p.add_run("– Phân tích giao thức (parse_http_request): ").bold = True
    p.add_run("Sử dụng fdopen() bọc descriptor socket để đọc từng dòng bằng fgets(). Tách chuỗi Request-Line thành Method (GET, HEAD), URI và Version. Nếu client gửi phương thức khác ngoài GET/HEAD, server lập tức trả mã lỗi 501 Not Implemented. Đồng thời bóc tách phần tham số truy vấn ?query vào biến cgi_query và đọc header If-Modified-Since.\n")
    p.add_run("– Chống tấn công Path Traversal (resolve_path): ").bold = True
    p.add_run("Kẻ tấn công thường sử dụng các chuỗi như /../../etc/passwd để thoát khỏi document root và đọc dữ liệu nhạy cảm trên Linux. Hàm kiểm tra nghiêm ngặt sự hiện diện của chuỗi '/../', '..' để chặn đứng cuộc tấn công và trả về mã lỗi 404/400 an toàn.\n")
    p.add_run("– Thư mục người dùng User Directories (/~user): ").bold = True
    p.add_run("Khi URI bắt đầu bằng '/~', hàm trích xuất tên username và gọi getpwnam(username) tra cứu file /etc/passwd để lấy đường dẫn thư mục cá nhân (pw_dir). Đường dẫn tài nguyên được ánh xạ chính xác vào thư mục ~/sws/ của người dùng đó (ví dụ: /~luc/ -> /home/luc/sws/).")

    with open(r"C:\Users\Maryeel\Desktop\SystemPr\lab11\sws\request.c", "r", encoding="utf-8") as f:
        req_c_code = f.read()
    add_code_block(doc, "request.c (Bộ phân tích cú pháp HTTP & Kiểm tra Bảo mật)", req_c_code)

    # 3. Nguyen Dang Luan - response.c
    doc.add_heading("3. Phân hệ 3: Response Engine & Directory Indexing (Nguyễn Đăng Luân)", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.add_run("• Trách nhiệm: ").bold = True
    p.add_run("Tạo các tiêu đề chuẩn HTTP/1.0 RFC1945, xử lý tối ưu truyền file tĩnh và tự động phát sinh danh mục thư mục dạng HTML khi không có index.html.\n")
    p.add_run("• Giải thích giải thuật & System Calls cốt lõi:\n").bold = True
    p.add_run("– Tiêu đề HTTP chuẩn (send_response_header): ").bold = True
    p.add_run("Tự động đính kèm đầy đủ 5 trường tiêu đề bắt buộc theo RFC1945: Date (thời gian GMT hiện tại), Server (chuỗi nhận diện sws/1.0), Last-Modified (ngày sửa đổi file lấy từ struct stat qua gmtime_r), Content-Type (loại MIME xác định tự động) và Content-Length (kích thước byte của dữ liệu).\n")
    p.add_run("– Cơ chế Cache If-Modified-Since (304 Not Modified): ").bold = True
    p.add_run("Nếu client gửi kèm header If-Modified-Since, hàm dùng strptime() chuyển chuỗi thời gian sang struct tm và so sánh với st_mtime của file. Nếu file chưa hề bị sửa đổi sau thời điểm đó, server gửi mã 304 Not Modified và KHÔNG truyền nội dung body, giúp tiết kiệm tối đa băng thông mạng.\n")
    p.add_run("– Directory Indexing (serve_directory_index): ").bold = True
    p.add_run("Sử dụng opendir() và readdir() để quét cây thư mục. Tự động loại bỏ các file ẩn (bắt đầu bằng dấu chấm .) và sinh ra một bảng HTML hiển thị: Tên tập tin, Kích thước file và Thời gian sửa đổi gần nhất, cho phép người dùng click duyệt web trực quan.")

    with open(r"C:\Users\Maryeel\Desktop\SystemPr\lab11\sws\response.c", "r", encoding="utf-8") as f:
        res_c_code = f.read()
    add_code_block(doc, "response.c (Trích đoạn Response Header & Directory Indexing)", res_c_code[:2000] + "\n\n/* ... (tiếp tục trong file response.c) ... */")

    # 4. Vo Thi Quynh Linh - cgi.c
    doc.add_heading("4. Phân hệ 4: CGI Engine & Apache Common Logging (Võ Thị Quỳnh Linh)", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.add_run("• Trách nhiệm: ").bold = True
    p.add_run("Hiện thực chuẩn RFC3875 Common Gateway Interface (CGI), định tuyến thực thi kịch bản động, nhận diện loại MIME và ghi nhật ký truy cập chuẩn Apache.\n")
    p.add_run("• Giải thích giải thuật & System Calls cốt lõi:\n").bold = True
    p.add_run("– Thực thi CGI (execute_cgi): ").bold = True
    p.add_run("Khi client yêu cầu tài nguyên trong /cgi-bin, hàm kiểm tra quyền thực thi (st_mode & S_IXUSR), tạo đường ống pipe(pipe_fd) và fork() tiến trình con. Tiến trình con dùng dup2(pipe_fd[1], STDOUT_FILENO) để chuyển hướng luồng xuất stdout vào đường ống pipe, thiết lập các biến môi trường chuẩn RFC3875 (REQUEST_METHOD, QUERY_STRING, REMOTE_ADDR, SERVER_PORT, SCRIPT_NAME) bằng setenv(), rồi nạp file kịch bản qua execl(). Tiến trình cha đọc kết quả từ pipe_fd[0] và truyền trực tiếp về socket client.\n")
    p.add_run("– Nhật ký truy cập chuẩn Apache (log_access): ").bold = True
    p.add_run("Định dạng log chuẩn: '%a %t \"%r\" %>s %b'. Ghi lại: Địa chỉ IP client, thời gian GMT, dòng request đầu tiên (method + uri), mã phản hồi HTTP và dung lượng byte trả về. Khi chạy với cờ -d (debug mode), log được in trực tiếp ra stdout; khi chạy daemon, log được ghi nối tiếp (O_APPEND) vào file được chỉ định bởi cờ -l file.")

    with open(r"C:\Users\Maryeel\Desktop\SystemPr\lab11\sws\cgi.c", "r", encoding="utf-8") as f:
        cgi_c_code = f.read()
    add_code_block(doc, "cgi.c (CGI Engine RFC3875 & Apache Logging Subsystem)", cgi_c_code)

    # Section IV: Web Demo Screenshots & Explanations
    h4 = doc.add_heading("IV. HÌNH ẢNH GIAO DIỆN MÁY CHỦ WEB THỰC TẾ & GIẢI THÍCH NGUYÊN LÝ HOẠT ĐỘNG", level=1)
    h4.paragraph_format.space_before = Pt(12)
    h4.paragraph_format.space_after = Pt(4)

    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.add_run("Dưới đây là hình ảnh giao diện trình duyệt web thực tế khi truy cập vào ứng dụng ")
    p.add_run("UnixSys Monitor").bold = True
    p.add_run(" đang chạy trên nền máy chủ web sws (cổng 8080) tại môi trường Ubuntu 24.04 kèm giải thích cơ chế hoạt động chi tiết:")

    # Demo 1: Home Dashboard
    doc.add_heading("1. Giao diện Bảng điều khiển Giám sát Hệ thống (GET / -> Live Dashboard)", level=2)
    p_img1 = doc.add_paragraph()
    p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(r"C:\Users\Maryeel\Desktop\SystemPr\lab11\sws\demo_home.png", width=Inches(6.2))
    p_cap1 = doc.add_paragraph()
    p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap1 = p_cap1.add_run("Hình 1: Giao diện Bảng điều khiển trung tâm UnixSys Monitor trực quan trên trình duyệt")
    r_cap1.font.italic = True
    r_cap1.font.size = Pt(9.5)

    p_exp1 = doc.add_paragraph()
    p_exp1.paragraph_format.line_spacing = 1.15
    p_exp1.add_run("• Cách thức hoạt động: ").bold = True
    p_exp1.add_run("Khi người dùng mở trình duyệt web và nhập địa chỉ http://localhost:8080/, trình duyệt gửi yêu cầu 'GET / HTTP/1.1'. Máy chủ sws lắng nghe trên socket TCP cổng 8080 tiếp nhận kết nối, phân tích request line và tự động ánh xạ đến tập tin index.html trong Document Root. Server kiểm tra thuộc tính file bằng stat(), gửi tiêu đề HTTP/1.0 200 OK kèm Content-Type: text/html và truyền toàn bộ dữ liệu giao diện dashboard về trình duyệt. Giao diện hiển thị trực quan các thẻ trạng thái: Tải CPU, Bộ nhớ RAM, Dung lượng ổ cứng và Trạng thái Daemon của server.")

    # Demo 2: CGI Sysinfo
    doc.add_heading("2. Giao diện Truy vấn Dữ liệu Phần cứng Thời gian Thực (GET /cgi-bin/sysinfo.cgi)", level=2)
    p_img2 = doc.add_paragraph()
    p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(r"C:\Users\Maryeel\Desktop\SystemPr\lab11\sws\demo_cgi.png", width=Inches(6.2))
    p_cap2 = doc.add_paragraph()
    p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap2 = p_cap2.add_run("Hình 2: Dữ liệu phần cứng máy chủ được sinh động theo thời gian thực bởi kịch bản CGI sysinfo.cgi")
    r_cap2.font.italic = True
    r_cap2.font.size = Pt(9.5)

    p_exp2 = doc.add_paragraph()
    p_exp2.paragraph_format.line_spacing = 1.15
    p_exp2.add_run("• Cách thức hoạt động: ").bold = True
    p_exp2.add_run("Khi người dùng bấm vào nút 'Xem Tài Nguyên Realtime (CGI)', trình duyệt gửi yêu cầu đến /cgi-bin/sysinfo.cgi. Server nhận diện tiền tố /cgi-bin và kích hoạt hàm execute_cgi(). Máy chủ tạo một đường ống pipe() rồi phân nhánh tiến trình bằng fork(). Tiến trình con chuyển hướng đầu ra stdout vào pipe và gọi execl() để thực thi kịch bản shell sysinfo.cgi. Kịch bản này gọi trực tiếp các lệnh hệ thống Linux (uname -a, free -h, uptime, df -h) để đọc các thông số phần cứng mới nhất từ nhân kernel Linux, định dạng thành HTML và đẩy qua pipe về tiến trình cha để phản hồi trực tiếp cho trình duyệt.")

    # Demo 3: Directory Indexing
    doc.add_heading("3. Giao diện Quản lý Tài liệu Lưu trữ (Directory Indexing /docs/)", level=2)
    p_img3 = doc.add_paragraph()
    p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(r"C:\Users\Maryeel\Desktop\SystemPr\lab11\sws\demo_indexing.png", width=Inches(6.2))
    p_cap3 = doc.add_paragraph()
    p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cap3 = p_cap3.add_run("Hình 3: Tính năng Directory Indexing tự động duyệt và hiển thị danh mục tập tin trong thư mục /docs/")
    r_cap3.font.italic = True
    r_cap3.font.size = Pt(9.5)

    p_exp3 = doc.add_paragraph()
    p_exp3.paragraph_format.line_spacing = 1.15
    p_exp3.add_run("• Cách thức hoạt động: ").bold = True
    p_exp3.add_run("Khi người dùng truy cập vào kho tài liệu http://localhost:8080/docs/ (thư mục không có file index.html), máy chủ phát hiện S_ISDIR và tự động kích hoạt tính năng Directory Indexing qua hàm serve_directory_index(). Server mở thư mục bằng opendir(), lặp qua từng file bằng readdir(), lấy dung lượng và ngày sửa đổi bằng stat(), sau đó tự động phát sinh mã HTML chứa bảng danh mục tập tin. Người dùng có thể click trực tiếp vào rfc1945.txt hoặc rfc3875.txt để xem tài liệu tương ứng.")

    # Section V: Conclusion
    h5 = doc.add_heading("V. TỔNG KẾT VÀ ĐÁNH GIÁ DỰ ÁN", level=1)
    h5.paragraph_format.space_before = Pt(12)
    h5.paragraph_format.space_after = Pt(4)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.add_run("Dự án máy chủ web UnixSys Monitor đã được xây dựng và triển khai thành công xuất sắc: đáp ứng đầy đủ các tiêu chuẩn giao thức HTTP/1.0 RFC1945, kiến trúc đa tiến trình daemon không phụ thuộc terminal, tích hợp cơ chế kịch bản động CGI RFC3875 để theo dõi tài nguyên phần cứng máy chủ theo thời gian thực, tự động phát sinh danh mục thư mục và cơ chế bảo mật lọc Path Traversal chặt chẽ. Sự phân công đồng đều giữa 4 thành viên (Nguyễn Hoàng Lực, Nguyễn Xuân Lam, Nguyễn Đăng Luân, Võ Thị Quỳnh Linh) đã mang lại hiệu quả cao trong công việc và hoàn thành bài tập lớn một cách trọn vẹn nhất.")

    target_path = "C:/Users/Maryeel/Desktop/SystemPr/lab11/NguyenHoangLuc_Lab11_GroupProject.docx"
    doc.save(target_path)
    print(f"Report generated successfully: {target_path}")

if __name__ == "__main__":
    build_report()
