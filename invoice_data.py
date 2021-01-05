# import requests
# from requests.auth import HTTPBasicAuth
import pandas as pd
# import numpy as np
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
import gspread
# from df2gspread import df2gspread as d2g
from oauth2client.service_account import ServiceAccountCredentials
# from gspread_dataframe import (get_as_dataframe, set_with_dataframe)
# import json
from sheetfu import SpreadsheetApp
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

# read invoicing statistics table to pandas
# Specify path to your file with credentials
# Specify name of table in google sheets

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
path_to_credential = '/Users/lisanalyvaiko/Downloads/google_credentials.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(path_to_credential, scope)
gc = gspread.authorize(credentials)
# Specify name of table in google sheets
table_name = 'Invoicing Statistics 2020'
spr_id = '1gRd73DKLWuVGOUoOu9sv7iiym_JyDovVjOu7bT1aZO8'
spreadsheet = SpreadsheetApp(path_to_credential).open_by_id(spr_id)

needed_sheets = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                 'November', 'December']
month_sheets = [
    sheet for sheet in spreadsheet.sheets
    if sheet.name in needed_sheets
]
data = []
for month_sheet in month_sheets:
    data_range = month_sheet.get_data_range()
    values = data_range.get_values()
    for row in values:
        data.append(row)
headers = data.pop(1)

# Create df
df = pd.DataFrame(data, columns=headers)

df = df.drop(columns=['Comments', '', '',
                      'What stats?', 'Value', '', '', '', '', '', ''])
df = df.drop(0)
nan_value = float("NaN")
df = df.replace("", nan_value)
df.dropna(subset=["Project Name"], inplace=True)
df = df[~df["Client"].str.contains('Client')]

df['Date confirmed'] = df['Date confirmed'].astype(float)
df['Date confirmed'] = pd.to_datetime(df['Date confirmed'], unit='d', origin='1900-01-01')
df['Hours sold'] = df['Hours sold'].astype(float)
df['Total time spent'] = df['Total time spent'].astype(str).str.replace(',', '.', regex=False)
df['Total time spent'] = df['Total time spent'].astype(float)
df['Rate'] = df['Rate'].astype(str).str.replace(',', '.', regex=False)
df['Rate'] = df['Rate'].astype(str).str.replace('$', '', regex=False)
df['Rate'] = df['Rate'].astype(float).round(2)
df['Total price'] = df['Total price'].astype(float)
df['Cost, h'] = df['Cost, h'].astype(float).round(2)
df['Cost, total'] = df['Cost, total'].astype(float).round(2)
df['Proft, $'] = df['Proft, $'].astype(float).round(2)
df['Profit, %'] = df['Profit, %'].astype(float).round(2) * 100
df['AM'] = df['AM'].astype(str).str.replace('IT', 'IV', regex=False)

# revenue_by_type = df.groupby('Type',as_index=False) \
#                   .agg({'Total price':'sum'})
# x = revenue_by_type['Type']
# y = revenue_by_type['Total price']

# fig = px.bar(x=x, y=y, labels={'x':'work type', 'y':'revenue'})

external_stylesheets = ['https://codepen.io/lisa-nalyvaiko/pen/GRjdwrL.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

indicators_list = ['Client', 'Main Developer', 'Location', 'Seniority', 'Type', 'AM', 'Sales person']

app.layout = html.Div(children=[
    html.H1(children='Testing Dash'),

    html.Div(children='''
        Trying to make a dashboard for invoicing stats.
    '''),

    html.Div([
        dcc.Dropdown(
            id='xaxis-column',
            options=[{'label': i, 'value': i} for i in indicators_list],
            value=indicators_list[2]
        )]),

    dcc.Graph(
        id='revenue_graph'
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


if __name__ == '__main__':
    app.run_server(debug=True)
