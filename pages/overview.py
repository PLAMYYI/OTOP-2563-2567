import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

dash.register_page(__name__, path="/")

# ---------------- LOAD DATA ---------------- #
# ลบการโหลดไฟล์ forecast.csv ออกเนื่องจากเราย้ายไปจัดการใน app.py แทนแล้ว
df = pd.read_csv("data/cleaned_data.csv")

df["ค่าข้อมูล"] = df["ค่าข้อมูล"].astype(int)
df["ปีงบประมาณ"] = df["ปีงบประมาณ"].astype(int)

# ---------------- THEME & CONFIG ---------------- #
COLORS = {
    "primary": "#6366f1",  # Indigo
    "background": "#f8fafc",
    "card_bg": "#ffffff",
    "text": "#1e293b",
    "grid": "rgba(0,0,0,0.05)",
}

graph_config = {
    "scrollZoom": False,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["zoom2d", "select2d", "lasso2d", "autoScale2d"],
}


# ---------------- HELPER FUNCTIONS ---------------- #
def apply_pro_styling(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color=COLORS["text"]),
        title_font=dict(size=18, color=COLORS["text"]),
        margin=dict(l=40, r=20, t=60, b=40),
        hovermode="closest",
    )
    fig.update_xaxes(
        showgrid=True, gridcolor=COLORS["grid"], gridwidth=1, zeroline=False
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=COLORS["grid"], gridwidth=1, zeroline=False
    )
    return fig


# ---------------- STYLES ---------------- #
CARD_STYLE = {
    "background": COLORS["card_bg"],
    "padding": "25px",
    "borderRadius": "16px",
    "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
    "textAlign": "center",
    "flex": "1",
}

CONTROL_PANEL_STYLE = {
    "background": COLORS["card_bg"],
    "padding": "30px",
    "borderRadius": "20px",
    "boxShadow": "0 10px 30px rgba(99, 102, 241, 0.08)",
    "marginBottom": "40px",
    "border": "1px solid rgba(99, 102, 241, 0.1)",
}

