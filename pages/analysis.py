import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ลงทะเบียนหน้านี้ให้เป็นหน้า "/analysis" (Growth Analysis)
dash.register_page(__name__, path="/analysis")

# ---------------- MOCK DATA (แทนที่ด้วย data/cleaned_data.csv ของคุณ) ---------------- #
data = {
    "อำเภอ": [
        "เมืองสงขลา",
        "หาดใหญ่",
        "ระโนด",
        "สทิงพระ",
        "จะนะ",
        "เทพา",
        "สะบ้าย้อย",
        "นาทวี",
        "นาหม่อม",
        "คลองหอยโข่ง",
        "บางกล่ำ",
        "ควนเนียง",
        "รัตภูมิ",
        "สิงหนคร",
        "กระแสสินธุ์",
    ],
    "growth_percent": [
        42.4,
        38.0,
        33.5,
        24.1,
        23.0,
        21.5,
        20.2,
        18.5,
        10.1,
        -1.5,
        -25.0,
        -94.91,
        -38.5,
        -60.0,
        -75.0,
    ],
}
df = pd.DataFrame(data).sort_values(by="growth_percent", ascending=False)

# ---------------- STYLES ---------------- #
CARD_STYLE = {
    "background": "white",
    "padding": "25px",
    "borderRadius": "15px",
    "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
    "textAlign": "center",
    "flex": "1",
}

CONTAINER_STYLE = {
    "backgroundColor": "#f0f5ff",  # พื้นหลังสีฟ้าอ่อนตามรูป
    "padding": "40px",
    "minHeight": "100vh",
    "fontFamily": "sans-serif",
}

# ---------------- LAYOUT ---------------- #
layout = html.Div(
    style=CONTAINER_STYLE,
    children=[
        # KPI SECTION (3 Cards)
        html.Div(
            style={"display": "flex", "gap": "20px", "marginBottom": "30px"},
            children=[
                # Average Growth
                html.Div(
                    [
                        html.P(
                            "Average Growth",
                            style={
                                "color": "#666",
                                "fontSize": "16px",
                                "fontWeight": "600",
                            },
                        ),
                        html.H2(
                            f"{df['growth_percent'].mean():.2f}%",
                            style={"margin": "10px 0", "fontWeight": "bold"},
                        ),
                    ],
                    style=CARD_STYLE,
                ),
                # Highest Growth
                html.Div(
                    [
                        html.P(
                            "Highest Growth",
                            style={
                                "color": "#666",
                                "fontSize": "16px",
                                "fontWeight": "600",
                            },
                        ),
                        html.H2(
                            f"{df.iloc[0]['อำเภอ']} ({df.iloc[0]['growth_percent']}%)",
                            style={"margin": "10px 0", "fontWeight": "bold"},
                        ),
                    ],
                    style=CARD_STYLE,
                ),
                # Lowest Growth
                html.Div(
                    [
                        html.P(
                            "Lowest Growth",
                            style={
                                "color": "#666",
                                "fontSize": "16px",
                                "fontWeight": "600",
                            },
                        ),
                        html.H2(
                            f"{df.iloc[-1]['อำเภอ']} ({df.iloc[-1]['growth_percent']}%)",
                            style={"margin": "10px 0", "fontWeight": "bold"},
                        ),
                    ],
                    style=CARD_STYLE,
                ),
            ],
        ),
        # CHARTS SECTION
        html.Div(
            style={"display": "flex", "gap": "20px"},
            children=[
                # Left Chart: Growth by District
                html.Div(
                    style={
                        "flex": "1.5",
                        "background": "white",
                        "padding": "20px",
                        "borderRadius": "15px",
                        "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
                    },
                    children=[
                        html.H4(
                            "อัตราการเติบโตของรายได้ OTOP (%)",
                            style={"marginBottom": "20px", "fontSize": "16px"},
                        ),
                        dcc.Graph(
                            id="growth-all-graph", config={"displayModeBar": False}
                        ),
                    ],
                ),
                # Right Chart: Top 5
                html.Div(
                    style={
                        "flex": "1",
                        "background": "white",
                        "padding": "20px",
                        "borderRadius": "15px",
                        "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
                    },
                    children=[
                        html.H4(
                            "Top 5 อำเภอที่เติบโตสูงสุด",
                            style={"marginBottom": "20px", "fontSize": "16px"},
                        ),
                        dcc.Graph(
                            id="top5-growth-graph", config={"displayModeBar": False}
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# ---------------- CALLBACKS ---------------- #


@callback(
    Output("growth-all-graph", "figure"),
    Output("top5-growth-graph", "figure"),
    Input("growth-all-graph", "id"),
)
def update_graphs(_):
    # 1. Main Growth Graph (Color conditional)
    colors = []
    for val in df["growth_percent"]:
        if val > 30:
            colors.append("#059669")
        elif val > 10:
            colors.append("#65a30d")
        elif val > 0:
            colors.append("#a3e635")
        elif val > -50:
            colors.append("#f97316")
        else:
            colors.append("#ff0000")

    fig_all = go.Figure(
        data=[go.Bar(x=df["อำเภอ"], y=df["growth_percent"], marker_color=colors)]
    )
    fig_all.update_layout(
        margin=dict(l=20, r=20, t=5, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickfont=dict(size=10)),
        yaxis=dict(title="growth_percent", showgrid=True, gridcolor="#f0f0f0"),
    )

    # 2. Top 5 Graph (Solid Blue)
    top5 = df.head(5)
    fig_top5 = px.bar(
        top5, x="อำเภอ", y="growth_percent", color_discrete_sequence=["#6366f1"]
    )
    fig_top5.update_layout(
        margin=dict(l=20, r=20, t=5, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="growth_percent", showgrid=True, gridcolor="#f0f0f0"),
    )

    return fig_all, fig_top5


# สำหรับการรันแบบ Standalone เพื่อทดสอบ (เปิด use_pages=True)
if __name__ == "__main__":
    # เพิ่ม suppress_callback_exceptions=True เพื่อแก้ปัญหา ID not found ในระบบ Multi-page
    app = dash.Dash(
        __name__, use_pages=True, pages_folder="", suppress_callback_exceptions=True
    )

    # ลงทะเบียนหน้าแบบ manual สำหรับกรณีรันไฟล์เดียว
    dash.register_page("growth_analysis", layout=layout, path="/analysis")

    app.layout = html.Div([dash.page_container])
    app.run_server(debug=True)
