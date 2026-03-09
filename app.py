import dash
from dash import html, dcc

# เปิดใช้ pages system
app = dash.Dash(__name__, use_pages=True)

server = app.server

app.layout = html.Div([

    html.H1("OTOP Dashboard", className="dashboard-title"), # แก้ให้ใช้ class

    # เมนูเปลี่ยนหน้า
    html.Div([
        dcc.Link("Overview", href="/"), # แก้ให้ใช้ class

        dcc.Link("Growth Analysis", href="/analysis"),
    ], className="menu-bar"),
    

    html.Hr(),

    # ตำแหน่งที่ page จะถูกโหลด
    dash.page_container

])

if __name__ == "__main__":
    app.run(debug=True)