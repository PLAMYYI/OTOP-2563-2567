import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# โหลดข้อมูล
df = pd.read_csv("data/cleaned_data.csv")
forecast = pd.read_csv("data/forecast.csv")

app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("Thailand Data Dashboard"),

    dcc.Dropdown(
        id='district-dropdown',
        options=[{'label': i, 'value': i} for i in df['district'].unique()],
        value=df['district'].unique()[0]
    ),

    dcc.RangeSlider(
        id='year-slider',
        min=df['year'].min(),
        max=df['year'].max(),
        value=[df['year'].min(), df['year'].max()],
        marks={str(year): str(year) for year in df['year'].unique()}
    ),

    dcc.Graph(id='trend-graph'),

    dcc.Graph(id='forecast-graph')

])


@app.callback(
    Output('trend-graph', 'figure'),
    Input('district-dropdown', 'value'),
    Input('year-slider', 'value')
)

def update_graph(district, year_range):

    filtered = df[
        (df['district'] == district) &
        (df['year'] >= year_range[0]) &
        (df['year'] <= year_range[1])
    ]

    fig = px.line(filtered, x="year", y="value", title="Trend")

    return fig


@app.callback(
    Output('forecast-graph', 'figure'),
    Input('district-dropdown', 'value')
)

def forecast_graph(district):

    filtered = forecast[forecast['district'] == district]

    fig = px.line(filtered, x="year", y="prediction", title="Forecast")

    return fig


if __name__ == '__main__':
    app.run(debug=True)