import dash
from dash import html, dcc, dash_table
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import os


# 1. ภาคการคำนวณ MACHINE LEARNING (พยากรณ์แยกรายอำเภอ + สรุปผลลัพธ์)
def generate_forecast():
    """ฟังก์ชัน AI: พยากรณ์รายได้และจัดอันดับความสำคัญ"""
    print("--- [System] เริ่มต้น AI Engine: วิเคราะห์ผลพยากรณ์ ---")
    summary_data = {
        "next_year_total": 0,
        "growth_pct": 0,
        "next_year": "-",
        "ranking_list": [],
        "bar_fig": {},
    }

    try:
        data_path = "data/cleaned_data.csv"
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            all_districts = df["อำเภอ"].unique()
            forecast_results = []

            latest_year = df["ปีงบประมาณ"].max()
            latest_total = df[df["ปีงบประมาณ"] == latest_year]["ค่าข้อมูล"].sum()

            for district in all_districts:
                d_df = (
                    df[df["อำเภอ"] == district]
                    .groupby("ปีงบประมาณ")["ค่าข้อมูล"]
                    .sum()
                    .reset_index()
                )

                if len(d_df) >= 2:
                    X = d_df[["ปีงบประมาณ"]].values
                    y = d_df["ค่าข้อมูล"].values
                    model = RandomForestRegressor(n_estimators=50, random_state=42)
                    model.fit(X, y)

                    last_year_val = int(d_df["ปีงบประมาณ"].max())
                    future_years = np.array([[last_year_val + 1]])
                    preds = model.predict(future_years)

                    d_latest_val = d_df[d_df["ปีงบประมาณ"] == last_year_val][
                        "ค่าข้อมูล"
                    ].values[0]
                    d_growth = ((preds[0] - d_latest_val) / d_latest_val) * 100

                    forecast_results.append(
                        {
                            "อำเภอ": district,
                            "รายได้ปีล่าสุด": d_latest_val,
                            "ยอดพยากรณ์ปีหน้า": preds[0],
                            "แนวโน้มเติบโต": d_growth,
                        }
                    )

            if forecast_results:
                f_df = pd.DataFrame(forecast_results).sort_values(
                    by="ยอดพยากรณ์ปีหน้า", ascending=True
                )

                # สรุปภาพรวม
                next_year = latest_year + 1
                next_year_pred_total = f_df["ยอดพยากรณ์ปีหน้า"].sum()
                growth_pct = (
                    (next_year_pred_total - latest_total) / latest_total
                ) * 100

                summary_data["next_year_total"] = next_year_pred_total
                summary_data["growth_pct"] = growth_pct
                summary_data["next_year"] = next_year
                summary_data["ranking_list"] = f_df.sort_values(
                    by="ยอดพยากรณ์ปีหน้า", ascending=False
                ).to_dict("records")

                # สร้างกราฟแท่งแนวตั้ง (Ranking) แทนกราฟเส้นที่ดูยาก
                fig = px.bar(
                    f_df,
                    y="อำเภอ",
                    x="ยอดพยากรณ์ปีหน้า",
                    orientation="h",
                    title=f"อันดับรายได้พยากรณ์แยกตามอำเภอ (ปี {next_year})",
                    color="ยอดพยากรณ์ปีหน้า",
                    color_continuous_scale="Viridis",
                    text_auto=",.0f",
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(
                        title="รายได้พยากรณ์ (บาท)", showgrid=True, gridcolor="#f1f5f9"
                    ),
                    yaxis=dict(title=""),
                    margin=dict(l=20, r=40, t=50, b=20),
                    coloraxis_showscale=False,
                )
                summary_data["bar_fig"] = fig

                print(
                    f"--- [System] พยากรณ์สำเร็จ: คำนวณอันดับ {len(forecast_results)} อำเภอเรียบร้อย ---"
                )
                return summary_data
    except Exception as e:
        print(f"--- [Error] AI Engine Failed: {e} ---")

    return summary_data


# เรียกใช้ AI
ai_summary = generate_forecast()

# 2. ตั้งค่าแอป DASH
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    update_title="AI Analyzing...",
)

server = app.server

# ---------------- STYLES ---------------- #
HEADER_STYLE = {
    "textAlign": "center",
    "padding": "25px 0",
    "backgroundColor": "#ffffff",
    "boxShadow": "0 2px 10px rgba(0,0,0,0.05)",
    "position": "sticky",
    "top": "0",
    "zIndex": "1000",
    "width": "100%",
}

AI_CARD_STYLE = {
    "background": "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
    "color": "white",
    "padding": "20px",
    "borderRadius": "15px",
    "textAlign": "center",
    "flex": "1",
    "boxShadow": "0 10px 15px -3px rgba(79, 70, 229, 0.3)",
}

