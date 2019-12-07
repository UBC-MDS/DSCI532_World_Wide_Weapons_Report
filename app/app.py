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


# Configure global Altair theme
def configure_default_alt_theme():
    font = "Open Sans, Arial"
    axisColor = "#000000"
    gridColor = "#DEDDDD"
    return {
        "config": {
            "title": {
                "fontSize": 20,
                "font": font,
                "anchor": "center",  # equivalent of left-aligned.
                "fontColor": "#000000",
                "dx": 50,
                "dy": -10
            },
            'view': {
                "height": 300,
                "width": 400,
                "strokeOpacity": False
            },
            "axisX": {
                "domain": True,
                # "domainColor": axisColor,
                "gridColor": gridColor,
                "domainWidth": 1,
                "grid": False,
                "labelFont": font,
                "labelFontSize": 12,
                "labelAngle": 45,
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
                "titleFont": font,
                "titleFontSize": 16,
                "titlePadding": 10,  # guessing, not specified in styleguide
                "title": "Y Axis Title (units)",
                # titles are by default vertical left of axis so we need to hack this
            },
        }
    }


# register the custom theme under a chosen name
alt.themes.register('configure_default_alt_theme', configure_default_alt_theme)
alt.themes.enable('configure_default_alt_theme')
# alt.themes.enable('none') # to return to default

# Load datasets
world_map_skl = alt.topo_feature(data.world_110m.url, 'countries')
gdps = pd.read_csv(
    'https://raw.githubusercontent.com/UBC-MDS/DSCI532_World_Wide_Weapons_Report/master/data/clean/gdp_1960_2018_worldbank.csv')
arms = pd.read_csv(
    'https://raw.githubusercontent.com/UBC-MDS/DSCI532_World_Wide_Weapons_Report/master/data/clean/un-arms-and-ammunition_1988-2018.csv')
alt_country_ids = pd.read_csv(
    'https://raw.githubusercontent.com/KoGor/Map-Icons-Generator/master/data/world-110m-country-names.tsv',
    delimiter="\t")

# additional wrangling
replacements_country_names = {'Bosnia and Herzegovina': 'Bosnia Herzegovina',
                              'Central African Republic': 'Central African Rep.',
                              "Cote d'Ivoire": "Côte d'Ivoire",
                              'Czech Republic': 'Czech Rep.',
                              'Dominican Republic': 'Dominican Rep.',
                              'Solomon Islands': 'Solomon Isds',
                              'United States': 'USA'}
alt_country_ids = alt_country_ids.replace(replacements_country_names)
gdps = gdps.replace(replacements_country_names)
arms_cleaned = arms[['Country', 'Year', 'Direction', 'USD_Value']]
arms_gdp = arms_cleaned.merge(gdps, on=['Country', 'Year'], how='right')
arms_gdp['percent_GDP'] = 100 * arms_gdp['USD_Value'] / arms_gdp['GDP']
arms_gdp = (alt_country_ids
            .rename(columns={'name': 'Country'})
            .assign(key=1)
            .merge(pd.DataFrame(columns=['Year'], data=list(range(1990, 2019))).assign(key=1), on='key')
            .merge(pd.DataFrame(columns=['Direction'], data=['Import', 'Export']).assign(key=1), on='key')
            .drop('key', axis=1)
            .merge(arms_gdp, on=['Country', 'Year', 'Direction', ], how='left')).fillna(0)

# Init the app
app = dash.Dash(__name__, assets_folder='assets', external_scripts=[
    'https://code.jquery.com/jquery-3.4.1.min.js'
])
app.title = 'World Wide Arms and Ammunition Movement and GDP Effects'

