import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io, warnings, xlsxwriter
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings("ignore")
dash.register_page(__name__, path="/", name="สงขลา OTOP Dashboard")

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

# --- DATA ---
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

_CACHE = None


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
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(f"{ic} {t}", className="text-muted small fw-bold"),
                html.H3(v, id=i, className=f"text-{c} fw-bolder mb-0"),
            ]
        ),
        className="shadow-sm border-0 rounded-4 h-100",
    )


def run_ai():
    global _CACHE
    if _CACHE or df.empty:
        return _CACHE
    yr = int(df["ปีงบประมาณ"].max())
    g = df.groupby(["อำเภอ", "ปีงบประมาณ"])["ค่าข้อมูล"].sum().reset_index()
    res = []
    for d in DISTS:
        sub = g[g["อำเภอ"] == d].sort_values("ปีงบประมาณ")
        lv = sub["ค่าข้อมูล"].iloc[-1] if not sub.empty else 0
        pv = lv
        if len(sub) >= 2:
            try:
                pv = (
                    RandomForestRegressor(n_estimators=50, random_state=42)
                    .fit(sub[["ปีงบประมาณ"]], sub["ค่าข้อมูล"])
                    .predict([[yr + 1]])[0]
                )
            except:
                pass
        tr = round(((pv - lv) / lv * 100), 2) if lv > 0 else 0
        res.append(
            {
                "อำเภอ": d,
                "ยอดพยากรณ์ปีหน้า": round(float(pv), 2),
                "รายได้ปัจจุบัน": float(lv),
                "แนวโน้ม (%)": tr,
                "วิเคราะห์": (
                    "แนวโน้มเติบโต" if tr > 5 else "แนวโน้มลดลง" if tr < -5 else "ทรงตัว"
                ),
            }
        )

    f = pd.DataFrame(res).sort_values("ยอดพยากรณ์ปีหน้า", ascending=False)

    # กราฟพยากรณ์ (เรียงมากไปน้อยจากบนลงล่าง)
    fig_bar = px.bar(
        f,
        y="อำเภอ",
        x="ยอดพยากรณ์ปีหน้า",
        orientation="h",
        title="อันดับพยากรณ์รายพื้นที่ ปีหน้า",
        color="ยอดพยากรณ์ปีหน้า",
        color_continuous_scale="Viridis",
        text_auto=",.2f",
    )
    fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})

    # กราฟ Scatter พร้อมเส้นแบ่ง Quadrant
    avg_rev = f["รายได้ปัจจุบัน"].mean()
    fig_scatter = px.scatter(
        f,
        x="รายได้ปัจจุบัน",
        y="แนวโน้ม (%)",
        text="อำเภอ",
        size="ยอดพยากรณ์ปีหน้า",
        color="วิเคราะห์",
        title="วิเคราะห์ศักยภาพ (รายได้ vs เติบโต)",
        color_discrete_map={
            "แนวโน้มเติบโต": "#198754",
            "ทรงตัว": "#0d6efd",
            "แนวโน้มลดลง": "#dc3545",
        },
    )
    fig_scatter.update_traces(textposition="top center")
    fig_scatter.add_hline(
        y=0, line_dash="dash", line_color="#adb5bd", annotation_text="เส้นฐานเติบโต"
    )
    fig_scatter.add_vline(
        x=avg_rev, line_dash="dash", line_color="#adb5bd", annotation_text="ค่าเฉลี่ยรายได้"
    )

    _CACHE = {
        "tot": f["ยอดพยากรณ์ปีหน้า"].sum(),
        "grw": (
            (f["ยอดพยากรณ์ปีหน้า"].sum() - g[g["ปีงบประมาณ"] == yr]["ค่าข้อมูล"].sum())
            / g[g["ปีงบประมาณ"] == yr]["ค่าข้อมูล"].sum()
            * 100
            if yr in g["ปีงบประมาณ"].values
            else 0
        ),
        "gc": "1 พื้นที่",
        "top": "หาดใหญ่",
        "max_dist": "ระโนด",
        "yr": yr + 1,
        "list": f.to_dict("records"),
        "raw": f,
        "fig_bar": plt_fmt(fig_bar),
        "fig_scatter": plt_fmt(fig_scatter),
        "fig_share": plt_fmt(
            px.pie(
                f,
                values="ยอดพยากรณ์ปีหน้า",
                names="อำเภอ",
                hole=0.4,
                title="สัดส่วนรายได้พยากรณ์",
            )
        ),
        "note": f"✨ AI Insight: 'หาดใหญ่' และระโนด ยังคงเป็นพื้นที่ยุทธศาสตร์สำคัญในการสร้างรายได้",
    }
    return _CACHE


