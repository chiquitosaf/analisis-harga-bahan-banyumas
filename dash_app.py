from dash_app import Dash, html

app = Dash(__name__)


app.layout = html.Div([
    html.H1("Test")
])

if __name__ == '__main__':
    app.run(debug=True)