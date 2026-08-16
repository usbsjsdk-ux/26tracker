import time
import re
import requests
import subprocess
import undetected_chromedriver as uc

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1538142964058947596/wCemqcX7ToLAnlMH2gaSOhnQ_Ibi1XAqyG92WAvhWv8xYjcqnk8M2CaZw-26M7pCJZNU'
BUY_PAGE_URL = "https://www.samsung.com/sec/smartphones/galaxy-s26-ultra/buy/?modelCode=SM-S948NZVBKOO"

def send_discord_msg(msg):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
    except Exception as e:
        print("디스코드 전송 실패:", e)

def get_chrome_version():
    try:
        # 서버(리눅스) 환경에 설치된 크롬 메이저 버전 자동 추출
        version_str = subprocess.check_output(['google-chrome', '--version']).decode('utf-8')
        return int(version_str.strip().split()[2].split('.')[0])
    except:
        return None

def check_samsung_price():
    print("삼성닷컴 S26 Ultra (256GB) 가격 확인 중...")
    
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    v_main = get_chrome_version()
    if v_main:
        print(f"감지된 크롬 버전: {v_main}")
    
    driver = None
    try:
        # 감지된 크롬 버전에 맞춰서 드라이버 강제 실행
        if v_main:
            driver = uc.Chrome(options=options, version_main=v_main)
        else:
            driver = uc.Chrome(options=options)
            
        driver.get(BUY_PAGE_URL)
        time.sleep(7)
        
        price_elements = driver.find_elements("css selector", ".total-price, .price, span, strong, em")
        valid_prices = []
        for elem in price_elements:
            try:
                text = elem.text.strip()
                matches = re.findall(r'([\d,]{7,10})\s*원', text)
                for m in matches:
                    num = int(m.replace(',', ''))
                    if 1000000 <= num <= 2500000:
                        valid_prices.append(num)
            except:
                continue

        current_price = None
        if valid_prices:
            current_price = min(valid_prices)

        if current_price:
            print(f"현재 가격: {current_price:,}원")
            init_text = (
                f"🚀 **삼성닷컴 갤럭시 S26 Ultra (256GB)**\n"
                f"현재 최대혜택가: **{current_price:,}원**\n"
                f"구매 링크: {BUY_PAGE_URL}"
            )
            send_discord_msg(init_text)
        else:
            print("가격을 못 가져옴")
            
    except Exception as e:
        print("에러 발생:", e)
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == '__main__':
    check_samsung_price()