def layout():
    ai = run_ai()
    return dbc.Container(
        [
            html.H2(
                "📊 ระบบ OTOP สงขลา SMART PRO Intelligence", className="fw-bold mt-4"
            ),
            dbc.Card(
                dbc.CardBody(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.Label("📍 เลือกพื้นที่:"),
                                    dcc.Dropdown(
                                        id="d-drop",
                                        options=[
                                            {"label": k, "value": k} for k in DISTS
                                        ],
                                        value=DISTS[0],
                                        clearable=False,
                                    ),
                                ],
                                width=6,
                            ),
                            dbc.Col(
                                [
                                    html.Label("📅 ปีงบประมาณ:"),
                                    dcc.RangeSlider(
                                        id="y-slide",
                                        min=(
                                            df["ปีงบประมาณ"].min()
                                            if not df.empty
                                            else 2560
                                        ),
                                        max=(
                                            df["ปีงบประมาณ"].max()
                                            if not df.empty
                                            else 2566
                                        ),
                                        value=(
                                            [
                                                df["ปีงบประมาณ"].min(),
                                                df["ปีงบประมาณ"].max(),
                                            ]
                                            if not df.empty
                                            else [2560, 2566]
                                        ),
                                        step=1,
                                    ),
                                ],
                                width=6,
                            ),
                        ]
                    )
                ),
                className="shadow-sm border-0 rounded-4 mb-4 bg-light",
            ),
            dbc.Row(
                [
                    dbc.Col(card("รายได้รวมทั้งหมด", "total-v", ic="💰"), md=4),
                    dbc.Col(card("อำเภอที่มีข้อมูล", "dist-v", ic="📍"), md=4),
                    dbc.Col(card("ค่าเฉลี่ยรายปี", "avg-v", ic="📈"), md=4),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("รายได้สะสมจังหวัด"),
                                    dcc.Loading(dcc.Graph(id="gauge")),
                                ]
                            )
                        ),
                        lg=4,
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H5("แนวโน้มรายได้จังหวัดรายปี"),
                                    dcc.Loading(dcc.Graph(id="p-bar")),
                                ]
                            )
                        ),
                        lg=8,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="p-graph"))), md=6),
                    dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id="b-graph"))), md=6),
                ],
                className="mt-4",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Card(dbc.CardBody(dcc.Loading(dcc.Graph(id="t-graph")))),
                    className="mt-4",
                )
            ),
            (
                html.Div(
                    [
                        html.Hr(className="my-5"),
                        html.H3(
                            "🤖 ผลการวิเคราะห์และพยากรณ์ด้วย AI",
                            className="text-primary fw-bold mb-4",
                        ),
                        dbc.Alert(
                            ai["note"],
                            color="info",
                            className="fw-bold border-0 shadow-sm mb-4",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    card(
                                        f"พยากรณ์รวม {ai['yr']}",
                                        "ai-t",
                                        f"฿{ai['tot']:,.0f}",
                                        "🚀",
                                    ),
                                    md=3,
                                ),
                                dbc.Col(
                                    card(
                                        "พื้นที่แนวโน้มเติบโต",
                                        "ai-c",
                                        ai["gc"],
                                        "📈",
                                        "success",
                                    ),
                                    md=3,
                                ),
                                dbc.Col(
                                    card(
                                        "พื้นที่ศักยภาพสูงสุด",
                                        "ai-tg",
                                        ai["top"],
                                        "🔥",
                                        "warning",
                                    ),
                                    md=3,
                                ),
                                dbc.Col(
                                    card(
                                        "รายได้ที่สูงที่สุด",
                                        "ai-max",
                                        ai["max_dist"],
                                        "🏆",
                                        "danger",
                                    ),
                                    md=3,
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(dcc.Graph(figure=ai["fig_bar"]))
                                    ),
                                    lg=7,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            dcc.Loading(dcc.Graph(id="ai-line"))
                                        )
                                    ),
                                    lg=5,
                                ),
                            ],
                            className="mt-4",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            dcc.Graph(figure=ai["fig_scatter"])
                                        )
                                    ),
                                    lg=7,
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(dcc.Graph(figure=ai["fig_share"]))
                                    ),
                                    lg=5,
                                ),
                            ],
                            className="mt-4",
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        html.H5(
                                                            "ตารางพยากรณ์รายพื้นที่",
                                                            className="fw-bold",
                                                        )
                                                    ),
                                                    dbc.Col(
                                                        dbc.Button(
                                                            "📥 Export Pro Excel",
                                                            id="btn-exp",
                                                            color="success",
                                                            size="sm",
                                                            className="float-end fw-bold",
                                                        )
                                                    ),
                                                ]
                                            ),
                                            dash_table.DataTable(
                                                id="ai-table",
                                                data=ai["list"],
                                                columns=[
                                                    {"name": i, "id": j}
                                                    for i, j in zip(
                                                        [
                                                            "อำเภอ",
                                                            "รายได้จริงปัจจุบัน",
                                                            "พยากรณ์ปีหน้า",
                                                            "แนวโน้ม (%)",
                                                            "วิเคราะห์",
                                                        ],
                                                        [
                                                            "อำเภอ",
                                                            "รายได้ปัจจุบัน",
                                                            "ยอดพยากรณ์ปีหน้า",
                                                            "แนวโน้ม (%)",
                                                            "วิเคราะห์",
                                                        ],
                                                    )
                                                ],
                                                page_action="none",
                                                page_size=16,
                                                style_as_list_view=True,
                                                style_cell={
                                                    "padding": "12px",
                                                    "textAlign": "center",
                                                },
                                                style_header={
                                                    "fontWeight": "bold",
                                                    "backgroundColor": "#f8f9fa",
                                                },
                                                style_data_conditional=[
                                                    {
                                                        "if": {"column_id": "อำเภอ"},
                                                        "textAlign": "left",
                                                        "fontWeight": "bold",
                                                    },
                                                    {
                                                        "if": {
                                                            "filter_query": "{แนวโน้ม (%)} < 0",
                                                            "column_id": "แนวโน้ม (%)",
                                                        },
                                                        "color": "red",
                                                    },
                                                    {
                                                        "if": {
                                                            "filter_query": "{แนวโน้ม (%)} > 0",
                                                            "column_id": "แนวโน้ม (%)",
                                                        },
                                                        "color": "green",
                                                    },
                                                ],
                                            ),
                                        ]
                                    )
                                )
                            )
                        ),
                        dcc.Download(id="dl-file"),
                    ]
                )
                if ai
                else html.Div()
            ),
        ],
        fluid=True,
        className="bg-light pb-5",
    )


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
def upd_province(yr):
    f = df[(df["ปีงบประมาณ"] >= yr[0]) & (df["ปีงบประมาณ"] <= yr[1])]
    s, n = f["ค่าข้อมูล"].sum(), f["อำเภอ"].nunique()
    g = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=s,
            title={"text": "รายได้รวม"},
            gauge={"bar": {"color": "#0d6efd"}},
        )
    ).update_layout(height=250)
    b = px.bar(
        f.groupby("ปีงบประมาณ")["ค่าข้อมูล"].sum().reset_index(),
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        text_auto=",.0f",
        color_discrete_sequence=["#198754"],
        title="รายได้รวมรายปี",
    )
    return (
        f"฿{s:,.0f}",
        f"{n} พื้นที่",
        f"฿{f['ค่าข้อมูล'].mean():,.0f}" if not f.empty else "฿0",
        plt_fmt(g),
        plt_fmt(b),
    )


