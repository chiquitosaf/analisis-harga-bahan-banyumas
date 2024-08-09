from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(
 external_stylesheets=[dbc.themes.BOOTSTRAP]
)


app.layout = html.Div(children=[
    #header - title
    html.Div(children=[
        html.H1(children="Analisis Data Harga Bahan Pokok Bulanan Tahun 2019 - 2023 Kab. Banyumas",
                id="main-title"),
    html.Hr(id="title-line")        
    ], id="main-header"),

    #subheader - business question
    html.Div(children=[
        html.H2(children="Pertanyaan Bisnis"),
        html.Ol(children=[
            html.Li(children="Apa saja komoditas yang memiliki harga tertinggi?"),
            html.Li(children="Apa saja komoditas yang memiliki standar deviasi tertinggi dan terendah?"),
            html.Li(children="Apa kategori komoditas yang memiliki harga tertinggi?"),
            html.Li(children="Apa kategori komoditas yang memiliki standar deviasi tertinggi?"),
            html.Li(children="Bagaimana kondisi harga musiman pada komoditas yang memiliki standar deviasi tinggi?"),
            html.Li(children="Bagaimana tren harga pada tiap kategori?"),
            html.Li(children="Bagaiman korelasi mengenai harga rata-rata pada tiap kategori?"),
            html.Li(children="Bagaimana perubahan harga dari komoditas?"),
            html.Li(children="Pada bulan apa saja komoditas mengalami kenaikan harga tertinggi?")
        ], type="1")
    ])

], id="main-container", style={"margin" : "50px"})

if __name__ == '__main__':
    app.run(debug=True)