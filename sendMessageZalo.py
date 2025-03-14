import threading
import time
from fastapi import FastAPI
import uvicorn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
from PIL import Image
from io import BytesIO

app = FastAPI(title="FastAPI với Selenium")
# Hàm để chạy trình duyệt Selenium
def run_selenium():
    time.sleep(2)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Cần thiết cho một số hệ thống
    options.add_argument('--window-size=1920,1080')  # Đặt kích thước cửa sổ lớn
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')  # Giải quyết vấn đề bộ nhớ trên một số hệ thống

    # Quan trọng: Đặt tỷ lệ thiết bị để chụp màn hình chất lượng cao
    options.add_argument('--force-device-scale-factor=1')

    # Thêm tham số để tránh lỗi khi chụp màn hình trong headless mode
    options.add_argument('--hide-scrollbars')
    options.add_argument('--disable-extensions')
    
    # Khởi tạo driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Mở trang Zalo Web
    driver.get("https://chat.zalo.me/")
    
    # Đặt kích thước cửa sổ cụ thể
    driver.set_window_size(1920, 1080)
    
    # Chuyển sang chế độ toàn màn hình
    driver.fullscreen_window()
    
    # Đợi cho mã QR xuất hiện (tối đa 20 giây)
    try:
        # Đợi cho trang tải xong và mã QR xuất hiện
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "qrcode"))
        )
        
        print("Đã tìm thấy mã QR, đang chụp màn hình...")
        
        # Tìm phần tử QR code
        qr_element = driver.find_element(By.CLASS_NAME, "qrcode")
        
        # Cuộn đến phần tử QR để đảm bảo nó hiển thị đầy đủ
        driver.execute_script("arguments[0].scrollIntoView(true);", qr_element)
        
        # Thêm thời gian chờ để đảm bảo cuộn hoàn tất
        time.sleep(1)
        
        # Chụp màn hình toàn bộ trang
        screenshot = driver.get_screenshot_as_png()
        
        # Chuyển đổi ảnh PNG sang PDF
        image = Image.open(BytesIO(screenshot))
        image_path = "zalo_qr_code.png"
        pdf_path = "zalo_qr_code.pdf"
        
        # Lưu ảnh PNG
        image.save(image_path)
        print(f"Đã lưu ảnh mã QR tại: {os.path.abspath(image_path)}")
        
        # Chuyển đổi sang PDF
        image_rgb = image.convert('RGB')
        image_rgb.save(pdf_path)
        print(f"Đã lưu PDF mã QR tại: {os.path.abspath(pdf_path)}")
        
        # Thử chụp riêng phần tử QR bằng JavaScript
        try:
            # Sử dụng JavaScript để lấy kích thước và vị trí chính xác
            rect = driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                return {
                    top: rect.top,
                    left: rect.left,
                    width: rect.width,
                    height: rect.height,
                    devicePixelRatio: window.devicePixelRatio || 1
                };
            """, qr_element)
            
            # Tính toán tọa độ với tỷ lệ pixel thiết bị
            device_pixel_ratio = rect['devicePixelRatio']
            left = rect['left'] * device_pixel_ratio
            top = rect['top'] * device_pixel_ratio
            right = (rect['left'] + rect['width']) * device_pixel_ratio
            bottom = (rect['top'] + rect['height']) * device_pixel_ratio
            
            # Thêm padding để đảm bảo không bị cắt
            padding = 10 * device_pixel_ratio
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = right + padding
            bottom = bottom + padding
            
            # Cắt ảnh
            qr_image = image.crop((int(left), int(top), int(right), int(bottom)))
            qr_image_path = "zalo_qr_only.png"
            qr_pdf_path = "zalo_qr_only.pdf"
            
            # Lưu ảnh QR
            qr_image.save(qr_image_path)
            print(f"Đã lưu ảnh chỉ mã QR tại: {os.path.abspath(qr_image_path)}")
            
            # Chuyển đổi sang PDF
            qr_image_rgb = qr_image.convert('RGB')
            qr_image_rgb.save(qr_pdf_path)
            print(f"Đã lưu PDF chỉ mã QR tại: {os.path.abspath(qr_pdf_path)}")
            
            # Phương pháp thay thế: Chụp ảnh phần tử trực tiếp
            qr_element.screenshot("zalo_qr_direct.png")
            print(f"Đã lưu ảnh QR trực tiếp tại: {os.path.abspath('zalo_qr_direct.png')}")
            
            # Chuyển đổi ảnh trực tiếp sang PDF
            direct_image = Image.open("zalo_qr_direct.png")
            direct_image_rgb = direct_image.convert('RGB')
            direct_image_rgb.save("zalo_qr_direct.pdf")
            print(f"Đã lưu PDF QR trực tiếp tại: {os.path.abspath('zalo_qr_direct.pdf')}")
            
        except Exception as e:
            print(f"Lỗi khi cắt ảnh QR: {str(e)}")
        
    except Exception as e:
        print(f"Lỗi khi chụp mã QR: {str(e)}")
# Định nghĩa route mặc định
@app.get("/")
async def root():
    return {"message": "FastAPI đang chạy cùng với Selenium"}

# Hàm để chạy máy chủ FastAPI
def start_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Chạy server khi chạy script này
if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Cần thiết cho một số hệ thống
    options.add_argument('--window-size=1920,1080')  # Đặt kích thước cửa sổ lớn
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')  # Giải quyết vấn đề bộ nhớ trên một số hệ thống

    # Quan trọng: Đặt tỷ lệ thiết bị để chụp màn hình chất lượng cao
    options.add_argument('--force-device-scale-factor=1')

    # Thêm tham số để tránh lỗi khi chụp màn hình trong headless mode
    options.add_argument('--hide-scrollbars')
    options.add_argument('--disable-extensions')
    
    # Khởi tạo driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Mở trang Zalo Web
    driver.get("https://chat.zalo.me/")
    
    # Đặt kích thước cửa sổ cụ thể
    driver.set_window_size(1920, 1080)
    
    # Chuyển sang chế độ toàn màn hình
    driver.fullscreen_window()
    
    # Đợi cho mã QR xuất hiện (tối đa 20 giây)
    try:
        # Đợi cho trang tải xong và mã QR xuất hiện
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "qrcode"))
        )
        
        print("Đã tìm thấy mã QR, đang chụp màn hình...")
        
        # Tìm phần tử QR code
        qr_element = driver.find_element(By.CLASS_NAME, "qrcode")
        
        # Cuộn đến phần tử QR để đảm bảo nó hiển thị đầy đủ
        driver.execute_script("arguments[0].scrollIntoView(true);", qr_element)
        
        # Thêm thời gian chờ để đảm bảo cuộn hoàn tất
        time.sleep(1)
        
        # Chụp màn hình toàn bộ trang
        screenshot = driver.get_screenshot_as_png()
        
        # Chuyển đổi ảnh PNG sang PDF
        image = Image.open(BytesIO(screenshot))
        image_path = "zalo_qr_code.png"
        pdf_path = "zalo_qr_code.pdf"
        
        # Lưu ảnh PNG
        image.save(image_path)
        print(f"Đã lưu ảnh mã QR tại: {os.path.abspath(image_path)}")
        
        # Chuyển đổi sang PDF
        image_rgb = image.convert('RGB')
        image_rgb.save(pdf_path)
        print(f"Đã lưu PDF mã QR tại: {os.path.abspath(pdf_path)}")
        
        # Thử chụp riêng phần tử QR bằng JavaScript
        try:
            # Sử dụng JavaScript để lấy kích thước và vị trí chính xác
            rect = driver.execute_script("""
                var rect = arguments[0].getBoundingClientRect();
                return {
                    top: rect.top,
                    left: rect.left,
                    width: rect.width,
                    height: rect.height,
                    devicePixelRatio: window.devicePixelRatio || 1
                };
            """, qr_element)
            
            # Tính toán tọa độ với tỷ lệ pixel thiết bị
            device_pixel_ratio = rect['devicePixelRatio']
            left = rect['left'] * device_pixel_ratio
            top = rect['top'] * device_pixel_ratio
            right = (rect['left'] + rect['width']) * device_pixel_ratio
            bottom = (rect['top'] + rect['height']) * device_pixel_ratio
            
            # Thêm padding để đảm bảo không bị cắt
            padding = 10 * device_pixel_ratio
            left = max(0, left - padding)
            top = max(0, top - padding)
            right = right + padding
            bottom = bottom + padding
            
            # Cắt ảnh
            qr_image = image.crop((int(left), int(top), int(right), int(bottom)))
            qr_image_path = "zalo_qr_only.png"
            qr_pdf_path = "zalo_qr_only.pdf"
            
            # Lưu ảnh QR
            qr_image.save(qr_image_path)
            print(f"Đã lưu ảnh chỉ mã QR tại: {os.path.abspath(qr_image_path)}")
            
            # Chuyển đổi sang PDF
            qr_image_rgb = qr_image.convert('RGB')
            qr_image_rgb.save(qr_pdf_path)
            print(f"Đã lưu PDF chỉ mã QR tại: {os.path.abspath(qr_pdf_path)}")
            
            # Phương pháp thay thế: Chụp ảnh phần tử trực tiếp
            qr_element.screenshot("zalo_qr_direct.png")
            print(f"Đã lưu ảnh QR trực tiếp tại: {os.path.abspath('zalo_qr_direct.png')}")
            
            # Chuyển đổi ảnh trực tiếp sang PDF
            direct_image = Image.open("zalo_qr_direct.png")
            direct_image_rgb = direct_image.convert('RGB')
            direct_image_rgb.save("zalo_qr_direct.pdf")
            print(f"Đã lưu PDF QR trực tiếp tại: {os.path.abspath('zalo_qr_direct.pdf')}")
            
        except Exception as e:
            print(f"Lỗi khi cắt ảnh QR: {str(e)}")
        
    except Exception as e:
        print(f"Lỗi khi chụp mã QR: {str(e)}")
    
    # Khởi động thread cho server FastAPI
    threading.Thread(target=start_server, daemon=True).start()
    
    # Giữ cho chương trình chính không kết thúc
    while True:
        time.sleep(1)