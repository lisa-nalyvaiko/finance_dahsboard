import pandas as pd
import os
import dash
import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import dash_table

# reading csv with invoices data
revenue = pd.read_csv('./revenue.csv')
revenue = revenue.replace({'IT': 'IV', 'Aleksander Martynenko': 'Oleksandr Martynenko', 'Oleg Kozyk': 'Oleh Kozyk'})

# Clients stats and visualisation
clients_by_revenue = revenue.groupby('Client', as_index=False) \
    .agg({'Total price': 'sum'}) \
    .sort_values(by='Total price', ascending=False)
clients_by_revenue['Total price'] = clients_by_revenue['Total price'].astype(int)
top_10_clients = clients_by_revenue.head(10)
fig_clients = px.bar(
    x=top_10_clients['Client'],
    y=top_10_clients['Total price'],
    labels={'x': 'Client', 'y': 'Revenue'},
    color_discrete_sequence=["#a51140", "#a51140"])

clients_by_type = revenue.groupby(['Client', 'Type'], as_index=False) \
    .agg({'Total price': 'sum'})
clients_by_type = clients_by_type.replace({'T&M': 'Project', 'FP': 'Project'}) \
    .groupby(['Client', 'Type'], as_index=False) \
    .agg({'Total price': 'sum'}) \
    .sort_values(by='Total price', ascending=False)

# reading csv files with team data
pu_data_2019 = pd.read_csv('./pu_data_2019.csv')
pu_data_2020 = pd.read_csv('./pu_data_2020.csv')
pu_data_2020['revenue_per_person'] = pu_data_2020.turnover / pu_data_2020.dev_team
pu_data_2019['revenue_per_person'] = pu_data_2019.turnover / pu_data_2019.dev_team
pu_data_2020['avg_h_cost'] = pu_data_2020.total_hours / pu_data_2020.total_costs_total_oh

# key metrics for report
revenue_2020 = int(round(pu_data_2020.turnover.sum()))
revenue_2019 = int(round(pu_data_2019.turnover.sum()))
total_revenue_2019 = '{0:,}'.format(revenue_2019)
total_revenue_2020 = '{0:,}'.format(revenue_2020)
revenue_growth_perc = int(round((revenue_2020 - revenue_2019) / revenue_2019 * 100))

expenses_2020 = int(round(pu_data_2020.total_costs_total_oh.sum()))
expenses_2019 = int(round(pu_data_2019.total_costs_total_oh.sum()))
total_expenses = '{0:,}'.format(expenses_2020)
expenses_dif = abs(expenses_2020 - expenses_2019)
expenses_dif_perc = round(expenses_dif / expenses_2019 * 100, 2)
total_expenses_2019 = '{0:,}'.format(expenses_2019)

net_profit_2019 = int(round(pu_data_2019.net_profit.sum()))
net_profit_2020 = int(revenue_2020 - expenses_2020)
#net_profit_2020 = int((pu_data_2020.net_profit.sum()))
net_profit_growth = int(net_profit_2020 - net_profit_2019)
net_profit_growth_perc = round(net_profit_growth / net_profit_2019 * 100)
formatted_profit_2019 = '{0:,}'.format(net_profit_2019)
formatted_profit_2020 = '{0:,}'.format(net_profit_2020)

net_profit_2020_perc = round((net_profit_2020 / expenses_2020) * 100, 2)
net_profit_2019_perc = round((net_profit_2019 / expenses_2019) * 100, 2)

team_size_2020 = 57
team_size_2019 = 44
team_growth_2020 = round((team_size_2020 - team_size_2019) / team_size_2019 * 100)

revenue_growth_2020 = round((revenue_2020 - revenue_2019) / revenue_2019 * 100)
revenue_per_dev_2020 = round(pu_data_2020.revenue_per_person.median())
revenue_per_dev_2019 = round(pu_data_2019.revenue_per_person.median())

median_h_cost_2020 = round(pu_data_2020['avg_h_cost'].median(), 2)
median_h_rate_2020 = round(revenue['Total price'].sum() / revenue['Hours sold'].sum(), 2)

total_unbilled_h_2020 = round(pu_data_2020.total_hours.sum() - revenue['Hours sold'].sum())
unbilled_h_median_2020 = pu_data_2020.unbilled_hours.median()
unbilled_h_max_2020 = pu_data_2020.unbilled_hours.max()
unbilled_h_min_2020 = pu_data_2020.unbilled_hours.min()
efficiency_hours_2020 = round(pu_data_2020.billed_hours.sum() / pu_data_2020.total_hours.sum() * 100)
efficiency_revenue_2020 = round((revenue_2020 / pu_data_2020.total_invoiceable.sum()) * 100)

client_number_2020 = revenue['Client'].nunique()

