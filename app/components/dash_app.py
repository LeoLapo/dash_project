import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import pandas as pd

def create_dash_app(flask_app):
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dashboard/',
        suppress_callback_exceptions=True
    )

    # Dados para gráficos
    data = pd.DataFrame({
        'open': [100, 105, 110, 108, 107, 106],
        'high': [110, 112, 115, 114, 113, 111],
        'low': [98, 103, 106, 105, 104, 103],
        'close': [104, 110, 108, 107, 106, 109],
        'volume': [1000, 1500, 2000, 1300, 1600, 1700]
    })

    # Dados para o DataFrame (tabela)
    table_data = pd.DataFrame({
        'ativo': ['PETR4', 'VALE3', 'ITUB4', 'ABEV3', 'BBDC4'],
        'data da compra': ['2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05'],
        'quantidade': [100, 50, 150, 200, 120],
        'preço da compra': [30.5, 75.8, 26.3, 17.5, 22.0],
        'preço de venda': [32.0, 78.0, 28.5, 18.0, 23.5]
    })

    # Função para criar gráficos
    def create_candlestick_chart():
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='Candlestick Chart'
        )])
        return fig

    def create_engolfo_alta_chart():
        fig = go.Figure(data=[
            go.Scatter(x=data.index, y=data['close'], mode='lines+markers', name='Engolfo Alta')
        ])
        return fig

    def create_doji_chart():
        fig = go.Figure(data=[
            go.Scatter(x=data.index, y=(data['open'] + data['close']) / 2, mode='lines+markers', name='Doji')
        ])
        return fig

    def create_martelo_chart():
        fig = go.Figure(data=[
            go.Bar(x=data.index, y=data['volume'], name='Martelo')
        ])
        return fig

    # Layout do Dash
    dash_app.layout = html.Div([
        html.H1("Dashboard de Análise de Padrões", style={'text-align': 'center'}),
        dcc.Graph(id='main-graph', figure=create_candlestick_chart()),
        html.Div([
            html.Div([
                html.Button("Candlestick", id='candlestick-btn', n_clicks=0, className='card'),
                html.Button("Engolfo de Alta", id='engolfo-btn', n_clicks=0, className='card'),
                html.Button("Doji", id='doji-btn', n_clicks=0, className='card'),
                html.Button("Martelo", id='martelo-btn', n_clicks=0, className='card'),
            ], style={'display': 'flex', 'gap': '20px', 'justify-content': 'center'}),
        ], style={'margin-top': '20px'}),
        html.Div([
            dash_table.DataTable(
                id='table',
                columns=[{"name": col, "id": col} for col in table_data.columns],
                data=table_data.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'center',
                    'padding': '10px',
                    'fontFamily': 'Arial',
                },
                style_header={
                    'backgroundColor': 'lightgrey',
                    'fontWeight': 'bold'
                },
                style_data={
                    'backgroundColor': 'white',
                    'color': 'black'
                }
            )
        ], style={'margin-top': '30px'})
    ])

    # Callbacks para trocar o gráfico principal
    @dash_app.callback(
        Output('main-graph', 'figure'),
        [Input('candlestick-btn', 'n_clicks'),
         Input('engolfo-btn', 'n_clicks'),
         Input('doji-btn', 'n_clicks'),
         Input('martelo-btn', 'n_clicks')]
    )
    def update_graph(candlestick_clicks, engolfo_clicks, doji_clicks, martelo_clicks):
        # Determinar qual botão foi clicado
        ctx = dash.callback_context
        if not ctx.triggered:
            return create_candlestick_chart()
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Retornar o gráfico correspondente
        if button_id == 'engolfo-btn':
            return create_engolfo_alta_chart()
        elif button_id == 'doji-btn':
            return create_doji_chart()
        elif button_id == 'martelo-btn':
            return create_martelo_chart()
        else:
            return create_candlestick_chart()

    return dash_app