import pandas as pd
import numpy as np
import os
from pycaret.regression import setup, compare_models, finalize_model, predict_model

print("===== AI Engine: เริ่มการพยากรณ์รายอำเภอ =====")

# รายชื่ออำเภอสงขลา 16 อำเภอ
ALL_DISTRICTS = [
    "เมืองสงขลา",
    "หาดใหญ่",
    "จะนะ",
    "เทพา",
    "สะเดา",
    "นาทวี",
    "ระโนด",
    "สิงหนคร",
    "สะบ้าย้อย",
    "รัตภูมิ",
    "บางกล่ำ",
    "ควนเนียง",
    "คลองหอยโข่ง",
    "นาหม่อม",
    "สทิงพระ",
    "กระแสสินธุ์",
]

# โหลดข้อมูล
try:
    df = pd.read_csv("data/cleaned_data.csv")
    df.columns = df.columns.str.strip()

    df["อำเภอ"] = (
        df["อำเภอ"]
        .astype(str)
        .str.replace("อำเภอ", "")
        .str.replace("อ.", "")
        .str.strip()
    )

    df["ค่าข้อมูล"] = pd.to_numeric(df["ค่าข้อมูล"], errors="coerce").fillna(0)
    df["ปีงบประมาณ"] = pd.to_numeric(df["ปีงบประมาณ"], errors="coerce").fillna(0)

except:
    df = pd.DataFrame(columns=["อำเภอ", "ปีงบประมาณ", "ค่าข้อมูล"])

# แปลงประเภทข้อมูล
df["ปีงบประมาณ"] = pd.to_numeric(df["ปีงบประมาณ"], errors="coerce")
df["ค่าข้อมูล"] = pd.to_numeric(df["ค่าข้อมูล"], errors="coerce")

df = df.dropna()
df = df[df["ค่าข้อมูล"] >= 0]

# ปีล่าสุด
last_year = int(df["ปีงบประมาณ"].max())
future_years = [last_year + 1, last_year + 2, last_year + 3]

print(f"ปีล่าสุด: {last_year}")
print(f"พยากรณ์ถึงปี: {future_years}")

forecast_results = []

# วนทุกอำเภอ (บังคับครบ 16)
for district in ALL_DISTRICTS:

    print(f"\nกำลังพยากรณ์: {district}")

    district_data = (
        df[df["อำเภอ"] == district].groupby("ปีงบประมาณ")["ค่าข้อมูล"].sum().reset_index()
    )

    # ถ้ามีข้อมูลอย่างน้อย 2 ปี
    if len(district_data) >= 2:

        train_df = district_data.rename(
            columns={"ปีงบประมาณ": "year", "ค่าข้อมูล": "revenue"}
        )

        try:

            setup(
                data=train_df,
                target="revenue",
                session_id=42,
                fold=2,
                verbose=False,
                html=False,
            )

            best_model = compare_models()

            final_model = finalize_model(best_model)

            future_df = pd.DataFrame({"year": future_years})

            predictions_df = predict_model(final_model, data=future_df)

            predictions = predictions_df["prediction_label"].values

            for i, val in enumerate(predictions):

                forecast_results.append(
                    {
                        "อำเภอ": district,
                        "ปีงบประมาณ": future_years[i],
                        "prediction_label": float(val),
                    }
                )

        except Exception as e:

            print(f"AI Error -> ใช้ค่าเฉลี่ยแทน ({district})")

            avg_val = district_data["ค่าข้อมูล"].mean()

            for y in future_years:

                forecast_results.append(
                    {
                        "อำเภอ": district,
                        "ปีงบประมาณ": y,
                        "prediction_label": float(avg_val),
                    }
                )

    # ถ้าข้อมูลน้อย
    else:

        print(f"ข้อมูลน้อย -> ใช้ค่าล่าสุด ({district})")

        if not district_data.empty:
            last_val = district_data["ค่าข้อมูล"].iloc[-1]
        else:
            last_val = 0

        for y in future_years:

            forecast_results.append(
                {
                    "อำเภอ": district,
                    "ปีงบประมาณ": y,
                    "prediction_label": float(last_val),
                }
            )

# สร้าง DataFrame ผลลัพธ์
forecast_df = pd.DataFrame(forecast_results)

# สร้างโฟลเดอร์ถ้าไม่มี
os.makedirs("data", exist_ok=True)

# บันทึกไฟล์
forecast_df.to_csv("data/forecast.csv", index=False)

print("\n===== บันทึก forecast.csv สำเร็จ =====")
print(f"จำนวนข้อมูลพยากรณ์: {len(forecast_df)} แถว")

print("\nตัวอย่างข้อมูล:")
print(forecast_df.head())
