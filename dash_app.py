from dash import Dash, html, dash_table, dcc, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib  
import matplotlib.pyplot as plt
matplotlib.use('agg')
import seaborn as sns
from io import BytesIO
import base64

app = Dash(
 external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# data
df =  pd.read_csv("data/dataframe_data.csv")
df.drop(columns=["Unnamed: 0"], inplace=True)

# content for tab data
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

# content for tab visualisasi

# data 5 komoditas dengan harga tertinggi
max_prices = df.groupby('nama')['harga'].max().reset_index()
max_prices = max_prices.sort_values('harga', ascending=False)[:5].reset_index(drop=True)
fig_max_prices = px.bar(max_prices, x='nama', y='harga', 
             title='Harga Tertinggi untuk Bahan Pokok',
             labels={'nama': 'Bahan Pokok', 'harga': 'Harga Tertinggi'},
             template='plotly')

# data 5 komoditas dengan harga terendah
min_prices = df.groupby('nama')['harga'].min().reset_index()
min_prices = min_prices.sort_values('harga', ascending=True)[:5].reset_index(drop=True)
fig_min_prices = px.bar(min_prices, x='nama', y='harga', 
             title='Harga Tertinggi untuk Bahan Pokok',
             labels={'nama': 'Bahan Pokok', 'harga': 'Harga Tertinggi'},
             template='plotly')

# data 5 komoditas dengan standar deviasi tertinggi
std_prices = df.groupby('nama')['harga'].std().reset_index()
std_prices.columns = ['nama', 'std_dev']
std_prices_high = std_prices.sort_values(by = 'std_dev',ascending=False,  ignore_index=True)[:5]
fig_std_prices_high = px.bar(std_prices_high, x='nama', y='std_dev', 
             title='Standar Deviasi Tertinggi untuk Bahan Pokok',
             labels={'nama': 'Bahan Pokok', 'std_dev': 'Standar Deviasi'},
             template='plotly')

# data 5 komoditas dengan standar deviasi terendah
std_prices_low = std_prices.sort_values(by = 'std_dev',ascending=True,  ignore_index=True)[:5]
fig_std_prices_low = px.bar(std_prices_low, x='nama', y='std_dev', 
             title='Standar Deviasi Terendah untuk Bahan Pokok',
             labels={'nama': 'Bahan Pokok', 'std_dev': 'Standar Deviasi'},
             template='plotly')

# data rata-rata harga per kategori
avg_price_per_category = df.groupby('kategori')['harga'].mean().reset_index()
avg_price_per_category = avg_price_per_category.sort_values('harga', ascending=False, ignore_index=True)
fig_price_per_categori = px.bar(avg_price_per_category, x='kategori', y='harga', 
             title='Rata-rata Harga per Kategori',
             labels={'kategori': 'Kategori', 'harga': 'Rata-rata Harga'},
             template='plotly')

# data standar deviasi per kategori
avg_std_per_category = df.groupby(['kategori', 'nama'])['harga'].std().reset_index()
avg_std_per_category.rename(columns={'harga': 'std_dev'}, inplace=True)
avg_std_per_category = avg_std_per_category.groupby('kategori')['std_dev'].mean().reset_index()
avg_std_per_category = avg_std_per_category.sort_values('std_dev', ascending=False, ignore_index=True)
fig_std_per_category = px.bar(avg_std_per_category, x='kategori', y='std_dev', 
             title='Rata-rata Standar Deviasi per Kategori',
             labels={'kategori': 'Kategori', 'std_dev': 'Rata-rata Standar Deviasi'},
             template='plotly')

# data seasonal plot
@app.callback(
    Output('seasonal-plot', 'figure'),
    Input('dropdown-commodities', 'value')
)
def seasonal_plot(commodity):
    price_dist = df.copy()
    # selected_commodities = std_prices_high['nama'][:5].values
    # price_dist = price_dist[price_dist['nama'].isin(selected_commodities)].reset_index(drop=True)
    price_dist['tanggal'] = pd.to_datetime(price_dist['tanggal'])
    commodity_data = price_dist[price_dist['nama'] == commodity]
    commodity_data['year'] = commodity_data['tanggal'].dt.year
    commodity_data['month'] = commodity_data['tanggal'].dt.month

    # Create an empty figure
    # fig = px.line(commodity_data, x='month', y='harga', color='year', title=f'Harga {commodity} per Bulan')
    # Create an empty figure
    fig = go.Figure()

    # Loop through each unique year in the dataframe
    for year in commodity_data['year'].unique():
        subset = commodity_data[commodity_data['year'] == year]
        fig.add_trace(go.Scatter(
            x=subset['month'],
            y=subset['harga'],
            mode='lines+markers',
            name=str(year)
        ))

    # Update layout of the figure
    fig.update_layout(
        title=f'Seasonal Plot : {commodity}',
        xaxis_title='Bulan',
        yaxis_title='Harga',
        legend_title='Tahun',
        template='plotly_white'
    )
    return fig

# data tren pada tiap kategori
# avg_price_per_date_cat= df.groupby(['kategori', 'tanggal'])['harga'].mean().reset_index()
# avg_price_per_date_cat['tanggal'] = pd.to_datetime(avg_price_per_date_cat['tanggal'])
df['tanggal'] = pd.to_datetime(df['tanggal'])
kategoris = df['kategori'].unique()
fig = plt.figure(figsize=(14, 7))
for kategori in kategoris:
    subset = df[df['kategori'] == kategori]
    sns.lineplot(x='tanggal', y='harga', data=subset, label=kategori)
plt.title('Tren Harga Tiap Kategori Bahan Pokok Tahun 2019-2023')
plt.xlabel('Tanggal')
plt.ylabel('Harga')
plt.legend(title='Kategori')
plt.xticks(rotation=45)
 # Save it to a temporary buffer.
buf = BytesIO()
fig.savefig(buf, format="png")
# Embed the result in the html output.
fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
fig_bar_matplotlib = f'data:image/png;base64,{fig_data}'

tabvisualisasi_content = html.Div(children=[
    html.H3(children="Visualisasi Data Harga"),
    html.Hr(),
    html.Div(children=[
        html.H4(children="1. Komoditas dengan harga tertinggi dan terendah"),
        dbc.Row([
            dbc.Col(children=dcc.Graph(figure=fig_max_prices)),
            dbc.Col(children=dcc.Graph(figure=fig_min_prices))
        ]),
        dbc.Row([
            dbc.Col(children=html.P(children="5 komoditas dengan harga tertinggi")),
            dbc.Col(children=html.P(children="5 komoditas dengan harga terendah"))
        ])
    ], style={"margin-top" : "20px"}),
    html.Hr(),
    html.Div(children=[
        html.H4(children="2. Komoditas dengan standar deviasi tertinggi dan terendah"),
        dbc.Row([
            dbc.Col(children=dcc.Graph(figure=fig_std_prices_high)),
            dbc.Col(children=dcc.Graph(figure=fig_std_prices_low))
        ]),
        dbc.Row([
            dbc.Col(children=html.P(children="5 komoditas dengan standar deviasi tertinggi")),
            dbc.Col(children=html.P(children="5 komoditas dengan standar deviasi terendah"))
        ])
    ]),
    html.Hr(),
    html.Div(children=[
        html.H4(children="3. Rata-rata Harga per Kategori"),
        dcc.Graph(figure=fig_price_per_categori)
    ]),
    html.Hr(),
    html.Div(children=[
        html.H4(children="4. Rata-rata Standar Deviasi per Kategori"),
        dbc.Col(children=dcc.Graph(figure=fig_std_per_category))
    ]),
    html.Hr(),
    html.Div(children=[
        html.H4(children="5. Visualisasi musiman pada harga komoditas"),
        dbc.Row([
            dbc.Col(children=[
                dcc.Dropdown(options=df['nama'].unique(), value=df['nama'].unique()[0], id="dropdown-commodities"),
            ], width=3)
        ]),
        dcc.Graph(id="seasonal-plot", figure={})
    ]),
    html.Hr(),
    html.Div(children=[
        html.H4(children="6. Tren pada tiap kategori"),
        html.Img(src=fig_bar_matplotlib)   
    ]),
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
            dbc.Tab(tabdata_content, label="Data", tab_id="data"),
            dbc.Tab(tabvisualisasi_content, label="Visualisasi", tab_id="visualisasi"),
            dbc.Tab(label="Analisis", tab_id="analisis")
        ], id="main-tabs", active_tab="data"),
        html.Div(id="tabs-content")
    ])

    

], id="main-container", style={"margin" : "50px"})

if __name__ == '__main__':
    app.run(debug=True)