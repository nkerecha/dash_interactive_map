
import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup
import bs4 as bs
import lxml.html as lh
import pandas as pd
import copy
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import chart_studio.plotly as py
import chart_studio.tools as tls
import plotly.io as pio
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
import matplotlib.pyplot as plt
import numpy as np
import geopandas
import math
from dash.dependencies import Input, Output, State
import flask

stylesheets = ['/assets/bootstrap/css/styles.css']

app = dash.Dash(__name__)
server = app.server


url= 'https://www.worldometers.info/coronavirus'

page = requests.get(url)
soup = bs.BeautifulSoup(page.content, features='html.parser')
datadiv = soup.find(class_='main_table_countries_div')
table_rows = soup.find_all('tr')
list_data = []
for tr in datadiv.findAll('tr'):
    td = tr.find_all('td')
    row = [tr.text for tr in td]
    list_data.append(row)


# In[33]:


final_list_data = list_data[9:len(list_data)-8]


# In[34]:


continent_data = list_data[0:7]


# In[35]:


list_header = [['Country_Other','Total_Cases','New_Cases','Total_Deaths','New_Deaths','Total_Recovered',
                'Active_Cases','Serious_Critical','Total_Cases/1M_pop','Total_Deaths 1m/pop','Total_Tests','Total_Tests 1m/pop','Continent_en']]
continent_header = [['Contient','Total_Cases','New_Cases','Total_Deaths','New_Deaths','Total_Recovered',
                'Active_Cases','Serious_Critical','Total_Cases/1M_pop','Total_Deaths 1m/pop','Total_Tests','Total_Tests 1m/pop','Continent']]


# In[36]:


current_row_length = len(final_list_data[0])
list_header_length = len(list_header[0])
continent_length = len(continent_data[0])


# In[37]:


def column_constructor(length1, length2, list_to_add, is_2d):
    difference = length1 - length2
    if (difference > 0):
        for i in range(difference):
            count = i + 1
            value = 'Unknown_column_' + str(count)
            if (is_2d == True):
                list_to_add[0].append(value)
            else:
                list_to_add.append(value)


# In[38]:


column_constructor(current_row_length,list_header_length,list_header,True)
column_constructor(continent_length,len(continent_header[0]),continent_header,True)


# In[39]:


uncleaned_data = list_header + final_list_data
continent_uncleaned = continent_header + continent_data[1:]


# In[40]:


def type_cleaner(given_list,i,j):
    if (str(given_list[i][j]).strip() != ''):
        value = str(given_list[i][j]).replace("+", "")
        new_value = str(given_list[i][j]).replace("\n", "")
        created = new_value.replace(",", "")
        if given_list[i][j] != None and (given_list[i][j] != 'N/A'):
            new_value = int(created)
            final_value = new_value
            given_list[i][j] = final_value
        elif (given_list[i][j] == 'N/A'):
            given_list[i][j] = None
        else:
            given_list[i][j] = None
    else:
        given_list[i][j] = None
    return None
for i in range(1,len(uncleaned_data)):
    for j in range(1,7):
        type_cleaner(uncleaned_data,i,j)
for i in range(1,len(continent_uncleaned)):
    for j in range(1,7):
        type_cleaner(continent_uncleaned,i,j)
for i in range(1,len(continent_uncleaned)):
        continent_uncleaned[i][0] = str(continent_uncleaned[i][0]).replace('\n','')


# In[41]:


for i in range(1,len(uncleaned_data)):
    uncleaned_data[i][0] = str(uncleaned_data[i][0]).strip()
for i in range(1,len(uncleaned_data)):
    if uncleaned_data[i][0] == 'USA':
        uncleaned_data[i][0] = 'United States of America'
    elif (uncleaned_data[i][0] == 'DRC'):
        uncleaned_data[i][0] = 'Dem. Rep. Congo'
    elif  (uncleaned_data[i][0] == 'CAR'):
        uncleaned_data[i][0] = 'Central African Rep.'


# In[42]:


column_names= list_header[0]
df = pd.DataFrame(uncleaned_data[1:],columns =column_names)


# In[43]:


continent_df = pd.DataFrame(continent_uncleaned[1:],columns = continent_header[0])


