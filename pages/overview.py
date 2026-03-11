import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px

dash.register_page(__name__, path="/")

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv("data/cleaned_data.csv")
forecast = pd.read_csv("data/forecast.csv")

df["ค่าข้อมูล"] = df["ค่าข้อมูล"].astype(int)
df["ปีงบประมาณ"] = df["ปีงบประมาณ"].astype(int)

# ---------------- GRAPH CONFIG ---------------- #

graph_config = {
    "scrollZoom": False,
    "displaylogo": False,
    "modeBarButtonsToRemove": [
        "zoom2d",
        "select2d",
        "lasso2d",
        "zoomIn2d",
        "zoomOut2d",
        "autoScale2d",
        "resetScale2d",
    ],
}

# ---------------- LAYOUT ---------------- #

layout = html.Div(
    [

        # KPI SECTION
        html.Div(
            [
                html.Div(
                    [html.H4("Total Revenue"), html.H2(id="total-value")],
                    className="card",
                ),
                html.Div(
                    [html.H4("District Count"), html.H2(id="district-count")],
                    className="card",
                ),
                html.Div(
                    [html.H4("Average Revenue"), html.H2(id="avg-value")],
                    className="card",
                ),
            ],
            style={"display": "flex", "gap": "40px", "justifyContent": "center"},
        ),

        html.Br(),

        # FILTER
        html.Div(
            [
                dcc.Dropdown(
                    id="district-dropdown",
                    options=[{"label": i, "value": i} for i in df["อำเภอ"].unique()],
                    value=df["อำเภอ"].unique()[0],
                ),
                html.Br(),
                dcc.RangeSlider(
                    id="year-slider",
                    min=int(df["ปีงบประมาณ"].min()),
                    max=int(df["ปีงบประมาณ"].max()),
                    value=[int(df["ปีงบประมาณ"].min()), int(df["ปีงบประมาณ"].max())],
                    marks={int(i): str(i) for i in sorted(df["ปีงบประมาณ"].unique())},
                ),
            ],
            style={
                "background": "white",
                "padding": "20px",
                "borderRadius": "15px",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.1)",
                "marginBottom": "30px",
            },
        ),

        html.Br(),

        # TREND GRAPH (BLOCK)
        html.Div(
            dcc.Graph(id="trend-graph", config=graph_config),
            style={
                "background": "white",
                "padding": "20px",
                "borderRadius": "15px",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.1)",
                "marginBottom": "30px",
            },
        ),

        # PIE + FORECAST
        html.Div(
            [
                html.Div(
                    dcc.Graph(id="pie-graph", config=graph_config),
                    style={
                        "width": "50%",
                        "background": "white",
                        "padding": "20px",
                        "borderRadius": "15px",
                        "boxShadow": "0 4px 12px rgba(0,0,0,0.1)",
                    },
                ),
                html.Div(
                    dcc.Graph(id="forecast-graph", config=graph_config),
                    style={
                        "width": "50%",
                        "background": "white",
                        "padding": "20px",
                        "borderRadius": "15px",
                        "boxShadow": "0 4px 12px rgba(0,0,0,0.1)",
                    },
                ),
            ],
            style={"display": "flex", "gap": "20px", "marginBottom": "30px"},
        ),

        # TOP 10
        html.Div(
            dcc.Graph(id="top-graph", config=graph_config),
            style={
                "background": "white",
                "padding": "20px",
                "borderRadius": "15px",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.1)",
            },
        ),
    ]
)

# ---------------- KPI ---------------- #
@callback(
    Output("total-value", "children"),
    Output("district-count", "children"),
    Output("avg-value", "children"),
    Input("year-slider", "value"),
)
def update_kpi(year_range):

    filtered = df[
        (df["ปีงบประมาณ"] >= year_range[0]) & (df["ปีงบประมาณ"] <= year_range[1])
    ]

    total = filtered["ค่าข้อมูล"].sum()
    count = filtered["อำเภอ"].nunique()
    avg = filtered["ค่าข้อมูล"].mean()

    return f"{total:,.0f}", count, f"{avg:,.0f}"

# ---------------- TREND ---------------- #

@callback(
    Output("trend-graph", "figure"),
    Input("district-dropdown", "value"),
    Input("year-slider", "value"),
)
def update_trend(district, year_range):

    filtered = df[
        (df["อำเภอ"] == district)
        & (df["ปีงบประมาณ"] >= year_range[0])
        & (df["ปีงบประมาณ"] <= year_range[1])
    ]

    fig = px.line(
        filtered,
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        title="OTOP Revenue Trend",
        markers=True,
    )

    fig.update_layout(yaxis_tickformat=",", dragmode=False)
    fig.update_xaxes(dtick=1)

    return fig

# ---------------- PIE ---------------- #

@callback(Output("pie-graph", "figure"), Input("year-slider", "value"))
def pie_chart(year_range):

    filtered = df[
        (df["ปีงบประมาณ"] >= year_range[0]) & (df["ปีงบประมาณ"] <= year_range[1])
    ]

    pie = filtered.groupby("อำเภอ")["ค่าข้อมูล"].sum().reset_index()

    fig = px.pie(pie, values="ค่าข้อมูล", names="อำเภอ", title="Revenue Share by District")

    fig.update_traces(texttemplate="%{value:,.0f}")

    return fig

# ---------------- FORECAST ---------------- #

@callback(Output("forecast-graph", "figure"), Input("district-dropdown", "value"))
def forecast_graph(district):

    fig = px.line(
        forecast,
        x=forecast.columns[0],
        y=forecast.columns[1],
        title="Revenue Forecast",
        markers=True,
    )

    fig.update_layout(yaxis_tickformat=",", dragmode=False)
    fig.update_xaxes(dtick=1)

    return fig

# ---------------- TOP 10 ---------------- #

@callback(Output("top-graph", "figure"), Input("year-slider", "value"))
def top_graph(year_range):

    filtered = df[
        (df["ปีงบประมาณ"] >= year_range[0]) & (df["ปีงบประมาณ"] <= year_range[1])
    ]

    top = filtered.groupby("อำเภอ")["ค่าข้อมูล"].sum().nlargest(10).reset_index()

    fig = px.bar(
        top,
        x="อำเภอ",
        y="ค่าข้อมูล",
        title="Top 10 District Revenue",
        text="ค่าข้อมูล",
    )

    fig.update_layout(yaxis_tickformat=",", dragmode=False)
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")

    return fig