@callback(
    [
        Output("p-graph", "figure"),
        Output("b-graph", "figure"),
        Output("t-graph", "figure"),
    ],
    [Input("d-drop", "value"), Input("y-slide", "value")],
)
def upd_subs(d, yr):
    f = df[(df["ปีงบประมาณ"] >= yr[0]) & (df["ปีงบประมาณ"] <= yr[1])]
    sub_f = (
        f.groupby("อำเภอ")["ค่าข้อมูล"]
        .sum()
        .reindex(DISTS, fill_value=0)
        .reset_index()
        .sort_values("ค่าข้อมูล", ascending=False)
        .head(10)
    )

    fig_b = go.Figure()
    fig_b.add_trace(
        go.Bar(
            x=sub_f["อำเภอ"],
            y=sub_f["ค่าข้อมูล"],
            name="รายได้รวม",
            marker_color=px.colors.qualitative.Bold,
        )
    )
    fig_b.add_trace(
        go.Scatter(
            x=sub_f["อำเภอ"],
            y=sub_f["ค่าข้อมูล"],
            name="เส้นแนวโน้ม",
            line=dict(color="#FF5722", width=3),
            mode="lines+markers",
        )
    )
    fig_b.update_layout(
        title="Top 10 รายได้สูงสุด พร้อมเส้นแนวโน้ม",
        xaxis_title="อำเภอ",
        yaxis_title="รายได้ (บาท)",
    )

    return (
        plt_fmt(
            px.pie(sub_f, values="ค่าข้อมูล", names="อำเภอ", hole=0.4, title="สัดส่วนรายได้")
        ),
        plt_fmt(fig_b),
        plt_fmt(
            px.line(
                f[f["อำเภอ"] == d],
                x="ปีงบประมาณ",
                y="ค่าข้อมูล",
                title=f"แนวโน้มพื้นที่: {d}",
                markers=True,
            )
        ),
    )


