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
import numpy as np
from dash.dash_table.Format import Format, Scheme, Trim

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

def matplotlib_to_plotly(fig):
    # Convert a matplotlib figure to Plotly figure
    buf = BytesIO()
    fig.savefig(buf, format="png")
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f'data:image/png;base64,{fig_data}'

# data tren pada tiap kategori
avg_price_per_date_cat= df.groupby(['kategori', 'tanggal'])['harga'].mean().reset_index()
avg_price_per_date_cat['tanggal'] = pd.to_datetime(avg_price_per_date_cat['tanggal'])
df['tanggal'] = pd.to_datetime(df['tanggal'])
kategoris = df['kategori'].unique()
fig_tren = plt.figure(figsize=(13, 6))
for kategori in kategoris:
    subset = df[df['kategori'] == kategori]
    sns.lineplot(x='tanggal', y='harga', data=subset, label=kategori)
plt.title('Tren Harga Tiap Kategori Bahan Pokok Tahun 2019-2023')
plt.xlabel('Tanggal')
plt.ylabel('Harga')
plt.legend(title='Kategori')
plt.xticks(rotation=45)
fig_bar_matplotlib = matplotlib_to_plotly(fig_tren)

# data korelasi antar kategori
df_corr = avg_price_per_date_cat.pivot_table(index='tanggal', columns='kategori', values='harga')
fig_corr = plt.figure(figsize=(15, 6))
sns.heatmap(df_corr.corr(), annot=True, cmap='coolwarm')
plt.title('Korelasi antar Kategori Bahan Pokok')
fig_corr_matplotlib = matplotlib_to_plotly(fig_corr)

# data perubahan harga bahan pokok
# Perubahan Harga Bahan Pokok dari tahun 2019 sampai 2023

df_perubahan = pd.DataFrame()
commodities = df['nama'].unique()

df_perubahan['komoditas'] = commodities
price_changes = []
naik_turun = []
for commodity in commodities:
    subset = df[df['nama'] == commodity]['harga']
    for i in range(len(subset)):
        if subset.iloc[i] != 0 and not np.isnan(subset.iloc[i]):
            price_changes.append(np.abs(subset.iloc[len(subset)-1] - subset.iloc[i]) / subset.iloc[i] * 100)
            naik_turun.append('naik' if subset.iloc[len(subset)-1] > subset.iloc[i] else 'turun')
            break
df_perubahan['perubahan_harga(%)'] = price_changes
df_perubahan['naik_turun'] = naik_turun
df_perubahan = df_perubahan.sort_values('perubahan_harga(%)', ascending=False, ignore_index=True)

fig_pie = plt.figure(figsize=(4, 6))
plt.pie(df_perubahan['naik_turun'].value_counts(), labels=['Naik', 'Turun'], autopct='%1.1f%%', startangle=90)
plt.suptitle('Perbandingan Jumlah Harga Naik dan Turun')
plt.title(f'Naik : {df_perubahan["naik_turun"].value_counts()["naik"]}\nTurun : {df_perubahan["naik_turun"].value_counts()["turun"]}',
           y = 0.9,
           loc='left')
fig_pie_matplotlib = matplotlib_to_plotly(fig_pie)

columns_perubahan = [
    dict(id='komoditas', name='Komoditas'),
    dict(id='perubahan_harga(%)', name='Perubahan Harga (%)', type='numeric', format=Format(precision=2, scheme=Scheme.fixed)),
    dict(id='naik_turun', name='Naik/Turun')
]


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
    html.Hr(),
    html.Div(children=[
        html.H4(children="7. Korelasi mengenai harga rata-rata pada tiap kategori"),
        html.Img(src=fig_corr_matplotlib)   
    ]),
    html.Hr(),
    html.Div(children=[
        html.H4(children="8. Perubahan harga dari komoditas"),
        html.Div(children=[
           dbc.Row([
            # TODO Customize the table
               dbc.Col(children=dash_table.DataTable(df_perubahan[:(len(df_perubahan)//2) + 1].to_dict('records'),
                                                      columns=columns_perubahan,
                                                      style_header={'backgroundColor': 'rgb(128, 128, 128)',
                                                                    'fontWeight': 'bold',
                                                                    'color' : 'white'},
                                                      style_cell={'textAlign': 'left'},
                                                      style_data_conditional=[
                                                          {
                                                              'if': {
                                                                  'filter_query': "{naik_turun} eq 'turun'",
                                                              },
                                                                'backgroundColor': 'rgb(153, 0, 0)',
                                                                'color': 'white'
                                                          }
                                                      ])),
               dbc.Col(children=dash_table.DataTable(df_perubahan[(len(df_perubahan)//2) + 1:].to_dict('records'),
                                                      columns=columns_perubahan,
                                                      style_header={'backgroundColor': 'rgb(128, 128, 128)',
                                                                    'fontWeight': 'bold',
                                                                    'color' : 'white'},
                                                      style_cell={'textAlign': 'left'},
                                                      style_data_conditional=[
                                                          {
                                                              'if': {
                                                                  'filter_query': "{naik_turun} eq 'turun'",
                                                              },
                                                                'backgroundColor': 'rgb(255, 127, 4)',
                                                                'color': 'white'
                                                          }
                                                      ])),
               dbc.Col(html.Img(src=fig_pie_matplotlib))
           ]) 
        ])
    ])
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