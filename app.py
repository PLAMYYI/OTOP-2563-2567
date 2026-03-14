import dash
from dash import html, dcc

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

if __name__ == "__main__":
    app.run(debug=True)
