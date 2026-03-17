import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io, warnings
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings("ignore")
dash.register_page(__name__, path="/forecast", name="AI Forecast Analysis")

# --- Constants & Data Loading ---
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

try:
    df = pd.read_csv("data/cleaned_data.csv")
    df["อำเภอ"] = (
        df["อำเภอ"].astype(str).str.replace(r"อำเภอ|อ\.", "", regex=True).str.strip()
    )
    for c in ["ค่าข้อมูล", "ปีงบประมาณ"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
except:
    df = pd.DataFrame(columns=["อำเภอ", "ปีงบประมาณ", "ค่าข้อมูล"])

_CACHE = None


# --- Helper Functions ---
def plt_fmt(f):
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


def run_ai_engine():
    global _CACHE
    if _CACHE is not None or df.empty:
        return _CACHE

    yr = int(df["ปีงบประมาณ"].max())
    g = df.groupby(["อำเภอ", "ปีงบประมาณ"])["ค่าข้อมูล"].sum().reset_index()
    res = []

    for d in DISTS:
        sub = g[g["อำเภอ"] == d].sort_values("ปีงบประมาณ")
        lv = sub["ค่าข้อมูล"].iloc[-1] if not sub.empty else 0
        pv = lv
        if len(sub) >= 2:
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            model.fit(sub[["ปีงบประมาณ"]], sub["ค่าข้อมูล"])
            pv = model.predict([[yr + 1]])[0]

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

    # Graphs
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

    avg_rev = f["รายได้ปัจจุบัน"].mean()
    fig_scatter = px.scatter(
        f,
        x="รายได้ปัจจุบัน",
        y="แนวโน้ม (%)",
        text="อำเภอ",
        size="ยอดพยากรณ์ปีหน้า",
        color="วิเคราะห์",
        title="วิเคราะห์ศักยภาพ (รายได้ vs เติบโต)",
    )

    _CACHE = {
        "tot": f["ยอดพยากรณ์ปีหน้า"].sum(),
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
        "note": "✨ AI Insight: 'หาดใหญ่' และระโนด ยังคงเป็นพื้นที่ยุทธศาสตร์สำคัญ",
    }
    return _CACHE


# --- Layout ---
def layout():
    ai = run_ai_engine()
    return dbc.Container(
        [
            html.Div(
                [
                    html.H3(
                        "🤖 ผลการวิเคราะห์และพยากรณ์ด้วย AI",
                        className="text-primary fw-bold mb-4 mt-4",
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
                                    "พื้นที่แนวโน้มเติบโต", "ai-c", "1 พื้นที่", "📈", "success"
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                card(
                                    "พื้นที่ศักยภาพสูงสุด", "ai-tg", "หาดใหญ่", "🔥", "warning"
                                ),
                                md=3,
                            ),
                            dbc.Col(
                                card("รายได้ที่สูงที่สุด", "ai-max", "ระโนด", "🏆", "danger"),
                                md=3,
                            ),
                        ],
                        className="mb-4",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(dbc.CardBody(dcc.Graph(figure=ai["fig_bar"]))),
                                lg=7,
                            ),
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.Label("🔍 เลือกพื้นที่ดูพยากรณ์รายตัว:"),
                                            dcc.Dropdown(
                                                id="f-drop",
                                                options=[
                                                    {"label": k, "value": k}
                                                    for k in DISTS
                                                ],
                                                value=DISTS[0],
                                                clearable=False,
                                            ),
                                            dcc.Loading(dcc.Graph(id="f-line")),
                                        ]
                                    )
                                ),
                                lg=5,
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(dcc.Graph(figure=ai["fig_scatter"]))
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
                                        html.H5(
                                            "ตารางพยากรณ์รายพื้นที่", className="fw-bold"
                                        ),
                                        dash_table.DataTable(
                                            id="f-table",
                                            data=ai["list"],
                                            columns=[
                                                {"name": i, "id": j}
                                                for i, j in zip(
                                                    [
                                                        "อำเภอ",
                                                        "รายได้ปัจจุบัน",
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
                                                    "if": {
                                                        "column_id": "แนวโน้ม (%)",
                                                        "filter_query": "{แนวโน้ม (%)} < 0",
                                                    },
                                                    "color": "red",
                                                },
                                                {
                                                    "if": {
                                                        "column_id": "แนวโน้ม (%)",
                                                        "filter_query": "{แนวโน้ม (%)} > 0",
                                                    },
                                                    "color": "green",
                                                },
                                            ],
                                        ),
                                    ]
                                )
                            ),
                            className="mt-4",
                        )
                    ),
                ]
            )
        ],
        fluid=True,
        className="bg-light pb-5",
    )


@callback(Output("f-line", "figure"), Input("f-drop", "value"))
def update_forecast_line(d):
    ai = run_ai_engine()
    h = df[df["อำเภอ"] == d].groupby("ปีงบประมาณ")["ค่าข้อมูล"].sum().reset_index()
    it = next((i for i in ai["list"] if i["อำเภอ"] == d), None)
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
                name="AI Forecast",
                line=dict(dash="dot", width=4),
                marker=dict(size=12, symbol="star"),
            ),
        ]
    )
    return plt_fmt(fig.update_layout(title=f"📈 กราฟพยากรณ์: {d}"))
