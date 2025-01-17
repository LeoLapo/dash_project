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
    data = generate_simulated_data()

    # Funções para criar gráficos
    def create_candlestick_chart(start_date=None, end_date=None):
        filtered_data = data['PETR4']
        if start_date and end_date:
            filtered_data = filtered_data.loc[start_date:end_date]

        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=filtered_data.index,
                open=filtered_data['open'],
                high=filtered_data['high'],
                low=filtered_data['low'],
                close=filtered_data['close'],
                name='Candlestick Chart'
            )
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price",
            title="Candlestick Chart with Date Range",
            hovermode="x unified"
        )
        return fig

    def create_bar_chart():
        fig = go.Figure(
            data=[go.Bar(x=data['PETR4'].index, y=data['PETR4']['volume'], name="Volume")]
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Volume",
            title="Bar Chart (Volume)"
        )
        return fig

    def create_line_chart():
        fig = go.Figure(
            data=[go.Scatter(x=data['PETR4'].index, y=data['PETR4']['close'], mode='lines', name="Close Price")]
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Close Price",
            title="Line Chart (Close Price)"
        )
        return fig

    def create_martelo_chart():
        fig = go.Figure(data=[
            go.Bar(x=data['PETR4'].index, y=data['PETR4']['volume'], name='Martelo')
        ])
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Volume",
            title="Gráfico de Martelo"
        )
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
                start_date=data['PETR4'].index.min(),
                end_date=data['PETR4'].index.max(),
                display_format='YYYY-MM-DD',
                style={'margin': '10px'}
            )
        ], style={'text-align': 'center', 'margin-top': '20px'}),

        html.Div([
            dcc.Graph(id='candlestick-graph'),
        ], style={'margin-top': '30px'}),

        html.Div([
            html.Button("Mostrar Gráfico de Martelo", id="martelo-btn", n_clicks=0),
            html.Button("Mostrar Gráfico de Barras", id="show-bar-chart", n_clicks=0),
            html.Button("Mostrar Gráfico de Linhas", id="show-line-chart", n_clicks=0)
        ], style={'text-align': 'center', 'margin-top': '20px'}),

        html.Div([
            dcc.Graph(id='additional-graph'),
        ], style={'margin-top': '30px'}),
    ])

    # Callback para atualizar o gráfico de candlestick com base no intervalo de datas selecionado
    @dash_app.callback(
        Output('candlestick-graph', 'figure'),
        [Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date')]
    )
    def update_candlestick_chart(start_date, end_date):
        return create_candlestick_chart(start_date, end_date)

    # Callback para alternar entre os gráficos de candlestick, martelo, barras e linhas
    @dash_app.callback(
        Output('additional-graph', 'figure'),
        [Input('show-bar-chart', 'n_clicks'),
         Input('show-line-chart', 'n_clicks'),
         Input('martelo-btn', 'n_clicks')]
    )
    def update_additional_graph(bar_clicks, line_clicks, martelo_clicks):
        # Verificar qual botão foi clicado
        ctx = dash.callback_context
        if not ctx.triggered:
            return create_line_chart()  # Valor inicial padrão

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Retornar o gráfico correspondente
        if button_id == 'show-bar-chart':
            return create_bar_chart()
        elif button_id == 'martelo-btn':
            return create_martelo_chart()
        elif button_id == 'show-line-chart':
            return create_line_chart()
        else:
            return create_line_chart()

    return dash_app