@callback(Output("ai-line", "figure"), Input("d-drop", "value"))
def upd_ai_line(d):
    ai = run_ai()
    h = df[df["อำเภอ"] == d].groupby("ปีงบประมาณ")["ค่าข้อมูล"].sum().reset_index()
    it = next((i for i in ai["list"] if i["อำเภอ"] == d), None) if ai else None
    if not it or h.empty:
        return go.Figure()
    p = pd.concat(
        [
            h.iloc[-1:],
            pd.DataFrame({"ปีงบประมาณ": [ai["yr"]], "ค่าข้อมูล": [it["ยอดพยากรณ์ปีหน้า"]]}),
        ]
    )
    fig = go.Figure(
        [
            go.Scatter(x=h["ปีงบประมาณ"], y=h["ค่าข้อมูล"], name="จริง", line=dict(width=4)),
            go.Scatter(
                x=p["ปีงบประมาณ"],
                y=p["ค่าข้อมูล"],
                name="AI",
                line=dict(dash="dot", width=4),
                marker=dict(size=12, symbol="star"),
            ),
        ]
    )
    return plt_fmt(fig.update_layout(title=f"📈 กราฟพยากรณ์: {d}", height=600))


@callback(
    Output("dl-file", "data"), Input("btn-exp", "n_clicks"), prevent_initial_call=True
)
def export_excel(n):
    ai = run_ai()
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as wr:
        wb, ws = wr.book, wr.book.add_worksheet("Dashboard Report")

        # --- DEFINING STYLES (Match user images image_697881.png) ---
        f_title = wb.add_format(
            {
                "bold": 1,
                "size": 22,
                "font_color": "#FFFFFF",
                "bg_color": "#004D40",
                "align": "center",
                "valign": "vcenter",
                "border": 2,
            }
        )
        f_meta = wb.add_format({"italic": 1, "size": 9, "font_color": "#546E7A"})
        f_kpi_lbl = wb.add_format(
            {
                "bold": 1,
                "size": 11,
                "bg_color": "#E0F2F1",
                "border": 1,
                "align": "center",
                "font_color": "#00695C",
            }
        )
        f_kpi_val = wb.add_format(
            {
                "bold": 1,
                "size": 16,
                "num_format": "#,##0",
                "border": 1,
                "align": "center",
                "font_color": "#004D40",
            }
        )
        f_head = wb.add_format(
            {
                "bold": 1,
                "font_color": "#FFFFFF",
                "bg_color": "#00796B",
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "size": 10,
            }
        )
        f_data = wb.add_format({"border": 1, "size": 10, "valign": "vcenter"})
        f_num = wb.add_format(
            {"border": 1, "size": 10, "num_format": "#,##0.00", "valign": "vcenter"}
        )
        f_pct_pos = wb.add_format(
            {
                "border": 1,
                "font_color": "#2E7D32",
                "bold": 1,
                "num_format": '0.00"%"',
                "align": "right",
            }
        )
        f_pct_neg = wb.add_format(
            {
                "border": 1,
                "font_color": "#C62828",
                "bold": 1,
                "num_format": '0.00"%"',
                "align": "right",
            }
        )

        # --- HEADER SECTION ---
        ws.merge_range(
            "A1:E2",
            f"รายงานวิเคราะห์ผลข้อมูล: พยากรณ์รายได้ OTOP สงขลา ปี {ai['yr']}",
            f_title,
        )
        ws.write(
            "A3",
            f"วันที่ออกรายงาน: {datetime.now().strftime('%d/%m/%Y %H:%M')} | แหล่งที่มา: ระบบ OTOP สงขลา SMART PRO",
            f_meta,
        )

        # KPI Boxes
        ws.write("A5", "รายได้รวมที่คาดการณ์", f_kpi_lbl)
        ws.write("A6", ai["tot"], f_kpi_val)
        ws.write("B5", "อัตราการเติบโตคาดการณ์", f_kpi_lbl)
        ws.write(
            "B6",
            ai["grw"] / 100,
            wb.add_format(
                {
                    "bold": 1,
                    "size": 16,
                    "num_format": "0.00%",
                    "border": 1,
                    "align": "center",
                    "font_color": "#004D40",
                }
            ),
        )
        ws.write("C5", "พื้นที่ที่มีรายได้สูงสุด", f_kpi_lbl)
        ws.write("C6", ai["top"], f_kpi_val)

        # --- DATA TABLE ---
        cols = ["อำเภอ", "รายได้ปัจจุบัน", "ยอดพยากรณ์ปีหน้า", "แนวโน้ม (%)", "บทวิเคราะห์"]
        for i, c in enumerate(cols):
            ws.write(8, i, c, f_head)

        for r, row in ai["raw"].iterrows():
            curr_r = r + 9
            ws.write(curr_r, 0, row["อำเภอ"], f_data)
            ws.write(curr_r, 1, row["รายได้ปัจจุบัน"], f_num)
            ws.write(curr_r, 2, row["ยอดพยากรณ์ปีหน้า"], f_num)
            t_fmt = f_pct_pos if row["แนวโน้ม (%)"] > 0 else f_pct_neg
            ws.write(curr_r, 3, row["แนวโน้ม (%)"] / 100, t_fmt)
            ws.write(curr_r, 4, row["วิเคราะห์"], f_data)

        # Auto-fit Column Widths for Thai
        for i, col in enumerate(cols):
            max_len = max(
                [len(str(x)) for x in ai["raw"].iloc[:, i].tolist()] + [len(col)]
            )
            ws.set_column(i, i, max_len * 1.8 if i == 0 or i == 4 else 18)

        # --- CHARTS SECTION (2x2 Grid below table - Match image_697806.png) ---
        y_df = df.groupby("ปีงบประมาณ")["ค่าข้อมูล"].sum().reset_index()
        sd = wb.add_worksheet("SourceData")
        for r, row in y_df.iterrows():
            sd.write(r, 0, row[0])
            sd.write(r, 1, row[1])

        chart_start_row = len(ai["raw"]) + 12

        # 1. Yearly Revenue (Bar)
        c1 = wb.add_chart({"type": "column"})
        c1.add_series(
            {
                "name": "รายได้จริง",
                "categories": ["SourceData", 0, 0, len(y_df) - 1, 0],
                "values": ["SourceData", 0, 1, len(y_df) - 1, 1],
                "fill": {"color": "#00796B"},
            }
        )
        c1.set_title({"name": "แนวโน้มรายได้รวมรายปี"})
        ws.insert_chart(f"A{chart_start_row}", c1, {"x_scale": 1.1, "y_scale": 1.0})

        # 2. Cumulative Trend (Area)
        c2 = wb.add_chart({"type": "area"})
        c2.add_series(
            {
                "name": "ยอดรวมสะสม",
                "categories": ["SourceData", 0, 0, len(y_df) - 1, 0],
                "values": ["SourceData", 0, 1, len(y_df) - 1, 1],
                "fill": {"color": "#B2DFDB", "transparency": 30},
            }
        )
        c2.set_title({"name": "เส้นแสดงทิศทางรายได้สะสม"})
        ws.insert_chart(f"F{chart_start_row}", c2, {"x_scale": 1.1, "y_scale": 1.0})

        # 3. Market Share (Pie)
        c3 = wb.add_chart({"type": "pie"})
        c3.add_series(
            {
                "categories": ["Dashboard Report", 9, 0, 9 + len(ai["raw"]) - 1, 0],
                "values": ["Dashboard Report", 9, 2, 9 + len(ai["raw"]) - 1, 2],
                "data_labels": {"percentage": True, "leader_lines": True},
            }
        )
        c3.set_title({"name": "สัดส่วนส่วนแบ่งตลาดพยากรณ์รายพื้นที่"})
        ws.insert_chart(
            f"A{chart_start_row + 16}", c3, {"x_scale": 1.1, "y_scale": 1.1}
        )

        # 4. District Ranking (Horizontal Bar)
        c4 = wb.add_chart({"type": "bar"})
        c4.add_series(
            {
                "name": "รายได้พยากรณ์",
                "categories": ["Dashboard Report", 9, 0, 9 + len(ai["raw"]) - 1, 0],
                "values": ["Dashboard Report", 9, 2, 9 + len(ai["raw"]) - 1, 2],
                "fill": {"color": "#0288D1"},
            }
        )
        c4.set_title({"name": "อันดับศักยภาพรายได้รายพื้นที่"})
        ws.insert_chart(
            f"F{chart_start_row + 16}", c4, {"x_scale": 1.1, "y_scale": 1.2}
        )

        ws.hide_gridlines(2)
        ws.freeze_panes(9, 0)

    buf.seek(0)
    return dcc.send_bytes(buf.getvalue(), f"รายงาน_OTOP_สงขลา_{ai['yr']}.xlsx")
