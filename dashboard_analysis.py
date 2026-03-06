import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

from modules.analysis_module import calculate_growth

# โหลดข้อมูล
df = pd.read_csv("data/cleaned_data.csv")

# คำนวณ growth
growth_df = calculate_growth(df)

# หา Top 5 อำเภอที่เติบโตมากที่สุด
top5 = growth_df.sort_values("growth_percent", ascending=False).head(5)

# กราฟที่ 1: ทุกอำเภอ
fig = px.bar(
    growth_df,
    x="อำเภอ",
    y="growth_percent",
    title="อัตราการเติบโตของรายได้ OTOP แต่ละอำเภอ (%)"
)

# กราฟที่ 2: Top 5 อำเภอที่โตที่สุด
fig2 = px.bar(
    top5,
    x="อำเภอ",
    y="growth_percent",
    title="Top 5 อำเภอที่รายได้ OTOP โตที่สุด"
)

# สร้าง Dash app
app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1(
        "OTOP Sales Growth Dashboard",
        style={"textAlign": "center"}
    ),

    # กราฟทั้งหมด
    dcc.Graph(
        id="growth-chart",
        figure=fig
    ),

    # กราฟ Top 5
    dcc.Graph(
        id="top5-chart",
        figure=fig2
    )

])

if __name__ == "__main__":
    app.run(debug=True)