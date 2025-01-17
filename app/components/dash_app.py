import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_dash_app(flask_app):
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dashboard/',
        suppress_callback_exceptions=True
    )

    # Função para gerar dados simulados
    def generate_simulated_data():
        np.random.seed(0)
        dates = pd.date_range('2025-01-01', periods=30, freq='D')
        assets = ['PETR4', 'VALE3', 'ITUB4', 'ABEV3', 'BBDC4']
        data = {}
        for asset in assets:
            close_prices = np.random.normal(loc=100, scale=5, size=30).cumsum() + 100
            open_prices = close_prices - np.random.normal(loc=0, scale=1, size=30)
            high_prices = close_prices + np.random.normal(loc=1, scale=1, size=30)
            low_prices = close_prices - np.random.normal(loc=1, scale=1, size=30)
            volume = np.random.randint(100, 500, size=30)

            data[asset] = pd.DataFrame({
                'date': dates,
                'open': open_prices,
                'high': high_prices,
                'low': low_prices,
                'close': close_prices,
                'volume': volume
            }).set_index('date')
        return data

    # Carregar dados simulados
    data = generate_simulated_data()['PETR4']

    # Funções para criar gráficos
    def create_candlestick_chart(filtered_data):
        fig = go.Figure(data=[go.Candlestick(
            x=filtered_data.index,
            open=filtered_data['open'],
            high=filtered_data['high'],
            low=filtered_data['low'],
            close=filtered_data['close'],
            name='Candlestick Chart'
        )])
        return fig

    def create_engolfo_alta_chart(filtered_data):
        fig = go.Figure(data=[
            go.Scatter(x=filtered_data.index, y=filtered_data['close'], mode='lines+markers', name='Engolfo Alta')
        ])
        return fig

    def create_doji_chart(filtered_data):
        fig = go.Figure(data=[
            go.Scatter(x=filtered_data.index, y=(filtered_data['open'] + filtered_data['close']) / 2, mode='lines+markers', name='Doji')
        ])
        return fig

    def create_martelo_chart(filtered_data):
        fig = go.Figure(data=[
            go.Bar(x=filtered_data.index, y=filtered_data['volume'], name='Martelo')
        ])
        return fig

    # Layout do Dash
    dash_app.layout = html.Div([
        html.Div([
            dash_table.DataTable(
                id='table',
                columns=[{"name": col, "id": col} for col in ['ativo', 'preço de compra', 'preço de venda', 'quantidade', 'porcentagem de mudança']],
                data=[
                    {'ativo': 'PETR4', 'preço de compra': 30.5, 'preço de venda': 32.0, 'quantidade': 100, 'porcentagem de mudança': 5.0},
                    {'ativo': 'VALE3', 'preço de compra': 75.8, 'preço de venda': 78.0, 'quantidade': 50, 'porcentagem de mudança': 3.0},
                    {'ativo': 'ITUB4', 'preço de compra': 26.3, 'preço de venda': 28.5, 'quantidade': 150, 'porcentagem de mudança': 2.5},
                    {'ativo': 'ABEV3', 'preço de compra': 17.5, 'preço de venda': 18.0, 'quantidade': 200, 'porcentagem de mudança': 1.8},
                    {'ativo': 'BBDC4', 'preço de compra': 22.0, 'preço de venda': 23.5, 'quantidade': 120, 'porcentagem de mudança': 4.2},
                ],
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'center', 'padding': '10px', 'fontFamily': 'Arial'},
                style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
                style_data={'backgroundColor': 'white', 'color': 'black'}
            )
        ], style={'margin-top': '30px'}),

        html.Div([
            html.Label("Selecione o intervalo de datas:"),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=data.index.min(),
                end_date=data.index.max(),
                display_format='YYYY-MM-DD',
                style={'margin': '10px'}
            )
        ], style={'text-align': 'center', 'margin-top': '20px'}),

        html.Div([
            dcc.Graph(id='main-graph'),
        ], style={'margin-top': '30px'}),

        html.Div([
            html.Button("Mostrar Candlestick", id="show-candlestick-chart", n_clicks=0),
            html.Button("Mostrar Engolfo de Alta", id="show-engolfo-alta-chart", n_clicks=0),
            html.Button("Mostrar Doji", id="show-doji-chart", n_clicks=0),
            html.Button("Mostrar Martelo", id="show-martelo-chart", n_clicks=0)
        ], style={'text-align': 'center', 'margin-top': '20px'}),
    ])

    # Callback para atualizar o gráfico principal com base no intervalo de datas e no gráfico escolhido
    @dash_app.callback(
        Output('main-graph', 'figure'),
        [Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('show-candlestick-chart', 'n_clicks'),
         Input('show-engolfo-alta-chart', 'n_clicks'),
         Input('show-doji-chart', 'n_clicks'),
         Input('show-martelo-chart', 'n_clicks')]
    )
    def update_graph(start_date, end_date, candlestick_clicks, engolfo_clicks, doji_clicks, martelo_clicks):
        # Filtrar os dados conforme o intervalo de datas
        filtered_data = data
        if start_date and end_date:
            filtered_data = data.loc[start_date:end_date]

        # Verificar qual gráfico foi solicitado
        if candlestick_clicks > engolfo_clicks and candlestick_clicks > doji_clicks and candlestick_clicks > martelo_clicks:
            return create_candlestick_chart(filtered_data)
        elif engolfo_clicks > candlestick_clicks and engolfo_clicks > doji_clicks and engolfo_clicks > martelo_clicks:
            return create_engolfo_alta_chart(filtered_data)
        elif doji_clicks > candlestick_clicks and doji_clicks > engolfo_clicks and doji_clicks > martelo_clicks:
            return create_doji_chart(filtered_data)
        elif martelo_clicks > candlestick_clicks and martelo_clicks > engolfo_clicks and martelo_clicks > doji_clicks:
            return create_martelo_chart(filtered_data)
        else:
            return create_candlestick_chart(filtered_data)  # Default para Candlestick

    return dash_app
