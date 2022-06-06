#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 21:33:47 2022

@author: medhahegde
"""

# import dash
#import dash_html_components as html
from dash import html
#import dash_core_components as dcc
from dash import dcc,dash_table,Dash
import dash_bootstrap_components as dbc
from dash import Input, Output


import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import pycountry
import ast

#data import for predictions
pred_data = pd.read_csv('https://raw.githubusercontent.com/jackmheller/modernDataAnalytics/main/Data/pred_rankings.txt', sep="\t", header=None)
true_data = pd.read_csv('https://raw.githubusercontent.com/jackmheller/modernDataAnalytics/main/Data/true_rankings.txt', sep="\t", header=None)
predictions = ast.literal_eval(pred_data.iloc[0,0])
true_rankings = ast.literal_eval(true_data.iloc[0,0])

year = 2022
pred = pd.DataFrame([range(1,6),predictions[year][:5],true_rankings[year][:5]]).T
pred.columns = ['Rank','Predicted Top 5', 'True Top 5']

def cond_formatting(pred):
    cond_formatting_list=[]
    for row_id in pred.index:
        counter =0
        if pred.iloc[row_id,1] in pred['True Top 5'].tolist():
            query1 = {'if': {"row_index": row_id, 'column_id': 'Predicted Top 5'},
      'backgroundColor': '#BCF7B3'}
            counter+=1
        if pred.iloc[row_id,2] in pred['Predicted Top 5'].tolist():
            query2 = {'if': {"row_index": row_id, 'column_id': 'True Top 5'},
      'backgroundColor': '#BCF7B3'}
            counter+=1
        if pred.iloc[row_id,1] == pred.iloc[row_id,2]:
            query1 = {'if': {"row_index": row_id, 'column_id': 'Predicted Top 5'},
      'backgroundColor': '#7FB277'}
            query2 = {'if': {"row_index": row_id, 'column_id': 'True Top 5'},
      'backgroundColor': '#7FB277'}
            counter+=1
        if counter>0:
            cond_formatting_list.append(query1)
            cond_formatting_list.append(query2)
    return cond_formatting_list  

app = Dash(__name__,title='MDA Eurovision Interactive',external_stylesheets=[dbc.themes.BOOTSTRAP])

# add this for heroku
server = app.server

# Chart
noWeightData = pd.read_csv('https://raw.githubusercontent.com/jackmheller/modernDataAnalytics/main/Data/GroupsScoreNoWeight.csv')
weightedData = pd.read_csv('https://raw.githubusercontent.com/jackmheller/modernDataAnalytics/main/Data/GroupsScoreWeight.csv')
data = noWeightData.merge(weightedData, on='name', suffixes = ("_noweight", "_weight"))

df = pd.read_csv('https://raw.githubusercontent.com/jackmheller/modernDataAnalytics/main/Data/yearBias.csv')

countries = []
for country in df['From country']:
    countries.append(pycountry.countries.get(name=country).alpha_3)

df['iso code'] = countries

cols_dd = df['From country'].unique()
# we need to add this to select which trace 
# is going to be visible
visible = np.array(cols_dd)

# define traces and buttons at once
traces = []
buttons = []
for value in cols_dd:
    traces.append(go.Choropleth(
        locations=df[df['To country'] == value]['iso code'], # Spatial coordinates
        z=df[df['From country'] == value]['True_Bias'].astype(float), # Data to be color-coded
        colorbar_title='Above Mean Vote Bias',
        visible= True if value==cols_dd[0] else False
        ))

    buttons.append(dict(label=value,
                        method="update",
                        args=[{"visible":list(visible==value)},
                              {"title":f"<b>{value}</b>"}]))

updatemenus = [{"active":0,
                "buttons":buttons,
               }]


# Show figure
fig = go.Figure(data=traces,
                layout=dict(updatemenus=updatemenus))
# This is in order to get the first title displayed correctly
first_title = cols_dd[0]
fig.update_layout(title="<b>{first_title}</b>",title_x=0.5)

fig2 = px.choropleth(locationmode="country names", scope="world", data_frame=data, locations='name', color='communityId_weight')
fig2.update_layout(width=1500)

data2 = pd.read_csv('https://raw.githubusercontent.com/jackmheller/modernDataAnalytics/main/Data/group_unweighted_Mean.csv')

fig3 = px.choropleth(locationmode="country names", scope="world", data_frame=data2, locations='name', color='communityId')
fig3.update_layout(width=1500)


card =dbc.Card([
dcc.Dropdown([str(x) for x in list(predictions.keys())], '2022', id='demo-dropdown'),
]
)

app.layout = dbc.Container(
    [
        html.Div(children=[html.H1(children='Mozambique Group World Visualizations'),
                           html.H2(children='Weighted Voting Communities'),
                           html.H4(children='',id='id_title')],
                 style={'textAlign':'center','color':'black'}),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="id_graph",figure=fig2), md=10),
            ],
            align="center",
        ),
        html.Div(children=[html.H2(children='Identify Which Countries Are Biased Toward Recipients')],
        style = {'textAlign': 'center', 'color': 'black'}),
        html.Hr(),

        dbc.Row([dbc.Col(dcc.Graph(id="id_graph2",figure=fig), md=10),],
                align = "center"),
        html.Div(children=[html.H2(children='Voting Communities Based on Mean Vote')],
        style = {'textAlign': 'center', 'color': 'black'}),
        html.Hr(),

        dbc.Row([dbc.Col(dcc.Graph(id="id_graph3",figure=fig3), md=10),],
                align = "center"),
        

        html.Div(children=[html.H2(children='Prediction for Different Years')],
        style = {'textAlign': 'center', 'color': 'black'}),
        html.Hr(),
        
         dbc.Row([dbc.Col(card, md=4)],align='center',justify="center",),
        
        html.Br(),
        html.Br(),
        
        html.Div(id='update-table',children=[dash_table.DataTable(
        id='pred_table',
        columns=[{"name": i, "id": i} 
                  for i in pred.columns],
        data=pred.to_dict('records'),
        style_cell=dict(textAlign='center',font_family = 'arial',font_size = 12),
        
        style_header=dict(backgroundColor="#c7bebd",fontWeight='bold'),
        style_data_conditional=cond_formatting(pred),  
        fill_width=False)],style={'margin-left':'550px'}),
          html.Br(),
        html.Br()
    
        
    ],
    fluid=True,
)

@app.callback(
    Output("update-table", "children"),
    [Input("demo-dropdown", "value")],
)
def update_output(value):
    
    year = int(value)
    pred = pd.DataFrame([range(1,6),predictions[year][:5],true_rankings[year][:5]]).T
    pred.columns = ['Rank','Predicted Top 5', 'True Top 5']

    return html.Div(
        [
            dash_table.DataTable(
        id='pred_table',
        columns=[{"name": i, "id": i} 
                  for i in pred.columns],
        data=pred.to_dict('records'),
        style_cell=dict(textAlign='center',font_family = 'arial',font_size = 12),
          style_cell_conditional=[
        {'if': {'column_id': 'Rank'},
          'width': '50px'},
        {'if': {'column_id': 'Predicted Top 5'},
          'width': '150px'},
        {'if': {'column_id': 'True Top 5'},
          'width': '150px'}],
        style_header=dict(backgroundColor="#c7bebd",fontWeight='bold'),
        style_data_conditional=cond_formatting(pred),  
        fill_width=False)
            
        ])

if __name__ == '__main__':
    app.run_server(debug=False)