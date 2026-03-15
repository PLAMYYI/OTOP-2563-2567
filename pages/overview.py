import dash, pandas as pd, numpy as np, io, plotly.express as px
from dash import dcc, html, Input, Output, callback, dash_table, ctx, State
from sklearn.ensemble import RandomForestRegressor

dash.register_page(__name__, path="/")
df = pd.read_csv("data/cleaned_data.csv")

# ลบช่องว่างชื่อ column
df.columns = df.columns.str.strip()

# แปลงเป็นตัวเลข
df["ค่าข้อมูล"] = pd.to_numeric(df["ค่าข้อมูล"], errors="coerce")
df["ปีงบประมาณ"] = pd.to_numeric(df["ปีงบประมาณ"], errors="coerce")

# ลบค่า NaN
df = df.dropna()

# ลบค่าซ้ำ
df = df.drop_duplicates()

# ลบค่าผิดปกติ (รายได้ติดลบ)
df = df[df["ค่าข้อมูล"] >= 0]

# แปลงเป็น int
df["ค่าข้อมูล"] = df["ค่าข้อมูล"].astype(int)
df["ปีงบประมาณ"] = df["ปีงบประมาณ"].astype(int)

# reset index
df = df.reset_index(drop=True)
C, S = {"P": "#6366f1", "G": "rgba(0,0,0,0.05)"}, {
    "c": {
        "background": "#fff",
        "padding": "25px",
        "borderRadius": "16px",
        "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
        "textAlign": "center",
        "flex": "1",
    }
}

sf = (
    lambda f: f.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=60, b=40),
        font=dict(size=12, color="#1e293b"),
    )
    .update_xaxes(showgrid=True, gridcolor=C["G"])
    .update_yaxes(showgrid=True, gridcolor=C["G"])
    or f
)
mc = lambda t, i=None, v=None, ic="", bg=None: html.Div(
    [
        html.P(
            f"{ic} {t}",
            style={"color": "#64748b" if not bg else "#fff", "fontWeight": "600"},
        ),
        html.H2(
            v,
            style={"fontWeight": "800", "fontSize": "32px"},
            **({"id": i} if i else {}),
        ),
    ],
    style={**S["c"], "background": bg, "color": "#fff"} if bg else S["c"],
)


def get_ai():
    try:
        res, ly, lt = (
            [],
            df["ปีงบประมาณ"].max(),
            df[df["ปีงบประมาณ"] == df["ปีงบประมาณ"].max()]["ค่าข้อมูล"].sum(),
        )
        for d in df["อำเภอ"].unique():
            d_df = (
                df[df["อำเภอ"] == d].groupby("ปีงบประมาณ")["ค่าข้อมูล"].sum().reset_index()
            )
            if len(d_df) > 1:
                p = (
                    RandomForestRegressor(n_estimators=50, random_state=42)
                    .fit(d_df[["ปีงบประมาณ"]].values, d_df["ค่าข้อมูล"].values)
                    .predict([[ly + 1]])[0]
                )
                res.append(
                    {
                        "อำเภอ": d,
                        "ยอดพยากรณ์ปีหน้า": round(p, 2),
                        "แนวโน้ม (%)": round(
                            ((p - d_df.iloc[-1]["ค่าข้อมูล"]) / d_df.iloc[-1]["ค่าข้อมูล"])
                            * 100,
                            2,
                        ),
                    }
                )
        f = pd.DataFrame(res)
        tp = f.nlargest(10, "ยอดพยากรณ์ปีหน้า").iloc[0]
        fig = px.bar(
            f.sort_values("ยอดพยากรณ์ปีหน้า"),
            y="อำเภอ",
            x="ยอดพยากรณ์ปีหน้า",
            orientation="h",
            title=f"อันดับพยากรณ์ปี {ly+1}",
            color="ยอดพยากรณ์ปีหน้า",
            color_continuous_scale="Viridis",
            text_auto=",.2f",
        ).update_layout(coloraxis_showscale=False, clickmode="event+select")
        return {
            "total": f["ยอดพยากรณ์ปีหน้า"].sum(),
            "growth": ((f["ยอดพยากรณ์ปีหน้า"].sum() - lt) / lt) * 100,
            "yr": ly + 1,
            "list": f.sort_index().to_dict("records"),
            "fig": sf(fig),
            "nar": f"✨ บทวิเคราะห์จาก AI: อำเภอ {tp['อำเภอ']} จะมีรายได้สูงสุดในปีหน้า (฿{tp['ยอดพยากรณ์ปีหน้า']:,.0f}) โดยภาพรวมจังหวัดมีแนวโน้มพุ่งขึ้น",
            "df": f,
        }
    except:
        return None


