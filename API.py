import requests

# พิกัดของ Aeroklas
latitude = 12.8760497
longitude = 101.0916021

# API Key ของคุณ
api_key = "40efb028358b9bae4bfd0c2643b2a402"

# เรียก API ข้อมูลอากาศแบบปัจจุบัน
url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"

# ส่งคำขอ
response = requests.get(url)

# ตรวจสอบและแสดงผล
if response.status_code == 200:
    data = response.json()
    print("✅ สภาพอากาศที่ Aeroklas:")
    print(f"🌡️ อุณหภูมิ: {data['main']['temp']} °C")
    print(f"🌥️ สภาพอากาศ: {data['weather'][0]['description']}")
    print(f"💧 ความชื้น: {data['main']['humidity']}%")
    print(f"🌬️ ความเร็วลม: {data['wind']['speed']} m/s")
else:
    print("❌ ไม่สามารถดึงข้อมูลได้:", response.status_code)
3
