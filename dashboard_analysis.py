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

# กราฟ Growth ทุกอำเภอ
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

# กราฟ Top 5
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

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([

    # Title
    html.Div(
        "OTOP Sales Growth Dashboard",
        className="dashboard-title"
    ),

    # Dropdown
    html.Div([

        html.Label(
            "เลือกอำเภอ",
            style={"fontFamily": "Prompt", "fontSize": "18px"}
        ),

        dcc.Dropdown(
            id="district-dropdown",
            options=[{"label": i, "value": i} for i in df["อำเภอ"].unique()],
            value=df["อำเภอ"].unique()[0]
        )

    ], className="dropdown-box"),


    # กราฟใหญ่ (อยู่ตรงกลาง)

    html.Div([

        html.Div([
            dcc.Graph(id="income-chart")
        ], className="card big-chart")

    ], className="big-chart-container"),


    # กราฟล่าง 2 อัน

    html.Div([

        html.Div([
            dcc.Graph(figure=fig_growth)
        ], className="card graph-box"),

        html.Div([
            dcc.Graph(figure=fig_top5)
        ], className="card graph-box"),

    ], className="graph-row")

])


# Callback
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
        title=f"รายได้ OTOP ของ {selected_district}",
        template="plotly_white"
    )

    fig.update_layout(
        font=dict(family="Prompt"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # ป้องกันปีเป็นทศนิยม
    fig.update_xaxes(type="category")

    return fig


if __name__ == "__main__":
    app.run(debug=True)