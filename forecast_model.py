import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import os

# 1. โหลดข้อมูลจริง (Data Loading)
print("--- [AI Engine] เริ่มต้นกระบวนการพยากรณ์รายอำเภอ ---")
try:
    df = pd.read_csv("data/cleaned_data.csv")
    print(f"โหลดข้อมูลสำเร็จ: พบข้อมูลทั้งหมด {len(df)} แถว")
except FileNotFoundError:
    print("--- [Error] ไม่พบไฟล์ data/cleaned_data.csv กรุณาตรวจสอบโฟลเดอร์ ---")
    exit()

# 2. เตรียมข้อมูลและตั้งค่าตัวแปร
all_districts = df["อำเภอ"].unique()
forecast_results = []
last_year = int(df["ปีงบประมาณ"].max())
# พยากรณ์ล่วงหน้า 3 ปี (เช่น 2568, 2569, 2570)
future_years = np.array([[last_year + 1], [last_year + 2], [last_year + 3]])

print(f"ปีล่าสุดในข้อมูลคือ: {last_year} | กำลังพยากรณ์ถึงปี: {last_year + 3}")

# 3. เริ่มต้นสร้างโมเดลแยกตามอำเภอ (District-wise ML Training)
for district in all_districts:
    # กรองข้อมูลและรวมรายได้รายปีของอำเภอนั้นๆ
    district_data = (
        df[df["อำเภอ"] == district].groupby("ปีงบประมาณ")["ค่าข้อมูล"].sum().reset_index()
    )

    # ตรวจสอบว่ามีข้อมูลเพียงพอต่อการเทรนโมเดลหรือไม่ (ต้องมีอย่างน้อย 2 ปี)
    if len(district_data) >= 2:
        X = district_data[["ปีงบประมาณ"]].values
        y = district_data["ค่าข้อมูล"].values

        # ใช้ Random Forest Regressor (โมเดลระดับสูงที่มีความแม่นยำและทนทานต่อข้อมูลที่ผันผวน)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # ทำนายผลลัพธ์ 3 ปีล่วงหน้า
        predictions = model.predict(future_years)

        # เก็บผลลัพธ์ลงใน List
        for i, pred_val in enumerate(predictions):
            forecast_results.append(
                {
                    "อำเภอ": district,
                    "ปีงบประมาณ": int(future_years[i][0]),
                    "prediction_label": pred_val,
                }
            )
    else:
        print(f"--- [Warning] อำเภอ {district} มีข้อมูลน้อยเกินไป ข้ามการพยากรณ์ ---")

# 4. บันทึกผลลัพธ์ลงไฟล์ CSV
if forecast_results:
    forecast_df = pd.DataFrame(forecast_results)

    # สร้างโฟลเดอร์ data หากยังไม่มี
    if not os.path.exists("data"):
        os.makedirs("data")

    forecast_df.to_csv("data/forecast.csv", index=False)

    print("--- [Success] บันทึกผลพยากรณ์แยกรายอำเภอเรียบร้อยแล้ว ---")
    print(f"ไฟล์ถูกบันทึกที่: data/forecast.csv (จำนวน {len(forecast_df)} รายการ)")

    # แสดงตัวอย่างผลลัพธ์ 5 แถวแรก
    print("\nตัวอย่างข้อมูลพยากรณ์:")
    print(forecast_df.head())
else:
    print("--- [Critical Error] ไม่สามารถสร้างข้อมูลพยากรณ์ได้ ---")