# graph for time efficiency data
time_efficiency_fig = go.Figure(go.Indicator(
    domain={'x': [0, 1], 'y': [0, 1]},
    value=efficiency_hours_2020,
    mode="gauge+number",
    title={'text': "Time efficiency, %<br>Total time billed to total time spent"},
    gauge={'axis': {'range': [None, 100]},
           'bar': {'color': "#a51140"},
           'steps': [
               {'range': [0, 25], 'color': "#c2acbf"},
               {'range': [25, 50], 'color': "#f5cdd9"},
               {'range': [50, 75], 'color': "#e3aabc"},
               {'range': [75, 100], 'color': "#f587a7"}],
           }))
# graph for turnover efficiency data
revenue_efficiency_graph = go.Figure(go.Indicator(
    domain={'x': [0, 1], 'y': [0, 1]},
    value=efficiency_revenue_2020,
    mode="gauge+number",
    title={'text': "Revenue efficiency, %<br>Revenue generated to potential revenue"},
    gauge={'axis': {'range': [None, 100]},
           'bar': {'color': "#a51140"},
           'steps': [
               {'range': [0, 25], 'color': "#c2acbf"},
               {'range': [25, 50], 'color': "#f5cdd9"},
               {'range': [50, 75], 'color': "#e3aabc"},
               {'range': [75, 100], 'color': "#f587a7"}],
           }))

# reading csv with developers data
dev_stats = pd.read_csv('./dev_stats_2020.csv')

# df for detailed data table
pu_2020_for_report = pu_data_2020[['month', 'turnover', 'total_costs_total_oh', 'net_profit', 'net_profit_perc']]
pu_2020_for_report.rename(columns={
    'month': 'Month',
    'turnover': 'Turnover, $',
    'total_costs_total_oh': 'Total Costs',
    'net_profit': 'Net Profit, $',
    'net_profit_perc': 'Net Profit, %',
}, inplace=True)

# plotly dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

LOGIN = os.getenv('BASIC_LOGIN') if os.getenv('BASIC_LOGIN') else 'report'
PASSWORD = os.environ.get('BASIC_PASSWORD') if os.environ.get('BASIC_PASSWORD') else 'report123'
VALID_USERNAME_PASSWORD_PAIRS = {
    LOGIN: PASSWORD
}
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
server = app.server
indicators_list = ['Client', 'Main Developer', 'Location', 'Seniority', 'Type', 'AM', 'Sales person']
clients_types = ['Total', 'Project', 'Retainer']
dev_stats_criteria = ['Developer', 'Location', 'Seniority']
dev_stats_units = ['Hours', 'Dollars']

# Dash app
app.layout = html.Div(
    className="container-xl",
    children=[
        html.H1(
            className='title',
            children='PU Results 2020'),

        dcc.Markdown(
            '''
            ### Interactive visual report of PU results in 2020.
            '''),

        dcc.Markdown('''
        There will be some general summary text later and there will be a couple of sentences of it.
        There will be some general summary text later and there will be a couple of sentences of it.
        There will be some general summary text later and there will be a couple of sentences of it.
    '''),

        dcc.Markdown(f'''
        Our total revenue in 2020 - **${total_revenue_2020}**
    '''),
        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col col-lg-3 text-center kpi-block",
                    children=[
                        html.H3("Revenue"),
                        html.H2(
                            className="fw-bold",
                            children=[
                                f'''${total_revenue_2020}''']),
                        f'${total_revenue_2019} in 2019 (+{revenue_growth_perc}%)'
                    ]
                ),

                html.Div(
                    className="col col-lg-3 text-center kpi-block",
                    children=[
                        html.H3("Net profit, $"),
                        html.H2(f'''
                ${formatted_profit_2020}'''),
                        f'${formatted_profit_2019} in 2019'
                    ]
                ),

                html.Div(
                    className="col col-lg-3 text-center kpi-block",
                    children=[
                        html.H3("Expenses, $"),
                        html.H2(f'''
                ${total_expenses}'''),
                        f'${total_expenses_2019} in 2019 (+{expenses_dif_perc}%) '
                    ]
                ),

                html.Div(
                    className="col col-lg-3 text-center kpi-block",
                    children=[
                        html.H3("Profit, %"),
                        html.H2(f'''
              +{net_profit_2020_perc}%'''),
                        f'{net_profit_2019_perc}% in 2019'
                    ]
                )
            ]
        ),

        html.Div(
            className="row",
            children=[
                html.Div(
                    className="col col-lg-6 text-center",
                    children=[
                        dcc.Graph(
                            id='time_efficiency_graph',
                            figure=time_efficiency_fig
                        )
                    ]
                )
                ,

                html.Div(
                    className="col col-lg-6 text-center",
                    children=[
                        dcc.Graph(
                            figure=revenue_efficiency_graph
                        ),
                    ]
                )
            ]
        ),

        html.Div(
            html.H3("Developers data on time and revenue efficiency")
        ),

        html.Div([
            dcc.Dropdown(
                id='dev_criterium',
                options=[{'label': i, 'value': i} for i in dev_stats_criteria],
                value=dev_stats_criteria[1]
            ),

            dcc.Dropdown(
                id='dev_units',
                options=[{'label': i, 'value': i} for i in dev_stats_units],
                value=dev_stats_units[1]
            ),

            dcc.Graph(
                id='dev_stats_graph'
            )
        ]),

        html.Div(
            html.H3("Revenue detailed")
        ),

        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in indicators_list],
                value=indicators_list[3]
            )]),

        dcc.Graph(
            id='revenue_graph'
        ),

        html.H3(children='Top 10 clients by revenue'),

        html.Div([
            dcc.Dropdown(
                id='client-type',
                options=[{'label': i, 'value': i} for i in clients_types],
                value=clients_types[0]
            )]),

        dcc.Graph(
            id='top-clients_graph'
        ),

        html.Div(
            html.H3("Monthly P&L data for the reference"),
        ),

        html.Div(
            className="style_cell",
            children=[
                dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in pu_2020_for_report.columns],
                    data=pu_2020_for_report.to_dict('records'),
                    style_data_conditional=[
                        {
                            'if': {
                                'filter_query': '{Net Profit, $} < 0',
                                'column_id': 'Net Profit, $'
                            },
                            'backgroundColor': '#f2b6be'
                        },
                        {
                            'if': {
                                'filter_query': '{Net Profit, $} > 0',
                                'column_id': 'Net Profit, $'
                            },
                            'backgroundColor': '#b4e0c8'
                        },

                        {
                            'if': {
                                'filter_query': '{Net Profit, %} < 0',
                                'column_id': 'Net Profit, %'
                            },
                            'backgroundColor': '#f2b6be'
                        },
                        {
                            'if': {
                                'filter_query': '{Net Profit, %} > 0',
                                'column_id': 'Net Profit, %'
                            },
                            'backgroundColor': '#b4e0c8'
                        }]
                )
            ]
        )
    ]
)