# ---------------- MAIN LAYOUT ---------------- #
app.layout = html.Div(
    style={
        "backgroundColor": "#f8fafc",
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', Roboto, sans-serif",
    },
    children=[
        # Shared Header
        html.Div(
            style=HEADER_STYLE,
            children=[
                html.H1(
                    "OTOP Smart Dashboard Pro",
                    style={
                        "fontWeight": "800",
                        "color": "#1e293b",
                        "margin": "0",
                        "fontSize": "28px",
                        "letterSpacing": "-1px",
                    },
                ),
                html.Div(
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "gap": "15px",
                        "marginTop": "10px",
                    },
                    children=[
                        dcc.Link(
                            "Overview",
                            href="/",
                            style={
                                "textDecoration": "none",
                                "color": "#6366f1",
                                "fontWeight": "600",
                            },
                        ),
                        dcc.Link(
                            "Growth Analysis",
                            href="/analysis",
                            style={
                                "textDecoration": "none",
                                "color": "#6366f1",
                                "fontWeight": "600",
                            },
                        ),
                    ],
                ),
            ],
        ),
        # ส่วนแสดงเนื้อหาของแต่ละหน้า (Overview / Analysis)
        html.Div(
            style={"width": "100%", "padding": "40px", "boxSizing": "border-box"},
            children=[dash.page_container],
        ),
        # AI INSIGHT SECTION (ส่วนพยากรณ์ด้านล่าง)
        html.Div(
            style={
                "padding": "0 40px 40px 40px",
                "maxWidth": "1400px",
                "margin": "0 auto",
            },
            children=[
                html.Hr(style={"marginBottom": "40px", "opacity": "0.1"}),
                # Row 1: KPI Cards
                html.Div(
                    style={"display": "flex", "gap": "20px", "marginBottom": "30px"},
                    children=[
                        html.Div(
                            [
                                html.P(
                                    f"ยอดพยากรณ์รายได้รวมทั้งจังหวัด (ปี {ai_summary.get('next_year', '-')})",
                                    style={
                                        "margin": "0",
                                        "fontSize": "14px",
                                        "opacity": "0.9",
                                    },
                                ),
                                html.H2(
                                    f"฿{ai_summary['next_year_total']:,.0f}",
                                    style={
                                        "margin": "5px 0",
                                        "fontWeight": "800",
                                        "fontSize": "28px",
                                    },
                                ),
                            ],
                            style=AI_CARD_STYLE,
                        ),
                        html.Div(
                            [
                                html.P(
                                    "คาดการณ์อัตราการเติบโตเฉลี่ย",
                                    style={
                                        "margin": "0",
                                        "fontSize": "14px",
                                        "opacity": "0.9",
                                    },
                                ),
                                html.H2(
                                    f"{ai_summary['growth_pct']:+.2f}%",
                                    style={
                                        "margin": "5px 0",
                                        "fontWeight": "800",
                                        "fontSize": "28px",
                                    },
                                ),
                            ],
                            style={
                                **AI_CARD_STYLE,
                                "background": "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                            },
                        ),
                    ],
                ),
                # Row 2: Charts & Table
                html.Div(
                    style={"display": "flex", "gap": "30px", "flexWrap": "wrap"},
                    children=[
                        # กราฟแท่ง Ranking (มาแทนกราฟเส้นที่ดูไม่ออก)
                        html.Div(
                            style={
                                "flex": "1.2",
                                "minWidth": "500px",
                                "background": "white",
                                "padding": "25px",
                                "borderRadius": "20px",
                                "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
                            },
                            children=[
                                dcc.Graph(
                                    figure=ai_summary.get("bar_fig", {}),
                                    config={"displayModeBar": False},
                                )
                            ],
                        ),
                        # ตารางพยากรณ์แบบละเอียด
                        html.Div(
                            style={
                                "flex": "1",
                                "minWidth": "500px",
                                "background": "white",
                                "padding": "25px",
                                "borderRadius": "20px",
                                "boxShadow": "0 4px 20px rgba(0,0,0,0.05)",
                            },
                            children=[
                                html.H4(
                                    "ตารางสรุปข้อมูลพยากรณ์",
                                    style={"marginTop": "0", "marginBottom": "20px"},
                                ),
                                dash_table.DataTable(
                                    data=ai_summary["ranking_list"],
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
                                            "id": "แนวโน้มเติบโต",
                                            "type": "numeric",
                                            "format": {"specifier": ".2f"},
                                        },
                                    ],
                                    sort_action="native",
                                    style_table={
                                        "height": "400px",
                                        "overflowY": "auto",
                                    },
                                    style_header={
                                        "backgroundColor": "#f8fafc",
                                        "fontWeight": "bold",
                                        "border": "none",
                                    },
                                    style_cell={
                                        "textAlign": "left",
                                        "padding": "12px",
                                        "fontFamily": "inherit",
                                        "border": "none",
                                        "borderBottom": "1px solid #f1f5f9",
                                    },
                                    # เงื่อนไขสีสำหรับตัวเลขแนวโน้ม
                                    style_data_conditional=[
                                        {
                                            "if": {
                                                "filter_query": "{แนวโน้มเติบโต} > 0",
                                                "column_id": "แนวโน้มเติบโต",
                                            },
                                            "color": "#059669",
                                            "fontWeight": "bold",
                                        },
                                        {
                                            "if": {
                                                "filter_query": "{แนวโน้มเติบโต} < 0",
                                                "column_id": "แนวโน้มเติบโต",
                                            },
                                            "color": "#ef4444",
                                            "fontWeight": "bold",
                                        },
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # Footer
        html.Footer(
            "© 2024 OTOP Predictive Dashboard - AI Visual Ranking System",
            style={
                "textAlign": "center",
                "color": "#94a3b8",
                "fontSize": "12px",
                "padding": "30px 0",
            },
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
