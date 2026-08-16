import time
import re
import requests
import schedule
import undetected_chromedriver as uc

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1538142964058947596/wCemqcX7ToLAnlMH2gaSOhnQ_Ibi1XAqyG92WAvhWv8xYjcqnk8M2CaZw-26M7pCJZNU'
BUY_PAGE_URL = "https://www.samsung.com/sec/smartphones/galaxy-s26-ultra/buy/?modelCode=SM-S948NZVBKOO"

last_price = None

def send_discord_msg(msg):
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
    except Exception as e:
        print("디스코드 전송 실패:", e)

def check_samsung_price():
    global last_price
    print("삼성닷컴 S26 Ultra (256GB) 가격 확인 중...")
    
    options = uc.ChromeOptions()
    options.add_argument("--headless=new") # 서버용 무헤드 옵션
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    driver = None
    try:
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
            
            if last_price is None:
                last_price = current_price
                init_text = (
                    f"🚀 **삼성닷컴 갤럭시 S26 Ultra (256GB)**\n"
                    f"현재 최대혜택가: **{current_price:,}원**\n"
                    f"구매 링크: {BUY_PAGE_URL}"
                )
                send_discord_msg(init_text)
            elif current_price != last_price:
                price_diff = current_price - last_price
                diff_str = f"({price_diff:+,}원)"
                
                alert_text = (
                    f"@everyone 🔔 **삼성닷컴 갤럭시 S26 Ultra (256GB) 가격 변동 감지!**\n"
                    f"이전 가격: {last_price:,}원\n"
                    f"현재 가격: **{current_price:,}원** {diff_str}\n"
                    f"구매 링크: {BUY_PAGE_URL}"
                )
                send_discord_msg(alert_text)
                last_price = current_price
            else:
                print("가격 변동 없음")
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

schedule.every().day.at("10:00").do(check_samsung_price)

if __name__ == '__main__':
    print("서버 가동 시작 (매일 10시 정기 점검)")
    check_samsung_price()
    
    while True:
        schedule.run_pending()
        time.sleep(1)