import dash
import pandas as pd
from dash import dcc, html, Input, Output, callback
import plotly.express as px

from modules.analysis_module import calculate_growth

# ลงทะเบียน page
dash.register_page(__name__, path="/analysis")

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv("data/cleaned_data.csv")

# แปลงปีงบประมาณให้เป็น int
df["ปีงบประมาณ"] = df["ปีงบประมาณ"].astype(int)

# คำนวณ Growth
growth_df = calculate_growth(df)

# Top 5 โตสูงสุด
top5 = growth_df.sort_values("growth_percent", ascending=False).head(5)

# ---------------- FIGURES ---------------- #

fig_growth = px.bar(
    growth_df,
    x="อำเภอ",
    y="growth_percent",
    title="อัตราการเติบโตของรายได้ OTOP (%)",
    template="plotly_white"
)

fig_growth.update_layout(
    font=dict(family="Prompt"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=40, t=60, b=40)
)

fig_top5 = px.bar(
    top5,
    x="อำเภอ",
    y="growth_percent",
    title="Top 5 อำเภอที่เติบโตสูงสุด",
    template="plotly_white"
)

fig_top5.update_layout(
    font=dict(family="Prompt"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=40, t=60, b=40)
)

# ---------------- LAYOUT ---------------- #

layout = html.Div([

    # Dropdown
    html.Div([

        html.Label(
            "เลือกอำเภอ",
            style={"fontFamily": "Prompt", "fontSize": "18px"}
        ),

        dcc.Dropdown(
            id="district-dropdown-analysis",
            options=[{"label": i, "value": i} for i in df["อำเภอ"].unique()],
            value=df["อำเภอ"].unique()[0]
        )

    ], className="dropdown-box"),

    # กราฟใหญ่

    html.Div([

        html.Div([
            dcc.Graph(id="income-chart")
        ], className="card big-chart")

    ], className="big-chart-container"),

    # กราฟล่าง

    html.Div([

        html.Div([
            dcc.Graph(figure=fig_growth)
        ], className="card graph-box"),

        html.Div([
            dcc.Graph(figure=fig_top5)
        ], className="card graph-box"),

    ], className="graph-row")

])

# ---------------- CALLBACK ---------------- #

@callback(
    Output("income-chart", "figure"),
    Input("district-dropdown-analysis", "value")
)
def update_chart(selected_district):

    filtered_df = df[df["อำเภอ"] == selected_district]

    fig = px.line(
        filtered_df,
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        markers=True,
        title=f"รายได้ OTOP ของ {selected_district}",
        template="plotly_white"
    )

    fig.update_layout(
        font=dict(family="Prompt"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    fig.update_xaxes(type="category")

    return fig