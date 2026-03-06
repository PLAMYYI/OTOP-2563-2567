import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

from modules.analysis_module import calculate_growth

# โหลดข้อมูล
df = pd.read_csv("data/cleaned_data.csv")

# แปลงปีงบประมาณให้เป็นจำนวนเต็ม
df["ปีงบประมาณ"] = df["ปีงบประมาณ"].astype(int)

# คำนวณอัตราการเติบโต
growth_df = calculate_growth(df)

# Top 5 อำเภอที่โตที่สุด
top5 = growth_df.sort_values("growth_percent", ascending=False).head(5)

# กราฟ growth ทุกอำเภอ
fig_growth = px.bar(
    growth_df,
    x="อำเภอ",
    y="growth_percent",
    title="อัตราการเติบโตของรายได้ OTOP"
)

# กราฟ top 5
fig_top5 = px.bar(
    top5,
    x="อำเภอ",
    y="growth_percent",
    title="Top 5 อำเภอที่เติบโตสูงสุด"
)

# สร้าง Dash app
app = dash.Dash(__name__)

app.layout = html.Div([

    html.Div(
        "OTOP Sales Growth Dashboard",
        className="dashboard-title"
    ),

    html.Div([

        html.Label("เลือกอำเภอ"),

        dcc.Dropdown(
            id="district-dropdown",
            options=[{"label": i, "value": i} for i in df["อำเภอ"].unique()],
            value=df["อำเภอ"].unique()[0]
        )

    ], className="dropdown-box"),

    html.Div([
        dcc.Graph(id="income-chart")
    ], className="card section"),

    html.Div([

        html.Div([
            dcc.Graph(figure=fig_growth)
        ], className="card graph-box"),

        html.Div([
            dcc.Graph(figure=fig_top5)
        ], className="card graph-box"),

    ], className="graph-row")

])


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
        markers=True,
        title=f"รายได้ OTOP ของ {selected_district}"
    )

    # บังคับแกน X เป็น category เพื่อไม่ให้มี .0
    fig.update_xaxes(type="category")

    return fig


if __name__ == "__main__":
    app.run(debug=True)