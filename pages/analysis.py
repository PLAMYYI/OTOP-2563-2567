import dash
import pandas as pd
import numpy as np
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

from modules.analysis_module import calculate_growth

dash.register_page(__name__, path="/analysis")

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv("data/cleaned_data.csv")

if "prediction_label" in df.columns and "ค่าข้อมูล" not in df.columns:
    df = df.rename(columns={"prediction_label": "ค่าข้อมูล"})

df["ปีงบประมาณ"] = df["ปีงบประมาณ"].astype(int)

growth_df = calculate_growth(df)
growth_df = growth_df.sort_values("growth_percent", ascending=False)

top5 = growth_df.head(5)

years_sorted = sorted(df["ปีงบประมาณ"].unique())
first_yr = years_sorted[0]
last_yr = years_sorted[-1]
mid_yr = years_sorted[len(years_sorted) // 2]

# ---------------- KPI ---------------- #

avg_growth = round(growth_df["growth_percent"].mean(), 2)
max_row = growth_df.loc[growth_df["growth_percent"].idxmax()]
min_row = growth_df.loc[growth_df["growth_percent"].idxmin()]
positive_growth = growth_df[growth_df["growth_percent"] > 0].shape[0]
negative_growth = growth_df[growth_df["growth_percent"] < 0].shape[0]

# ---------------- DONUT CHART ---------------- #

status_df = pd.DataFrame(
    {"สถานะ": ["รายได้เพิ่มขึ้น", "รายได้ลดลง"], "จำนวน": [positive_growth, negative_growth]}
)

fig_donut = px.pie(
    status_df,
    names="สถานะ",
    values="จำนวน",
    hole=0.55,
    title="สัดส่วนการเติบโตของอำเภอ",
    color="สถานะ",
    color_discrete_map={"รายได้เพิ่มขึ้น": "#10b981", "รายได้ลดลง": "#ef4444"},
    template="plotly_white",
)
fig_donut.update_layout(height=420, font=dict(family="Prompt", size=16))

# ---------------- TOP 5 CHART ---------------- #

fig_top5 = px.bar(
    top5,
    x="อำเภอ",
    y="growth_percent",
    title="5 อำเภอที่มีการเติบโตสูงสุด",
    template="plotly_white",
    color="growth_percent",
    color_continuous_scale=["orange", "green"],
    text_auto=".1f",
)
fig_top5.update_layout(
    height=420,
    font=dict(family="Prompt", size=16),
    coloraxis_showscale=False,
)
fig_top5.update_xaxes(tickangle=0)

# ---------------- SCATTER: ปีแรก vs ปีสุดท้าย ---------------- #

pivot_scatter = df.pivot_table(
    index="อำเภอ", columns="ปีงบประมาณ", values="ค่าข้อมูล", aggfunc="sum"
).reset_index()

if first_yr in pivot_scatter.columns and last_yr in pivot_scatter.columns:
    pivot_scatter = pivot_scatter[["อำเภอ", first_yr, last_yr]].dropna()
    pivot_scatter.columns = ["อำเภอ", "ปีแรก", "ปีล่าสุด"]
    pivot_scatter["เปลี่ยนแปลง"] = pivot_scatter["ปีล่าสุด"] - pivot_scatter["ปีแรก"]

    fig_scatter = px.scatter(
        pivot_scatter,
        x="ปีแรก",
        y="ปีล่าสุด",
        text="อำเภอ",
        color="เปลี่ยนแปลง",
        color_continuous_scale="RdYlGn",
        size=pivot_scatter["ปีล่าสุด"].abs().clip(lower=1),
        title=f"เปรียบเทียบรายได้ ปี {first_yr} vs {last_yr} รายอำเภอ",
        template="plotly_white",
        labels={"ปีแรก": f"รายได้ปี {first_yr}", "ปีล่าสุด": f"รายได้ปี {last_yr}"},
    )
    # เส้น diagonal (ถ้าอยู่เหนือ = เพิ่มขึ้น)
    _min = pivot_scatter[["ปีแรก", "ปีล่าสุด"]].min().min()
    _max = pivot_scatter[["ปีแรก", "ปีล่าสุด"]].max().max()
    fig_scatter.add_shape(
        type="line",
        x0=_min,
        y0=_min,
        x1=_max,
        y1=_max,
        line=dict(color="#94a3b8", dash="dash"),
    )
    fig_scatter.add_annotation(
        x=_max * 0.9,
        y=_max * 0.95,
        text="เหนือเส้น = รายได้เพิ่มขึ้น",
        showarrow=False,
        font=dict(size=11, color="#64748b"),
    )
    fig_scatter.update_traces(textposition="top center")
    fig_scatter.update_layout(
        height=480,
        font=dict(family="Prompt", size=14),
        coloraxis_showscale=True,
        coloraxis_colorbar=dict(title="เปลี่ยนแปลง"),
    )
else:
    fig_scatter = go.Figure()

# ---------------- HEATMAP: อำเภอ x ปี ---------------- #

heatmap_data = (
    df.groupby(["อำเภอ", "ปีงบประมาณ"])["ค่าข้อมูล"]
    .sum()
    .reset_index()
    .pivot(index="อำเภอ", columns="ปีงบประมาณ", values="ค่าข้อมูล")
    .fillna(0)
)

fig_heatmap = px.imshow(
    heatmap_data,
    title="Heatmap รายได้ OTOP รายอำเภอ × ปี",
    color_continuous_scale="RdYlGn",
    aspect="auto",
    text_auto=".2s",
    template="plotly_white",
    labels=dict(color="รายได้"),
)
fig_heatmap.update_layout(
    height=520,
    font=dict(family="Prompt", size=13),
    xaxis_title="ปีงบประมาณ",
    yaxis_title="อำเภอ",
    coloraxis_colorbar=dict(title="รายได้ (บาท)"),
)
fig_heatmap.update_xaxes(tickformat="d")

# ---------------- ANIMATED BAR RACE: รายได้รายอำเภอแต่ละปี ---------------- #

race_df = df.groupby(["ปีงบประมาณ", "อำเภอ"])["ค่าข้อมูล"].sum().reset_index()

districts_all = race_df["อำเภอ"].unique()
palette = px.colors.qualitative.Plotly + px.colors.qualitative.D3
color_map = {d: palette[i % len(palette)] for i, d in enumerate(districts_all)}

x_min = race_df["ค่าข้อมูล"].min() * 1.3
x_max = race_df["ค่าข้อมูล"].max() * 1.25

sorted_years = sorted(race_df["ปีงบประมาณ"].unique())

frames = []
for yr in sorted_years:
    yr_data = race_df[race_df["ปีงบประมาณ"] == yr].sort_values("ค่าข้อมูล", ascending=True)
    frames.append(
        go.Frame(
            name=str(yr),
            data=[
                go.Bar(
                    x=yr_data["ค่าข้อมูล"],
                    y=yr_data["อำเภอ"],
                    orientation="h",
                    marker_color=[color_map[d] for d in yr_data["อำเภอ"]],
                    text=[f"{v/1e6:.1f}M" for v in yr_data["ค่าข้อมูล"]],
                    textposition="outside",
                )
            ],
            layout=go.Layout(title_text=f"🏁 Bar Race — รายได้ OTOP ปี {yr}"),
        )
    )

init_data = race_df[race_df["ปีงบประมาณ"] == sorted_years[0]].sort_values(
    "ค่าข้อมูล", ascending=True
)

fig_race = go.Figure(
    data=[
        go.Bar(
            x=init_data["ค่าข้อมูล"],
            y=init_data["อำเภอ"],
            orientation="h",
            marker_color=[color_map[d] for d in init_data["อำเภอ"]],
            text=[f"{v/1e6:.1f}M" for v in init_data["ค่าข้อมูล"]],
            textposition="outside",
        )
    ],
    frames=frames,
    layout=go.Layout(
        title=f"🏁 Bar Race — รายได้ OTOP ปี {sorted_years[0]}",
        template="plotly_white",
        height=560,
        font=dict(family="Prompt", size=13),
        xaxis=dict(range=[x_min, x_max], tickformat=".2s", title="รายได้ (บาท)"),
        yaxis=dict(title="", autorange=True),
        margin=dict(t=70, b=60, l=20, r=90),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                y=1.1,
                x=0,
                xanchor="left",
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=900, redraw=True), fromcurrent=True
                            ),
                        ],
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[
                            [None],
                            dict(
                                frame=dict(duration=0, redraw=False), mode="immediate"
                            ),
                        ],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [str(yr)],
                            dict(
                                mode="immediate", frame=dict(duration=900, redraw=True)
                            ),
                        ],
                        label=str(yr),
                    )
                    for yr in sorted_years
                ],
                x=0,
                y=0,
                len=1.0,
                currentvalue=dict(prefix="ปีงบประมาณ: ", font=dict(size=14)),
                pad=dict(t=45),
            )
        ],
    ),
)

