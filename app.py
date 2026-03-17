import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

server = app.server

# สไตล์พื้นฐานสำหรับปุ่ม Nav (ถ้าคุณมี CSS แยก สามารถใช้ className แทนได้ครับ)
NAV_LINK_STYLE = {
    "padding": "10px 20px",
    "textDecoration": "none",
    "borderRadius": "8px",
    "margin": "0 5px",
    "transition": "0.3s",
}

app.layout = html.Div(
    className="container",
    children=[
        dcc.Location(id="url", refresh=False),  # เพิ่มตัวนี้เพื่อดักจับ URL
        html.Div(
            className="header",
            children=[
                html.H1("OTOP Smart Dashboard", className="dashboard-title"),
                html.Div(
                    className="navbar",
                    children=[
                        dcc.Link(
                            "Overview",
                            href="/",
                            id="nav-overview",
                            className="nav-button",
                            style=NAV_LINK_STYLE,
                        ),
                        dcc.Link(
                            "Growth Analysis",
                            href="/analysis",
                            id="nav-analysis",
                            className="nav-button",
                            style=NAV_LINK_STYLE,
                        ),
                        dcc.Link(
                            "AI Forecast",
                            href="/forecast",
                            id="nav-forecast",
                            className="nav-button",
                            style=NAV_LINK_STYLE,
                        ),  # เพิ่มปุ่ม Forecast
                    ],
                ),
            ],
        ),
        dash.page_container,
    ],
)

# ---------------- ACTIVE NAV BUTTON CALLBACK ---------------- #


@app.callback(
    [
        Output("nav-overview", "style"),
        Output("nav-analysis", "style"),
        Output("nav-forecast", "style"),  # เพิ่ม Output สำหรับหน้า forecast
    ],
    Input("url", "pathname"),
)
def highlight_nav(pathname):
    # เริ่มต้นด้วยสไตล์ปกติ
    overview_style = NAV_LINK_STYLE.copy()
    analysis_style = NAV_LINK_STYLE.copy()
    forecast_style = NAV_LINK_STYLE.copy()

    # สไตล์เมื่อปุ่มถูกเลือก (Active)
    active_style = {
        "backgroundColor": "#4f46e5",
        "color": "white",
        "fontWeight": "bold",
        "border": "none",
    }

    # ตรวจสอบ Path ปัจจุบัน
    if pathname == "/":
        overview_style.update(active_style)
    elif pathname == "/analysis":
        analysis_style.update(active_style)
    elif pathname == "/forecast":
        forecast_style.update(active_style)

    return overview_style, analysis_style, forecast_style


if __name__ == "__main__":
    app.run(debug=True)