# Build app layout
app.layout = html.Div([
    html.H1("World Wide Arms and Ammunition Movement and GDP Effects"),

    html.Div([
        html.P(
        "This app is designed to explore how the movement of weapons globally has changed over the last 30 years, and how imports and exports of arms and ammunition relate to a country's GDP.",
        style = {'textAlign': 'Center',
                 'margin-top': '10px',
                 'margin-bottom': '10px'
        }),
        html.Div([
            html.Div([
                
                html.P('Choose statistic:'),
                html.Div([
                    dcc.RadioItems(
                        id='stat-type',
                        options=[
                            {'label': 'Import', 'value': 'Import'},
                            {'label': 'Export', 'value': 'Export'},
                        ],
                        value='Import'
                    ),
                ], className='button-switches'),

                html.P('Choose country:'),
                dcc.Dropdown(
                    id='country-name',
                    options=list(
                        map(lambda x: {"label": x, "value": x}, arms_gdp['Country'].dropna().sort_values().unique())),
                    value='USA',
                    clearable=False
                ),
                html.P("Explore changes through time of a single country using the lowermost visualizations.",
                        style = {'textAlign': 'Left',
                                 'margin-top': '2px',
                                 'margin-bottom': '16px',
                                 'font-size': '10px'
                }),
                daq.ToggleSwitch(
                    label='Include USA',
                    labelPosition='right',
                    value=True,
                    theme='dark',
                    size=35,
                    id='include-usa'
                ),
                html.P(
                "Remove the outlier USA to better visualize differences between other nations.",
                style = {'textAlign': 'Left',
                         'margin-top': '2px',
                         'margin-bottom': '16px',
                         'font-size': '10px'
                }),
                daq.ToggleSwitch(
                    label='% of GDP',
                    labelPosition='right',
                    value=False,
                    theme='dark',
                    size=35,
                    id='gdp-pct'
                )
            ], className='left-col'),
            html.Div([
                html.Div(id='world-chart'),
                dcc.Slider(
                    id='year-slider',
                    min=1990,
                    max=2018,
                    step=1,
                    value=2018,
                    updatemode='drag',
                    included=False,
                    # FIXME: Have no idea why Dash complains
                    # FIXME: at np.arange(1980, 2018, 5)
                    # FIXME: Have to do this nasty workaround...
                    marks=dict(map(lambda x: (x, str(x)), [  # 1980, 1985,
                        1990, 1995,
                        2000, 2005,
                        2010, 2015,
                        2018]))
                ),
            ], className='right-col')
        ], className='top-container'),

        html.Div([
            html.Div(),
            html.Iframe(
                sandbox='allow-scripts',
                id='plot3',
                height='350',
                width='1300',
                style={'border-width': '0'},
            )
        ]),

        html.Div([
            html.Div(),
            html.Iframe(
                sandbox='allow-scripts',
                id='plot2',
                height='390',
                width='1300',
                style={'border-width': '0'},
            )
        ], className='bottom-container'),
        "The data has been sourced from the United Nations Statistics Division and the World Bank.",
        dcc.Markdown('''
        Data sources: [GDP by Country](https://data.worldbank.org/indicator/NY.GDP.MKTP.CD), [Worldwide Arms and Ammunition Trading](http://data.un.org/Data.aspx?d=ComTrade&f=_l1Code%3a93)
        '''),
    ], className='main-container')
])


#################################################
################# Callbacks #####################
#################################################

@app.callback(
    dash.dependencies.Output('plot2', 'srcDoc'),
    [dash.dependencies.Input('stat-type', 'value'),
     dash.dependencies.Input('country-name', 'value'),
     dash.dependencies.Input('year-slider', 'value')])
def update_plot(stat_type_column_name,
                country_column_name,
                year):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    updated_plot = update_country_chart(stat_type_column_name,
                                        country_column_name,
                                        year).to_html()
    return updated_plot


@app.callback(
    dash.dependencies.Output('plot3', 'srcDoc'),
    [dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('stat-type', 'value')])
def update_plot3(year_val, stat_val):
    '''
    Takes in an xaxis_column_name and calls make_plot to update our Altair figure
    '''
    updated_plot = make_gdp_perc_chart(year_val, stat_val).to_html()
    return updated_plot


@app.callback(dash.dependencies.Output('world-chart', 'children'),
              [dash.dependencies.Input('year-slider', 'value'),
               dash.dependencies.Input('stat-type', 'value'),
               dash.dependencies.Input('include-usa', 'value'),
               dash.dependencies.Input('gdp-pct', 'value')])
def update_world_chart(year, stat_type, include_usa, gdp_pct):
    map_stat = 'percent_GDP' if gdp_pct else 'USD_Value'
    map_legend = '% GDP' if gdp_pct else 'USD Value'
    arms_df_tmp = arms_gdp.copy()
    if not include_usa:
        arms_df_tmp.loc[arms_df_tmp['Country'] == 'USA', map_stat] = 0

    print(year, stat_type, include_usa, gdp_pct)
    chart = alt.Chart(world_map_skl).mark_geoshape(stroke='white').encode(
        color=alt.condition(alt.FieldEqualPredicate(field=map_stat, equal=0),
                            alt.value('lightgray'), map_stat + ':Q',
                            scale=alt.Scale(scheme='goldorange'),
                            legend=alt.Legend(title=map_legend)),
        tooltip=['Country:N', map_stat + ':Q']
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(arms_df_tmp.query("Year == " + str(year)).query("Direction == '%s'" % (stat_type)), 'id',
                             [map_stat, 'Country'])
    ).project('equirectangular').properties(
        width=720,
        height=300,
        background='white'
    ).configure_axis(
        grid=False
    )

    return html.Iframe(
        sandbox='allow-scripts',
        id='plot',
        width='900',
        height='350',
        style={'border-width': '0'},
        srcDoc=chart.to_html()
    )