ai = get_ai()
layout = html.Div(
    style={"backgroundColor": "#f8fafc", "padding": "40px", "minHeight": "100vh"},
    children=[
        html.Div(
            [
                mc(t, i, ic=ic)
                for t, i, ic in [
                    ("Total Revenue", "total-value", "💰"),
                    ("Districts", "district-count", "📍"),
                    ("Average", "avg-value", "📊"),
                ]
            ],
            style={"display": "flex", "gap": "30px", "marginBottom": "40px"},
        ),
        html.Div(
            style={**S["c"], "padding": "30px", "textAlign": "left"},
            children=[
                html.Div(
                    [
                        html.Label("🔍 วิเคราะห์รายพื้นที่:"),
                        dcc.Dropdown(
                            id="dist-drop",
                            options=[
                                {"label": k, "value": k} for k in df["อำเภอ"].unique()
                            ],
                            value=df["อำเภอ"].unique()[0],
                            clearable=False,
                        ),
                    ],
                    style={
                        "width": "40%",
                        "display": "inline-block",
                        "marginRight": "5%",
                    },
                ),
                html.Div(
                    [
                        html.Label("📅 ช่วงปี:"),
                        dcc.RangeSlider(
                            id="yr-slide",
                            min=df["ปีงบประมาณ"].min(),
                            max=df["ปีงบประมาณ"].max(),
                            value=[df["ปีงบประมาณ"].min(), df["ปีงบประมาณ"].max()],
                            marks={int(i): str(i) for i in df["ปีงบประมาณ"].unique()},
                            step=1,
                        ),
                    ],
                    style={
                        "width": "50%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                    },
                ),
            ],
        ),
        html.Div([dcc.Graph(id="trend-graph")], style={**S["c"], "margin": "30px 0"}),
        html.Div(
            [
                html.Div([dcc.Graph(id="pie-graph")], style=S["c"]),
                html.Div([dcc.Graph(id="top-graph")], style={**S["c"], "flex": "1.5"}),
            ],
            style={"display": "flex", "gap": "30px"},
        ),
        (
            html.Div(
                [
                    html.Hr(style={"margin": "50px 0", "opacity": "0.1"}),
                    html.H3(
                        "📊 สรุปผลการพยากรณ์รายได้ด้วย AI", style={"textAlign": "center"}
                    ),
                    html.Div(
                        ai["nar"],
                        style={
                            "backgroundColor": "#f0f4ff",
                            "color": "#3730a3",
                            "padding": "15px",
                            "borderRadius": "12px",
                            "margin": "20px 0",
                            "fontWeight": "600",
                            "textAlign": "center",
                            "border": "1px solid #c7d2fe",
                        },
                    ),
                    html.Div(
                        [
                            mc(
                                f"พยากรณ์ {ai['yr']}",
                                v=f"฿{ai['total']:,.0f}",
                                ic="🚀",
                                bg="linear-gradient(135deg,#6366f1,#4f46e5)",
                            ),
                            mc(
                                "อัตราขยายตัว",
                                v=f"{ai['growth']:+.2f}%",
                                ic="📈",
                                bg="linear-gradient(135deg,#10b981,#059669)",
                            ),
                        ],
                        style={
                            "display": "flex",
                            "gap": "20px",
                            "marginBottom": "30px",
                        },
                    ),
                    html.Div(
                        [
                            html.Div(
                                [dcc.Graph(id="ai-rank-fig", figure=ai["fig"])],
                                style={**S["c"], "flex": "1.3"},
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H4("รายงานวิเคราะห์รายพื้นที่"),
                                            html.Button(
                                                "📥 Export",
                                                id="btn-export",
                                                style={
                                                    "padding": "5px 20px",
                                                    "borderRadius": "8px",
                                                    "border": "none",
                                                    "background": C["P"],
                                                    "color": "#fff",
                                                    "cursor": "pointer",
                                                },
                                            ),
                                        ],
                                        style={
                                            "display": "flex",
                                            "justifyContent": "space-between",
                                            "marginBottom": "15px",
                                        },
                                    ),
                                    dcc.Download(id="download-forecast"),
                                    dash_table.DataTable(
                                        data=ai["list"],
                                        columns=[
                                            {
                                                "name": i,
                                                "id": i,
                                                "type": "numeric",
                                                "format": {"specifier": ",.2f"},
                                            }
                                            for i in [
                                                "อำเภอ",
                                                "ยอดพยากรณ์ปีหน้า",
                                                "แนวโน้ม (%)",
                                            ]
                                        ],
                                        style_table={
                                            "height": "345px",
                                            "overflowY": "auto",
                                        },
                                        style_cell={
                                            "textAlign": "left",
                                            "padding": "12px",
                                        },
                                        style_header={
                                            "fontWeight": "bold",
                                            "backgroundColor": "#f8fafc",
                                        },
                                        style_data_conditional=[
                                            {
                                                "if": {
                                                    "filter_query": f"{{{k}}} {op} 0",
                                                    "column_id": k,
                                                },
                                                "color": c,
                                                "fontWeight": "bold",
                                            }
                                            for k, op, c in [
                                                ("แนวโน้ม (%)", ">", "#059669"),
                                                ("แนวโน้ม (%)", "<", "#ef4444"),
                                            ]
                                        ],
                                    ),
                                ],
                                style={**S["c"], "textAlign": "left"},
                            ),
                        ],
                        style={"display": "flex", "gap": "25px", "flexWrap": "wrap"},
                    ),
                ]
            )
            if ai
            else html.Div()
        ),
    ],
)


