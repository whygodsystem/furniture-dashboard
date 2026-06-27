import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import base64
import io

app = dash.Dash(__name__)
app.title = "Финансовый дашборд мебельной компании"
df = None

app.layout = html.Div([
    html.H1("📊 Финансовый дашборд мебельной компании", style={'textAlign': 'center', 'color': '#2c3e50'}),
    html.Hr(),
    
    # Блок загрузки файла
    html.Div([
        html.H3("Загрузите CSV-файл с данными"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Перетащите файл сюда или ',
                html.A('выберите файл', style={'color': '#3498db', 'cursor': 'pointer'})
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px 0',
                'borderColor': '#3498db'
            },
            multiple=False
        ),
        html.Div(id='upload-status', style={'color': 'green', 'margin': '10px 0'})
    ]),
    
    # Фильтры
    html.Div([
        html.Div([
            html.Label("Период анализа:"),
            dcc.Dropdown(
                id='period-dropdown',
                options=[
                    {'label': 'Месяц', 'value': 'M'},
                    {'label': 'Квартал', 'value': 'Q'},
                    {'label': 'Год', 'value': 'Y'}
                ],
                value='M',
                style={'width': '200px'}
            )
        ], style={'display': 'inline-block', 'marginRight': '30px'}),
        
        html.Div([
            html.Label("Категория:"),
            dcc.Dropdown(
                id='category-dropdown',
                options=[],
                value=[],
                multi=True,
                style={'width': '300px'}
            )
        ], style={'display': 'inline-block'})
    ], style={'padding': '10px 0'}),
    
    # KPI-карточки
    html.Div([
        html.Div(id='kpi-revenue', style={'display': 'inline-block', 'width': '23%', 'padding': '15px', 
                                          'borderRadius': '10px', 'backgroundColor': '#f8f9fa', 
                                          'textAlign': 'center', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)'}),
        html.Div(id='kpi-cost', style={'display': 'inline-block', 'width': '23%', 'padding': '15px', 
                                       'borderRadius': '10px', 'backgroundColor': '#f8f9fa', 
                                       'textAlign': 'center', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)'}),
        html.Div(id='kpi-profit', style={'display': 'inline-block', 'width': '23%', 'padding': '15px', 
                                         'borderRadius': '10px', 'backgroundColor': '#f8f9fa', 
                                         'textAlign': 'center', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)'}),
        html.Div(id='kpi-orders', style={'display': 'inline-block', 'width': '23%', 'padding': '15px', 
                                         'borderRadius': '10px', 'backgroundColor': '#f8f9fa', 
                                         'textAlign': 'center', 'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)'})
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'flexWrap': 'wrap'}),
    
    # Графики
    html.Div([
        html.Div([dcc.Graph(id='line-chart')], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='pie-chart')], style={'width': '48%', 'display': 'inline-block'})
    ]),
    html.Div([
        html.Div([dcc.Graph(id='histogram')], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([dcc.Graph(id='scatter-chart')], style={'width': '48%', 'display': 'inline-block'})
    ]),
    
    # Таблица
    html.Div([
        html.H3("Детальные данные по заказам"),
        dash_table.DataTable(
            id='data-table',
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'backgroundColor': '#3498db', 'color': 'white', 'fontWeight': 'bold'}
        )
    ], style={'marginTop': '20px'})
])

# Callback загрузки файла
@app.callback(
    [Output('upload-status', 'children'),
     Output('category-dropdown', 'options'),
     Output('category-dropdown', 'value')],
    Input('upload-data', 'contents')
)
def upload_file(contents):
    global df
    if contents is None:
        return "Файл не загружен. Пожалуйста, загрузите CSV-файл.", [], []
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        df['date'] = pd.to_datetime(df['date'])
        categories = [{'label': cat, 'value': cat} for cat in df['category'].unique()]
        return f"✅ Файл успешно загружен! Записей: {len(df)}", categories, []
    except Exception as e:
        return f"❌ Ошибка загрузки: {str(e)}", [], []

# Основной callback для обновления всех графиков
@app.callback(
    [Output('kpi-revenue', 'children'),
     Output('kpi-cost', 'children'),
     Output('kpi-profit', 'children'),
     Output('kpi-orders', 'children'),
     Output('line-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('histogram', 'figure'),
     Output('scatter-chart', 'figure'),
     Output('data-table', 'data'),
     Output('data-table', 'columns')],
    [Input('period-dropdown', 'value'),
     Input('category-dropdown', 'value')]
)
def update_dashboard(period, selected_categories):
    global df
    if df is None:
        empty_fig = px.scatter(title="Загрузите данные для отображения")
        return ("💰 Выручка: —", "📉 Расходы: —", "📈 Прибыль: —", "📦 Заказы: —",
                empty_fig, empty_fig, empty_fig, empty_fig, [], [])
    
    filtered_df = df.copy()
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
    
    filtered_df['period'] = filtered_df['date'].dt.to_period(period).astype(str)
    agg_df = filtered_df.groupby('period').agg({
        'revenue': 'sum',
        'cost': 'sum',
        'profit': 'sum',
        'orders_count': 'sum'
    }).reset_index()
    
    total_revenue = agg_df['revenue'].sum()
    total_cost = agg_df['cost'].sum()
    total_profit = agg_df['profit'].sum()
    total_orders = agg_df['orders_count'].sum()
    
    kpi_revenue = f"💰 Выручка\n{total_revenue:,.0f} руб."
    kpi_cost = f"📉 Расходы\n{total_cost:,.0f} руб."
    kpi_profit = f"📈 Прибыль\n{total_profit:,.0f} руб."
    kpi_orders = f"📦 Заказы\n{total_orders:,.0f}"
    
    line_fig = px.line(agg_df, x='period', y=['revenue', 'cost', 'profit'],
                       title='Динамика доходов, расходов и прибыли',
                       labels={'value': 'Рубли', 'variable': 'Показатель'},
                       color_discrete_map={'revenue': '#2ecc71', 'cost': '#e74c3c', 'profit': '#3498db'})
    
    cat_cost = filtered_df.groupby('category')['cost'].sum().reset_index()
    pie_fig = px.pie(cat_cost, values='cost', names='category',
                     title='Структура расходов по категориям')
    
    hist_fig = px.histogram(filtered_df, x='profit', nbins=30,
                            title='Распределение прибыли по заказам',
                            labels={'profit': 'Прибыль (руб.)', 'count': 'Количество заказов'})
    
    # Убираем trendline, чтобы не требовать statsmodels
    scatter_fig = px.scatter(filtered_df, x='revenue', y='profit', color='category',
                             title='Корреляция между выручкой и прибылью',
                             labels={'revenue': 'Выручка (руб.)', 'profit': 'Прибыль (руб.)'})
    
    table_data = filtered_df[['date', 'category', 'revenue', 'cost', 'profit', 'orders_count']].to_dict('records')
    table_columns = [{'name': col, 'id': col} for col in ['date', 'category', 'revenue', 'cost', 'profit', 'orders_count']]
    
    return (kpi_revenue, kpi_cost, kpi_profit, kpi_orders,
            line_fig, pie_fig, hist_fig, scatter_fig,
            table_data, table_columns)

if __name__ == '__main__':
    app.run(debug=True, port=8050)