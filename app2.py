import dash
#import dash_html_components as html
from dash import html
#import dash_core_components as dcc
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import pycountry

from graphs import make_plot


app = dash.Dash(__name__,title='MDA Eurovision Interactive',external_stylesheets=[dbc.themes.BOOTSTRAP],serve_locally = False)

# add this for heroku
server = app.server

# Chart
df = pd.read_csv('yearBias.csv')

countries = []
for country in df['From country']:
    countries.append(pycountry.countries.get(name=country).alpha_3)

df['iso code'] = countries


#fig = px.choropleth(locationmode="country names", scope="world", data_frame=data, locations='name', color='communityId_weight')
#fig.update_layout(width=1500)

# Data
#df = df.rename(columns=dict(fromCount="From country",
#                            toCount="To country",
#                            bias="True_Bias"))
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
fig.update_layout(title=f"<b>{first_title}</b>",title_x=0.5)
fig.show()

app.layout = dbc.Container(
    [
        html.Div(children=[html.H1(children='Communities of Voting'),
                           html.H2(children='Voting Communities'),
                           html.H4(children='',id='id_title')],
                 style={'textAlign':'center','color':'black'}),
        html.Hr(),
        dbc.Row(
            [
                #dbc.Col(dropdown, md=2),
                dbc.Col(dcc.Graph(id="id_graph",figure=fig), md=10),
            ],
            align="center",
        ),
    ],
    fluid=True,
)

@app.callback(
    Output('id_title','children'),
    Output('id_graph','figure'),
    [Input('data_set', 'value'),
     ]
)
def update_chart(currency_value):
    return



if __name__ == '__main__':
    app.run_server(debug=True)