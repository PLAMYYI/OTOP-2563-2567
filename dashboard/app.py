import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# ---------------- LOAD DATA ---------------- #

df = pd.read_csv("data/cleaned_data.csv")
forecast = pd.read_csv("data/forecast.csv")

app = Dash(__name__)

# ---------------- LAYOUT ---------------- #

app.layout = html.Div([

    html.H1("OTOP Dashboard",
            style={"textAlign": "center"}),

    # KPI SECTION
    html.Div([

        html.Div([
            html.H4("Total Revenue"),
            html.H2(id="total-value")
        ], className="card"),

        html.Div([
            html.H4("District Count"),
            html.H2(id="district-count")
        ], className="card"),

        html.Div([
            html.H4("Average Revenue"),
            html.H2(id="avg-value")
        ], className="card")

    ], style={
        "display": "flex",
        "gap": "40px",
        "justifyContent": "center"
    }),

    html.Br(),

    # FILTER
    dcc.Dropdown(
        id='district-dropdown',
        options=[{'label': i, 'value': i} for i in df['อำเภอ'].unique()],
        value=df['อำเภอ'].unique()[0]
    ),

    html.Br(),

    dcc.RangeSlider(
        id='year-slider',
        min=df['ปีงบประมาณ'].min(),
        max=df['ปีงบประมาณ'].max(),
        value=[df['ปีงบประมาณ'].min(), df['ปีงบประมาณ'].max()],
        marks={int(i): str(i) for i in df['ปีงบประมาณ'].unique()}
    ),

    html.Br(),

    # TREND GRAPH
    dcc.Graph(
        id='trend-graph',
        config={
            "scrollZoom": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d"
            ]
        }
    ),

    # PIE + FORECAST
    html.Div([

        dcc.Graph(
            id='pie-graph',
            style={"width": "50%"},
            config={
                "scrollZoom": True,
                "displaylogo": False
            }
        ),

        dcc.Graph(
            id='forecast-graph',
            style={"width": "50%"},
            config={
                "scrollZoom": True,
                "displaylogo": False
            }
        ),

    ], style={"display": "flex"}),

    html.Br(),

    # TOP 10 (ล่างสุด)
    dcc.Graph(
        id='top-graph',
        config={
            "scrollZoom": True,
            "displaylogo": False
        }
    )

])

# ---------------- KPI ---------------- #

@app.callback(
    Output("total-value", "children"),
    Output("district-count", "children"),
    Output("avg-value", "children"),
    Input("year-slider", "value")
)
def update_kpi(year_range):

    filtered = df[
        (df['ปีงบประมาณ'] >= year_range[0]) &
        (df['ปีงบประมาณ'] <= year_range[1])
    ]

    total = filtered['ค่าข้อมูล'].sum()
    count = filtered['อำเภอ'].nunique()
    avg = filtered['ค่าข้อมูล'].mean()

    return f"{total:,.0f}", count, f"{avg:,.0f}"

# ---------------- TREND ---------------- #

@app.callback(
    Output('trend-graph', 'figure'),
    Input('district-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_trend(district, year_range):

    filtered = df[
        (df['อำเภอ'] == district) &
        (df['ปีงบประมาณ'] >= year_range[0]) &
        (df['ปีงบประมาณ'] <= year_range[1])
    ]

    fig = px.line(
        filtered,
        x="ปีงบประมาณ",
        y="ค่าข้อมูล",
        title="OTOP Revenue Trend"
    )

    fig.update_layout(dragmode=False)

    return fig

# ---------------- PIE ---------------- #

@app.callback(
    Output('pie-graph', 'figure'),
    Input('year-slider', 'value')
)
def pie_chart(year_range):

    filtered = df[
        (df['ปีงบประมาณ'] >= year_range[0]) &
        (df['ปีงบประมาณ'] <= year_range[1])
    ]

    pie = filtered.groupby("อำเภอ")["ค่าข้อมูล"].sum().reset_index()

    fig = px.pie(
        pie,
        values="ค่าข้อมูล",
        names="อำเภอ",
        title="Revenue Share by District"
    )

    fig.update_layout(dragmode=False)

    return fig

# ---------------- FORECAST ---------------- #

@app.callback(
    Output('forecast-graph', 'figure'),
    Input('district-dropdown', 'value')
)
def forecast_graph(district):

    fig = px.line(
        forecast,
        x=forecast.columns[0],
        y=forecast.columns[1],
        title="Revenue Forecast"
    )

    fig.update_layout(dragmode=False)

    return fig

# ---------------- TOP 10 ---------------- #

@app.callback(
    Output('top-graph', 'figure'),
    Input('year-slider', 'value')
)
def top_graph(year_range):

    filtered = df[
        (df['ปีงบประมาณ'] >= year_range[0]) &
        (df['ปีงบประมาณ'] <= year_range[1])
    ]

    top = filtered.groupby("อำเภอ")["ค่าข้อมูล"].sum().nlargest(10).reset_index()

    fig = px.bar(
        top,
        x="อำเภอ",
        y="ค่าข้อมูล",
        title="Top 10 District Revenue"
    )

    fig.update_layout(dragmode=False)

    return fig


# ---------------- RUN SERVER ---------------- #

if __name__ == '__main__':
    app.run(debug=True)