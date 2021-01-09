import pandas as pd
from sheetfu import SpreadsheetApp
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
#
# path_to_credential = './google_credentials.json'
# #sa = SpreadsheetApp(from_env=True)
# #google sheets auth & pulling data from the spreadsheet
# table_name = 'Invoicing Statistics 2020'
# spr_id = '1gRd73DKLWuVGOUoOu9sv7iiym_JyDovVjOu7bT1aZO8'
# spreadsheet = SpreadsheetApp(path_to_credential).open_by_id(spr_id)
# needed_sheets = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
#                  'November', 'December']
# month_sheets = [
#     sheet for sheet in spreadsheet.sheets
#     if sheet.name in needed_sheets
# ]
# data = []
# for month_sheet in month_sheets:
#     data_range = month_sheet.get_data_range()
#     values = data_range.get_values()
#     for row in values:
#         data.append(row)
# headers = data.pop(1)
#
# # Create df
# df = pd.DataFrame(data, columns=headers)
# #cleaning data
# df = df.drop(columns=['Comments', '', '',
#                       'What stats?', 'Value', '', '', '', '', '', ''])
# df = df.drop(0)
# nan_value = float("NaN")
# df = df.replace("", nan_value)
# df.dropna(subset=["Project Name"], inplace=True)
# df = df[~df["Client"].str.contains('Client')]
#
# #changing data types
# df['Date confirmed'] = df['Date confirmed'].astype(float)
# df['Date confirmed'] = pd.to_datetime(df['Date confirmed'], unit='d', origin='1899-12-30')
# df['Hours sold'] = df['Hours sold'].astype(float)
# df['Total time spent'] = df['Total time spent'].astype(str).str.replace(',', '.', regex=False)
# df['Total time spent'] = df['Total time spent'].astype(float)
# df['Rate'] = df['Rate'].astype(str).str.replace(',', '.', regex=False)
# df['Rate'] = df['Rate'].astype(str).str.replace('$', '', regex=False)
# df['Rate'] = df['Rate'].astype(float).round(2)
# df['Total price'] = df['Total price'].astype(float)
# df['Cost, h'] = df['Cost, h'].astype(float).round(2)
# df['Cost, total'] = df['Cost, total'].astype(float).round(2)
# df['Proft, $'] = df['Proft, $'].astype(float).round(2)
# df['Profit, %'] = df['Profit, %'].astype(float).round(2) * 100
# df['AM'] = df['AM'].astype(str).str.replace('IT', 'IV', regex=False)

revenue = pd.read_csv('./revenue.csv')
revenue = revenue.replace({'IT':'IV'})
total_revenue = '{0:,}'.format(int(round(revenue['Total price'].sum(),0)))

#Clients stats and visualisation
clients_by_revenue = revenue.groupby('Client',as_index=False) \
    .agg({'Total price':'sum'}) \
    .sort_values(by='Total price',ascending=False)
clients_by_revenue['Total price'] = clients_by_revenue['Total price'].astype(int)
top_10_clients = clients_by_revenue.head(10)
fig_clients = px.bar(
                    x=top_10_clients['Client'],
                    y=top_10_clients['Total price'],
                    labels={'x':'Client', 'y':'Revenue'},
                    color_discrete_sequence=["#a51140", "#a51140"])

clients_by_type = revenue.groupby(['Client','Type'],as_index=False) \
    .agg({'Total price':'sum'})
clients_by_type = clients_by_type.replace({'T&M':'Project','FP':'Project'}) \
                                .groupby(['Client','Type'],as_index=False) \
                                .agg({'Total price':'sum'}) \
                                .sort_values(by='Total price',ascending=False)

#reading csv files with team data
pu_data_2019 = pd.read_csv('~/pu_data_2019.csv')
pu_data_2020 = pd.read_csv('~/pu_data_2020.csv')
pu_data_2020['revenue_per_person'] = pu_data_2020.turnover / pu_data_2020.dev_team
pu_data_2019['revenue_per_person'] = pu_data_2019.turnover / pu_data_2019.dev_team
pu_data_2020['avg_h_cost'] = pu_data_2020.total_hours / pu_data_2020.total_costs_total_oh

