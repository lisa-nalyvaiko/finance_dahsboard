import pandas as pd
from sheetfu import SpreadsheetApp
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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

df = pd.read_csv('./revenue.csv')
df = df.replace({'IT':'IV'})
total_revenue = '{0:,}'.format(int(round(df['Total price'].sum(),0)))

#Clients stats and visualisation
clients_by_revenue = df.groupby('Client',as_index=False) \
    .agg({'Total price':'sum'}) \
    .sort_values(by='Total price',ascending=False)
clients_by_revenue['Total price'] = clients_by_revenue['Total price'].astype(int)
top_10_clients = clients_by_revenue.head(10)
fig_clients = px.bar(
                    x=top_10_clients['Client'],
                    y=top_10_clients['Total price'],
                    labels={'x':'Client', 'y':'Revenue'},
                    color_discrete_sequence=["#a51140", "#a51140"])

clients_by_type = df.groupby(['Client','Type'],as_index=False) \
    .agg({'Total price':'sum'})
clients_by_type = clients_by_type.replace({'T&M':'Project','FP':'Project'}) \
                                .groupby(['Client','Type'],as_index=False) \
                                .agg({'Total price':'sum'}) \
                                .sort_values(by='Total price',ascending=False)

#plotly dash app
#external_stylesheets = ['https://codepen.io/lisa-nalyvaiko/pen/GRjdwrL.css']
app = dash.Dash(__name__)
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
    grouped_df = df.groupby(xaxis_column_name, as_index=False).agg({'Total price': 'sum'})
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
