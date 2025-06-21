import requests
from datetime import datetime, timedelta

# ตั้งค่าระบบ
panel_area_m2 = 40000
efficiency = 0.18
interval_hr = 0.5
total_energy_kwh = 0

# เวลาปัจจุบันในไทย
thai_now = datetime.now()

# กำหนดช่วงเวลา 06:00 เมื่อวาน → 06:00 วันนี้
thai_end = thai_now.replace(hour=6, minute=0, second=0, microsecond=0)
if thai_now.hour < 6:
    thai_end -= timedelta(days=1)
thai_start = thai_end - timedelta(days=1)

# แปลงเป็น UTC
utc_start = thai_start - timedelta(hours=7)
utc_end = thai_end - timedelta(hours=7)

# API URL
url = (
    "https://api.solcast.com.au/data/live/radiation_and_weather"
    f"?latitude=12.8760497&longitude=101.0916021"
    f"&start={utc_start.isoformat()}&end={utc_end.isoformat()}"
    "&output_parameters=ghi&period=PT30M&format=json"
)

# API Key
api_key = "KelYCfROII1uii4Bwt-i6zV6XqzGrMqx"
headers = {"Authorization": f"Bearer {api_key}"}

# เรียก API
response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    records = data.get("radiation_and_weather", [])

    print("☀️ GHI ย้อนหลัง 06:00 เมื่อวาน → 06:00 วันนี้\n")

    for entry in records:
        ghi = entry.get("ghi", 0)
        if ghi > 0:
            utc_time = datetime.fromisoformat(entry["period_end"].replace("Z", "+00:00"))
            thai_time = utc_time + timedelta(hours=7)
            time_str = thai_time.strftime('%Y-%m-%d %H:%M')

            energy_kwh = (ghi * panel_area_m2 * efficiency * interval_hr) / 1000
            total_energy_kwh += energy_kwh

            print(f"เวลา: {time_str} | GHI: {ghi:<4.0f} W/m² | พลังงาน: {energy_kwh:>6.2f} kWh")

    print("\n" + "="*60)
    print(f"✅ รวมพลังงานที่ผลิตได้: {total_energy_kwh:.2f} kWh")
    print("="*60)

else:
    print(f"❌ ดึงข้อมูลไม่สำเร็จ: {response.status_code} - {response.text}")
