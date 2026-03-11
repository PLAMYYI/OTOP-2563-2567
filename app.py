import dash
from dash import html, dcc

# เปิดใช้ pages system
app = dash.Dash(__name__, use_pages=True)

server = app.server

app.layout = html.Div(
    [
        html.H1("OTOP Dashboard", style={"textAlign": "center"}),
        # เมนูเปลี่ยนหน้า
        html.Div(
            [
                dcc.Link("Overview", href="/", style={"marginRight": "20px"}),
            ],
            style={"textAlign": "center", "marginBottom": "30px"},
        ),
        html.Hr(),
        # ตำแหน่งที่ page จะถูกโหลด
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run(debug=True)
