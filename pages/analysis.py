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

# ---------------- DROPDOWN OPTIONS ---------------- #

district_options = [{"label": d, "value": d} for d in growth_df["อำเภอ"]]

# ---------------- FIGURE TOP5 ---------------- #

fig_top5 = px.bar(
    top5,
    x="อำเภอ",
    y="growth_percent",
    title="Top 5 Fastest Growing Districts",
    template="plotly_white",
    color="growth_percent",
    color_continuous_scale=["orange", "green"]
)

fig_top5.update_layout(height=350)

# ---------------- DONUT ---------------- #

status_df = pd.DataFrame({
    "status": ["Growing", "Declining"],
    "count": [positive_growth, negative_growth]
})

fig_donut = px.pie(
    status_df,
    names="status",
    values="count",
    hole=0.5,
    title="District Growth Status",
    template="plotly_white"
)

fig_donut.update_layout(height=350)

# ---------------- LAYOUT ---------------- #

layout = html.Div([

    # KPI
    html.Div([

        html.Div([
            html.H6("Average Growth"),
            html.H3(f"{avg_growth}%")
        ], className="card kpi-small"),

        html.Div([
            html.H6("Highest Growth"),
            html.H3(max_row["อำเภอ"])
        ], className="card kpi-small"),

        html.Div([
            html.H6("Lowest Growth"),
            html.H3(min_row["อำเภอ"])
        ], className="card kpi-small"),

        html.Div([
            html.H6("Growing Districts"),
            html.H3(positive_growth)
        ], className="card kpi-small"),

        html.Div([
            html.H6("Declining Districts"),
            html.H3(negative_growth)
        ], className="card kpi-small"),

    ], style={
        "display":"grid",
        "gridTemplateColumns":"repeat(5,1fr)",
        "gap":"10px",
        "marginBottom":"20px"
    }),

    # Dropdown Filter
    html.Div([
        html.H5("Select District"),
        dcc.Dropdown(
            id="district_filter",
            options=district_options,
            placeholder="Choose district",
            clearable=True
        )
    ], style={"width":"300px","marginBottom":"20px"}),

    # Graph Row
    html.Div([

        html.Div([
            dcc.Graph(id="growth_chart")
        ], style={"width":"60%"}),

        html.Div([
            dcc.Graph(figure=fig_donut)
        ], style={"width":"40%"})

    ], style={"display":"flex","gap":"20px"}),

    # Second Row
    html.Div([

        html.Div([
            dcc.Graph(figure=fig_top5)
        ], style={"width":"50%"}),

    ], style={"display":"flex","marginTop":"20px"}),

    html.Div([

    html.H4("Insight", style={"fontFamily":"Prompt"}),

    html.P(
        f"จากการวิเคราะห์ข้อมูลรายได้สินค้า OTOP พบว่าอำเภอ {max_row['อำเภอ']} "
        f"มีอัตราการเติบโตของรายได้สูงที่สุด โดยมีการเพิ่มขึ้นประมาณ "
        f"{round(max_row['growth_percent'],2)}% ซึ่งสะท้อนถึงศักยภาพทางเศรษฐกิจ "
        "และการพัฒนาผลิตภัณฑ์ในพื้นที่ดังกล่าว"
    ),

    html.P(
        f"ในทางตรงกันข้าม อำเภอ {min_row['อำเภอ']} มีอัตราการเติบโตของรายได้ต่ำที่สุด "
        f"ประมาณ {round(min_row['growth_percent'],2)}% ซึ่งอาจสะท้อนถึงข้อจำกัดด้านตลาด "
        "การพัฒนาผลิตภัณฑ์ หรือปัจจัยทางเศรษฐกิจในพื้นที่"
    ),

    html.P(
        f"โดยภาพรวม อัตราการเติบโตเฉลี่ยของรายได้สินค้า OTOP ในทุกอำเภออยู่ที่ "
        f"{avg_growth}% แสดงให้เห็นว่าการพัฒนาทางเศรษฐกิจในแต่ละพื้นที่มีความแตกต่างกัน"
    ),

    html.P(
        f"จากการวิเคราะห์ยังพบว่า มีอำเภอที่มีแนวโน้มรายได้เติบโตจำนวน "
        f"{positive_growth} อำเภอ และมีอำเภอที่รายได้ลดลงจำนวน "
        f"{negative_growth} อำเภอ ซึ่งข้อมูลดังกล่าวสามารถนำไปใช้ประกอบการวางแผน "
        "พัฒนาเศรษฐกิจชุมชนในอนาคตได้"
    )

], className="card insight-box")
])

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
        title="OTOP Revenue Growth by District",
        template="plotly_white",
        color="growth_percent",
        color_continuous_scale=["red","orange","green"]
    )

    fig.update_layout(height=350)

    return fig