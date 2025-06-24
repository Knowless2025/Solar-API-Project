import requests
from datetime import datetime, timedelta
import schedule
import time
import os

# --- 1. CONFIGURATION (กรุณาตั้งค่าตัวแปรในส่วนนี้) ---

# API Keys & IDs
# หมายเหตุ: เพื่อความปลอดภัยในการใช้งานจริง ควรเก็บ Key เป็น Environment Variables
# แทนการใส่ในโค้ดโดยตรง
SOLCAST_API_KEY = "KelYCfROII1uii4Bwt-i6zV6XqzGrMqx"
OPENWEATHER_API_KEY = "40efb028358b9bae4bfd0c2643b2a402" 
TELEGRAM_BOT_TOKEN = "7165717388:AAEpj8xC8dlBc9GruW-9iNqTKNWDvYS3Uh8"
TELEGRAM_CHAT_ID = "7738622893" # <-- 🚧 หากเป็น ID กลุ่ม, ต้องขึ้นต้นด้วย - (เช่น "-100123456789")

# Location Coordinates
LATITUDE = 12.8760497
LONGITUDE = 101.0916021

# Solar Panel System Parameters
PANEL_AREA_M2 = 37827.32
EFFICIENCY = 0.15
INTERVAL_HR = 0.5


# --- 2. FUNCTIONS (ส่วนของฟังก์ชันการทำงาน) ---

def get_solar_forecast():
    """
    ดึงข้อมูลพยากรณ์การผลิตพลังงานแสงอาทิตย์จาก Solcast API
    และคำนวณพลังงานรวมที่คาดว่าจะผลิตได้ในหน่วย kWh
    """
    print("Fetching Solcast forecast...")
    url = f"https://api.solcast.com.au/data/forecast/radiation_and_weather?latitude={LATITUDE}&longitude={LONGITUDE}&hours=24&output_parameters=ghi&period=PT30M&format=json"
    headers = {"Authorization": f"Bearer {SOLCAST_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # หาก Status Code ไม่ใช่ 2xx จะเกิด Exception

        data = response.json()
        forecasts = data.get("forecasts", [])
        total_energy_kwh = 0

        for entry in forecasts:
            ghi = entry.get("ghi", 0)
            if ghi > 0:
                # คำนวณพลังงานที่ผลิตได้ในแต่ละช่วงเวลา
                energy_kwh = (ghi * PANEL_AREA_M2 * EFFICIENCY * INTERVAL_HR) / 1000
                total_energy_kwh += energy_kwh
        
        print(f"Solcast forecast successful. Total estimated energy: {total_energy_kwh:.2f} kWh")
        return total_energy_kwh

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching Solcast data: {e}")
        return None

def get_current_weather():
    """
    ดึงข้อมูลสภาพอากาศปัจจุบันจาก OpenWeatherMap API
    และสร้างข้อความสรุปสภาพอากาศ
    """
    print("Fetching current weather...")
    # เพิ่ม &lang=th เพื่อให้คำอธิบายสภาพอากาศเป็นภาษาไทย
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHER_API_KEY}&units=metric&lang=th"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        description = data['weather'][0]['description'].capitalize()
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        
        # จัดรูปแบบข้อความสรุป
        weather_summary = (
            f"ท้องฟ้า: {description}\n"
            f"อุณหภูมิ: {temp}°C\n"
            f"ความชื้น: {humidity}%"
        )
        print("OpenWeatherMap data successful.")
        return weather_summary

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching OpenWeatherMap data: {e}")
        return "ไม่สามารถดึงข้อมูลสภาพอากาศได้"
    except (KeyError, IndexError):
        print("❌ Error parsing weather data. Check API response format.")
        return "ไม่สามารถแปลข้อมูลสภาพอากาศได้"


def send_telegram_message(message_text):
    """
    ส่งข้อความที่กำหนดไปยัง Telegram Bot โดยใช้ Parse Mode เป็น Markdown
    """
    print("Sending message to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown" # ใช้ Markdown เพื่อจัดรูปแบบข้อความ (ตัวหนา, ตัวเอียง)
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Message sent successfully to Telegram!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending message to Telegram: {e}\nResponse: {e.response.text}")


# --- 3. MAIN JOB (ส่วนการทำงานหลัก) ---

def create_and_send_report():
    """
    สร้างรายงานโดยการดึงข้อมูลจาก API ทั้งสอง และส่งไปยัง Telegram
    """
    print("\n--- Running daily report job ---")
    # ตั้งค่าโซนเวลาเป็นของไทย (UTC+7) สำหรับแสดงวันที่
    thai_time = datetime.utcnow() + timedelta(hours=7)
    today_str = thai_time.strftime('%d %B %Y')
    
    total_energy = get_solar_forecast()
    weather_info = get_current_weather()
    
    if total_energy is not None:
        # สร้างข้อความสรุปสำหรับวันที่ดึงข้อมูลสำเร็จ
        message = (
            f"☀️ *พยากรณ์การผลิตไฟฟ้าพลังงานแสงอาทิตย์*\n"
            f"📅 *ประจำวันที่: {today_str}*\n"
            f"----------------------------------------\n"
            f"⚡️ *พลังงานที่คาดว่าจะผลิตได้ทั้งหมด:*\n"
            f"`{total_energy:,.2f} kWh`\n\n"
            f"🌦️ *สภาพอากาศปัจจุบัน:*\n"
            f"{weather_info}\n"
            f"----------------------------------------\n"
            f"_Automation by AEI Dept._"
        )
    else:
        # สร้างข้อความแจ้งเตือนเมื่อดึงข้อมูล Solcast ไม่สำเร็จ
        message = (
            f"⚠️ *แจ้งเตือน: ไม่สามารถดึงข้อมูลพยากรณ์ได้*\n"
            f"📅 *วันที่: {today_str}*\n"
            f"เกิดข้อผิดพลาดในการเชื่อมต่อกับ Solcast API กรุณาตรวจสอบระบบ"
        )
        
    send_telegram_message(message)
    print("--- Job finished ---")


# --- 4. SCHEDULER (ส่วนการตั้งเวลา) ---

if __name__ == "__main__":
    print("🚀 Automation script started. Waiting for scheduled time...")
    
    # --- สำหรับทดสอบการทำงานทันที (เอา comment ด้านล่างออกเพื่อทดสอบ) ---
    create_and_send_report()
    
    # --- ตั้งเวลาให้ทำงานทุกวัน เวลา 06:00 น. ---
    # เวลาที่ตั้งนี้จะเป็นเวลาของเครื่องที่รันสคริปต์
    schedule.every().day.at("06:00").do(create_and_send_report)
    
    # Loop เพื่อให้โปรแกรมทำงานและรอเวลาที่กำหนด
    while True:
        schedule.run_pending()
        time.sleep(1)