#key metrics for report
revenue_2020 = round(pu_data_2020.turnover.sum())
revenue_2019 = round(pu_data_2019.turnover.sum())

net_profit_2019 = round(pu_data_2019.net_profit.sum())
net_profit_2020 = round(pu_data_2020.net_profit.sum())

expenses_2020 = round(pu_data_2020.total_costs_total_oh.sum())
expenses_2019 = round(pu_data_2019.total_costs_total_oh.sum())

net_profit_2020_perc = round(net_profit_2020 / expenses_2020,2)
net_profit_2019_perc = round((net_profit_2019 / expenses_2019) * 100,2)

team_size_2020 = 57
team_size_2019 = 44
team_growth_2020 = round((team_size_2020 - team_size_2019)/team_size_2019 * 100)

revenue_growth_2020 = round((revenue_2020-revenue_2019)/revenue_2019 * 100)
revenue_per_dev_2020 = round(pu_data_2020.revenue_per_person.median())
revenue_per_dev_2019 = round(pu_data_2019.revenue_per_person.median())

median_h_cost_2020 = round(pu_data_2020['avg_h_cost'].median(),2)
median_h_rate_2020 = round(revenue['Total price'].sum() / revenue['Hours sold'].sum(),2)

total_unbilled_h_2020 = round(pu_data_2020.total_hours.sum()-revenue['Hours sold'].sum())
unbilled_h_median_2020 = pu_data_2020.unbilled_hours.median()
unbilled_h_max_2020 = pu_data_2020.unbilled_hours.max()
unbilled_h_min_2020 = pu_data_2020.unbilled_hours.min()
efficiency_hours_2020 = round(pu_data_2020.billed_hours.sum() / pu_data_2020.total_hours.sum() * 100)

client_number_2020 = revenue['Client'].nunique()

#plotly dash app
#external_stylesheets = ['https://codepen.io/lisa-nalyvaiko/pen/GRjdwrL.css']
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
indicators_list = ['Client', 'Main Developer', 'Location', 'Seniority', 'Type', 'AM', 'Sales person']
clients_types = ['Total','Project','Retainer']

app.layout = html.Div(children=[
    html.H1(children='PU Revenue 2020'),

    dcc.Markdown(
        '''
        #### Interactive visualisation of PU revenue in 2020.
        '''),

    dcc.Markdown(f'''
        Our total revenue in 2020 - **${total_revenue}**
    '''),

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
    )
])


@app.callback(
    Output('revenue_graph', 'figure'),
    Input('xaxis-column', 'value'))
def update_revenue_graph(xaxis_column_name):
    print(xaxis_column_name)
    grouped_df = revenue.groupby(xaxis_column_name, as_index=False).agg({'Total price': 'sum'})
    figure = px.bar(
        grouped_df,
        x=grouped_df.iloc[:, 0],
        y=grouped_df['Total price'],
        labels={'x': 'indicator', 'y': 'revenue, $'},
        color_discrete_sequence=["#a51140", "#a51140"])
    return figure

@app.callback(
    Output('top-clients_graph', 'figure'),
    Input('client-type', 'value'))
def update_revenue_by_clients_graph(client_type):
    data = clients_by_type
    if client_type == "Total":
        return fig_clients
    d = data[data["Type"]==client_type].groupby('Client',as_index=False)\
                                        .agg({'Total price':'sum'})\
                                        .sort_values(by='Total price',ascending=False)\
                                        .head(10)
    figure = px.bar(
            d,
            x=d['Client'],
            y=d['Total price'],
            labels={'x': 'Client', 'y': 'Revenue'},
            color_discrete_sequence=["#a51140", "#a51140"])
    return figure



if __name__ == '__main__':
    app.run_server(debug=True)
