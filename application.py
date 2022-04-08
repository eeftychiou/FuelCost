import pandas as pd
import fueltools as ft
import preprocess as pp
import dash
from dash import dcc
from dash import html
from dash import dash_table
import plotly.graph_objects as go
import plotly.express as px


app = dash.Dash(__name__) #external_stylesheets=external_stylesheets)

app.title='Fit for 55 Impact on Air Transport'

pp.pre_process()

#dataYear = 2018

dataSetSelection = ft.getYears()
dataYear = max(dataSetSelection)
flights_df={}
for yearIn in dataSetSelection:
    flights_df[yearIn] = pp.loadDefaultDataset(year=yearIn)

    flights_df[yearIn] = ft.CalculateSAFCost(flights_df[yearIn])
    flights_df[yearIn] = ft.CalculateFuelCost(flights_df[yearIn])
    flights_df[yearIn] = ft.CalculateTotalFuelCost(flights_df[yearIn])
    flights_df[yearIn] = ft.CalculateTaxCost(flights_df[yearIn])
    flights_df[yearIn] = ft.CalculateETSCost(flights_df[yearIn])

    flights_df[yearIn]['TOTAL_COST'] = flights_df[yearIn]['SAF_COST'] + flights_df[yearIn]['TAX_COST'] + flights_df[yearIn]['ETS_COST']

regions_df = pd.read_excel('data/ICAOPrefix.xlsx')
#default from selection
fromSelection = regions_df.columns[2:].tolist()
defFromSelection = fromSelection[3]

finalDf=flights_df

dataSetPeriod = ft.getMonths()

fromSelDict = ft.get_dd_selection(fromSelection, DepOrDes='ADEP')
toSelDict = ft.get_dd_selection(fromSelection, DepOrDes='ADES')

groupByDict = [
    { 'label' : 'Country'   , 'value': 'ADEP_COUNTRY'},
    { 'label' : 'Aerodrome' , 'value': 'ADEP'},
    { 'label' : 'Airline'   , 'value': 'AC_Operator' },
    { 'label' : 'Country/Country Pair', 'value': "'ADEP_COUNTRY','ADES_COUNTRY'"}
]

marketSelection = flights_df[dataYear].STATFOR_Market_Segment.unique().tolist()

