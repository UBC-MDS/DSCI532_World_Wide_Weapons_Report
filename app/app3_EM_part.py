import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import altair as alt
from vega_datasets import data
import grasia_dash_components as gdc
from dash.dependencies import Input, Output


def configure_default_alt_theme():
    font = "Arial"
    axisColor = "#000000"
    gridColor = "#DEDDDD"
    return {
        "config": {
            "title": {
                "fontSize": 24,
                "font": font,
                "anchor": "start",  # equivalent of left-aligned.
                "fontColor": "#000000"
            },
            'view': {
                "height": 300,
                "width": 400
            },
            "axisX": {
                "domain": True,
                # "domainColor": axisColor,
                "gridColor": gridColor,
                "domainWidth": 1,
                "grid": False,
                "labelFont": font,
                "labelFontSize": 12,
                "labelAngle": 0,
                "tickColor": axisColor,
                "tickSize": 5,  # default, including it just to show you can change it
                "titleFont": font,
                "titleFontSize": 16,
                "titlePadding": 10,  # guessing, not specified in styleguide
                "title": "X Axis Title (units)",
            },
            "axisY": {
                "domain": False,
                "grid": True,
                "gridColor": gridColor,
                "gridWidth": 1,
                "labelFont": font,
                "labelFontSize": 14,
                "labelAngle": 0,
                # "ticks": False, # even if you don't have a "domain" you need to turn these off.
                "titleFont": font,
                "titleFontSize": 16,
                "titlePadding": 10,  # guessing, not specified in styleguide
                "title": "Y Axis Title (units)",
                # titles are by default vertical left of axis so we need to hack this
                # "titleAngle": 0, # horizontal
                # "titleY": -10, # move it up
                # "titleX": 18, # move it to the right so it aligns with the labels
            },
        }
    }


# register the custom theme under a chosen name
alt.themes.register('configure_default_alt_theme', configure_default_alt_theme)
alt.themes.enable('configure_default_alt_theme')
# alt.themes.enable('none') # to return to default

# Load datasets
world_map_skl = alt.topo_feature(data.world_110m.url, 'countries')
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

# Init app
app = dash.Dash(__name__, assets_folder='assets')
app.title = 'World Wide Arms and Ammunition Movement and GDP Effects'

def update_country_chart(stat_type = 'Import', country = 'Germany'):
    country_USD = alt.Chart(arms_gdp.query(f'Direction == "{stat_type}" & Country == "{country}"')).mark_area().encode(
        alt.X('Year:O', title = "Year"),
        alt.Y('USD_Value:Q', title = "USD Value"),
    ).properties(title=f'{country} Weapons {stat_type} value in USD', width=350, height=250)
    
    country_gdp = alt.Chart(arms_gdp.query(f'Direction == "{stat_type}" & Country == "{country}"')).mark_bar().encode(
        alt.X('Year:O', title = "Year"),
        alt.Y('percent_GDP:Q', title = "% of GDP"),
    ).properties(title=f'{country} Weapons {stat_type} share in GDP', width=350, height=250)
    
    return (country_gdp | country_USD).properties(background='white')

# Build app layout
app.layout = html.Div([
    html.H1("World Wide Arms and Ammunition Movement and GDP Effects"),

    html.Div([
        html.Div([
            html.P('Choose statistic:'),
            html.Div([
                dcc.RadioItems(
                    id='stat-type',
                    options=[
                        {'label': 'Import', 'value': 'Import'},
                        {'label': 'Export', 'value': 'Export'},
                        {'label': 'Net', 'value': 'net'}
                    ],
                    value='import'
                )
            ], className='button-switches')
        ], className='left-col'),
        html.Div([
            html.Div(id='world-chart'),
            dcc.Slider(
                id='year-slider',
                min=1980,
                max=2018,
                step=1,
                value=2018,
                updatemode='drag',
                # FIXME: Have no idea why Dash complains
                # FIXME: at np.arange(1980, 2018, 5)
                # FIXME: Have to do this nasty workaround...
                marks=dict(map(lambda x: (x, str(x)), [1980, 1985,
                                                       1990, 1995,
                                                       2000, 2005,
                                                       2010, 2015,
                                                       2018]))
            ),
        ], className='right-col')
    ], className='top-container'),

    html.Div([
        html.Div('Weapons as % of GDP')
    ], className='mid-container'),

    html.Div([
        html.Div('Country charts'),
            html.Iframe(
            sandbox='allow-scripts',
            id='plot2',
            height='370',
            width='1000',
            style={'border-width': '1px'},

            ################ The magic happens here
            srcDoc = update_country_chart().to_html()
            ################ The magic happens here
            ),
        dcc.Dropdown(
        id='country-name',
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
    ], className='bottom-container')
], className='main-container')

@app.callback(
    dash.dependencies.Output('plot2', 'srcDoc'),
    [dash.dependencies.Input('stat-type', 'value'),
     dash.dependencies.Input('country-name', 'value')])

def update_plot(stat_type_column_name,
                country_column_name):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    updated_plot = update_country_chart(stat_type_column_name,
                            country_column_name).to_html()
    return updated_plot

@app.callback(dash.dependencies.Output('world-chart', 'children'),
    [dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('stat-type', 'value'),
     # dash.dependencies.Input('country-name', 'value'),
     ])

def update_world_chart(year, stat_type):
    print(year, stat_type)
    chart = alt.Chart(world_map_skl).mark_geoshape().encode(
        alt.Color('GDP:Q', scale=alt.Scale(scheme='goldorange'))
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(gdp_ids.query("Year == " + str(year)), 'id', ['GDP'])
    ).project('equirectangular').properties(
        width=820,
        height=380,
        background='white'
    ).configure_axis(
        grid=False
    ).configure_view(
        strokeOpacity=0
    )

    return html.Iframe(
        sandbox='allow-scripts',
        id='plot',
        width='820',
        height='380',
        style={'border-width': '0'},
        srcDoc=chart.to_html()
    )


# server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)
