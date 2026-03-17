import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

dash.register_page(__name__, path="/", name="Overview Dashboard")


# --- 📥 DATA LOADING ---
def load_data():
    paths = ["data/cleaned_data.csv", "../data/cleaned_data.csv", "cleaned_data.csv"]
    for p in paths:
        if os.path.exists(p):
            df_raw = pd.read_csv(p)
            df_raw.columns = df_raw.columns.str.strip()
            return df_raw
    return pd.DataFrame()


df_raw = load_data()

if not df_raw.empty:
    col_map = {"อำเภอ": "อำเภอ", "ปีงบประมาณ": "ปีงบประมาณ", "ค่าข้อมูล": "ค่าข้อมูล"}
    df_raw = df_raw.rename(columns=lambda x: col_map.get(x, x))
    if "อำเภอ" in df_raw.columns:
        df_raw["อำเภอ"] = (
            df_raw["อำเภอ"]
            .astype(str)
            .str.replace(r"อำเภอ|อ\.", "", regex=True)
            .str.strip()
        )
    for c in ["ค่าข้อมูล", "ปีงบประมาณ"]:
        if c in df_raw.columns:
            df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce").fillna(0).astype(int)
    df = df_raw.drop_duplicates()
    if "ค่าข้อมูล" in df.columns:
        df = df[df["ค่าข้อมูล"] >= 0]
    df = df.reset_index(drop=True)
else:
    df = pd.DataFrame(columns=["อำเภอ", "ปีงบประมาณ", "ค่าข้อมูล"])

DISTS = sorted(df["อำเภอ"].unique()) if not df.empty else []


def plt_fmt(f):
    return f.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family="Prompt"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )


def card(t, i, v="0", ic="", c="primary"):
    colors = {"primary": "#4f46e5", "success": "#10b981", "info": "#0ea5e9"}
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(f"{ic} {t}", className="text-muted small fw-bold"),
                html.H3(v, id=i, className=f"text-{c} fw-bolder mb-0"),
            ]
        ),
        className="shadow-sm border-0 rounded-4 h-100",
        style={"borderLeft": f"6px solid {colors.get(c, '#4f46e5')}"},
    )


# --- 🏗️ LAYOUT ---
def layout():
    min_yr, max_yr = (
        (df["ปีงบประมาณ"].min(), df["ปีงบประมาณ"].max()) if not df.empty else (2560, 2567)
    )
    return dbc.Container(
        [
            # 1. Filters
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
                                        value=DISTS[0] if DISTS else None,
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
                                            int(i): str(int(i))
                                            for i in range(min_yr, max_yr + 1)
                                        },
                                    ),
                                ],
                                md=6,
                            ),
                        ]
                    )
                ),
                className="shadow-sm border-0 rounded-4 mb-4 bg-light",
            ),
            # 2. KPI Cards
            dbc.Row(
                [
                    dbc.Col(
                        card(
                            "รายได้รวมตามช่วงเวลาที่เลือก",
                            "range-total-v",
                            ic="💰",
                            c="primary",
                        ),
                        md=3,
                    ),
                    dbc.Col(
                        card("รายได้รวมสะสมพื้นที่", "total-v", ic="💰", c="info"), md=3
                    ),
                    dbc.Col(
                        card("จำนวนปีที่เก็บข้อมูล", "dist-v", ic="📅", c="success"), md=3
                    ),
                    dbc.Col(card("รายได้เฉลี่ยต่อปี", "avg-v", ic="📈", c="info"), md=3),
                ],
                className="mb-5 g-3",
            ),
            # 3. กราฟเส้นประวัติรายได้ (กราฟที่คุณขอให้เอาไว้บนสุด)
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5(id="line-title", className="fw-bold"),
                                dcc.Loading(
                                    dcc.Graph(
                                        id="dist-line-chart", style={"height": "400px"}
                                    )
                                ),
                            ]
                        ),
                        className="shadow-sm border-0 rounded-4 mb-4",
                        style={"borderLeft": "6px solid #f59e0b"},
                    )
                )
            ),
            # 4. Gauge และ Bar รายพื้นที่
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(id="gauge-title", className="fw-bold"),
                                    dcc.Graph(
                                        id="gauge-chart", style={"height": "350px"}
                                    ),
                                ]
                            ),
                            className="shadow-sm border-0 rounded-4 mb-4",
                        ),
                        lg=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(id="bar-title", className="fw-bold"),
                                    dcc.Graph(
                                        id="dist-bar-chart", style={"height": "350px"}
                                    ),
                                ]
                            ),
                            className="shadow-sm border-0 rounded-4 mb-4",
                        ),
                        lg=8,
                    ),
                ]
            ),
            # 5. กราฟภาพรวมจังหวัด
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5(
                                        "สัดส่วนรายได้สะสมทั้งจังหวัด", className="fw-bold"
                                    ),
                                    dcc.Graph(id="donut-chart"),
                                ]
                            ),
                            className="shadow-sm border-0 rounded-4 mb-4",
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
                                    dcc.Graph(id="top10-bar-chart"),
                                ]
                            ),
                            className="shadow-sm border-0 rounded-4 mb-4",
                        ),
                        md=6,
                    ),
                ],
                className="mb-5",
            ),
        ],
        fluid=True,
        className="bg-white",
        style={
            "paddingTop": "30px",
            "paddingBottom": "50px",
            "paddingLeft": "60px",
            "paddingRight": "60px",
        },
    )


