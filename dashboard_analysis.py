import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

from modules.analysis_module import calculate_growth

# โหลดข้อมูล
df = pd.read_csv("data/cleaned_data.csv")

# คำนวณ growth
growth_df = calculate_growth(df)

# Top 5 อำเภอที่โตที่สุด
top5 = growth_df.sort_values("growth_percent", ascending=False).head(5)

# กราฟ Growth ทุกอำเภอ
fig_growth = px.bar(
    growth_df,
    x="อำเภอ",
    y="growth_percent",
    title="อัตราการเติบโตของรายได้ OTOP แต่ละอำเภอ (%)"
)

# กราฟ Top5
fig_top5 = px.bar(
    top5,
    x="อำเภอ",
    y="growth_percent",
    title="Top 5 อำเภอที่รายได้ OTOP เติบโตสูงสุด"
)

# สร้าง Dash app
app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1(
        "OTOP Sales Growth Dashboard",
        style={"textAlign": "center"}
    ),

    # Dropdown เลือกอำเภอ
    html.Label("เลือกอำเภอ"),

    dcc.Dropdown(
        id="district-dropdown",
        options=[{"label": i, "value": i} for i in df["อำเภอ"].unique()],
        value=df["อำเภอ"].unique()[0]
    ),

    # กราฟรายได้รายปี
    dcc.Graph(id="income-chart"),

    # กราฟ Growth
    dcc.Graph(
        id="growth-chart",
        figure=fig_growth
    ),

    # กราฟ Top5
    dcc.Graph(
        id="top5-chart",
        figure=fig_top5
    )

])

# callback สำหรับ dropdown
@app.callback(
    Output("income-chart", "figure"),
    Input("district-dropdown", "value")
)

def update_chart(selected_district):

    filtered_df = df[df["อำเภอ"] == selected_district]

    fig = px.line(
        filtered_df,
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        title=f"รายได้ OTOP ของอำเภอ {selected_district}"
    )

    return fig


if __name__ == "__main__":
    app.run(debug=True)