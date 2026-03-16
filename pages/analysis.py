import dash
import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px

from modules.analysis_module import calculate_growth

dash.register_page(__name__, path="/analysis")

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv("data/cleaned_data.csv")
df["ปีงบประมาณ"] = df["ปีงบประมาณ"].astype(int)

growth_df = calculate_growth(df)
growth_df = growth_df.sort_values("growth_percent", ascending=False)

top5 = growth_df.head(5)

# ---------------- KPI ---------------- #

avg_growth = round(growth_df["growth_percent"].mean(), 2)
max_row = growth_df.loc[growth_df["growth_percent"].idxmax()]
min_row = growth_df.loc[growth_df["growth_percent"].idxmin()]

positive_growth = growth_df[growth_df["growth_percent"] > 0].shape[0]
negative_growth = growth_df[growth_df["growth_percent"] < 0].shape[0]

# ---------------- DROPDOWN ---------------- #

district_options = [{"label": d, "value": d} for d in growth_df["อำเภอ"]]

# ---------------- DONUT CHART ---------------- #

status_df = pd.DataFrame({
    "สถานะ": ["รายได้เพิ่มขึ้น", "รายได้ลดลง"],
    "จำนวน": [positive_growth, negative_growth]
})

fig_donut = px.pie(
    status_df,
    names="สถานะ",
    values="จำนวน",
    hole=0.55,
    title="สัดส่วนการเติบโตของอำเภอ",
    template="plotly_white"
)

fig_donut.update_layout(
    height=420,
    font=dict(family="Prompt", size=16)
)

# ---------------- TOP 5 CHART ---------------- #

fig_top5 = px.bar(
    top5,
    x="อำเภอ",
    y="growth_percent",
    title="5 อำเภอที่มีการเติบโตสูงสุด",
    template="plotly_white",
    color="growth_percent",
    color_continuous_scale=["orange","green"]
)

fig_top5.update_layout(
    height=420,
    font=dict(family="Prompt", size=16),
    coloraxis_showscale=False
)

fig_top5.update_xaxes(tickangle=0)

# ---------------- LAYOUT ---------------- #

layout = html.Div([

    # KPI
    html.Div([

        html.Div([
            html.P("Average Growth"),
            html.H3(f"{avg_growth}%")
        ], className="card kpi-small"),

        html.Div([
            html.P("Highest Growth"),
            html.H3(max_row["อำเภอ"])
        ], className="card kpi-small"),

        html.Div([
            html.P("Lowest Growth"),
            html.H3(min_row["อำเภอ"])
        ], className="card kpi-small"),

        html.Div([
            html.P("Growing Districts"),
            html.H3(positive_growth)
        ], className="card kpi-small"),

        html.Div([
            html.P("Declining Districts"),
            html.H3(negative_growth)
        ], className="card kpi-small"),

    ], style={
        "display":"grid",
        "gridTemplateColumns":"repeat(5,1fr)",
        "gap":"12px",
        "marginBottom":"25px"
    }),

    # Dropdown
    html.Div([
        html.H5("เลือกอำเภอเพื่อดูข้อมูล"),
        dcc.Dropdown(
            id="district_filter",
            options=district_options,
            placeholder="เลือกอำเภอ",
            clearable=True
        )
    ], style={"width":"300px","marginBottom":"25px"}),

    # ---------------- ROW 1 : BIG GROWTH CHART ---------------- #

    html.Div([
        dcc.Graph(id="growth_chart")
    ]),

    # ---------------- ROW 2 : DONUT + TOP5 ---------------- #

    html.Div([

        html.Div([
            dcc.Graph(figure=fig_donut)
        ], style={"width":"50%"}),

        html.Div([
            dcc.Graph(figure=fig_top5)
        ], style={"width":"50%"})

    ], style={
        "display":"flex",
        "gap":"20px",
        "marginTop":"20px"
    }),

    # ---------------- ROW 3 : INSIGHT ---------------- #

    html.Div([

        html.H4("Key Insights"),

        html.Ul([

            html.Li(
                f"อำเภอ {max_row['อำเภอ']} มีอัตราการเติบโตของรายได้ OTOP สูงที่สุด "
                f"ประมาณ {round(max_row['growth_percent'],2)}%"
            ),

            html.Li(
                f"อำเภอ {min_row['อำเภอ']} มีอัตราการเติบโตต่ำที่สุด "
                f"ประมาณ {round(min_row['growth_percent'],2)}%"
            ),

            html.Li(
                f"อัตราการเติบโตเฉลี่ยของรายได้ OTOP ทุกอำเภออยู่ที่ {avg_growth}%"
            ),

            html.Li(
                f"จำนวนอำเภอที่รายได้เพิ่มขึ้นมีทั้งหมด {positive_growth} อำเภอ"
            ),

            html.Li(
                f"จำนวนอำเภอที่รายได้ลดลงมีทั้งหมด {negative_growth} อำเภอ"
            )

        ])

    ], className="card insight-box", style={"marginTop":"25px"})

])

# ---------------- CALLBACK ---------------- #

@dash.callback(
    Output("growth_chart","figure"),
    Input("district_filter","value")
)

def update_chart(selected):

    data = growth_df

    if selected:
        data = growth_df[growth_df["อำเภอ"] == selected]

    fig = px.bar(
        data,
        x="อำเภอ",
        y="growth_percent",
        title="อัตราการเติบโตของรายได้ OTOP รายอำเภอ",
        template="plotly_white",
        color="growth_percent",
        color_continuous_scale=["red","orange","green"]
    )

    fig.update_layout(
        height=500,
        font=dict(family="Prompt", size=16),
        coloraxis_showscale=False
    )
    
    fig.update_xaxes(
        tickangle=0,
        tickfont=dict(size=13)   # ลดขนาดชื่ออำเภอ
    )
    return fig