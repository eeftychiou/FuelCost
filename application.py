import json

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


dataSetSelection = ft.getYears()
dataYear = max(dataSetSelection)
flights_df={}
for yearIn in dataSetSelection:
    flights_df[yearIn] = pp.loadDefaultDataset(year=yearIn)

regions_df = pd.read_excel('data/ICAOPrefix.xlsx')

#default from selection

fromSelection = regions_df.columns[6:].tolist()
defFromSelection = fromSelection[3]

finalDf=flights_df

dataSetPeriod = ft.getMonths()

fromSelDict = ft.get_dd_selection(fromSelection, DepOrDes='ADEP')
toSelDict = ft.get_dd_selection(fromSelection, DepOrDes='ADES')

groupByDict = [
    { 'label' : 'Country'   , 'value': 'ADEP_COUNTRY'},
    { 'label' : 'Aerodrome' , 'value': 'ADEP'},
    { 'label' : 'Airline'   , 'value': 'AC_Operator' },
    { 'label' : 'Country/Country Pair', 'value': 'ADEP_COUNTRY_PAIR'}
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
                id='fromSelection', multi=True,
                options=fromSelDict,
                value=[fromSelDict[3]['value']], clearable = False
            ),
            html.P('Enter additional comma delimited Departure Country codes', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Input(id="fromSelAdd", type="text", placeholder='', value='', debounce=True),

            html.P('Select Destination Region', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(
                id='toSelection',
                options=toSelDict,multi=True,
                value=[toSelDict[3]['value']], clearable = True
            ),
            html.P('Enter additional comma delimited Destination Country codes', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Input(id="toSelAdd", type="text", placeholder='', value='', debounce=True),

            html.P('Enter Custom Criteria, Field to update and Value', style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Input(id="custCriteria", type="text", placeholder='', value='', debounce=True),
            dcc.Input(id="custField", type="text", placeholder='', value='', debounce=True),
            dcc.Input(id="custValue", type="text", placeholder='', value='', debounce=True),

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
            dcc.Tabs([
            dcc.Tab(label='Results', children=[
            html.P(id = "option1text",children=["From Country"] , style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(id='SelectedOptions', multi=True, clearable=False,searchable=True),
            html.P(id = "option2text",children=["To Country"], style={"height": "auto", "margin-bottom": "auto"}),
            dcc.Dropdown(id='CompareOption', multi=False, clearable=False, searchable=True,  disabled= True),
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
                ]),
                dcc.Tab(label='Country Settings', children=[
                    dcc.Graph(
                        figure={
                            'data': [
                                {'x': [1, 2, 3], 'y': [2, 4, 3],
                                 'type': 'bar', 'name': 'SF'},
                                {'x': [1, 2, 3], 'y': [5, 4, 3],
                                 'type': 'bar', 'name': u'Montréal'},
                            ]
                        }
                    )
                ]),
            ]),
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
     dash.dependencies.Output('ds_heatmap', 'data'),
     dash.dependencies.Output('CompareOption', 'options'),
     dash.dependencies.Output('CompareOption', 'value'),
     dash.dependencies.Output('CompareOption', 'disabled' )
     ],
    [dash.dependencies.State('monthSelection', 'value'),
     dash.dependencies.State('fromSelection', 'value'),
     dash.dependencies.State('fromSelAdd', 'value'),
     dash.dependencies.State('toSelection', 'value'),
     dash.dependencies.State('toSelAdd', 'value'),
     dash.dependencies.State('marketSelection', 'value'),
     dash.dependencies.State('safPrice', 'value'),
     dash.dependencies.State('blendingMandate', 'value'),
     dash.dependencies.State('jetPrice', 'value'),
     dash.dependencies.State('taxRate', "value"),
     dash.dependencies.State('emissionsPercent', 'value'),
     dash.dependencies.State('emissionsPrice', 'value'),
     dash.dependencies.State('DatasetSelection', 'value'),
     dash.dependencies.State('groupSelection', 'value'),
     dash.dependencies.State('yearGDP', 'value'),
     dash.dependencies.State('gdpGrowth' ,'value'),
     dash.dependencies.Input('submitButton', 'n_clicks'),
     dash.dependencies.State('extrapolateRet', 'value'),
     dash.dependencies.State('flightGrowth', 'value'),
     dash.dependencies.State('emGrowth', 'value'),
     dash.dependencies.State('custCriteria', 'value'),
     dash.dependencies.State('custField', 'value'),
     dash.dependencies.State('custValue', 'value')

     ])
def calculate_costs(monthSel, fromSel,fromSelAdd, toSel,toSelAdd, market, safPrice, blending, jetPrice, taxRate,
                 emissionsPercent, emissionsPrice, yearSelected, groupSel,
                 yearGDP, gdpGrowth, nclicks, extrapolateRet, flightGrowth, emissionsGrowth, custCriteria, custField, custValue):


    if fromSelAdd:
        fromSelAdd=fromSelAdd.split(',')
        for i,addRegion in enumerate(fromSelAdd):
            if addRegion[0]!='!':
                fromSelAdd[i] = 'ADEP_PREFIX =="' + addRegion + '"'
            elif addRegion[0] =='!':
                fromSelAdd[i] = 'ADEP_PREFIX !="' + addRegion[1:] + '"'
            else:
                raise ValueError('Malformed country include clause')

        fromQuery = '(' + ' | '.join(fromSel) + ' | ' + ' | '.join(fromSelAdd) + ')'
    else:
        fromQuery = '(' + ' | '.join(fromSel) + ')'


    if toSelAdd:
        toSelAdd = toSelAdd.split(',')
        for i, addRegion in enumerate(toSelAdd):
            if addRegion[0] !='!':
                toSelAdd[i] = 'ADES_PREFIX =="' + addRegion + '"'
            elif addRegion[0] =='!':
                toSelAdd[i] = 'ADES_PREFIX !="' + addRegion[1:] + '"'
            else:
                raise ValueError('Malformed country include clause')

        toQuery = '(' + ' | '.join(toSel) + ' | ' + ' | '.join(toSelAdd) + ')'
    else:
        toQuery = '(' + ' | '.join(toSel) + ')'


    # Add market region to queries
    # fromQuery = fromQuery + ' & ' + 'STATFOR_Market_Segment in @market'
    # toQuery = toQuery + ' & ' + 'STATFOR_Market_Segment in @market'

    # #Build 1st subset level query based on input values
    # if outerCheck=='OUTER_CLOSE':
    #     fromQuery = '(' + fromSel + ' | ' + '(ADEP_OUTER_CLOSE=="Y"))'
    #     toQuery = toSel
    # elif outerCheck=='OUTERMOST_REGIONS':
    #     fromQuery = '(' + fromSel + ' | ' + '(ADEP_OUTERMOST_REGIONS=="Y"))'
    #     toQuery   = toSel
    # else:
    #     fromQuery =  fromSel
    #     toQuery   = toSel

    if toSel:
        dfquery =  fromQuery  + ' & ' + toQuery #+ ' & ' 'not ((ADEP_OUTERMOST_REGIONS == "Y"  &  ADES_OUTERMOST_REGIONS == "Y" ))' #+ ' & '  + 'STATFOR_Market_Segment in @market'
        allFlightsQuery = '(' + fromQuery + ' | ' + toQuery + ')' + ' & ' + 'STATFOR_Market_Segment in @market'
    else:
        dfquery = fromQuery #+ ' & ' 'not ((ADEP_OUTERMOST_REGIONS == "Y"  &  ADES_OUTERMOST_REGIONS == "Y" ))'  #+ ' & ' + 'STATFOR_Market_Segment in @market'
        allFlightsQuery = fromQuery + ' & ' + 'STATFOR_Market_Segment in @market'


    if 'OUTER_CLOSE' in fromSel:
        outerCheck='OUTER_CLOSE'
    else:
        outerCheck=''

    #1st Level query ADEP/ADES filter
    # market segment filtered already in all_flights_df
    all_flights_df = finalDf[yearSelected].query(allFlightsQuery)
    all_flights_df = ft.CalculateSAFCost(all_flights_df, costOfSafFuelPerKg = safPrice, safBlendingMandate = blending/100, subSet=dfquery)
    all_flights_df = ft.CalculateFuelCost(all_flights_df, costOfJetFuelPerKg = jetPrice, safBlendingMandate = blending/100, subSet=dfquery)
    all_flights_df = ft.CalculateTotalFuelCost(all_flights_df)
    all_flights_df = ft.CalculateTaxCost(all_flights_df, FuelTaxRateEurosPerGJ = taxRate, blendingMandate=blending/100, subSet=dfquery )
    all_flights_df = ft.CalculateETSCost(all_flights_df, safBlendingMandate=blending/100, ETSCostpertonne = emissionsPrice, ETSpercentage = emissionsPercent, subSet=dfquery )

    all_flights_df['FIT55_COST'] = all_flights_df['SAF_COST'] + all_flights_df['TAX_COST'] + all_flights_df['ETS_COST']
    all_flights_df['TOTAL_COST'] = all_flights_df['SAF_COST'] + all_flights_df['TAX_COST'] + all_flights_df['ETS_COST'] + all_flights_df['FUEL_COST']

    all_flights_df = ft.calculateCustom(all_flights_df, custCriteria, custField, custValue)

    flights_filtered_df = all_flights_df.query(dfquery)

    startSummerIATA, endSummerIATA = ft.getIATASeasons(yearSelected)

    dfRatio= ft.getDFRatio(set(monthSel))

    heatmap_df  = ft.calculatePairs(dfRatio, endSummerIATA, groupSel, flights_filtered_df, startSummerIATA)

    #fromSelected = [k['label'] for k in fromSelDict if k['value'] == fromSel][0]
    if groupSel == 'ADEP_COUNTRY':
        per_group_annual = ft.Newcalculate_group_aggregates(dfRatio, emissionsGrowth, endSummerIATA, flightGrowth, flights_filtered_df, groupSel, outerCheck, startSummerIATA, yearGDP)
    else:
        per_group_annual = ft.calculate_group_aggregates(dfRatio, emissionsGrowth, endSummerIATA, flightGrowth, flights_filtered_df, groupSel, outerCheck, startSummerIATA, yearGDP)


    #GDP Calculations
    gdpPerCountry = pd.read_csv('data/API_NY.GDP.MKTP.CD_DS2_en_csv_v2_2916952.csv', usecols=['COUNTRY', '2016', '2017', '2018', '2019', '2020'], index_col='COUNTRY')

    #calculate GDP Growth
    gdpPerCountry[yearGDP] = gdpPerCountry['2020'] * (1+ gdpGrowth/100)**(yearGDP-2020)

    compareOptiondisabled = True
    toSeloptions = []
    toSelvalue = []
    #Calculate GDP groups for from departure regions
    if groupSel == 'ADEP_COUNTRY':
        countryList=set()
        for sel in fromSel:
            countryList = countryList.union(set(regions_df.query(sel.replace('ADEP_', '')).loc[:, 'COUNTRY'].tolist()))
            #rowLoc = fromSel.replace('(ADEP_', '').replace('=="Y")', '')
        for sel in fromSelAdd:
            countryList = countryList.union(set(regions_df.query(sel.replace('ADEP_', '')).loc[:, 'COUNTRY'].tolist()))


        gdpPerCountry.loc["Selection"] = gdpPerCountry[gdpPerCountry.index.isin(countryList)].sum().tolist()
        countryList.add("Selection")
        gdpPerCountry = gdpPerCountry.loc[gdpPerCountry.index.isin(countryList)]
        per_group_annual_gdp = per_group_annual.join(gdpPerCountry, how='inner')

        if 'Yes' in extrapolateRet:
            retMult = 2
        else:
            retMult = 1

        per_group_annual_gdp['TOTAL_GDP_RATIO'] = (per_group_annual_gdp['TOTAL_COST_sum'] / per_group_annual_gdp[yearGDP]) * 100
        per_group_annual_gdp['FIT55_GDP_RATIO'] = (per_group_annual_gdp['FIT55_COST_sum'] / per_group_annual_gdp[yearGDP]) * 100
        per_group_annual_gdp['SAF_GDP_RATIO'] = (per_group_annual_gdp['SAF_COST_sum'] / per_group_annual_gdp[yearGDP]) * 100
        per_group_annual_gdp['ETS_GDP_RATIO'] = (per_group_annual_gdp['ETS_COST_sum'] / per_group_annual_gdp[yearGDP]) * 100
        per_group_annual_gdp['TAX_GDP_RATIO'] = (per_group_annual_gdp['TAX_COST_sum'] / per_group_annual_gdp[yearGDP]) * 100

    elif groupSel == 'ADEP':
        # TODO calculate the overall traffic for airport and determine the traffic affected by the measures vs not affected
        # Only filter on Market segment, ignore departure/destination filters

        all_per_group_annual = ft.calculate_group_aggregates(dfRatio, emissionsGrowth, endSummerIATA, flightGrowth, all_flights_df, fromSel, groupSel, outerCheck, startSummerIATA, yearGDP)

        per_group_annual_gdp = per_group_annual.set_index('ADEP').div(all_per_group_annual.set_index('ADEP'))

        per_group_annual_gdp = per_group_annual_gdp.dropna()

        per_group_annual_gdp = per_group_annual_gdp.reset_index()
        per_group_annual_gdp = per_group_annual_gdp.sort_values(by=['TOTAL_COST_mean'], ascending=False)
        per_group_annual_gdp = per_group_annual_gdp.round(2)
        pass
    elif groupSel == 'AC_Operator':
        #TODO for AC operator comparison. Calculate ratio of whole operations
        per_group_annual_gdp = per_group_annual.loc[:,[groupSel,'FUEL_sum','Actual_Distance_Flown_sum']]
        per_group_annual_gdp['FUEL_EFF'] = per_group_annual_gdp['FUEL_sum'] / per_group_annual_gdp['Actual_Distance_Flown_sum']
        pass
    elif groupSel == 'ADEP_COUNTRY_PAIR':
        #TODO GDP for Country Country Pair
        per_group_annual_gdp = pd.DataFrame()
        compareOptiondisabled = False
        torowNames = per_group_annual.query('Flights_size>700').index.get_level_values(1).unique().tolist()
        torowNames.sort()
        toSeloptions = [{'label': i, 'value': i} for i in torowNames]
        toSelvalue = torowNames[0]

    else:
        raise ValueError('Undefined Grouping')

    if heatmap_df is None:
        heatmap_df = pd.DataFrame()

    ds_heatmap = heatmap_df.to_json(date_format='iso', orient='split')
    ds_cost = per_group_annual.reset_index().to_json(date_format='iso', orient='split')
    ds_gdp = per_group_annual_gdp.to_json(date_format='iso', orient='split')


    #return options filter out less than 365 flights either per MS, airport or airline
    fromrowNames = per_group_annual.query('Flights_size>700').index.get_level_values(0).unique().tolist()
    fromrowNames.sort()

    Seloptions =[{'label': i, 'value': i} for i in fromrowNames]
    Selvalue = [x['value'] for x in Seloptions][:50]

    return Seloptions, Selvalue, ds_cost, ds_gdp, ds_heatmap, toSeloptions, toSelvalue,compareOptiondisabled



def update_per_airport(SelectedOptions, gdp_df, groupSelection, cost_df, heatmap_df):

    gdp_df = gdp_df.loc[gdp_df['ADEP'].isin(SelectedOptions)]
    cost_df = cost_df.loc[cost_df['ADEP'].isin(SelectedOptions)]

    colset=set(SelectedOptions)
    dffcols = set(heatmap_df.columns)
    dffrows = set(heatmap_df.index)
    finalCols = list(colset.intersection(dffcols, dffrows))
    heatmap_df = heatmap_df.loc[finalCols,finalCols]
    #heatmap_df = heatmap_df.dropna(axis=1)



    data = [
        go.Bar(name='SAF',
               x=cost_df[groupSelection],
               y=cost_df['SAF_COST_mean'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='TAX',
               x=cost_df[groupSelection],
               y=cost_df['TAX_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='ETS',
               x=cost_df[groupSelection],
               y=cost_df['ETS_COST_mean'],
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='JET A1',
               x=cost_df[groupSelection],
               y=cost_df['FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='Total Fuel Cost',
               x=cost_df[groupSelection],
               y=cost_df['TOTAL_FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=0.0,
               base=0
               ),
        go.Bar(name='Total Cost of Fit55 Measures',
               x=cost_df[groupSelection],
               y=cost_df['FIT55_COST_mean'], visible='legendonly',
               base=0,
               width=0.3,
               offset=0.3
               ),
        go.Bar(name='Total Cost of Fuel and Measures',
               x=cost_df[groupSelection],
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


    gdp_df = gdp_df.sort_values(by=['TOTAL_COST_mean'], ascending=False)

    dataGDP = [
        go.Bar(name='SAF',
               x=gdp_df['ADEP'],
               y=gdp_df['SAF_COST_mean'], visible='legendonly',
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.4,
               offset=-0.4,
               offsetgroup=1
               ),
        go.Bar(name='TAX',
               x=gdp_df['ADEP'],
               y=gdp_df['TAX_COST_mean'], visible='legendonly',
               width=0.4,
               offset=-0.4,
               offsetgroup=1
               ),
        go.Bar(name='ETS',
               x=gdp_df['ADEP'],
               y=gdp_df['ETS_COST_mean'], visible='legendonly',
               width=0.4,
               offset=-0.4,
               offsetgroup=1
               ),
        go.Bar(name='Total Ratio of FIT 55 Measures', visible='legendonly',
               x=gdp_df['ADEP'],
               y=gdp_df['FIT55_COST_mean'],
               width=0.4,
               offset=0.0,
               base=0,
               offsetgroup=1
               ),
        go.Bar(name='Total Ratio of Fuel and Fit55 Measures',
               x=gdp_df['ADEP'],
               y=gdp_df['TOTAL_COST_mean'],
               width=0.4,
               offset=0.0,
               base=0,
               offsetgroup=1
               )
    ]


    layout = go.Layout(title='Ratio of Selected Flights with all flights per Airport',
                       yaxis=dict(title='Ratio'),
                        barmode='stack',
                       legend = dict(yanchor="top", y=0.99, xanchor="right",x=1.21)
    )


    figGDP= go.Figure(data=dataGDP, layout= layout)


    #update table
    _col=[{"name": i, "id": i} for i in cost_df.columns]
    datatab=cost_df.to_dict('records')


    #update heatmap
    rowNames = heatmap_df.index.tolist()

    figPairs = px.imshow(heatmap_df, labels=dict(x="Destination Airport", y='Departure Airport', color='Number of Flights'))

    figPairs.update_layout(title="Number of flights between Airports",
                           width=2000,
                           height=2000,
                           xaxis={"tickangle": 45}, )

    return fig, figGDP, figPairs, datatab, _col

def update_per_operator(SelectedOptions, gdp_df, groupSel, cost_df, heatmap_df):
    #SelectedOptions, gdp_df, groupSelection, cost_df, heatmap_df
    # gdp_df = gdp_df.loc[gdp_df['ADEP'].isin(SelectedOptions)]
    cost_df = cost_df.loc[cost_df[groupSel].isin(SelectedOptions)]
    gdp_df = gdp_df.loc[gdp_df[groupSel].isin(SelectedOptions)]

    # colset=set(SelectedOptions)
    # dffcols = set(heatmap_df.columns)
    # finalCols = list(colset.intersection(dffcols))
    # heatmap_df = heatmap_df.loc[:,finalCols]
    # #heatmap_df = heatmap_df.dropna(axis=1)

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
               y=cost_df['FIT55_COST_mean'], visible='legendonly',
               base=0,
               width=0.3,
               offset=0.3
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



    gdp_df = gdp_df.sort_values(by=['FUEL_EFF'], ascending=True)

    dataGDP = [
        go.Bar(name='Fuel Efficiency',
               x=gdp_df['AC_Operator'],
               y=gdp_df['FUEL_EFF'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.4,
               offset=-0.4,
               offsetgroup=1
               )
    ]


    layout = go.Layout(title='Airline Fuel Efficiency',
                       yaxis=dict(title='Efficiency Fuel(kg)/nm'),
                        barmode='stack',
                       legend = dict(yanchor="top", y=0.99, xanchor="right",x=1.21)
    )


    figGDP= go.Figure(data=dataGDP, layout= layout)


    #update table
    _col=[{"name": i, "id": i} for i in cost_df.columns]
    datatab=cost_df.to_dict('records')

    return fig, figGDP,go.Figure(data=[go.Scatter(x=[], y=[])]), datatab, _col


def update_per_ms(SelectedOptions, gdp_df, groupSel, cost_df,  heatmap_df):

    gdp_df = gdp_df.loc[gdp_df.index.isin(SelectedOptions)]
    cost_df = cost_df.loc[cost_df.index.isin(SelectedOptions)]

    colset=set(SelectedOptions)
    dffcols = set(heatmap_df.columns)
    finalCols = list(colset.intersection(dffcols))
    heatmap_df = heatmap_df.loc[finalCols,:]
    heatmap_df = heatmap_df.dropna(axis=1)

    cost_df = cost_df.sort_values(by=['FIT55_COST_mean'], ascending=False)

    data = [
        go.Bar(name='SAF',
               x=cost_df.index,
               y=cost_df['SAF_COST_mean'],
               # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
               width=0.3,
               offset=-0.3,
               text=cost_df['SAF_COST_mean'],
               textposition='auto',
               ),
        go.Bar(name='TAX',
               x=cost_df.index,
               y=cost_df['TAX_COST_mean'],
               width=0.3,
               offset=-0.3,
               text=cost_df['TAX_COST_mean'],
               textposition='auto',
               ),
        go.Bar(name='ETS',
               x=cost_df.index,
               y=cost_df['ETS_COST_mean'],
               width=0.3,
               offset=-0.3,
               text=cost_df['ETS_COST_mean'],
               textposition='auto',
               ),
        go.Bar(name='JET A1',
               x=cost_df.index,
               y=cost_df['FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=-0.3
               ),
        go.Bar(name='Total Fuel Cost',
               x=cost_df.index,
               y=cost_df['TOTAL_FUEL_COST_mean'], visible='legendonly',
               width=0.3,
               offset=0.0,
               base=0
               ),
        go.Bar(name='Total Cost of Fuel and Measures',
               x=cost_df.index,
               y=cost_df['TOTAL_COST_mean'], visible='legendonly',
               base=0,
               width=0.3,
               offset=0.3
               ),
        go.Bar(name='Total Cost of FIT55 Measures',
               x=cost_df.index,
               y=cost_df['FIT55_COST_mean'], visible='legendonly',
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

    if groupSel == 'ADEP_COUNTRY':

        gdp_df = gdp_df.sort_values(by=['TOTAL_GDP_RATIO'], ascending=False)

        dataGDP = [
            go.Bar(name='SAF',
                   x=gdp_df.index,
                   y=gdp_df['SAF_GDP_RATIO'],
                   # error_y=dict(type='data', array=per_ms_Annual_out['SAF_COST_std'].to_list()), text=per_ms_Annual_out['SAF_COST_mean']
                   width=0.4,
                   offset=-0.4,
                   offsetgroup=1,
                   yaxis='y1'
                   ),
            go.Bar(name='TAX',
                   x=gdp_df.index,
                   y=gdp_df['TAX_GDP_RATIO'],
                   width=0.4,
                   offset=-0.4,
                   offsetgroup=1,
                   yaxis='y1'
                   ),
            go.Bar(name='ETS',
                   x=gdp_df.index,
                   y=gdp_df['ETS_GDP_RATIO'],
                   width=0.4,
                   offset=-0.4,
                   offsetgroup=1,
                   yaxis='y1'
                   ),
            go.Bar(name='Total GDP Ratio of Fuel and Measures',
                   x=gdp_df.index,
                   y=gdp_df['TOTAL_GDP_RATIO'], visible='legendonly',
                   width=0.4,
                   offset=0.0,
                   base=0,
                   offsetgroup=1,
                   yaxis = 'y1'
                   ),
            go.Bar(name='Total GDP Ratio of Fit55 Measures',
                   x=gdp_df.index,
                   y=gdp_df['FIT55_GDP_RATIO'], visible='legendonly',
                   width=0.4,
                   offset=0.0,
                   base=0,
                   offsetgroup=1,
                   yaxis='y1'
                   ),
            go.Scatter(name='Percent of total Emissions',
                       x=gdp_df.index,
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

        # update heatmap
        rowNames = heatmap_df.index.tolist()
        colNames = heatmap_df.columns.tolist()
        for rowName in rowNames:
            if rowName in colNames:
                heatmap_df.loc[rowName, rowName] = 0

        figPairs = px.imshow(heatmap_df.T, labels=dict(x="Departure Country", y='Destination Country', color='Number of Flights'))

        figPairs.update_layout(title="Number of flights between States",
                               width=2000,
                               height=3000,
                               xaxis={"tickangle": 45}, )


    else:
        figGDP =  go.Figure(data=[go.Scatter(x=[], y=[])])
        figPairs = go.Figure(data=[go.Scatter(x=[], y=[])])


    #update table
    cost_df= cost_df.reset_index()
    _col=[{"name": i, "id": i} for i in cost_df.columns]
    datatab=cost_df.to_dict('records')


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
     dash.dependencies.State('groupSelection', 'value'),
     dash.dependencies.Input('CompareOption', 'value')])
def update_graphs(SelectedOptions, ds_cost,ds_gdp, ds_heatmap, groupSelection, CompareOption):

    cost_df = pd.read_json(ds_cost, orient='split')
    gdp_df = pd.read_json(ds_gdp,orient='split')
    heatmap_df = pd.read_json(ds_heatmap, orient = 'split')

    if cost_df.empty is True:
        fig= go.Figure(data=[go.Scatter(x=[], y=[])])
        return fig,fig,fig

    if groupSelection=='ADEP_COUNTRY':
        cost_df = cost_df.set_index('ADEP_COUNTRY')
        figCost, figGDP, figHeat, tab,_cols = update_per_ms(SelectedOptions, gdp_df, groupSelection, cost_df, heatmap_df)
    elif groupSelection=='ADEP':
        figCost, figGDP, figHeat, tab,_cols = update_per_airport(SelectedOptions, gdp_df, groupSelection, cost_df, heatmap_df)
    elif groupSelection == 'AC_Operator':
        figCost, figGDP, figHeat, tab,_cols = update_per_operator(SelectedOptions, gdp_df, groupSelection, cost_df, heatmap_df)
    elif groupSelection == 'ADEP_COUNTRY_PAIR':
        cost_df = cost_df.set_index(['ADEP_COUNTRY', 'ADES_COUNTRY'])
        cost_df = cost_df.xs(CompareOption, level=1, drop_level=True)
        figCost, figGDP, figHeat, tab, _cols = update_per_ms(SelectedOptions, gdp_df, groupSelection, cost_df, heatmap_df)
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