# ---------------- LAYOUT ---------------- #
layout = html.Div(
    style={
        "backgroundColor": COLORS["background"],
        "padding": "40px",
        "minHeight": "100vh",
    },
    children=[
        # 1. KPI SECTION
        html.Div(
            style={"display": "flex", "gap": "30px", "marginBottom": "40px"},
            children=[
                html.Div(
                    [
                        html.P(
                            "รายได้รวมทั้งหมด",
                            style={"color": "#64748b", "fontWeight": "600"},
                        ),
                        html.H2(
                            id="total-value",
                            style={
                                "color": COLORS["primary"],
                                "fontWeight": "800",
                                "fontSize": "32px",
                            },
                        ),
                    ],
                    style=CARD_STYLE,
                ),
                html.Div(
                    [
                        html.P(
                            "จำนวนอำเภอ",
                            style={"color": "#64748b", "fontWeight": "600"},
                        ),
                        html.H2(
                            id="district-count",
                            style={
                                "color": COLORS["text"],
                                "fontWeight": "800",
                                "fontSize": "32px",
                            },
                        ),
                    ],
                    style=CARD_STYLE,
                ),
                html.Div(
                    [
                        html.P(
                            "รายได้เฉลี่ย", style={"color": "#64748b", "fontWeight": "600"}
                        ),
                        html.H2(
                            id="avg-value",
                            style={
                                "color": COLORS["text"],
                                "fontWeight": "800",
                                "fontSize": "32px",
                            },
                        ),
                    ],
                    style=CARD_STYLE,
                ),
            ],
        ),
        # 2. PARAMETER CONTROL SECTION
        html.Div(
            style=CONTROL_PANEL_STYLE,
            children=[
                html.Div(
                    [
                        html.Label(
                            "เลือกอำเภอที่ต้องการวิเคราะห์:",
                            style={
                                "fontWeight": "bold",
                                "marginBottom": "10px",
                                "display": "block",
                            },
                        ),
                        dcc.Dropdown(
                            id="district-dropdown",
                            options=[
                                {"label": i, "value": i} for i in df["อำเภอ"].unique()
                            ],
                            value=df["อำเภอ"].unique()[0],
                            clearable=False,
                            style={"borderRadius": "8px"},
                        ),
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "marginRight": "5%",
                        "verticalAlign": "top",
                    },
                ),
                html.Div(
                    [
                        html.Label(
                            "เลือกช่วงปีงบประมาณ:",
                            style={
                                "fontWeight": "bold",
                                "marginBottom": "10px",
                                "display": "block",
                            },
                        ),
                        dcc.RangeSlider(
                            id="year-slider",
                            min=int(df["ปีงบประมาณ"].min()),
                            max=int(df["ปีงบประมาณ"].max()),
                            value=[
                                int(df["ปีงบประมาณ"].min()),
                                int(df["ปีงบประมาณ"].max()),
                            ],
                            marks={
                                int(i): {
                                    "label": str(i),
                                    "style": {"fontWeight": "600"},
                                }
                                for i in sorted(df["ปีงบประมาณ"].unique())
                            },
                            step=1,
                        ),
                    ],
                    style={
                        "width": "60%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                    },
                ),
            ],
        ),
        # 3. MAIN TREND GRAPH
        html.Div(
            style={
                "background": COLORS["card_bg"],
                "padding": "25px",
                "borderRadius": "20px",
                "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
                "marginBottom": "30px",
            },
            children=[dcc.Graph(id="trend-graph", config=graph_config)],
        ),
        # 4. PIE CHART + TOP 10 BAR ROW (จัดวางใหม่ให้คู่กันและลบส่วน Forecast ออก)
        html.Div(
            style={"display": "flex", "gap": "30px", "marginBottom": "30px"},
            children=[
                html.Div(
                    style={
                        "flex": "1",
                        "background": COLORS["card_bg"],
                        "padding": "25px",
                        "borderRadius": "20px",
                        "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
                    },
                    children=[dcc.Graph(id="pie-graph", config=graph_config)],
                ),
                html.Div(
                    style={
                        "flex": "1.5",
                        "background": COLORS["card_bg"],
                        "padding": "25px",
                        "borderRadius": "20px",
                        "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
                    },
                    children=[dcc.Graph(id="top-graph", config=graph_config)],
                ),
            ],
        ),
    ],
)

# ---------------- CALLBACKS ---------------- #


@callback(
    Output("total-value", "children"),
    Output("district-count", "children"),
    Output("avg-value", "children"),
    Input("year-slider", "value"),
)
def update_kpi(year_range):
    filtered = df[
        (df["ปีงบประมาณ"] >= year_range[0]) & (df["ปีงบประมาณ"] <= year_range[1])
    ]
    total = filtered["ค่าข้อมูล"].sum()
    count = filtered["อำเภอ"].nunique()
    avg = filtered["ค่าข้อมูล"].mean() if not filtered.empty else 0
    return f"฿{total:,.0f}", f"{count} อำเภอ", f"฿{avg:,.0f}"


@callback(
    Output("trend-graph", "figure"),
    Input("district-dropdown", "value"),
    Input("year-slider", "value"),
)
def update_trend(district, year_range):
    filtered = df[
        (df["อำเภอ"] == district)
        & (df["ปีงบประมาณ"] >= year_range[0])
        & (df["ปีงบประมาณ"] <= year_range[1])
    ]
    fig = px.line(
        filtered,
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        title=f"แนวโน้มรายได้: {district}",
        markers=True,
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_layout(yaxis_tickformat=",", dragmode=False)
    fig.update_xaxes(dtick=1)
    return apply_pro_styling(fig)


@callback(Output("pie-graph", "figure"), Input("year-slider", "value"))
def pie_chart(year_range):
    filtered = df[
        (df["ปีงบประมาณ"] >= year_range[0]) & (df["ปีงบประมาณ"] <= year_range[1])
    ]
    pie_data = filtered.groupby("อำเภอ")["ค่าข้อมูล"].sum().reset_index()
    fig = px.pie(
        pie_data,
        values="ค่าข้อมูล",
        names="อำเภอ",
        title="สัดส่วนรายได้รายอำเภอ",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_traces(textinfo="percent+label")
    return apply_pro_styling(fig)


@callback(Output("top-graph", "figure"), Input("year-slider", "value"))
def top_graph(year_range):
    filtered = df[
        (df["ปีงบประมาณ"] >= year_range[0]) & (df["ปีงบประมาณ"] <= year_range[1])
    ]
    top = filtered.groupby("อำเภอ")["ค่าข้อมูล"].sum().nlargest(10).reset_index()
    fig = px.bar(
        top,
        x="อำเภอ",
        y="ค่าข้อมูล",
        title="10 อันดับอำเภอที่มีรายได้สูงสุด",
        text_auto=",.0f",
        color="ค่าข้อมูล",
        color_continuous_scale="Viridis",
    )
    fig.update_layout(yaxis_tickformat=",", dragmode=False, coloraxis_showscale=False)
    return apply_pro_styling(fig)
