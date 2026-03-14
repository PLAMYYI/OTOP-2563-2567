import dash
from dash import html, dcc

# Initialize the Dash app with multi-page support enabled
# use_pages=True allows Dash to automatically detect files in the 'pages/' directory
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
    "color": "#6366f1",
    "fontWeight": "600",
    "fontSize": "14px",
    "padding": "8px 16px",
    "borderRadius": "8px",
    "transition": "all 0.3s",
    "margin": "0 10px",
}

# ---------------- MAIN LAYOUT ---------------- #
# This layout acts as a wrapper for all pages.
# It ensures the Header and Navigation are consistent across the app.
app.layout = html.Div(
    style={
        "backgroundColor": "#f8fafc",
        "minHeight": "100vh",
        "fontFamily": "'Segoe UI', Roboto, sans-serif",
    },
    children=[
        # Shared Header section
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
                # Navigation Menu
                html.Div(
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "gap": "15px",
                        "marginTop": "10px",
                    },
                    children=[
                        dcc.Link("Overview", href="/", style=NAV_LINK_STYLE),
                        dcc.Link(
                            "Growth Analysis", href="/analysis", style=NAV_LINK_STYLE
                        ),
                    ],
                ),
            ],
        ),
        # The Page Container where content from files in pages/ will be rendered
        html.Div(
            style={"width": "100%", "padding": "20px", "boxSizing": "border-box"},
            children=[dash.page_container],
        ),
        # Consistent Footer
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

if __name__ == "__main__":
    # Start the local server
    app.run(debug=True)
