from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(
 external_stylesheets=[dbc.themes.BOOTSTRAP]
)


app.layout = html.Div(children=[
    #header
    html.Div(children=[
        html.H1(children="Analisis Data Harga Bahan Pokok Bulanan Tahun 2019 - 2023 Kab. Banyumas",
                id="main-title"),
    html.Hr(id="title-line")        
    ], id="main-header")

], id="main-container", style={"margin" : "50px"})

if __name__ == '__main__':
    app.run(debug=True)