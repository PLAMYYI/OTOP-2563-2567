import dash
import pandas as pd
from dash import dcc, html
import plotly.express as px

from modules.analysis_module import calculate_growth

# ลงทะเบียน page
dash.register_page(__name__, path="/analysis")

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv("data/cleaned_data.csv")
df["ปีงบประมาณ"] = df["ปีงบประมาณ"].astype(int)

# คำนวณ Growth
growth_df = calculate_growth(df)

# เรียงค่ามากไปน้อย
growth_df = growth_df.sort_values("growth_percent", ascending=False)

# Top 5 โตสูงสุด
top5 = growth_df.sort_values("growth_percent", ascending=False).head(5)

# ---------------- KPI ---------------- #

avg_growth = round(growth_df["growth_percent"].mean(), 2)

max_row = growth_df.loc[growth_df["growth_percent"].idxmax()]
min_row = growth_df.loc[growth_df["growth_percent"].idxmin()]

# ---------------- FIGURES ---------------- #

fig_growth = px.bar(
    growth_df,
    x="อำเภอ",
    y="growth_percent",
    title="อัตราการเติบโตของรายได้ OTOP (%)",
    template="plotly_white",
    color="growth_percent",
    color_continuous_scale=["red","orange","green"]
)

# เส้นค่าเฉลี่ย
fig_growth.add_hline(
    y=avg_growth,
    line_dash="dash",
    line_color="blue",
    annotation_text="Average Growth",
    annotation_position="top left"
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

    # KPI CARDS
    html.Div([

        html.Div([
            html.H4("Average Growth"),
            html.H2(f"{avg_growth}%")
        ], className="card kpi"),

        html.Div([
            html.H4("Highest Growth"),
            html.H2(f"{max_row['อำเภอ']} ({round(max_row['growth_percent'],2)}%)")
        ], className="card kpi"),

        html.Div([
            html.H4("Lowest Growth"),
            html.H2(f"{min_row['อำเภอ']} ({round(min_row['growth_percent'],2)}%)")
        ], className="card kpi"),

    ], className="kpi-row"),

    # กราฟ
    html.Div([

        html.Div([
            dcc.Graph(figure=fig_growth)
        ], className="card graph-box"),

        html.Div([
            dcc.Graph(figure=fig_top5)
        ], className="card graph-box"),

    ], className="graph-row"),

    # INSIGHT BOX
    html.Div([

        html.H3("Insight", style={"fontFamily": "Prompt"}),

        html.Ul([

            html.Li(
                f"{max_row['อำเภอ']} เป็นอำเภอที่มีอัตราการเติบโตของรายได้ OTOP สูงที่สุด "
                f"ประมาณ {round(max_row['growth_percent'],2)}%"
            ),

            html.Li(
                "อำเภอที่อยู่ใน Top 5 แสดงให้เห็นถึงพื้นที่ที่มีศักยภาพในการพัฒนา OTOP"
            ),

            html.Li(
                f"{min_row['อำเภอ']} มีการลดลงของรายได้มากที่สุด "
                f"ประมาณ {round(min_row['growth_percent'],2)}%"
            ),

            html.Li(
                f"โดยรวมแล้วอัตราการเติบโตเฉลี่ยของรายได้ OTOP อยู่ที่ {avg_growth}% "
                "แสดงให้เห็นว่าการเติบโตของแต่ละพื้นที่ยังมีความแตกต่างกัน"
            ),

        ])

    ], className="card insight-box")

])