# ====================================================================
#  DROPDOWN OPTIONS
# ====================================================================

district_options = [{"label": d, "value": d} for d in growth_df["อำเภอ"]]

# ====================================================================
#  SHARED STYLES
# ====================================================================

CARD = {
    "background": "#ffffff",
    "borderRadius": "16px",
    "boxShadow": "0 4px 20px rgba(0,0,0,0.07)",
    "padding": "24px",
    "marginBottom": "24px",
}

# ====================================================================
#  LAYOUT
# ====================================================================

layout = html.Div(
    style={
        "backgroundColor": "#f8fafc",
        "padding": "30px",
        "fontFamily": "Prompt, Tahoma, sans-serif",
    },
    children=[
        html.H2(
            "📊 Growth Analysis",
            style={"fontWeight": "800", "color": "#1e293b", "marginBottom": "6px"},
        ),
        html.P(
            "วิเคราะห์อัตราการเติบโตรายได้ OTOP รายอำเภอเชิงลึก",
            style={"color": "#64748b", "marginBottom": "30px"},
        ),
        # ── KPI ────────────────────────────────────────────────────
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Average Growth",
                            style={
                                "color": "#64748b",
                                "fontSize": "13px",
                                "margin": "0",
                            },
                        ),
                        html.H3(
                            f"{avg_growth}%",
                            style={"margin": "4px 0 0", "color": "#1e293b"},
                        ),
                    ],
                    className="card kpi-small",
                ),
                html.Div(
                    [
                        html.P(
                            "Highest Growth",
                            style={
                                "color": "#64748b",
                                "fontSize": "13px",
                                "margin": "0",
                            },
                        ),
                        html.H3(
                            max_row["อำเภอ"],
                            style={"margin": "4px 0 0", "color": "#1e293b"},
                        ),
                    ],
                    className="card kpi-small",
                ),
                html.Div(
                    [
                        html.P(
                            "Lowest Growth",
                            style={
                                "color": "#64748b",
                                "fontSize": "13px",
                                "margin": "0",
                            },
                        ),
                        html.H3(
                            min_row["อำเภอ"],
                            style={"margin": "4px 0 0", "color": "#1e293b"},
                        ),
                    ],
                    className="card kpi-small",
                ),
                html.Div(
                    [
                        html.P(
                            "Growing Districts",
                            style={
                                "color": "#64748b",
                                "fontSize": "13px",
                                "margin": "0",
                            },
                        ),
                        html.H3(
                            positive_growth,
                            style={"margin": "4px 0 0", "color": "#1e293b"},
                        ),
                    ],
                    className="card kpi-small",
                ),
                html.Div(
                    [
                        html.P(
                            "Declining Districts",
                            style={
                                "color": "#64748b",
                                "fontSize": "13px",
                                "margin": "0",
                            },
                        ),
                        html.H3(
                            negative_growth,
                            style={"margin": "4px 0 0", "color": "#1e293b"},
                        ),
                    ],
                    className="card kpi-small",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(5,1fr)",
                "gap": "12px",
                "marginBottom": "25px",
            },
        ),
        # ── Dropdown ────────────────────────────────────────────────
        html.Div(
            [
                html.H5("🔍 เลือกอำเภอเพื่อดูข้อมูล", style={"marginBottom": "8px"}),
                dcc.Dropdown(
                    id="district_filter",
                    options=district_options,
                    placeholder="แสดงทุกอำเภอ",
                    clearable=True,
                    style={"borderRadius": "10px"},
                ),
            ],
            style={"width": "320px", "marginBottom": "25px"},
        ),
        # ── ROW 1: Growth Bar (callback) ────────────────────────────
        html.Div([dcc.Graph(id="growth_chart")], style=CARD),
        # ── ROW 2: Donut + Top5 ─────────────────────────────────────
        html.Div(
            [
                html.Div([dcc.Graph(figure=fig_donut)], style={**CARD, "flex": "1"}),
                html.Div([dcc.Graph(figure=fig_top5)], style={**CARD, "flex": "1"}),
            ],
            style={"display": "flex", "gap": "20px"},
        ),
        # ── ROW 4: Heatmap ──────────────────────────────────────────
        html.Div(
            [
                html.H4(
                    "🌡️ Heatmap — รายได้ทุกอำเภอ × ทุกปี",
                    style={"marginBottom": "4px", "color": "#1e293b"},
                ),
                html.P(
                    "สีเขียว = รายได้สูง  |  สีแดง = รายได้ต่ำ/ติดลบ",
                    style={
                        "color": "#64748b",
                        "fontSize": "13px",
                        "marginBottom": "12px",
                    },
                ),
                dcc.Graph(figure=fig_heatmap),
            ],
            style=CARD,
        ),
        # ── ROW 5: Bar Race (full width) ────────────────────────────
        html.Div(
            [
                html.H4(
                    "🏁 Bar Race — รายได้ OTOP แต่ละปี",
                    style={"marginBottom": "4px", "color": "#1e293b"},
                ),
                html.P(
                    "กด ▶ Play เพื่อดูการเปลี่ยนแปลงรายได้แต่ละอำเภอตามปี",
                    style={
                        "color": "#64748b",
                        "fontSize": "13px",
                        "marginBottom": "12px",
                    },
                ),
                dcc.Graph(figure=fig_race),
            ],
            style=CARD,
        ),
        # ── ROW 6: Key Insights ──────────────────────────────────────
        html.Div(
            [
                html.H4(
                    "💡 Key Insights",
                    style={"marginBottom": "12px", "color": "#1e293b"},
                ),
                html.Ul(
                    [
                        html.Li(
                            f"อำเภอ {max_row['อำเภอ']} มีอัตราการเติบโตของรายได้ OTOP สูงที่สุด ประมาณ {round(max_row['growth_percent'],2)}%",
                            style={"marginBottom": "8px"},
                        ),
                        html.Li(
                            f"อำเภอ {min_row['อำเภอ']} มีอัตราการเติบโตต่ำที่สุด ประมาณ {round(min_row['growth_percent'],2)}%",
                            style={"marginBottom": "8px"},
                        ),
                        html.Li(
                            f"อัตราการเติบโตเฉลี่ยของรายได้ OTOP ทุกอำเภออยู่ที่ {avg_growth}%",
                            style={"marginBottom": "8px"},
                        ),
                        html.Li(
                            f"จำนวนอำเภอที่รายได้เพิ่มขึ้นมีทั้งหมด {positive_growth} อำเภอ",
                            style={"marginBottom": "8px"},
                        ),
                        html.Li(
                            f"จำนวนอำเภอที่รายได้ลดลงมีทั้งหมด {negative_growth} อำเภอ",
                            style={"marginBottom": "8px"},
                        ),
                        html.Li(
                            f"อำเภอที่มีรายได้สูงสุดในปี {last_yr} คือ "
                            f"{race_df[race_df['ปีงบประมาณ']==last_yr].nlargest(1,'ค่าข้อมูล').iloc[0]['อำเภอ']}",
                            style={"marginBottom": "8px"},
                        ),
                    ],
                    style={"lineHeight": "1.9", "color": "#334155"},
                ),
            ],
            className="card insight-box",
            style={**CARD, "marginTop": "4px"},
        ),
    ],
)