# In[44]:


df_country_data = df.filter(list_header[0], axis=1)
df_country_names = pd.DataFrame(df.astype(str)['Country_Other'])
data = df_country_data


# In[45]:


world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))


# In[46]:


data['log_data_cases'] = None
for i in range(0,len(data['Total_Cases'])):
    value = copy.deepcopy(data.loc[i,'Total_Cases'])
    returned = int(math.log(value))
    data.loc[i,'log_data_cases'] = returned


# In[47]:


merged_inner = pd.merge(left=world, right=data, how = 'inner',left_on = 'name',right_on = 'Country_Other')


# In[48]:


values = []
for i in range(len(merged_inner['iso_a3'])):
    if (merged_inner.loc[i,'iso_a3'] == '-99' and merged_inner.loc[i,'Country_Other'] == 'France' ):
        merged_inner.loc[i,'iso_a3'] = 'FRA'
    elif(merged_inner.loc[i,'iso_a3'] == '-99' and  merged_inner.loc[i,'Country_Other'] == 'Norway'):
        merged_inner.loc[i,'iso_a3'] = 'NOR'


# In[49]:


country_name = 'Country: ' + merged_inner['name'].astype(str)
text_total_cases = 'Total Cases: ' + merged_inner['Total_Cases'].astype(str)
text_recovered_cases = 'Recovered Cases: ' + merged_inner['Total_Recovered'].astype(str)
text_active_cases = 'Active Cases: ' + merged_inner['Active_Cases'].astype(str)
text_total_tests = 'Total Tests: ' + merged_inner['Total_Tests'].astype(str)
merged_inner['text'] = country_name + '<br>' + text_total_cases + '<br>' + text_recovered_cases + '<br>' + text_active_cases + '<br>' + text_total_tests


# In[50]:


continent_africa = merged_inner[merged_inner['Continent_en'] == 'Africa']
continent_europe = merged_inner[merged_inner['Continent_en'] == 'Europe']
continent_north = merged_inner[merged_inner['Continent_en'] == 'North America']
continent_asia = merged_inner[merged_inner['Continent_en'] == 'Asia']
continent_south = merged_inner[merged_inner['Continent_en'] == 'South America']
continent_aust = merged_inner[merged_inner['Continent_en'] == 'Australia/Oceania']


# In[51]:


country_name = 'Country: ' + merged_inner['name'].astype(str)
text_total_cases = 'Total Cases: ' + merged_inner['Total_Cases'].astype(str)
text_recovered_cases = 'Recovered Cases: ' + merged_inner['Total_Recovered'].astype(str)
text_active_cases = 'Active Cases: ' + merged_inner['Active_Cases'].astype(str)
text_total_tests = 'Total Tests: ' + merged_inner['Total_Tests'].astype(str)
merged_inner['text'] = country_name + '<br>' + text_total_cases + '<br>' + text_recovered_cases + '<br>' + text_active_cases + '<br>' + text_total_tests