# --- ⚡ CALLBACKS ---
@callback(
    [
        Output("range-total-v", "children"),
        Output("total-v", "children"),
        Output("dist-v", "children"),
        Output("avg-v", "children"),
        Output("dist-line-chart", "figure"),
        Output("gauge-chart", "figure"),
        Output("dist-bar-chart", "figure"),
        Output("donut-chart", "figure"),
        Output("top10-bar-chart", "figure"),
        Output("line-title", "children"),
        Output("gauge-title", "children"),
        Output("bar-title", "children"),
    ],
    [Input("d-drop", "value"), Input("y-slide", "value")],
)
def update_all_charts(selected_dist, yr_range):
    f_all = df[(df["ปีงบประมาณ"] >= yr_range[0]) & (df["ปีงบประมาณ"] <= yr_range[1])]
    f_dist = f_all[f_all["อำเภอ"] == selected_dist].sort_values("ปีงบประมาณ")

    # คำนวณค่า
    s_range_total = f_all["ค่าข้อมูล"].sum()  # รายได้รวมตามช่วงเวลาที่เลือก (ทุกอำเภอ)
    s_total = f_dist["ค่าข้อมูล"].sum()
    n_years = f_dist["ปีงบประมาณ"].nunique()
    avg_val = f_dist["ค่าข้อมูล"].mean() if not f_dist.empty else 0

    # 1. กราฟเส้น (Line Chart ตามรูปที่ส่งมา)
    fig_line = px.line(
        f_dist,
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#f59e0b"],
    )
    fig_line.update_xaxes(dtick=1, tickformat="d")

    # 2. Gauge Chart
    max_prov = f_all.groupby("อำเภอ")["ค่าข้อมูล"].sum().max() if not f_all.empty else 100
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=s_total,
            number={"prefix": "฿", "valueformat": ",.0f", "font": {"size": 35}},
            gauge={"bar": {"color": "#4f46e5"}, "axis": {"range": [0, max_prov * 1.1]}},
        )
    )

    # 3. Bar Chart รายพื้นที่
    fig_dist_bar = px.bar(
        f_dist,
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        text_auto=",.2s",
        color_discrete_sequence=["#10b981"],
    )
    fig_dist_bar.update_xaxes(dtick=1, tickformat="d")

    # 4. Donut Chart (ภาพรวม)
    dist_sum = f_all.groupby("อำเภอ")["ค่าข้อมูล"].sum().reset_index()
    fig_donut = px.pie(dist_sum, values="ค่าข้อมูล", names="อำเภอ", hole=0.5)

    # 5. Top 10 Trend (ภาพรวม)
    top_10 = dist_sum.sort_values("ค่าข้อมูล", ascending=False).head(10)
    fig_top10 = px.bar(
        top_10,
        x="อำเภอ",
        y="ค่าข้อมูล",
        color="อำเภอ",
        color_discrete_sequence=px.colors.qualitative.Bold,
        text_auto=",.0f",
        labels={"ค่าข้อมูล": "รายได้"},
    )
    # ซ่อน legend ของบาร์ แล้วแสดงเฉพาะเส้นแนวโน้ม
    fig_top10.update_traces(selector=dict(type="bar"), showlegend=False)

    fig_top10.add_trace(
        go.Scatter(
            x=top_10["อำเภอ"],
            y=top_10["ค่าข้อมูล"],
            mode="lines+markers",
            line=dict(color="#ef4444", width=3),
            marker=dict(size=8, color="#ef4444"),
            name="แนวโน้ม (เส้น)",
            showlegend=True,
        )
    )
    fig_top10.update_traces(marker_line_width=0)
    fig_top10.update_layout(
        legend=dict(
            title="Legend",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis_tickangle=-45,
        margin=dict(l=40, r=20, t=40, b=80),
    )

    return (
        f"฿{s_range_total:,.0f}",
        f"฿{s_total:,.0f}",
        f"{n_years} ปีงบประมาณ",
        f"฿{avg_val:,.0f}",
        plt_fmt(fig_line),
        plt_fmt(fig_gauge),
        plt_fmt(fig_dist_bar),
        plt_fmt(fig_donut),
        plt_fmt(fig_top10),
        f"📈 ประวัติรายได้รายปี: {selected_dist}",
        f"รายได้สะสม: {selected_dist}",
        f"แนวโน้มรายปี: {selected_dist}",
    )
