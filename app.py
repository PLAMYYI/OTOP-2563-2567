import dash
from dash import html, dcc, Input, Output

app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

server = app.server

app.layout = html.Div(
    className="container",
    children=[
        html.Div(
            className="header",
            children=[
                html.H1("OTOP Smart Dashboard Pro", className="dashboard-title"),
                html.Div(
                    className="navbar",
                    children=[
                        dcc.Link("Overview", href="/", className="nav-button"),
                        dcc.Link(
                            "Growth Analysis", href="/analysis", className="nav-button"
                        ),
                    ],
                ),
            ],
        ),
        dash.page_container,
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