app.layout = html.Div([
    html.Div([
        html.H1(children='Analysis of the Fit for 55 legislative proposals on Air Transport'),

    html.Div([
        html.P('Connect with me on: '),
        html.A(
            html.Img(src='assets/images/linkedin.png', className='img'),
            href='https://www.linkedin.com/in/eftychios-eftychiou-88686843/'),
        html.A(
            html.Img(src='/assets/images/twitter.png', className='img'),
            href='https://twitter.com/EEftychiou'
        ),
        html.A(
            html.Img(src='/assets/images/github.png', className='img',
                     id='github'),
            href='https://github.com/eeftychiou'
        ),
        html.A(
            html.Img(src='/assets/images/gmail.png', className='img',
                     id='gmail'),
            href='mailto:eftychios.eftychiou@gmail.com'
        )

    ]), ],id='header-div'),

    html.Div([
        html.P('Uses Eurocontrol R&D Archive', style={"height": "auto", "margin-bottom": "auto"}),
        html.A("Wiki Page", href="https://github.com/eeftychiou/FuelCost/wiki/Fit55-Impact-Calculator", target="_blank")]),

        html.Div([
            html.P('Select dataset', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='DatasetSelection',
                options=[{'label': i, 'value': i} for i in dataSetSelection],
                value=dataYear, disabled=False, clearable = False
            ),
            html.P('Select Period', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='monthSelection', multi=True,
                options=[{'label': i, 'value': i} for i in dataSetPeriod],
                value=dataSetPeriod, disabled=True, clearable = False
            ),
            html.P('Select Departure Region', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='fromSelection',
                options=fromSelDict,
                value=fromSelDict[3]['value'], clearable = False
            ),
            html.P('Include Close outermost regions', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='outerCheck',
                options=[
                    {'label': 'Close Outermost Regions', 'value': 'OUTER_CLOSE'},
                    {'label': 'Outermost Regions', 'value': 'OUTERMOST_REGIONS'}

                ]
            ),
            html.P('Select Destination Region', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='toSelection',
                options=toSelDict,
                value=toSelDict[3]['value'], clearable = True
            ),
            html.P('Select Market Segment', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='marketSelection',
                options=[{'label': i, 'value': i} for i in marketSelection], multi=True,
                value=['Traditional Scheduled', 'Lowcost'], clearable = False),
            html.P('Select Grouping option', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='groupSelection',
                options=groupByDict, multi=False,
                value='ADEP_COUNTRY', clearable=False),

            html.Div([
                html.Div([html.P('SAF Price(USD/kg)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="safPrice", type="number", placeholder=3.66, value=3.66, min=0, debounce=True), ]),
                html.Div([html.P('JetA1 Price(USD/kg)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="jetPrice", type="number", placeholder=0.81, value=0.81,min=0, debounce=True ), ]),
                html.Div([html.P('Blending (%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="blendingMandate", type="number", placeholder=2, min=0, max=100, step=0.1, value=2,debounce=True ), ]),
                html.Div([html.P('Tax rate(EURO/GJ)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="taxRate", type="number", placeholder=2.15, min=0, max=10.75, value=2.15,debounce=True ), ]),
                html.Div([html.P('ETS Price(EURO/tn) ', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="emissionsPrice", type="number", placeholder=80, min=0, max=1000, value=80,debounce=True ), ]),
                html.Div([html.P('Emissions (%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="emissionsPercent", type="number", placeholder=55, min=0, max=100, step=1, value=55, debounce=True), ]),
                html.Div([html.P('Projection Year', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="yearGDP", type="number", placeholder=2025, min=2021, max=2080, step=1, value=2025,debounce=True ), ]),
                html.Div([html.P('GDP Growth(%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="gdpGrowth", type="number", placeholder=1.09, min=-20, max=20, value=1.09, debounce=True),
                dcc.Checklist(id="extrapolateRet", options=[{'label': 'Extrapolate Return Leg', 'value': 'Yes'}], value=['Yes']),]),
                html.Div([html.P('Flight Growth(%)', style={"height": "auto", "margin-bottom": "auto",}),
                          dcc.Input(id="flightGrowth", type="number", placeholder=1.9, min=-20, max=20, value=1.9, debounce=True), ]),
                html.Div([html.P('Emissions Growth(%)', style={"height": "auto", "margin-bottom": "auto"}),
                          dcc.Input(id="emGrowth", type="number", placeholder=1, min=-20, max=20, value=1.0, debounce=True), ]),

            ], style=dict(display='flex', flexWrap='wrap', width='auto')),

            html.P([]),
            html.Div([html.Button('Submit', style={"height": "auto", "margin-bottom": "20", "margin-top": "20"},
                                  id='submitButton'), ]),

        ],
            style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(id='SelectedOptions', multi=True, clearable=False,searchable=True),
            dcc.Graph(
                id='Cost_graph',
            ),

            dcc.Graph(
                id='Gdp_graph',

            ),
            dcc.Graph(
                id='HeatMap_graph'
            ),
            dcc.Store(id='ds_cost'),
            dcc.Store(id='ds_gdp'),
            dcc.Store(id='ds_heatmap'),

            html.P('Cost Breakdown', style={"height": "auto", "margin-bottom": "auto"}),
            dash_table.DataTable(
                id='table',
                data=None,
                columns=None,
                editable=False,
                filter_action="native",
                sort_action="native",
                sort_mode="single",
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=100,
                export_format= 'csv'
            ),

            html.P('GDP Breakdown', style={"height": "auto", "margin-bottom": "auto"}),
            dash_table.DataTable(
                id='gdptable',
                data=None,
                columns=None,
                editable=False,
                filter_action="native",
                sort_action="native",
                sort_mode="single",
                row_deletable=False,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=100,
                export_format='csv'
            ),

            html.Div(id='datatable-interactivity-container')
        ], style={'width': '79%', 'float': 'right', 'display': 'inline-block'}),
    # signal value to trigger callbacks
    dcc.Store(id='signal')
    ], style={'padding': '10px 5px'}

)

application = app.server

@app.callback(
    [dash.dependencies.Output('SelectedOptions', 'options'),
     dash.dependencies.Output('SelectedOptions', 'value'),
     dash.dependencies.Output('ds_cost', 'data'),
     dash.dependencies.Output('ds_gdp', 'data'),
     dash.dependencies.Output('ds_heatmap', 'data')
     ],
    [dash.dependencies.State('monthSelection', 'value'),
     dash.dependencies.State('fromSelection', 'value'),
     dash.dependencies.State('toSelection', 'value'),
     dash.dependencies.State('marketSelection', 'value'),
     dash.dependencies.State('safPrice', 'value'),
     dash.dependencies.State('blendingMandate', 'value'),
     dash.dependencies.State('jetPrice', 'value'),
     dash.dependencies.State('taxRate', "value"),
     dash.dependencies.State('emissionsPercent', 'value'),
     dash.dependencies.State('emissionsPrice', 'value'),
     dash.dependencies.State('outerCheck', 'value'),
     dash.dependencies.State('DatasetSelection', 'value'),
     dash.dependencies.State('groupSelection', 'value'),
     dash.dependencies.State('yearGDP', 'value'),
     dash.dependencies.State('gdpGrowth' ,'value'),
     dash.dependencies.Input('submitButton', 'n_clicks'),
     dash.dependencies.State('extrapolateRet', 'value'),
     dash.dependencies.State('flightGrowth', 'value'),
     dash.dependencies.State('emGrowth', 'value')
     ])
def calculate_costs(monthSel, fromSel, toSel, market, safPrice, blending, jetPrice, taxRate,
                 emissionsPercent, emissionsPrice, outerCheck, yearSelected, groupSel,
                 yearGDP, gdpGrowth, nclicks, extrapolateRet, flightGrowth, emissionsGrowth):

    flights_df = finalDf[yearSelected]
    flights_df = ft.CalculateSAFCost(flights_df, costOfSafFuelPerKg = safPrice, safBlendingMandate = blending/100 )
    flights_df = ft.CalculateFuelCost(flights_df, costOfJetFuelPerKg = jetPrice, safBlendingMandate = blending/100)
    flights_df = ft.CalculateTotalFuelCost(flights_df)
    flights_df = ft.CalculateTaxCost(flights_df, FuelTaxRateEurosPerGJ = taxRate, blendingMandate=blending/100 )
    flights_df = ft.CalculateETSCost(flights_df, safBlendingMandate=blending/100, ETSCostpertonne = emissionsPrice, ETSpercentage = emissionsPercent )

    flights_df['TOTAL_COST'] = flights_df['SAF_COST'] + flights_df['TAX_COST'] + flights_df['ETS_COST']

    #Build 1st level query based on input values
    if outerCheck=='OUTER_CLOSE':
        fromQuery = '(' + fromSel + ' | ' + '(ADEP_OUTER_CLOSE=="Y"))'
        toQuery = toSel
    elif outerCheck=='OUTERMOST_REGIONS':
        fromQuery = '(' + fromSel + ' | ' + '(ADEP_OUTERMOST_REGIONS=="Y"))'
        toQuery   = toSel
    else:
        fromQuery =  fromSel
        toQuery   = toSel

    if toSel:
        dfquery =  fromQuery  + ' & ' + toQuery + ' & ' 'not ((ADEP_OUTERMOST_REGIONS == "Y"  &  ADES_OUTERMOST_REGIONS == "Y" ))' + ' & ' + \
                  'STATFOR_Market_Segment in @market'
    else:
        dfquery = fromQuery + ' & ' 'not ((ADEP_OUTERMOST_REGIONS == "Y"  &  ADES_OUTERMOST_REGIONS == "Y" ))' + ' & ' + \
                  'STATFOR_Market_Segment in @market'

    #1st Level query ADEP/ADES filter
    flights_filtered_df = flights_df.query(dfquery)

    startSummerIATA, endSummerIATA = ft.getIATASeasons(yearSelected)

    dfRatio= ft.getDFRatio(set(monthSel))

    heatmap_df  = ft.calculatePairs(dfRatio, endSummerIATA, groupSel, flights_filtered_df, startSummerIATA)

    # Calculate the aggregates per IATA season basis
    # Summer
    per_group_summer = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
        .groupby([groupSel])[['ECTRL_ID','Actual_Distance_Flown','FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size','Actual_Distance_Flown' : ['mean', 'std', 'sum'] , 'FUEL':'sum', 'EMISSIONS':'sum', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
              'TOTAL_FUEL_COST': ['mean', 'std','sum'], 'TAX_COST': ['mean', 'std','sum'], 'ETS_COST': ['mean', 'std','sum'], 'TOTAL_COST': ['mean', 'std','sum']})
    per_group_summer_quantiles = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
        .groupby([groupSel])[['SAF_COST', 'TAX_COST', 'ETS_COST']] \
        .describe().filter(like='%')
    per_group_summer = pd.concat([per_group_summer, per_group_summer_quantiles], axis=1)

    # Winter
    per_group_winter = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
        .groupby([groupSel])[['ECTRL_ID','Actual_Distance_Flown','FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size','Actual_Distance_Flown' : ['mean', 'std', 'sum'] ,'FUEL':'sum', 'EMISSIONS':'sum', 'SAF_COST': ['mean', 'std','sum'], 'FUEL_COST': ['mean', 'std','sum'],
              'TOTAL_FUEL_COST': ['mean', 'std','sum'], 'TAX_COST': ['mean', 'std','sum'], 'ETS_COST': ['mean', 'std','sum'], 'TOTAL_COST': ['mean', 'std','sum']})
    per_group_winter_quantiles = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
        .groupby([groupSel])[['SAF_COST', 'TAX_COST', 'ETS_COST']] \
        .describe().filter(like='%')
    per_group_winter = pd.concat([per_group_winter, per_group_winter_quantiles], axis=1)

    #Extrapolate each season, summer and winter, according to the determined ration of the dataset
    per_group_summer.columns = ["_".join(a) for a in per_group_summer.columns.to_flat_index()]
    per_group_winter.columns = ["_".join(a) for a in per_group_winter.columns.to_flat_index()]

    #exclude statistical components which cannot be extrapolated
    per_group_summer.loc[:, ~per_group_summer.columns.str.contains('mean|std|%')] = per_group_summer.loc[:, ~per_group_summer.columns.str.contains('mean|std|%')] / dfRatio[0]
    per_group_winter.loc[:, ~per_group_winter.columns.str.contains('mean|std|%')] = per_group_winter.loc[:, ~per_group_winter.columns.str.contains('mean|std|%')] / dfRatio[1]

    per_group_annual = ((per_group_summer * 7) + (per_group_winter * 5))

    per_group_annual.loc[:, per_group_annual.columns.str.contains('mean|std|%')] = per_group_annual.loc[:, per_group_annual.columns.str.contains('mean|std|%')] / 12


    #Calculate from selected region averages, eg EU_EEA_EFTA
    sel_avg_quantiles_sum = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['Actual_Distance_Flown', 'FUEL', 'EMISSIONS','SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].describe()
    sel_avg_sum_sum = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['Actual_Distance_Flown','FUEL', 'EMISSIONS','SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].sum().reset_index(name='sum')

    selected_summer = sel_avg_quantiles_sum.T
    selected_summer['sum'] = (sel_avg_sum_sum.loc[:, 'sum']/dfRatio[0]).tolist()

    sel_avg_quantiles_win = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)][['Actual_Distance_Flown','FUEL','EMISSIONS','SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].describe()
    sel_avg_sum_win = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)][['Actual_Distance_Flown','FUEL','EMISSIONS','SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'TOTAL_COST']].sum().reset_index(name='sum')

    selected_winter = sel_avg_quantiles_win.T
    selected_winter['sum'] = (sel_avg_sum_win.loc[:, 'sum']/dfRatio[1]).tolist()

    sel_ms_Annual = ((selected_summer * 7) + (selected_winter * 5))
    sel_ms_Annual = sel_ms_Annual.drop(columns=['min', 'max'])

    sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')] = sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')] / 12

    fromSelected = [k['label'] for k in fromSelDict if k['value'] == fromSel][0]

    # add record of selected region to dataframe
    per_group_annual.loc[fromSelected] = (int(sel_ms_Annual.loc['SAF_COST', 'count']),
                                               sel_ms_Annual.loc['Actual_Distance_Flown', 'mean'],
                                               sel_ms_Annual.loc['Actual_Distance_Flown', 'std'],
                                               sel_ms_Annual.loc['Actual_Distance_Flown', 'sum'],
                                               sel_ms_Annual.loc['FUEL', 'sum'] ,
                                               sel_ms_Annual.loc['EMISSIONS', 'sum'],
                                               sel_ms_Annual.loc['SAF_COST', 'mean'],
                                               sel_ms_Annual.loc['SAF_COST', 'std'],
                                               sel_ms_Annual.loc['SAF_COST', 'sum'],
                                               sel_ms_Annual.loc['FUEL_COST', 'mean'],
                                               sel_ms_Annual.loc['FUEL_COST', 'std'],
                                               sel_ms_Annual.loc['FUEL_COST', 'sum'],
                                               sel_ms_Annual.loc['TOTAL_FUEL_COST', 'mean'],
                                               sel_ms_Annual.loc['TOTAL_FUEL_COST', 'std'],
                                               sel_ms_Annual.loc['TOTAL_FUEL_COST', 'sum'],
                                               sel_ms_Annual.loc['TAX_COST', 'mean'],
                                               sel_ms_Annual.loc['TAX_COST', 'std'],
                                               sel_ms_Annual.loc['TAX_COST', 'sum'],
                                               sel_ms_Annual.loc['ETS_COST', 'mean'],
                                               sel_ms_Annual.loc['ETS_COST', 'std'],
                                               sel_ms_Annual.loc['ETS_COST', 'sum'],
                                               sel_ms_Annual.loc['TOTAL_COST', 'mean'],
                                               sel_ms_Annual.loc['TOTAL_COST', 'std'],
                                               sel_ms_Annual.loc['TOTAL_COST', 'sum'],
                                               sel_ms_Annual.loc['SAF_COST', '25%'],
                                               sel_ms_Annual.loc['SAF_COST', '50%'],
                                               sel_ms_Annual.loc['SAF_COST', '75%'],

                                               sel_ms_Annual.loc['TAX_COST', '25%'],
                                               sel_ms_Annual.loc['TAX_COST', '50%'],
                                               sel_ms_Annual.loc['TAX_COST', '75%'],

                                               sel_ms_Annual.loc['ETS_COST', '25%',],
                                               sel_ms_Annual.loc['ETS_COST', '50%',],
                                               sel_ms_Annual.loc['ETS_COST', '75%',]
                                               )

    app = dash.Dash(__name__)
    per_group_annual=per_group_annual.dropna()

    per_group_annual = ft.foldInOutermostWithMS(groupSel, outerCheck, per_group_annual)

    gdpPerCountry = pd.read_csv('data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_2916952.csv', usecols=['COUNTRY', '2016', '2017', '2018', '2019', '2020'], index_col='COUNTRY')

    #calculate GDP Growth
    gdpPerCountry[yearGDP] = gdpPerCountry['2020'] * (1+ gdpGrowth/100)**(yearGDP-2020)

    #Calculate Flight Growth. Use 2024 as the baseline which is the estimate time traffic will return to prepandemic levels
    if yearGDP>2024:
        per_group_annual.loc[:,~per_group_annual.columns.str.contains('mean|std|%|COUNTRY|EMISSIONS|Actual')] = per_group_annual.loc[:,~per_group_annual.columns.str.contains('mean|std|%|COUNTRY|EMISSIONS|Actual')] * (1+ flightGrowth/100)**(yearGDP-2024)

    #Calculate Emissions Growth
    per_group_annual['EMISSIONS_sum'] = per_group_annual["EMISSIONS_sum"] * (1+ emissionsGrowth/100)**(yearGDP-2024)

    per_group_annual['EMISSIONS_Percent'] = per_group_annual['EMISSIONS_sum'] / per_group_annual.loc[fromSelected,'EMISSIONS_sum'] * 100



    per_group_annual = per_group_annual.reset_index()
    per_group_annual = per_group_annual.sort_values(by=['SAF_COST_mean'], ascending=False)
    per_group_annual = per_group_annual.round(2)
    per_group_annual['ECTRL_ID_size'] = per_group_annual['ECTRL_ID_size'].astype(int)
    per_group_annual = per_group_annual.rename(columns={'ECTRL_ID_size': 'Flights_size'})


    #Calculate GDP groups
    if groupSel == 'ADEP_COUNTRY':
        countryList = regions_df.query(fromSel.replace('ADEP_', '')).loc[:, 'COUNTRY'].tolist()
        rowLoc = fromSel.replace('(ADEP_', '').replace('=="Y")', '')

        fromSelected = [k['label'] for k in fromSelDict if k['value'] == fromSel][0]

        gdpPerCountry.loc[fromSelected] = gdpPerCountry[gdpPerCountry.index.isin(countryList)].sum().tolist()
        per_group_annual_gdp = per_group_annual.join(gdpPerCountry, on='ADEP_COUNTRY', how='inner')

        if 'Yes' in extrapolateRet:
            retMult = 2
        else:
            retMult = 1

        per_group_annual_gdp['TOTAL_GDP_RATIO'] = (per_group_annual_gdp['TOTAL_COST_sum']*retMult / per_group_annual_gdp[yearGDP]) * 100
        per_group_annual_gdp['SAF_GDP_RATIO'] = (per_group_annual_gdp['SAF_COST_sum']*retMult / per_group_annual_gdp[yearGDP]) * 100
        per_group_annual_gdp['ETS_GDP_RATIO'] = (per_group_annual_gdp['ETS_COST_sum']*retMult / per_group_annual_gdp[yearGDP]) * 100
        per_group_annual_gdp['TAX_GDP_RATIO'] = (per_group_annual_gdp['TAX_COST_sum']*retMult / per_group_annual_gdp[yearGDP]) * 100
    elif groupSel == 'ADEP':
        # TODO calculate the overall traffic for airport and determine the traffic affected by the measures vs not affected
        pass
    elif groupSel == 'AC_Operator':
        #TODO for AC operator comparison. Calculate ratio of whole operations
        pass
    elif groupSel[0] == 'ADEP_COUNTRY' and groupSel[1] == 'ADES_COUNTRY':
        #TODO GDP for Country Country Pair
        pass
    else:
        raise ValueError('Undefined Grouping')

    if heatmap_df is None:
        heatmap_df = pd.DataFrame()

    ds_heatmap = heatmap_df.to_json(date_format='iso', orient='split')
    ds_cost = per_group_annual.to_json(date_format='iso', orient='split')
    ds_gdp = per_group_annual_gdp.to_json(date_format='iso', orient='split')


    #return options
    rowNames = per_group_annual['ADEP_COUNTRY'].tolist()
    Seloptions =[{'label': i, 'value': i} for i in rowNames]
    Selvalue = [x['value'] for x in Seloptions][:50]

    return Seloptions, Selvalue,ds_cost,ds_gdp, ds_heatmap



def update_per_airport(fromSel, gdpPerCountry, groupSel, cost_df, airportPairsTotal):

    data = [
        go.Bar(name='SAF',
               x=cost_df[groupSel],
               y=cost_df['SAF_COST_mean'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='TAX',
               x=cost_df[groupSel],
               y=cost_df['TAX_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='ETS',
               x=cost_df[groupSel],
               y=cost_df['ETS_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='JET A1',
               x=cost_df[groupSel],
               y=cost_df['FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='Total Fuel Cost',
               x=cost_df[groupSel],
               y=cost_df['TOTAL_FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=0.0,
               base=0
               ),
        go.Bar(name='Total Cost of Measures',
               x=cost_df[groupSel],
               y=cost_df['TOTAL_COST_mean'], visible='legendonly',
               base=0,
               width=0.3,
               offset=0.3
               )
    ]
    layout = go.Layout(
        barmode='stack',
        title='Average Cost per flight of Fit For 55 Proposals'
    )
    fig = go.Figure(data=data, layout=layout)
    fig.update_yaxes(title_text='USD per Flight')

    #update table
    _col=[{"name": i, "id": i} for i in cost_df.columns]
    datatab=cost_df.to_dict('records')


    #update heatmap
    rowNames = airportPairsTotal.index.tolist()

    figPairs = px.imshow(airportPairsTotal, labels=dict(x="Destination Airport",  y='Departure Airport', color='Number of Flights'))
    heatSelOptions =[{'label': i, 'value': i} for i in rowNames]
    heatSelValue = [x['value'] for x in heatSelOptions][:10]

    return fig, go.Figure(data=[go.Scatter(x=[], y=[])]), go.Figure(data=[go.Scatter(x=[], y=[])]), datatab, _col

def update_per_operator(fromSel, gdpPerCountry, groupSel, per_ms_Annual_out):
    data = [
        go.Bar(name='SAF',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['SAF_COST_mean'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='TAX',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TAX_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='ETS',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['ETS_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='JET A1',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='Total Fuel Cost',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TOTAL_FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=0.0,
               base=0
               ),
        go.Bar(name='Total Cost of Measures',
               x=per_ms_Annual_out[groupSel],
               y=per_ms_Annual_out['TOTAL_COST_mean'], visible='legendonly',
               base=0,
               width=0.3,
               offset=0.3
               )
    ]
    layout = go.Layout(
        barmode='stack',
        title='Average Cost per flight of Fit For 55 Proposals'
    )
    fig = go.Figure(data=data, layout=layout)
    fig.update_yaxes(title_text='USD per Flight')

    #update table
    _col=[{"name": i, "id": i} for i in per_ms_Annual_out.columns]
    datatab=per_ms_Annual_out.to_dict('records')

    return fig, go.Figure(data=[go.Scatter(x=[], y=[])]),go.Figure(data=[go.Scatter(x=[], y=[])]), datatab, _col

def update_per_ms(SelectedOptions, gdp_df, groupSel, cost_df,  heatmap_df):

    data = [
        go.Bar(name='SAF',
               x=cost_df[groupSel],
               y=cost_df['SAF_COST_mean'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='TAX',
               x=cost_df[groupSel],
               y=cost_df['TAX_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='ETS',
               x=cost_df[groupSel],
               y=cost_df['ETS_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='JET A1',
               x=cost_df[groupSel],
               y=cost_df['FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='Total Fuel Cost',
               x=cost_df[groupSel],
               y=cost_df['TOTAL_FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=0.0,
               base=0
               ),
        go.Bar(name='Total Cost of Measures',
               x=cost_df[groupSel],
               y=cost_df['TOTAL_COST_mean'], visible='legendonly',
               base=0,
               width=0.3,
               offset=0.3
               )
    ]
    layout = go.Layout(
        barmode='stack',
        title='Average Cost per flight of Fit For 55 Proposals'
    )
    fig = go.Figure(data=data, layout=layout)
    fig.update_yaxes(title_text='USD per Flight')

    gdp_df = gdp_df.sort_values(by=['TOTAL_GDP_RATIO'], ascending=False)

    dataGDP = [
        go.Bar(name='SAF',
               x=gdp_df['ADEP_COUNTRY'],
               y=gdp_df['SAF_GDP_RATIO'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.4,
               offset=-0.4,
               offsetgroup=1,
               yaxis='y1'
               ),
        go.Bar(name='TAX',
               x=gdp_df['ADEP_COUNTRY'],
               y=gdp_df['TAX_GDP_RATIO'],
               width=0.4,
               offset=-0.4,
               offsetgroup=1,
               yaxis='y1'
               ),
        go.Bar(name='ETS',
               x=gdp_df['ADEP_COUNTRY'],
               y=gdp_df['ETS_GDP_RATIO'],
               width=0.4,
               offset=-0.4,
               offsetgroup=1,
               yaxis='y1'
               ),
        go.Bar(name='Total GDP Ratio of Measures',
               x=gdp_df['ADEP_COUNTRY'],
               y=gdp_df['TOTAL_GDP_RATIO'], visible='legendonly',
               width=0.4,
               offset=0.0,
               base=0,
               offsetgroup=1,
               yaxis = 'y1'
               ),
        go.Scatter(name='Percent of total Emissions',
                   x=gdp_df['ADEP_COUNTRY'],
                   y=gdp_df['EMISSIONS_Percent'],
                   yaxis='y2',
                   mode= 'lines+markers',
                   )
    ]


    layout = go.Layout(title='Impact on GDP and Emissions contribution per Country',
                       yaxis=dict(title='Burden on GDP(%)'),
                       yaxis2=dict(title='Percent of total Emissions',
                                   overlaying='y',
                                   side='right',
                                   range =[0,20]),
                       barmode='stack',
                       legend = dict(yanchor="top", y=0.99, xanchor="right",x=1.21)
    )


    figGDP= go.Figure(data=dataGDP, layout= layout)


    #update table
    _col=[{"name": i, "id": i} for i in cost_df.columns]
    datatab=cost_df.to_dict('records')

    #update heatmap
    rowNames = heatmap_df.index.tolist()
    colNames = heatmap_df.columns.tolist()
    for rowName in rowNames:
        if rowName in colNames:
            heatmap_df.loc[rowName, rowName] = 0

    figPairs = px.imshow(heatmap_df, labels=dict(x="Destination Country",  y='Departure Country', color='Number of Flights'))
    heatSelOptions =[{'label': i, 'value': i} for i in rowNames]
    heatSelValue = [x['value'] for x in heatSelOptions][:10]

    return fig, figGDP,figPairs, datatab, _col

@app.callback(
    dash.dependencies.Output("Cost_graph", "figure"),
    dash.dependencies.Output("Gdp_graph", "figure"),
    dash.dependencies.Output("HeatMap_graph", "figure"),
    dash.dependencies.Output('table', 'data'),
    dash.dependencies.Output('table', 'columns'),
    [dash.dependencies.Input("SelectedOptions", "value"),
     dash.dependencies.State('ds_cost', 'data'),
     dash.dependencies.State('ds_gdp', 'data'),
     dash.dependencies.State('ds_heatmap', 'data'),
     dash.dependencies.State('groupSelection', 'value')])
def update_graphs(SelectedOptions, ds_cost,ds_gdp, ds_heatmap, groupSelection):
    if ds_cost is None or groupSelection=='AC_Operator':
        return go.Figure(data=[go.Scatter(x=[], y=[])])


    cost_df = pd.read_json(ds_cost, orient='split')
    gdp_df = pd.read_json(ds_gdp,orient='split')
    heatmap_df = pd.read_json(ds_heatmap, orient = 'split')

    if cost_df.empty is True or heatmap_df.empty is True:
        fig= go.Figure(data=[go.Scatter(x=[], y=[])])
        return fig,fig,fig

    if groupSelection=='ADEP_COUNTRY':
        figCost, figGDP, figHeat, tab,_cols = update_per_ms(SelectedOptions, gdp_df, groupSelection, cost_df, heatmap_df)
    elif groupSelection=='ADEP':
        figCost, figGDP, figHeat, tab,_cols = update_per_airport(SelectedOptions, gdp_df, groupSelection, cost_df, heatmap_df)
    elif groupSelection == 'AC_Operator':
        figCost, figGDP, figHeat, tab,_cols = update_per_operator(SelectedOptions, gdp_df, groupSelection, cost_df, heatmap_df)
    else:
        fig, figGDP , tab, figpairs = None,None, None, None

    # colset=set(cols)
    # dffcols = set(dff.columns)
    # finalCols = list(colset.intersection(dffcols))
    # newdf = dff.loc[cols,finalCols]
    # newdf = newdf.dropna(axis=1)
    # fig = px.imshow(newdf, labels=dict(x="Destination Country/Airport",  y='Departure Country/Airport', color='Number of Flights'))


    return figCost, figGDP, figHeat, tab,_cols






app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-7SVRF3W4H8"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'G-7SVRF3W4H8');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta property="og:type" content="article">
        <meta property="og:title" content="Air Transport Fit55 Dashboard"">
        <meta property="og:site_name" content="http://fit55.cyatcu.org">
        <meta property="og:url" content="http://fit55.cyatcu.org">
        <meta property="article:published_time" content="2020-11-01">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

if __name__ == '__main__':
   app.run_server(debug=True)
   #application.run()