# ====================================================================
#  CALLBACKS
# ====================================================================


@dash.callback(
    Output("growth_chart", "figure"),
    Input("district_filter", "value"),
)
def update_chart(selected):
    data = growth_df if not selected else growth_df[growth_df["อำเภอ"] == selected]

    val = data["growth_percent"].tolist()

    # สีตามค่าจริง: ติดลบ=แดง, ใกล้ศูนย์=เหลือง, บวกมาก=เขียว (เทียบกับ 0 เสมอ)
    ABS_MAX = max(
        abs(growth_df["growth_percent"].max()),
        abs(growth_df["growth_percent"].min()),
        1,
    )

    def val_to_color(v):
        n = v / ABS_MAX  # -1 ถึง +1
        if n >= 0:
            # 0 → เหลือง, +1 → เขียว
            r = int(255 * (1 - n))
            g = int(180 + 75 * n)
            b = 60
        else:
            # 0 → เหลือง, -1 → แดง
            r = int(220 + 35 * abs(n))
            g = int(180 * (1 - abs(n)))
            b = 60
        return f"rgb({min(r,255)},{min(g,255)},{b})"

    bar_colors = [val_to_color(v) for v in val]

    fig = go.Figure(
        go.Bar(
            x=data["อำเภอ"],
            y=data["growth_percent"],
            text=[f"{v:.1f}%" for v in val],
            textposition="outside",
            marker_color=bar_colors,
            width=0.4 if len(data) == 1 else None,  # แคบลงเมื่อเลือกอำเภอเดียว
        )
    )

    y_min = min(val)
    y_max = max(val)
    y_pad_top = abs(y_max) * 0.22 if y_max != 0 else 5
    y_pad_bottom = abs(y_min) * 0.22 if y_min != 0 else 5

    fig.update_layout(
        title="อัตราการเติบโตของรายได้ OTOP รายอำเภอ (%)",
        template="plotly_white",
        height=520,
        font=dict(family="Prompt", size=16),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, b=60, l=60, r=20),
        xaxis=dict(
            tickangle=0,
            tickfont=dict(size=13),
            range=[-0.8, 0.8] if len(data) == 1 else None,
        ),
        yaxis=dict(
            title="growth (%)",
            range=[y_min - y_pad_bottom, y_max + y_pad_top],
        ),
        bargap=0.4,
    )
    fig.add_hline(y=0, line_dash="dot", line_color="#94a3b8", line_width=1.5)
    return fig
