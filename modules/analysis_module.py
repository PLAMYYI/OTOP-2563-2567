import pandas as pd

def calculate_growth(df):

    result = []

    for district in df["อำเภอ"].unique():

        temp = df[df["อำเภอ"] == district].sort_values("ปีงบประมาณ")

        first = temp.iloc[0]["ค่าข้อมูล"]
        last = temp.iloc[-1]["ค่าข้อมูล"]

        growth = ((last - first) / first) * 100

        result.append({
            "อำเภอ": district,
            "growth_percent": growth
        })

    return pd.DataFrame(result)