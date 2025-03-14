from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def main():
    try:
        # Tự động tải và cài đặt ChromeDriver
        service = Service(ChromeDriverManager().install())
        
        # Khởi tạo Chrome WebDriver
        driver = webdriver.Chrome(service=service)
        
        # Mở trang Google
        driver.get("https://www.google.com")
        
        # Đợi 5 giây để bạn có thể thấy trang web
        time.sleep(5)
        
        # In tiêu đề trang web
        print("Tiêu đề trang:", driver.title)
        
    except Exception as e:
        print(f"Đã xảy ra lỗi: {str(e)}")
        
    finally:
        # Đóng trình duyệt
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()