#################################################
################## Helpers ######################
#################################################

def make_gdp_perc_chart(year=2018, stat_type='Export'):
    """
    Create a bar chart that shows Imports/Exports (Dynamic based on switch/callback) as a percentage of GDP
        in the year selected (based on year slider), and show the highest 15.
    
    Parameters
    -----------
    year: integer [1988, 2018]
        the year for which data is to be displayed - controlled by slider, default is 2018
    
    stat_type: string one of 'Import' or 'Export'
        determines whether this graph will show imports or exports as a percentage of GDP, 
        default is 'Export', and controlled by switch

    Returns
    -----------
    gdp_perc_chart: chart
        bar chart showing stat_type as a percentage of GDP for the specified year
    
    Example
    -----------
    >>> make_gdp_perc_chart(2017, 'Import')
    """
    countries = ['USA', 'Italy', 'Spain', 'Germany', 'Czech Rep.', 'Brazil', 'Norway',
                 'Switzerland', 'Turkey', 'Canada', 'Japan', 'Croatia', 'United Kingdom', 'France']

    # Wrangling specific to this chart:
    df_for_perc_of_gdp = arms_gdp[  # (arms_gdp['Country'].isin(countries)) &
        (arms_gdp['Year'] == year) &
        (arms_gdp['Direction'] == stat_type)].sort_values(by='percent_GDP', ascending=False).head(15)

    # df_for_perc_of_gdp['percent_GDP'] = df_for_perc_of_gdp['percent_GDP'] * 100

    # Make the chart:
    gdp_perc_chart = alt.Chart(df_for_perc_of_gdp).mark_bar().encode(
        alt.X('Country:N',
              sort=alt.EncodingSortField(field='percent_GDP',
                                         order='descending'),
              title='Country',
              axis=alt.Axis(labelAngle=45)),
        alt.Y('percent_GDP:Q',
              title='Arms Trade as a % of GDP',
              # scale=alt.Scale(domain=(0, (0.2 if stat_type == 'Import' else 0.5)))
              ),
        alt.Order(shorthand=['percent_GDP'], sort='descending'),
        alt.Tooltip(['Country', 'percent_GDP'])
    ).configure_bar(color='orange'
                    ).properties(width=920,
                                 height=230,
                                 background='white',
                                 title="Arms Trade as a Percentage of GDP for Major " + stat_type + "ers in %d" % (
                                     year))
    return gdp_perc_chart


def update_country_chart(stat_type, country, year):
    '''
    Creates two bar charts that show Imports/Exports (Dynamic based on switch/callback) as a percentage of GDP over time
    and Imports/Exports (Dynamic based on switch/callback) value in USD over time.

    Parameters
    -----------
    stat_type: string one of 'Import' or 'Export'
        determines whether this graph will show imports or exports as a percentage of GDP,
        default is 'Export', and controlled by switch

    Country: string
        the country for which data is to be displayed - controlled by drop down

    Returns
    -----------
    update_country_chart: chart
        two bar charts showing Imports/Exports as a percentage of GDP, and value USD over time

    Example
    -----------
    > make_gdp_perc_chart('Import', 'Germany')
    '''
    country_USD = (alt.Chart(arms_gdp.query(f'Direction == "{stat_type}" & Country == "{country}"')).mark_area().encode(
        alt.X('Year:O', title="Year"),
        alt.Y('USD_Value:Q', title="USD Value"),
    ) + alt.Chart(alt_country_ids.assign(intercept=year)).mark_rule(color='red').encode(
        alt.X('intercept:O')
    )).properties(title=f'{country} Weapons {stat_type} value in USD', width=375, height=250)

    country_gdp = (alt.Chart(arms_gdp.query(f'Direction == "{stat_type}" & Country == "{country}"')).mark_bar().encode(
        alt.X('Year:O', title="Year"),
        alt.Y('percent_GDP:Q', title="% of GDP"),
    ) + alt.Chart(alt_country_ids.assign(intercept=year)).mark_rule(color='red').encode(
        alt.X('intercept:O')
    )).properties(title=f'{country} Weapons {stat_type} share in GDP', width=375, height=250)

    return (country_gdp | country_USD).properties(background='white').configure_bar(color='orange').configure_area(
        color='orange')


# Run the app
server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)
