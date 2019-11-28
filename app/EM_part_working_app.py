# Create your app here
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import altair as alt
import vega_datasets
import grasia_dash_components as gdc
from dash.dependencies import Input, Output

app = dash.Dash(__name__, assets_folder='assets') # where we are giving the app a name. 
server = app.server

app.title = 'Dash app with pure Altair HTML' # give the app a title 

# Load datasets
# world_map_skl = alt.topo_feature(data.world_110m.url, 'countries')
gdps = pd.read_csv('https://raw.githubusercontent.com/UBC-MDS/DSCI532_World_Wide_Weapons_Report/master/data/clean/gdp_1960_2018_worldbank.csv')
arms = pd.read_csv('https://raw.githubusercontent.com/UBC-MDS/DSCI532_World_Wide_Weapons_Report/master/data/clean/un-arms-and-ammunition_1988-2018.csv')
alt_country_ids = pd.read_csv(
    'https://raw.githubusercontent.com/KoGor/Map-Icons-Generator/master/data/world-110m-country-names.tsv',
    delimiter="\t")

# additional wrangling
gdp_ids = pd.merge(gdps, alt_country_ids, left_on='Country', right_on='name')[['Country', 'id', 'Year', 'GDP']].dropna()
arms_cleaned = arms[['Country', 'Year', 'Direction', 'USD_Value']]
arms_gdp = arms_cleaned.merge(gdp_ids, on=['Country', 'Year'])
arms_gdp['percent_GDP'] = arms_gdp['USD_Value'] / arms_gdp['GDP']

# make plot goes here. 
def update_country_chart(stat_type = 'Import', country = 'Germany'):
    country_USD = alt.Chart(arms_gdp.query(f'Direction == "{stat_type}" & Country == "{country}"')).mark_area().encode(
        alt.X('Year:O', title = "Year"),
        alt.Y('USD_Value:Q', title = "USD Value"),
    ).properties(title=f'{country} Weapons {stat_type} value in USD', width=500, height=300)
    
    country_gdp = alt.Chart(arms_gdp.query(f'Direction == "{stat_type}" & Country == "{country}"')).mark_bar().encode(
        alt.X('Year:O', title = "Year"),
        alt.Y('percent_GDP:Q', title = "% of GDP"),
    ).properties(title=f'{country} Weapons {stat_type} share in GDP', width=500, height=300)
    
    return country_gdp | country_USD

app.layout = html.Div([

    ### ADD CONTENT HERE like: html.H1('text'),
    #html.Img(src=')
    ### Let's now add an iframe to bring in HTML content

        html.Iframe(
        sandbox='allow-scripts',
        id='plot',
        height='400',
        width='1200',
        style={'border-width': '5px'},

        ################ The magic happens here
        srcDoc = update_country_chart().to_html()
        ################ The magic happens here
        ),
    dcc.Dropdown(
    id='dd-chart',
    options=[
        {'label': 'Import', 'value': 'Import'},
        {'label': 'Export', 'value': 'Export'},
    ],
    value='Import',
    style=dict(width='45%',
               verticalAlign="middle")
    ),
    dcc.Dropdown(
    id='dd-chart-y',
    options=[
        {'label': 'Germany', 'value': 'Germany'},
        {'label': 'Canada', 'value': 'Canada'},
        {'label': 'China', 'value': 'China'},
    # Missing option here
    ],
    value='Germany',
    style=dict(width='45%',
               verticalAlign="middle")
    ),
])

@app.callback(
    dash.dependencies.Output('plot', 'srcDoc'),
    [dash.dependencies.Input('dd-chart', 'value'),
     dash.dependencies.Input('dd-chart-y', 'value')])
def update_plot(stat_type_column_name,
                country_column_name):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    updated_plot = update_country_gdp_chart(stat_type_column_name,
                            country_column_name).to_html()
    return updated_plot

if __name__ == '__main__': # this allows it to run in a python file
    app.run_server(debug=True)