app.layout = html.Div([
    html.Div([
            html.H2("Covid Data Analytics"),
            html.Img(src = "/assets/map_icon.png")

        ],className = "banner"),
    html.Div([
        html.Div([html.H3("World map")],
            style={'textAlign': "center", "padding-bottom": "30"}
            ),
            html.Div([
            html.Span("Metric to display : ", className="figure_out",
            style={"text-align": "center", "width": "40%", "padding-top": 10}
            ),
            dcc.Dropdown(id="value-selected",value = 'log_data_cases',
                    options=[
                    {'label': "New Cases", 'value': 'New_Cases'},
                    {'label': "Total Recoveries", 'value': 'Total_Recovered'},
                    {'label': "Total Deaths", 'value': 'Total_Deaths'}],
                    style={"display": "block", "margin-left": "auto", "margin-right": "auto","width": "70%"},
                    className="fig_r")], className="row"),
             dcc.Graph(id="my-graph",className = 'world_map')#style={'width': '90vh', 'height': '90vh'}
            ], className="container"),
    html.Div( children = [
        dcc.Graph(
        id = 'starter-graph',
        figure = {
            'data' :[{'x': continent_df['Continent'],'y': continent_df['Total_Recovered'],'type' : 'bar','name' : 'Recovered Cases'},
                 {'x': continent_df['Continent'],'y': continent_df['Active_Cases'],'type' : 'bar','name': 'Active Cases'},
                 {'x': continent_df['Continent'],'y': continent_df['Serious_Critical'],'type' : 'bar','name': 'Critical Cases'},
                ],
            'layout' : {
                'title' : 'Aggreagated Continent Data',

            }
        }
        )
        ],className = 'cont_bar'),
    html.Div([
        dcc.Graph(
        id = 'scatter_world',
        figure = {
            'data' : [
                dict(
                {'x' : merged_inner['Total_Recovered'], 'y': merged_inner['Total_Deaths'] ,'marker' : {'color':["red","green"]}},
                text= merged_inner['text'],
                mode = 'markers',
                opacity = 0.7,
                marker = {
                    'size': 15,
                    'line': {'width': 0.5,'color' : 'white'}
                },
                )],

            'layout': dict(
                xaxis={'title': 'Total Recoveries'},
                yaxis={'title': 'Total Deaths'},
                margin={'l': 60, 'b': 60, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'

            )
        })

    ],className = 'scatter_p'),
    html.Div( [
        dcc.Input(id = 'my-id',value = 'Initial Value',type = 'text'),
        html.Div(id = "my-div")
    ],className ='input_tester'),
    html.Div([
        dcc.Graph(id = 'graph_slider'),
        dcc.Slider(
            id = 'continent_slider',
            min = 0,
            max = 10,
            value =0,
            step= None,
            #marks={str(continent): str(continent) for continent in merged_inner['Continent_en'].unique()},
            marks={str(i) : str(continent) for i, continent in enumerate(merged_inner['Continent_en'].unique())},
            included = False

        )
    ],className = '1st_slider')
])


@app.callback(
    Output(component_id = "my-div",component_property = "children"),
    [Input(component_id = "my-id", component_property = "value")]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)

@app.callback(
    Output('graph_slider','figure'),
    [Input('continent_slider','value')],
    [State('continent_slider', 'marks')]
)
def update_fig_slider(selected_continent_key,marks):
    selected_continent = marks[str(selected_continent_key)]
    filter_continent = merged_inner[merged_inner['Continent_en'] == selected_continent]
    hopper = [dict(
             x = filter_continent['Total_Cases'],
             y = filter_continent['Total_Deaths'],
             text = filter_continent['text'],
             mode = 'markers',
             opacity = 0.7,
             marker = {
                 'size' : 15,
                  'line': {'width' : 0.5,'color' : 'green'}
             },
            )]

    return {
        'data' : hopper,
        'layout' : dict(
        xaxis={'type': 'log', 'title': 'Log of Total Cases'},
        yaxis={'title': 'Total Deaths'},
        margin={'l': 60, 'b': 60, 't': 10, 'r': 10},
        legend={'x': 0, 'y': 1},
        hovermode='closest',
        transition = {'duration': 200},
        )
    }

@app.callback(
    Output("my-graph", "figure"),
    [Input("value-selected", "value")]
)
def update_figure(selected):
    def title(text):
        if text == "New_Cases":
            return "New Cases (Covid Cases)"
        elif text == "Total_Recovered":
            return "Total Recovered (Covid Cases)"
        elif text == None:
            return "Total Log Data"
        else:
            return "Total Deaths (Covid Cases)"
    trace = go.Choropleth(
        locations = merged_inner['iso_a3'],
        z = merged_inner[selected],
        text = merged_inner['text'],
        colorscale = 'viridis',
        reversescale=False,
        marker_line_color='darkgray',
        marker={
            'line': {'color': 'rgb(180,180,180)','width': 0.5}},
    )
    return {
        "data": [trace],

        "layout": go.Layout(title=title(selected),
                #height=900,
                #width = 1200,
                geo={'showframe': False,
                'showcoastlines': True,
                'showcoastlines' : True,
                'showocean' : True,
                'oceancolor' :"LightBlue",
                'showlakes' : True,
                'lakecolor' : "LightBlue",
                'projection': {'type': "natural earth"}
                })
        }


if __name__ == '__main__':
    app.run_server(debug=True,port=3004)
