import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

# พารามิเตอร์ระบบ
panel_area_m2 = 40000
efficiency = 0.18
interval_hr = 0.5

# URL สำหรับดึงข้อมูลย้อนหลัง 7 วัน
url = (
    "https://api.solcast.com.au/data/live/radiation_and_weather"
    "?latitude=12.8760497&longitude=101.0916021"
    "&hours=168&output_parameters=ghi,dni,air_temp"
    "&period=PT30M&format=csv"
)

# API Key
api_key = "KelYCfROII1uii4Bwt-i6zV6XqzGrMqx"
headers = {"Authorization": f"Bearer {api_key}"}

# ดึงข้อมูล
response = requests.get(url, headers=headers)
if response.status_code == 200:
    csv_data = response.text
    df = pd.read_csv(StringIO(csv_data))

    total_energy_kwh = 0
    print("☀️ ปริมาณ GHI และพลังงานย้อนหลัง 7 วัน\n")

    for _, row in df.iterrows():
        ghi = row.get("ghi", 0)
        if ghi > 0:
            utc_time = datetime.fromisoformat(row["period_end"].replace("Z", "+00:00"))
            thai_time = utc_time + timedelta(hours=7)
            time_str = thai_time.strftime('%Y-%m-%d %H:%M')

            energy_kwh = (ghi * panel_area_m2 * efficiency * interval_hr) / 1000
            total_energy_kwh += energy_kwh

            print(f"เวลา: {time_str} | GHI: {ghi:.0f} W/m² | พลังงาน: {energy_kwh:>6.2f} kWh")

    print("\n" + "="*60)
    print(f"✅ รวมพลังงานย้อนหลัง 7 วัน: {total_energy_kwh:.2f} kWh")
    print("="*60)

else:
    print(f"❌ ไม่สามารถดึงข้อมูล CSV: {response.status_code} - {response.text}")
