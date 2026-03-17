import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ลงทะเบียนหน้าเป็นหน้าแรก (Home)
dash.register_page(__name__, path="/", name="Overview Dashboard")

# --- Constants ---
DISTS = [
    "เมืองสงขลา",
    "หาดใหญ่",
    "จะนะ",
    "เทพา",
    "สะเดา",
    "นาทวี",
    "ระโนด",
    "สิงหนคร",
    "สะบ้าย้อย",
    "รัตภูมิ",
    "บางกล่ำ",
    "ควนเนียง",
    "คลองหอยโข่ง",
    "นาหม่อม",
    "สทิงพระ",
    "กระแสสินธุ์",
]

# --- DATA LOADING ---
try:
    df = pd.read_csv("data/cleaned_data.csv")
    df.columns = df.columns.str.strip()
    if "อำเภอ" in df.columns:
        df["อำเภอ"] = (
            df["อำเภอ"]
            .astype(str)
            .str.replace(r"อำเภอ|อ\.", "", regex=True)
            .str.strip()
        )
    for c in ["ค่าข้อมูล", "ปีงบประมาณ"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    df = df.drop_duplicates().query("ค่าข้อมูล >= 0").reset_index(drop=True)
except:
    df = pd.DataFrame(columns=["อำเภอ", "ปีงบประมาณ", "ค่าข้อมูล"])


# --- Helper Functions ---
def plt_fmt(f):
    if f is None:
        return go.Figure()
    return f.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family="Prompt"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )


def card(t, i, v="0", ic="", c="primary"):
    color_map = {
        "primary": "#4f46e5",
        "success": "#10b981",
        "info": "#0ea5e9",
    }
    border_color = color_map.get(c, "#4f46e5")
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(f"{ic} {t}", className="text-muted small fw-bold"),
                html.H3(v, id=i, className=f"text-{c} fw-bolder mb-0"),
            ]
        ),
        className="shadow-sm border-0 rounded-4 h-100",
        style={"borderLeft": f"6px solid {border_color}"},
    )


# --- Layout ---
def layout():
    min_yr = df["ปีงบประมาณ"].min() if not df.empty else 2560
    max_yr = df["ปีงบประมาณ"].max() if not df.empty else 2566

    return dbc.Container(
        [
            html.H2("📊 สรุปภาพรวมรายได้ OTOP สงขลา", className="fw-bold mt-4 mb-4"),
            # --- Filters ---
            dbc.Card(
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label(
                                        "📍 เลือกพื้นที่วิเคราะห์:", className="fw-bold"
                                    ),
                                    dcc.Dropdown(
                                        id="d-drop",
                                        options=[
                                            {"label": k, "value": k} for k in DISTS
                                        ],
                                        value=DISTS[0],
                                        clearable=False,
                                    ),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    html.Label(
                                        "📅 เลือกช่วงปีงบประมาณ:", className="fw-bold"
                                    ),
                                    dcc.RangeSlider(
                                        id="y-slide",
                                        min=min_yr,
                                        max=max_yr,
                                        value=[min_yr, max_yr],
                                        step=1,
                                        marks={
                                            i: str(i) for i in range(min_yr, max_yr + 1)
                                        },
                                    ),
                                ],
                                md=6,
                            ),
                        ]
                    )
                ),
                className="shadow-sm border-0 rounded-4 mb-4 bg-light",
                style={"borderLeft": "6px solid #6366f1"},
            ),
            # --- Row Headers (KPI Cards) ---
            dbc.Row(
                [
                    dbc.Col(
                        card(
                            "รายได้รวมตามช่วงเวลาที่เลือก", "total-v", ic="💰", c="primary"
                        ),
                        md=4,
                    ),
                    dbc.Col(
                        card("จำนวนพื้นที่ที่มีข้อมูล", "dist-v", ic="📍", c="success"), md=4
                    ),
                    dbc.Col(
                        card("ค่าเฉลี่ยรายได้ต่อรายการ", "avg-v", ic="📈", c="info"), md=4
                    ),
                ],
                className="mb-4",
            ),
            # --- แก้ไขแถวที่ 1: ประวัติรายได้รายปี (ย้ายจากล่างสุดขึ้นมา) ---
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5(id="t-title", className="fw-bold"),
                                dcc.Loading(dcc.Graph(id="t-graph")),
                            ]
                        ),
                        className="shadow-sm border-0 rounded-4 mb-4",
                        style={"borderLeft": "6px solid #f59e0b"},  # สีขอบตามภาพตัวอย่าง
                    ),
                    width=12,
                )
            ),
            # --- แก้ไขแถวที่ 2: สัดส่วนรายได้สะสม และ แนวโน้มจังหวัด ---
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("สัดส่วนรายได้สะสม", className="fw-bold"),
                                    # ปรับความสูงการ์ดให้เท่าข้างๆ (400px) เพื่อความสวยงาม
                                    dcc.Loading(
                                        dcc.Graph(id="gauge", style={"height": "400px"})
                                    ),
                                ]
                            ),
                            className="shadow-sm border-0 rounded-4 mb-4",
                            style={"borderLeft": "6px solid #4f46e5"},
                        ),
                        lg=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "แนวโน้มรายได้รวมรายปี (ทั้งจังหวัด)",
                                        className="fw-bold",
                                    ),
                                    # ปรับความสูงการ์ดให้เท่าข้างๆ (400px) เพื่อความสวยงาม
                                    dcc.Loading(
                                        dcc.Graph(id="p-bar", style={"height": "400px"})
                                    ),
                                ]
                            ),
                            className="shadow-sm border-0 rounded-4 mb-4",
                            style={"borderLeft": "6px solid #10b981"},
                        ),
                        lg=8,
                    ),
                ]
            ),
            # --- แก้ไขแถวที่ 3: สัดส่วนแยกอำเภอ และ Top 10 ---
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "สัดส่วนรายได้แยกตามอำเภอ", className="fw-bold"
                                    ),
                                    dcc.Graph(id="p-graph"),
                                ]
                            ),
                            className="shadow-sm border-0 rounded-4 mb-4",
                            style={"borderLeft": "6px solid #4f46e5"},
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "Top 10 อำเภอรายได้สูงสุด", className="fw-bold"
                                    ),
                                    dcc.Graph(id="b-graph"),
                                ]
                            ),
                            className="shadow-sm border-0 rounded-4 mb-4",
                            style={"borderLeft": "6px solid #6366f1"},
                        ),
                        md=6,
                    ),
                ],
                className="mt-4 mb-5",  # เพิ่มระยะห่างด้านล่างสุด
            ),
        ],
        fluid=True,
        className="bg-light px-4",
    )


