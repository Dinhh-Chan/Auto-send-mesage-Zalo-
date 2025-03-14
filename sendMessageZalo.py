# Cài đặt các thư viện cần thiết (chạy lệnh trước khi chạy script)
# pip install fastapi uvicorn selenium webdriver-manager

import threading
import time
from fastapi import FastAPI
import uvicorn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = FastAPI(title="FastAPI với Selenium")

# Hàm để chạy trình duyệt Selenium
def run_selenium():
    # Chờ một chút để FastAPI kịp khởi động
    time.sleep(2)
    
    # Thiết lập trình duyệt Chrome
    options = webdriver.ChromeOptions()
    # Bỏ comment dòng dưới nếu muốn chạy ở chế độ headless (không hiển thị UI)
    # options.add_argument('--headless')
    
    # Khởi tạo driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Mở trang Google
    driver.get("https://www.google.com")
    
    # Giữ trình duyệt mở trong 60 giây
    time.sleep(60)
    
    # Đóng trình duyệt
    driver.quit()

# Định nghĩa route mặc định
@app.get("/")
async def root():
    return {"message": "FastAPI đang chạy cùng với Selenium"}

# Sự kiện startup để chạy Selenium khi ứng dụng khởi động
@app.on_event("startup")
def on_startup():
    # Chạy Selenium trong một luồng riêng biệt
    selenium_thread = threading.Thread(target=run_selenium)
    selenium_thread.daemon = True  # Đảm bảo luồng kết thúc khi chương trình chính kết thúc
    selenium_thread.start()

# Hàm để chạy máy chủ FastAPI
def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Chạy server khi chạy script này
if __name__ == "__main__":
    start_server() 