import dash
from dash import dcc, html, Input, Output, callback, dash_table
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px

dash.register_page(__name__, path="/")

# 1. DATA & CONFIG
df = pd.read_csv("data/cleaned_data.csv")
df["ค่าข้อมูล"], df["ปีงบประมาณ"] = df["ค่าข้อมูล"].astype(int), df["ปีงบประมาณ"].astype(int)
C = {"P": "#6366f1", "BG": "#f8fafc", "W": "#ffffff", "T": "#1e293b"}
S = {
    "card": {
        "background": C["W"],
        "padding": "25px",
        "borderRadius": "16px",
        "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
        "textAlign": "center",
        "flex": "1",
    }
}


def style_fig(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=60, b=40),
        font=dict(size=12, color=C["T"]),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
    return fig


# 2. AI ENGINE
def get_ai():
    try:
        results = []
        latest_year, latest_total = (
            df["ปีงบประมาณ"].max(),
            df[df["ปีงบประมาณ"] == df["ปีงบประมาณ"].max()]["ค่าข้อมูล"].sum(),
        )
        for d in df["อำเภอ"].unique():
            d_df = (
                df[df["อำเภอ"] == d].groupby("ปีงบประมาณ")["ค่าข้อมูล"].sum().reset_index()
            )
            if len(d_df) >= 2:
                m = RandomForestRegressor(n_estimators=50, random_state=42).fit(
                    d_df[["ปีงบประมาณ"]].values, d_df["ค่าข้อมูล"].values
                )
                p = m.predict([[latest_year + 1]])[0]
                v = d_df[d_df["ปีงบประมาณ"] == latest_year]["ค่าข้อมูล"].values[0]
                results.append(
                    {"อำเภอ": d, "ยอดพยากรณ์ปีหน้า": p, "แนวโน้ม (%)": ((p - v) / v) * 100}
                )
        f = pd.DataFrame(results)
        fig = px.bar(
            f.sort_values("ยอดพยากรณ์ปีหน้า"),
            y="อำเภอ",
            x="ยอดพยากรณ์ปีหน้า",
            orientation="h",
            title=f"อันดับพยากรณ์ปี {latest_year+1}",
            color="ยอดพยากรณ์ปีหน้า",
            color_continuous_scale="Viridis",
            text_auto=",.0f",
        )
        return {
            "total": f["ยอดพยากรณ์ปีหน้า"].sum(),
            "growth": ((f["ยอดพยากรณ์ปีหน้า"].sum() - latest_total) / latest_total) * 100,
            "yr": latest_year + 1,
            "list": f.sort_values("ยอดพยากรณ์ปีหน้า", ascending=False).to_dict("records"),
            "fig": style_fig(fig),
        }
    except:
        return None


ai = get_ai()

