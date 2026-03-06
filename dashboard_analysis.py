import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px

from modules.analysis_module import calculate_growth

# โหลดข้อมูล
df = pd.read_csv("data/cleaned_data.csv")

# คำนวณ growth
growth_df = calculate_growth(df)

# สร้างกราฟ
fig = px.bar(
    growth_df,
    x="อำเภอ",
    y="growth_percent",
    title="อัตราการเติบโตของรายได้ OTOP แต่ละอำเภอ (%)"
)

# สร้าง Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    
    html.H1("OTOP Sales Growth Dashboard", style={"textAlign": "center"}),

    dcc.Graph(
        id="growth-chart",
        figure=fig
    )

])

if __name__ == "__main__":
    app.run(debug=True)