@callback(
    [
        Output("total-value", "children"),
        Output("district-count", "children"),
        Output("avg-value", "children"),
    ],
    Input("yr-slide", "value"),
)
def uk(v):
    f = df[(df["ปีงบประมาณ"] >= v[0]) & (df["ปีงบประมาณ"] <= v[1])]
    return (
        f"฿{f['ค่าข้อมูล'].sum():,.0f}",
        f"{f['อำเภอ'].nunique()}",
        f"฿{f['ค่าข้อมูล'].mean():,.0f}",
    )


@callback(
    [Output("trend-graph", "figure"), Output("dist-drop", "value")],
    [
        Input("dist-drop", "value"),
        Input("ai-rank-fig", "clickData"),
        Input("yr-slide", "value"),
    ],
)
def ut(dd, cl, v):
    d = cl["points"][0]["y"] if ctx.triggered_id == "ai-rank-fig" and cl else dd
    f = df[(df["อำเภอ"] == d) & (df["ปีงบประมาณ"] >= v[0]) & (df["ปีงบประมาณ"] <= v[1])]
    return (
        sf(
            px.line(
                f,
                x="ปีงบประมาณ",
                y="ค่าข้อมูล",
                title=f"📈 ทิศทาง: {d}",
                markers=True,
                color_discrete_sequence=[C["P"]],
            )
        ),
        d,
    )


@callback(
    [Output("pie-graph", "figure"), Output("top-graph", "figure")],
    Input("yr-slide", "value"),
)
def uc(v):
    f = (
        df[(df["ปีงบประมาณ"] >= v[0]) & (df["ปีงบประมาณ"] <= v[1])]
        .groupby("อำเภอ")["ค่าข้อมูล"]
        .sum()
        .reset_index()
    )

    # สร้างกราฟวงกลมพร้อมปรับแต่งระยะห่างตัวเลข
    fig_pie = px.pie(
        f,
        values="ค่าข้อมูล",
        names="อำเภอ",
        title="🥧 ส่วนแบ่งรายได้",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )

    # ขยับตัวเลขออกด้านนอก แยกชิ้นเค้ก และซ่อนชื่อในวงเพื่อลดความแออัด
    fig_pie.update_traces(
        textposition="outside", textinfo="percent", pull=[0.03] * len(f)
    )

    # ขยับ Legend และเพิ่มระยะห่างกราฟ
    fig_pie.update_layout(
        legend=dict(x=1.1, y=0.5),  # ขยับ Legend ไปทางขวา
        margin=dict(r=150),  # เพิ่ม Margin ขวาเพื่อให้ตัวเลขมีที่ว่าง
    )

    fig_bar = px.bar(
        f.nlargest(10, "ค่าข้อมูล"),
        x="อำเภอ",
        y="ค่าข้อมูล",
        title="🏆 Top 10",
        text_auto=",.2f",
        color="ค่าข้อมูล",
        color_continuous_scale="Viridis",
    ).update_layout(coloraxis_showscale=False)

    return sf(fig_pie), sf(fig_bar)


@callback(
    Output("download-forecast", "data"),
    Input("btn-export", "n_clicks"),
    prevent_initial_call=True,
)
def dfi(n):
    if not n:
        return None
    b = io.BytesIO()
    with pd.ExcelWriter(b, engine="xlsxwriter") as wr:
        ai["df"].to_excel(wr, index=False, sheet_name="Forecast")
        wb, ws, nm, hd = (
            wr.book,
            wr.sheets["Forecast"],
            wr.book.add_format({"num_format": "#,##0.00"}),
            wr.book.add_format({"bold": 1, "bg_color": "#F8FAFC", "border": 1}),
        )
        for c, v in enumerate(ai["df"].columns):
            ws.write(0, c, v, hd)
            ws.set_column(
                c,
                c,
                max(ai["df"][v].astype(str).map(len).max(), len(v)) + 5,
                nm if c > 0 else None,
            )
    return dcc.send_bytes(b.getvalue(), "otop_forecast_report.xlsx")