# --- Callbacks ---


@callback(
    [
        Output("total-v", "children"),
        Output("dist-v", "children"),
        Output("avg-v", "children"),
        Output("gauge", "figure"),
        Output("p-bar", "figure"),
    ],
    Input("y-slide", "value"),
)
def update_province_stats(yr_range):
    f = df[(df["ปีงบประมาณ"] >= yr_range[0]) & (df["ปีงบประมาณ"] <= yr_range[1])]
    s = f["ค่าข้อมูล"].sum()
    n = f["อำเภอ"].nunique()
    avg = f["ค่าข้อมูล"].mean() if not f.empty else 0

    # --- แก้ไข Gauge: ปรับแต่ง Figure เพื่อแก้ตัวเลขซ้อน ---
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=s,
            number={"prefix": "฿", "valueformat": ",.0f", "font": {"size": 32}},
            gauge={
                "bar": {"color": "#4f46e5"},
                "axis": {
                    "range": [0, s * 1.5],
                    "tickformat": ".2s",
                },  # ปรับสเกลให้อัตโนมัติ (เช่น 20B แทน 20M) ลดการซ้อน
            },
        )
    ).update_layout(
        height=350,  # ปรับความสูงภายในกราฟให้เหมาะสม
        margin=dict(l=30, r=30, t=50, b=20),  # เพิ่มพื้นที่ขอบเพื่อป้องกันเลขสเกลด้านนอกซ้อนกัน
    )

    yearly_df = f.groupby("ปีงบประมาณ")["ค่าข้อมูล"].sum().reset_index()
    fig_bar = px.bar(
        yearly_df,
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        text_auto=",.0f",
        color_discrete_sequence=["#10b981"],
    )

    return (
        f"฿{s:,.0f}",
        f"{n} พื้นที่",
        f"฿{avg:,.0f}",
        plt_fmt(fig_gauge),
        plt_fmt(fig_bar),
    )


@callback(
    [
        Output("p-graph", "figure"),
        Output("b-graph", "figure"),
        Output("t-graph", "figure"),
        Output("t-title", "children"),
    ],
    [Input("d-drop", "value"), Input("y-slide", "value")],
)
def update_district_charts(selected_dist, yr_range):
    f = df[(df["ปีงบประมาณ"] >= yr_range[0]) & (df["ปีงบประมาณ"] <= yr_range[1])]

    dist_sum = f.groupby("อำเภอ")["ค่าข้อมูล"].sum().reset_index()
    top_10 = dist_sum.sort_values("ค่าข้อมูล", ascending=False).head(10)

    fig_pie = px.pie(dist_sum, values="ค่าข้อมูล", names="อำเภอ", hole=0.4)

    fig_top10 = go.Figure()
    fig_top10.add_trace(
        go.Bar(
            x=top_10["อำเภอ"], y=top_10["ค่าข้อมูล"], marker_color="#6366f1", name="รายได้"
        )
    )
    fig_top10.add_trace(
        go.Scatter(
            x=top_10["อำเภอ"],
            y=top_10["ค่าข้อมูล"],
            mode="lines+markers",
            line=dict(color="#f43f5e", width=2),
            name="Trend",
        )
    )

    dist_history = f[f["อำเภอ"] == selected_dist].sort_values("ปีงบประมาณ")
    fig_line = px.line(
        dist_history,
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#f59e0b"],  # สีขอบตามภาพตัวอย่าง
    )

    return (
        plt_fmt(fig_pie),
        plt_fmt(fig_top10),
        plt_fmt(fig_line),
        f"📈 ประวัติรายได้รายปี: {selected_dist}",
    )