# 3. LAYOUT
layout = html.Div(
    style={"backgroundColor": C["BG"], "padding": "40px", "minHeight": "100vh"},
    children=[
        html.Div(
            [
                html.Div(
                    [
                        html.P(t, style={"color": "#64748b", "fontWeight": "600"}),
                        html.H2(id=i, style={"fontWeight": "800", "fontSize": "32px"}),
                    ],
                    style=S["card"],
                )
                for t, i in [
                    ("Total Revenue", "total-value"),
                    ("District Count", "district-count"),
                    ("Average Revenue", "avg-value"),
                ]
            ],
            style={"display": "flex", "gap": "30px", "marginBottom": "40px"},
        ),
        html.Div(
            style={**S["card"], "padding": "30px", "textAlign": "left"},
            children=[
                html.Div(
                    [
                        html.Label("เลือกอำเภอ:"),
                        dcc.Dropdown(
                            id="dist-drop",
                            options=[
                                {"label": i, "value": i} for i in df["อำเภอ"].unique()
                            ],
                            value=df["อำเภอ"].unique()[0],
                            clearable=False,
                        ),
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "marginRight": "5%",
                    },
                ),
                html.Div(
                    [
                        html.Label("เลือกช่วงปี:"),
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
                        "width": "60%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                    },
                ),
            ],
        ),
        html.Div(
            [dcc.Graph(id="trend-graph")], style={**S["card"], "margin": "30px 0"}
        ),
        html.Div(
            [
                html.Div([dcc.Graph(id="pie-graph")], style=S["card"]),
                html.Div(
                    [dcc.Graph(id="top-graph")], style={**S["card"], "flex": "1.5"}
                ),
            ],
            style={"display": "flex", "gap": "30px"},
        ),
        (
            html.Div(
                [
                    html.Hr(style={"margin": "50px 0", "opacity": "0.1"}),
                    html.H3(
                        "📊 สรุปผลการพยากรณ์รายได้ด้วย AI",
                        style={"textAlign": "center", "marginBottom": "30px"},
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P(t, style={"margin": "0"}),
                                    html.H2(v, style={"fontWeight": "800"}),
                                ],
                                style={**S["card"], "background": b, "color": "white"},
                            )
                            for t, v, b in [
                                (
                                    f"ยอดพยากรณ์ปี {ai['yr']}",
                                    f"฿{ai['total']:,.0f}",
                                    "linear-gradient(135deg, #6366f1, #4f46e5)",
                                ),
                                (
                                    "อัตราเติบโตคาดการณ์",
                                    f"{ai['growth']:+.2f}%",
                                    "linear-gradient(135deg, #10b981, #059669)",
                                ),
                            ]
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
                                [dcc.Graph(figure=ai["fig"])],
                                style={**S["card"], "flex": "1.3"},
                            ),
                            html.Div(
                                [
                                    html.H4("สรุปรายอำเภอ"),
                                    dash_table.DataTable(
                                        data=ai["list"],
                                        columns=[
                                            {"name": "อำเภอ", "id": "อำเภอ"},
                                            {
                                                "name": "ยอดพยากรณ์ปีหน้า",
                                                "id": "ยอดพยากรณ์ปีหน้า",
                                                "type": "numeric",
                                                "format": {"specifier": ",.0f"},
                                            },
                                            {
                                                "name": "แนวโน้ม (%)",
                                                "id": "แนวโน้ม (%)",
                                                "type": "numeric",
                                                "format": {"specifier": ".2f"},
                                            },
                                        ],
                                        style_table={
                                            "height": "400px",
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
                                style={**S["card"], "textAlign": "left"},
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


# 4. CALLBACKS
@callback(
    Output("total-value", "children"),
    Output("district-count", "children"),
    Output("avg-value", "children"),
    Input("yr-slide", "value"),
)
def upd_kpi(v):
    f = df[(df["ปีงบประมาณ"] >= v[0]) & (df["ปีงบประมาณ"] <= v[1])]
    return (
        f"฿{f['ค่าข้อมูล'].sum():,.0f}",
        f"{f['อำเภอ'].nunique()} อำเภอ",
        f"฿{f['ค่าข้อมูล'].mean():,.0f}",
    )


@callback(
    Output("trend-graph", "figure"),
    Input("dist-drop", "value"),
    Input("yr-slide", "value"),
)
def upd_trend(d, v):
    return style_fig(
        px.line(
            df[
                (df["อำเภอ"] == d)
                & (df["ปีงบประมาณ"] >= v[0])
                & (df["ปีงบประมาณ"] <= v[1])
            ],
            x="ปีงบประมาณ",
            y="ค่าข้อมูล",
            title=f"แนวโน้มรายได้: {d}",
            markers=True,
            color_discrete_sequence=[C["P"]],
        )
    )


@callback(Output("pie-graph", "figure"), Input("yr-slide", "value"))
def upd_pie(v):
    f = (
        df[(df["ปีงบประมาณ"] >= v[0]) & (df["ปีงบประมาณ"] <= v[1])]
        .groupby("อำเภอ")["ค่าข้อมูล"]
        .sum()
        .reset_index()
    )
    fig = px.pie(
        f,
        values="ค่าข้อมูล",
        names="อำเภอ",
        title="สัดส่วนรายได้รายอำเภอ",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_traces(textinfo="percent+label")
    return style_fig(fig)


@callback(Output("top-graph", "figure"), Input("yr-slide", "value"))
def upd_top(v):
    f = (
        df[(df["ปีงบประมาณ"] >= v[0]) & (df["ปีงบประมาณ"] <= v[1])]
        .groupby("อำเภอ")["ค่าข้อมูล"]
        .sum()
        .nlargest(10)
        .reset_index()
    )
    return style_fig(
        px.bar(
            f,
            x="อำเภอ",
            y="ค่าข้อมูล",
            title="10 อันดับอำเภอที่มีรายได้สูงสุด",
            text_auto=",.0f",
            color="ค่าข้อมูล",
            color_continuous_scale="Viridis",
        ).update_layout(coloraxis_showscale=False)
    )
