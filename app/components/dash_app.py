import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import dash_table
from datetime import datetime, timedelta

# Função para gerar dados financeiros simulados
def generate_fake_stock_data(ticker, start_date, end_date):
    # Gerar uma lista de datas
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # 'B' é para dias úteis

    # Gerar preços fictícios (de forma simples, com base em um preço inicial)
    np.random.seed(42)  # Para consistência nos valores aleatórios
    open_prices = np.random.uniform(low=100, high=200, size=len(dates))  # Preços de abertura
    close_prices = open_prices + np.random.uniform(low=-5, high=5, size=len(dates))  # Preços de fechamento (variação simples)
    high_prices = np.maximum(open_prices, close_prices) + np.random.uniform(low=0, high=5, size=len(dates))  # Preços máximos
    low_prices = np.minimum(open_prices, close_prices) - np.random.uniform(low=0, high=5, size=len(dates))  # Preços mínimos
    volumes = np.random.randint(100000, 1000000, size=len(dates))  # Volume de negociações

    # Criar o DataFrame
    stock_data = pd.DataFrame({
        'Date': dates,
        'Open': open_prices,
        'Close': close_prices,
        'High': high_prices,
        'Low': low_prices,
        'Volume': volumes
    })
    
    # Calcular a variação percentual entre abertura e fechamento
    stock_data['change_percentage'] = ((stock_data['Close'] - stock_data['Open']) / stock_data['Open']) * 100
    stock_data.set_index('Date', inplace=True)
    
    # Limitar casas decimais a 2
    stock_data = stock_data.round({'Open': 2, 'Close': 2, 'High': 2, 'Low': 2, 'Volume': 0, 'change_percentage': 2})
    
    return stock_data

# Função para criar o gráfico candlestick com linha de preço (fechamento)
def create_candlestick_chart(filtered_data):
    fig = go.Figure()

    # Adicionar o gráfico Candlestick
    fig.add_trace(
        go.Candlestick(
            x=filtered_data.index,
            open=filtered_data['Open'],
            high=filtered_data['High'],
            low=filtered_data['Low'],
            close=filtered_data['Close'],
            name='Candlestick Chart'
        )
    )

    # Linha de preço de fechamento
    fig.add_trace(
        go.Scatter(
            x=filtered_data.index,
            y=filtered_data['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        title="Candlestick Chart with Close Price Line",
        hovermode="x unified"
    )

    return fig

# Função para criar o gráfico de barras com linha de preço (fechamento)
def create_bar_chart(filtered_data):
    fig = go.Figure()

    # Adicionar o gráfico de barras
    fig.add_trace(
        go.Bar(
            x=filtered_data.index,
            y=filtered_data['Volume'],
            name='Volume',
            marker_color='blue'
        )
    )

    # Linha de preço de fechamento
    fig.add_trace(
        go.Scatter(
            x=filtered_data.index,
            y=filtered_data['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='red', width=2)
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Volume",
        title="Volume Bar Chart with Close Price Line",
        hovermode="x unified"
    )

    return fig

# Função para criar o gráfico de martelo com linha de preço (fechamento)
def create_hammer_chart(filtered_data):
    fig = go.Figure()

    hammer_signal = filtered_data[(filtered_data['Close'] - filtered_data['Low']) > 
                                  (filtered_data['High'] - filtered_data['Close'])]

    fig.add_trace(
        go.Scatter(
            x=hammer_signal.index,
            y=hammer_signal['Close'],
            mode='markers',
            marker=dict(size=10, color='red'),
            name='Hammer Signal'
        )
    )

    # Linha de preço de fechamento
    fig.add_trace(
        go.Scatter(
            x=filtered_data.index,
            y=filtered_data['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='green', width=2)
        )
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        title="Hammer Chart with Close Price Line",
        hovermode="x unified"
    )

    return fig

# Função para configurar o layout e os callbacks do Dash
def create_dash_app(flask_app):
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dashboard/',
        suppress_callback_exceptions=True,
        assets_url_path='/dashboard/assets'
    )

    dash_app.layout = html.Div([
        html.H1("Stock Data Dashboard"),
        
        # Seleção de Ativo
        html.Label("Choose a Stock:"),
        dcc.Dropdown(
            id='stock-dropdown',
            options=[
                {'label': 'Apple (AAPL)', 'value': 'AAPL'},
                {'label': 'Google (GOOGL)', 'value': 'GOOGL'},
                {'label': 'Amazon (AMZN)', 'value': 'AMZN'},
                {'label': 'Microsoft (MSFT)', 'value': 'MSFT'}
            ],
            value='AAPL',  # Valor inicial
            style={'width': '50%'}
        ),

        # Seleção de Período
        html.Label("Choose Date Range:"),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date='2025-01-01',
            end_date='2025-01-30',
            display_format='YYYY-MM-DD',
            style={'width': '50%'}
        ),

        # Botões para selecionar o gráfico
        html.Div([
            html.Button('Candlestick Chart', id='candlestick-button', n_clicks=0),
            html.Button('Bar Chart', id='bar-chart-button', n_clicks=0),
            html.Button('Hammer Chart', id='hammer-chart-button', n_clicks=0)
        ], style={'margin-top': '20px'}),

        # Layout para a Tabela de Dados e Gráficos
        html.Div([
            # Tabela de Dados
            html.Div([
                dash_table.DataTable(
                    id='data-table',
                    style_table={'height': '400px', 'overflowY': 'auto'},
                    style_cell={'textAlign': 'center'},
                    style_data={'whiteSpace': 'normal', 'height': 'auto'},
                )
            ], style={'width': '50%', 'display': 'inline-block'}),

            # Gráfico Principal
            html.Div([
                dcc.Graph(id='main-graph')
            ], style={'width': '50%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justify-content': 'space-between'})
    ])

    @dash_app.callback(
        [Output('data-table', 'data'),
         Output('main-graph', 'figure')],
        [Input('stock-dropdown', 'value'),
         Input('date-picker-range', 'start_date'),
         Input('date-picker-range', 'end_date'),
         Input('candlestick-button', 'n_clicks'),
         Input('bar-chart-button', 'n_clicks'),
         Input('hammer-chart-button', 'n_clicks')]
    )
    def update_output(ticker, start_date, end_date, candlestick_clicks, bar_chart_clicks, hammer_chart_clicks):
        # Obter os dados financeiros do ativo escolhido (simulados)
        filtered_data = generate_fake_stock_data(ticker, start_date, end_date)

        # Preencher a tabela com os dados filtrados
        table_data = filtered_data.reset_index().to_dict('records')

        # Formatar os valores da tabela para mostrar apenas 2 casas decimais e porcentagem quando necessário
        for row in table_data:
            row['Open'] = f"{row['Open']:.2f}"
            row['Close'] = f"{row['Close']:.2f}"
            row['High'] = f"{row['High']:.2f}"
            row['Low'] = f"{row['Low']:.2f}"
            row['Volume'] = f"{int(row['Volume']):,}"  # Formatar volume com separadores de milhar
            row['change_percentage'] = f"{row['change_percentage']:.2f}%"  # Formatar como porcentagem

        # Verificar qual gráfico foi escolhido com base no número de cliques
        if candlestick_clicks > bar_chart_clicks and candlestick_clicks > hammer_chart_clicks:
            return table_data, create_candlestick_chart(filtered_data)
        elif bar_chart_clicks > hammer_chart_clicks:
            return table_data, create_bar_chart(filtered_data)
        else:
            return table_data, create_hammer_chart(filtered_data)

    return dash_app
