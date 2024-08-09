from dash import Dash, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd

app = Dash(
 external_stylesheets=[dbc.themes.BOOTSTRAP]
)

#content for tab data
df =  pd.read_csv("data/dataframe_data.csv")
df.drop(columns=["Unnamed: 0"], inplace=True)
tabdata_content = html.Div(children=[
        html.H3(children="Data Harga"),
        html.P(children="Data bersumber dari Dinas Perindustrian dan Perdagangan Kabupaten Banyumas langsung dengan tambahan data dari https://sigaokmas.banyumaskab.go.id dan https://www.bi.go.id/hargapangan"),
        html.H4(children="Nama-nama komoditas"),
        html.Ol(children=[html.Li(children=i) for i in df["nama"].unique()],
                style={"display" : "grid",
                       "grid-template-rows" : "repeat(13, 1fr)",
                       "grid-auto-flow" : "column"}),
        dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],
                             page_size=10, style_table={"overflowX" : "auto"},
                             filter_action="native", sort_action="native")
    ], style={"margin-top" : "20px"})

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
    ]),

    #tabs
    html.Div(children=[
        dbc.Tabs([
            dbc.Tab(tabdata_content,label="Data", tab_id="data"),
            dbc.Tab(label="Visualisasi", tab_id="visualisasi"),
            dbc.Tab(label="Analisis", tab_id="analisis")
        ], id="main-tabs", active_tab="data"),
        html.Div(id="tabs-content")
    ])

    

], id="main-container", style={"margin" : "50px"})

if __name__ == '__main__':
    app.run(debug=True)