# callback function for revenue detailed graph update
@app.callback(
Output('revenue_graph', 'figure'),
Input('xaxis-column', 'value'))
def update_revenue_graph(xaxis_column_name):
    grouped_df = revenue.groupby(xaxis_column_name, as_index=False).agg({'Total price': 'sum'})
    figure = px.bar(
        grouped_df,
        x=grouped_df.iloc[:, 0],
        y=grouped_df['Total price'],
        labels={'x': 'indicator', 'y': 'revenue, $'},
        color_discrete_sequence=["#a51140", "#a51140"])
    return figure


# callback function for top-clients graph update
@app.callback(
    Output('top-clients_graph', 'figure'),
    Input('client-type', 'value'))
def update_revenue_by_clients_graph(client_type):
    data = clients_by_type
    if client_type == "Total":
        return fig_clients
    d = data[data["Type"] == client_type].groupby('Client', as_index=False) \
        .agg({'Total price': 'sum'}) \
        .sort_values(by='Total price', ascending=False) \
        .head(10)
    figure = px.bar(
        d,
        x=d['Client'],
        y=d['Total price'],
        labels={'x': 'Client', 'y': 'Revenue'},
        color_discrete_sequence=["#a51140", "#a51140"])
    return figure


# callback function for "developers data detailed" graph
@app.callback(
    Output('dev_stats_graph', 'figure'),
    Input('dev_criterium', 'value'),
    Input('dev_units', 'value'))
def update_dev_stats_graph(dev_criterium, dev_units):
    d = dev_stats
    if dev_units == "Hours":
        df = d.groupby(dev_criterium, as_index=False).agg({'Unbilled': 'sum'})
        df1 = d.groupby(dev_criterium, as_index=False).agg({'Billed hours': 'sum'})
        figure = go.Figure(data=[
            go.Bar(name="Unbilled hours", x=df[dev_criterium], y=df['Unbilled'], marker_color='#c2acbf'),
            go.Bar(name='Billed hours', x=df[dev_criterium], y=df1['Billed hours'], marker_color='#a51140')
        ], )
        figure.update_layout(barmode='group')
        return figure
    df = d.groupby(dev_criterium, as_index=False).agg({'Cost': 'sum'})
    df1 = d.groupby(dev_criterium, as_index=False).agg({'Revenue': 'sum'})
    figure = go.Figure(data=[
        go.Bar(name="Developers cost", x=df[dev_criterium], y=df['Cost'], marker_color='#c2acbf'),
        go.Bar(name='Revenue generated by developer', x=df1[dev_criterium], y=df1['Revenue'], marker_color='#a51140')
    ])
    figure.update_layout(barmode='group')
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
