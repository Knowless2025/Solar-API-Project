import requests
from datetime import datetime, timedelta

# Solcast API URL - ปรับแก้ให้ดึงข้อมูล 24 ชั่วโมง
url = "https://api.solcast.com.au/data/forecast/radiation_and_weather?latitude=12.8760497&longitude=101.0916021&hours=24&output_parameters=ghi&period=PT30M&format=json"

# ใส่ API Key ของคุณตรงนี้
api_key = "KelYCfROII1uii4Bwt-i6zV6XqzGrMqx" # หมายเหตุ: เพื่อความปลอดภัย ควรเก็บ API Key เป็นความลับ

# ค่าระบบของโรงงาน
panel_area_m2 = 37827.32      # พื้นที่แผงรวม (m²)
efficiency = 0.18          # ประสิทธิภาพแผง (18%)
interval_hr = 0.5          # ช่วงเวลาทุก 30 นาที

# ตัวแปรสำหรับเก็บยอดรวมพลังงาน
total_energy_kwh = 0

# ดึงข้อมูลจาก API
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    forecasts = data.get("forecasts", [])

    print("🌞 พยากรณ์แสงอาทิตย์และพลังงานที่คาดว่าจะผลิตได้ (เฉพาะช่วงกลางวัน):\n")
    
    for entry in forecasts:
        # ดึงค่า GHI (Global Horizontal Irradiance)
        ghi = entry.get("ghi", 0)  # W/m²

        # --- กรองข้อมูลเฉพาะช่วงกลางวัน ---
        if ghi > 0:
            # เวลาใน UTC → เปลี่ยนเป็นเวลาไทย
            utc_time = datetime.fromisoformat(entry["period_end"].replace("Z", "+00:00"))
            thai_time = utc_time + timedelta(hours=7)
            time_str = thai_time.strftime('%Y-%m-%d %H:%M')

            # คำนวณพลังงานที่ผลิตได้ (kWh) ในแต่ละช่วงเวลา
            energy_kwh = (ghi * panel_area_m2 * efficiency * interval_hr) / 1000
            
            # --- บวกค่าพลังงานเข้ายอดรวม ---
            total_energy_kwh += energy_kwh

            print(f"เวลา: {time_str} | GHI: {ghi:<4.0f} W/m² | พลังงานที่คาดว่าจะได้: {energy_kwh:>6.2f} kWh")

    # --- แสดงผลสรุป ---
    print("\n" + "="*50)
    print(f"✅ สรุปพลังงานที่คาดว่าจะผลิตได้ทั้งหมดในวันนี้: {total_energy_kwh:.2f} kWh")
    print("="*50)

else:
    print(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูล: {response.status_code} - {response.text}")