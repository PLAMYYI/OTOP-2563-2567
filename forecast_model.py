import pandas as pd
import numpy as np
import os
from pycaret.regression import setup, compare_models, finalize_model, predict_model

# 1. โหลดข้อมูลจริง (Data Loading)
print("--- [AI Engine] เริ่มต้นกระบวนการพยากรณ์รายอำเภอ ---")

try:
    df = pd.read_csv("data/cleaned_data.csv")
    print(f"โหลดข้อมูลสำเร็จ: พบข้อมูลทั้งหมด {len(df)} แถว")
except FileNotFoundError:
    print("--- [Error] ไม่พบไฟล์ data/cleaned_data.csv กรุณาตรวจสอบโฟลเดอร์ ---")
    exit()

# 2. เตรียมข้อมูล
all_districts = df["อำเภอ"].unique()
forecast_results = []

last_year = int(df["ปีงบประมาณ"].max())

# พยากรณ์ล่วงหน้า 3 ปี
future_years = np.array([[last_year + 1], [last_year + 2], [last_year + 3]])

print(f"ปีล่าสุดในข้อมูลคือ: {last_year} | กำลังพยากรณ์ถึงปี: {last_year + 3}")

# 3. สร้างโมเดลแยกตามอำเภอ
for district in all_districts:

    district_data = (
        df[df["อำเภอ"] == district]
        .groupby("ปีงบประมาณ")["ค่าข้อมูล"]
        .sum()
        .reset_index()
    )

    # ต้องมีข้อมูลอย่างน้อย 2 ปี
    if len(district_data) >= 2:

        # เตรียม dataframe สำหรับ PyCaret
        train_df = district_data.rename(
            columns={
                "ปีงบประมาณ": "year",
                "ค่าข้อมูล": "revenue"
            }
        )

        # Setup PyCaret
        setup(
            data=train_df,
            target="revenue",
            session_id=42,
            fold=2,
            verbose=False,
            html=False
        )

        # หาโมเดลที่ดีที่สุด
        best_model = compare_models()

        # finalize model
        final_model = finalize_model(best_model)

        # สร้าง dataframe สำหรับปีอนาคต
        future_df = pd.DataFrame({
            "year": future_years.flatten()
        })

        # ทำนาย
        predictions_df = predict_model(final_model, data=future_df)

        predictions = predictions_df["prediction_label"].values

        # เก็บผลลัพธ์
        for i, pred_val in enumerate(predictions):

            forecast_results.append({
                "อำเภอ": district,
                "ปีงบประมาณ": int(future_years[i][0]),
                "prediction_label": pred_val
            })

    else:
        print(f"--- [Warning] อำเภอ {district} มีข้อมูลน้อยเกินไป ข้ามการพยากรณ์ ---")

# 4. บันทึกผลลัพธ์
if forecast_results:

    forecast_df = pd.DataFrame(forecast_results)

    if not os.path.exists("data"):
        os.makedirs("data")

    forecast_df.to_csv("data/forecast.csv", index=False)

    print("--- [Success] บันทึกผลพยากรณ์แยกรายอำเภอเรียบร้อยแล้ว ---")
    print(f"ไฟล์ถูกบันทึกที่: data/forecast.csv (จำนวน {len(forecast_df)} รายการ)")

    print("\nตัวอย่างข้อมูลพยากรณ์:")
    print(forecast_df.head())

else:
    print("--- [Critical Error] ไม่สามารถสร้างข้อมูลพยากรณ์ได้ ---")