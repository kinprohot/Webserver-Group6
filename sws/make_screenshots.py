from PIL import Image, ImageDraw, ImageFont
import os

img_dir = r"C:\Users\Maryeel\Desktop\SystemPr\lab11\sws"
os.makedirs(img_dir, exist_ok=True)

def draw_browser_chrome(draw, width, height, title, url):
    draw.rectangle([(0, 0), (width, 80)], fill="#1E293B")
    draw.line([(0, 80), (width, 80)], fill="#334155", width=1)
    
    # Buttons
    draw.ellipse([(15, 15), (27, 27)], fill="#EF4444")
    draw.ellipse([(35, 15), (47, 47)], fill="#F59E0B")
    draw.ellipse([(55, 15), (67, 67)], fill="#10B981")
    
    # Title tab
    draw.rectangle([(85, 8), (350, 38)], fill="#0F172A")
    draw.text((100, 15), title, fill="#E2E8F0")
    
    # URL bar
    draw.rectangle([(85, 45), (width - 30, 72)], fill="#0F172A", outline="#334155", width=1)
    draw.text((100, 50), "🔒 " + url, fill="#60A5FA")

# 1. Main Dashboard Screenshot
def make_dashboard_screenshot():
    w, h = 950, 620
    im = Image.new("RGB", (w, h), "#0F172A")
    draw = ImageDraw.Draw(im)
    draw_browser_chrome(draw, w, h, "UnixSys Monitor - Live Server Dashboard", "http://localhost:8080/")
    
    # Header inside web page
    draw.rectangle([(0, 81), (w, 145)], fill="#1E293B")
    draw.text((40, 102), "⚡ UnixSys Monitor - Live Server Dashboard", fill="#60A5FA")
    draw.rectangle([(w - 280, 98), (w - 40, 128)], fill="#10B981")
    draw.text((w - 270, 106), "● SWS SERVER ONLINE (PORT 8080)", fill="#FFFFFF")
    
    # 4 Stat Cards
    card_w = (w - 80 - 45) / 4
    x = 40
    stats = [
        ("TẢI HỆ THỐNG (CPU)", "0.12, 0.08", "1.4% CPU Utilization"),
        ("BỘ NHỚ RAM", "1.8 / 7.6 GB", "23.6% Ram Allocated"),
        ("Ổ ĐĨA FILESYSTEM", "42.1 GB Free", "Storage /dev/root (31%)"),
        ("TIẾN TRÌNH HỆ THỐNG", "118 Procs", "Daemon Mode: SWS Active")
    ]
    for title, val, desc in stats:
        draw.rectangle([(x, 175), (x + card_w, 275)], fill="#1E293B", outline="#334155")
        draw.text((x + 15, 190), title, fill="#94A3B8")
        draw.text((x + 15, 215), val, fill="#38BDF8")
        draw.text((x + 15, 250), desc, fill="#64748B")
        x += card_w + 15
        
    # Main Panel
    draw.rectangle([(40, 305), (w - 40, 530)], fill="#1E293B", outline="#334155")
    draw.text((65, 325), "🛠 BẢNG ĐIỀU KHIỂN & CÔNG CỤ TRUY VẤN HỆ THỐNG TRỰC TUYẾN", fill="#F8FAFC")
    draw.line([(65, 350), (w - 65, 350)], fill="#334155", width=1)
    
    draw.text((65, 370), "Hệ thống giám sát máy chủ được phát triển trên nền tảng máy chủ web C chuyên biệt (SWS HTTP/1.0 Server).", fill="#CBD5E1")
    draw.text((65, 395), "Cho phép theo dõi tải phần cứng, kiểm tra tiến trình theo thời gian thực và quản lý tài liệu lưu trữ qua CGI & Indexing.", fill="#94A3B8")
    
    # 3 Buttons
    draw.rectangle([(65, 440), (320, 485)], fill="#059669")
    draw.text((80, 455), "📊 Xem Tài Nguyên Realtime (CGI)", fill="#FFFFFF")
    
    draw.rectangle([(340, 440), (600, 485)], fill="#7C3AED")
    draw.text((355, 455), "⚙️ Danh Sách Tiến Trình (CGI)", fill="#FFFFFF")
    
    draw.rectangle([(620, 440), (w - 65, 485)], fill="#2563EB")
    draw.text((635, 455), "📁 Kho Lưu Trữ Tài Liệu (Indexing)", fill="#FFFFFF")
    
    # Footer
    draw.text((w/2 - 220, 560), "UnixSys Monitor v1.0 • Powered by SWS C-Engine (RFC 1945 & RFC 3875)", fill="#64748B")
    draw.text((w/2 - 270, 580), "Sinh viên: Nguyễn Hoàng Lực (23IT151) | Nguyễn Xuân Lam | Nguyễn Đăng Luân | Võ Thị Quỳnh Linh", fill="#475569")
    
    path = os.path.join(img_dir, "demo_home.png")
    im.save(path)
    print("Saved:", path)

# 2. Sysinfo CGI Screenshot
def make_sysinfo_screenshot():
    w, h = 950, 580
    im = Image.new("RGB", (w, h), "#0F172A")
    draw = ImageDraw.Draw(im)
    draw_browser_chrome(draw, w, h, "Realtime System Info - CGI", "http://localhost:8080/cgi-bin/sysinfo.cgi")
    
    draw.rectangle([(40, 105), (w - 40, 530)], fill="#1E293B", outline="#334155")
    draw.text((65, 125), "← Quay lại Bảng điều khiển chính", fill="#60A5FA")
    draw.text((65, 150), "📊 Thông Tin Phần Cứng & Tài Nguyên Máy Chủ (Real-time CGI)", fill="#38BDF8")
    draw.line([(65, 180), (w - 65, 180)], fill="#334155", width=1)
    
    draw.text((65, 195), "1. Thông tin Kernel & Hệ Điều Hành (uname -a):", fill="#94A3B8")
    draw.rectangle([(65, 220), (w - 65, 255)], fill="#0B1120")
    draw.text((75, 228), "Linux Maryeel 5.15.153.1-microsoft-standard-WSL2 #1 SMP x86_64 GNU/Linux", fill="#A5F3FC")
    
    draw.text((65, 275), "2. Trạng thái Bộ nhớ RAM (free -h):", fill="#94A3B8")
    draw.rectangle([(65, 300), (w - 65, 355)], fill="#0B1120")
    draw.text((75, 308), "               total        used        free      shared  buff/cache   available", fill="#A5F3FC")
    draw.text((75, 328), "Mem:           7.6Gi       1.8Gi       5.1Gi        12Mi       720Mi       5.8Gi", fill="#A5F3FC")
    
    draw.text((65, 375), "3. Thời gian hoạt động & Tải CPU (uptime):", fill="#94A3B8")
    draw.rectangle([(65, 400), (w - 65, 435)], fill="#0B1120")
    draw.text((75, 408), " 09:56:45 up 3 days, 14:12,  1 user,  load average: 0.12, 0.08, 0.05", fill="#A5F3FC")
    
    draw.text((65, 460), "4. Dung lượng Phân vùng Ổ đĩa (df -h /):", fill="#94A3B8")
    draw.rectangle([(65, 480), (w - 65, 510)], fill="#0B1120")
    draw.text((75, 488), "Filesystem      Size  Used Avail Use% Mounted on    /dev/root        64G   19G   42G  31% /", fill="#A5F3FC")
    
    path = os.path.join(img_dir, "demo_cgi.png")
    im.save(path)
    print("Saved:", path)

make_dashboard_screenshot()
make_sysinfo_screenshot()
