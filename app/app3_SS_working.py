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
gdps = pd.read_csv('../data/clean/gdp_1960_2018_worldbank.csv')
arms = pd.read_csv('../data/clean/un-arms-and-ammunition_1988-2018.csv')
alt_country_ids = pd.read_csv(
    'https://raw.githubusercontent.com/KoGor/Map-Icons-Generator/master/data/world-110m-country-names.tsv',
    delimiter="\t")

# additional wrangling
gdp_ids = pd.merge(gdps, alt_country_ids, left_on='Country', right_on='name')[['Country', 'id', 'Year', 'GDP']].dropna()
arms_cleaned = arms[['Country', 'Year', 'Direction', 'USD_Value']]
arms_gdp = arms_cleaned.merge(gdp_ids, on=['Country', 'Year'], how="left")
arms_gdp['percent_GDP'] = arms_gdp['USD_Value'] / arms_gdp['GDP']

###Samantha's Stuff:
def gdp_perc_chart(year=2018, stat_type='Export'):
    countries = ['USA', 'Italy', 'Spain', 'Germany', 'Czech Rep.', 'Brazil', 'Norway', 
                 'Switzerland', 'Turkey', 'Canada', 'Japan', 'Croatia', 'United Kingdom', 'France']
    
    # Wrangling specific to this chart:
    df_for_perc_of_gdp = arms_gdp[(arms_gdp['Country'].isin(countries)) & 
                                  (arms_gdp['Year'] == year) & 
                                  (arms_gdp['Direction'] == stat_type)].drop_duplicates('Country')

    df_for_perc_of_gdp['percent_GDP'] = df_for_perc_of_gdp['percent_GDP'] * 100
    
    # Make the chart:
    gdp_perc_chart = alt.Chart(df_for_perc_of_gdp).mark_bar().encode(
        alt.X('Country:N', 
              sort=alt.EncodingSortField(field='percent_GDP', 
                                         order='descending'),
              title='Country',
              axis=alt.Axis(labelAngle=45)),
        alt.Y('percent_GDP:Q',
              title='Arms Trade as a Percentage of GDP',
              scale=alt.Scale(domain=(0, 0.5))),
        alt.Order(shorthand=['percent_GDP'], sort='descending'),
        alt.Tooltip(['Country', 'percent_GDP'])
    ).configure_bar(color='orange'
    ).properties(width=880, 
                 height=230)
    
    return gdp_perc_chart


# Init app
app = dash.Dash(__name__, assets_folder='assets')
app.title = 'World Wide Arms and Ammunition Movement and GDP Effects'

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
                        {'label': 'Import', 'value': 'import'},
                        {'label': 'Export', 'value': 'export'},
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

    html.Div([html.Iframe(
        sandbox='allow-scripts',
        id='plot',
        height='300',
        width='990',
        style={'border-width': '0'},

        ################ The magic happens here
        srcDoc = gdp_perc_chart().to_html()
        ################ The magic happens here
        
    )], className='mid-container'),

    html.Div([
        html.Div([
            html.Div("Weapons Import share in GDP placeholder")
        ], className='left-col'),
        html.Div([
            html.Div("Weapons Import placeholder")
        ], className='right-col'),
    ], className='bottom-container')
], className='main-container')

@app.callback(
    dash.dependencies.Output('world-chart', 'children'),
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


# def update_gdp_perc_chart(year=2018, stat_type='Export'):
#     '''
#     Takes in an xaxis_column_name and calls make_plot to update our Altair figure
#     '''
#     updated_plot = gdp_perc_chart(year, stat_type).to_html()
#     return updated_plot

# server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)
