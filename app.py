import dash
from dash import html, dcc, Input, Output

# Initialize the Dash app with multi-page support enabled
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    update_title="Loading Dashboard...",
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

NAV_LINK_STYLE = {
    "textDecoration": "none",
    "color": "#4f46e5",
    "fontWeight": "600",
    "fontSize": "15px",
    "padding": "10px 24px",
    "borderRadius": "25px",
    "backgroundColor": "#ffffff",
    "border": "1px solid #e2e8f0",
    "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
    "transition": "all 0.25s ease",
    "margin": "0 6px",
}

# ---------------- MAIN LAYOUT ---------------- #

app.layout = html.Div(
    style={
        "backgroundColor": "#f8fafc",
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', Roboto, sans-serif",
    },
    children=[

        # Detect current page
        dcc.Location(id="url"),

        # Header
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

                # Navigation
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
                            id="nav-overview",
                            style=NAV_LINK_STYLE,
                        ),

                        dcc.Link(
                            "Growth Analysis",
                            href="/analysis",
                            id="nav-analysis",
                            style=NAV_LINK_STYLE,
                        ),
                    ],
                ),
            ],
        ),

        # Page Content
        html.Div(
            style={
                "width": "100%",
                "padding": "20px",
                "boxSizing": "border-box",
            },
            children=[dash.page_container],
        ),

        # Footer
        html.Footer(
            "© 2024 OTOP Predictive Analytics System - AI District Forecasting Project",
            style={
                "textAlign": "center",
                "color": "#94a3b8",
                "fontSize": "12px",
                "padding": "30px 0",
            },
        ),
    ],
)

# ---------------- ACTIVE NAV BUTTON ---------------- #

@app.callback(
    Output("nav-overview", "style"),
    Output("nav-analysis", "style"),
    Input("url", "pathname"),
)
def highlight_nav(pathname):

    overview_style = NAV_LINK_STYLE.copy()
    analysis_style = NAV_LINK_STYLE.copy()

    active_style = {
        "backgroundColor": "#4f46e5",
        "color": "white",
        "border": "none",
    }

    if pathname == "/":
        overview_style.update(active_style)

    elif pathname == "/analysis":
        analysis_style.update(active_style)

    return overview_style, analysis_style


if __name__ == "__main__":
    app.run(debug=True)