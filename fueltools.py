import os
from datetime import datetime
import pandas as pd
from dateutil import relativedelta
import datetime as dt


# Current Exchange rate from Euros to USD
EurosToUsdExchangeRate = 1.182

def getYears():

    dateDict= {}
    directory = 'data'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        fname, file_extension = os.path.splitext(f)
        if os.path.isfile(f) and file_extension=='.pkl' and "Flights_" in filename:
            res =filename.replace("Flights_", "")
            res=res.replace(".csv.raw.pkl", "")
            splitDates=res.split("_")
            date_time_obj1 = datetime.strptime(splitDates[0], '%Y%m%d')
            year = date_time_obj1.year

            dateDict[year] = dateDict.get(year,0) +1

    res = [key for key, val in dateDict.items() if val>=3]


    return res

def getMonths(yearSelection=2018):

    dateDict= {}
    directory = 'data'
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        fname, file_extension = os.path.splitext(f)
        if os.path.isfile(f) and file_extension=='.pkl' and "Flights_" in filename:
            res =filename.replace("Flights_", "")
            res=res.replace(".csv.raw.pkl", "")
            splitDates=res.split("_")
            date_time_obj1 = datetime.strptime(splitDates[0], '%Y%m%d')
            year = date_time_obj1.year
            month = date_time_obj1.month
            if year==yearSelection:
                dateDict[month] = dateDict.get(month,0) +1

    res = [key for key, val in dateDict.items() if val>=1]


    return res


def getfilenamesForProcessing(directory):
    fileListGz=[]
    fileListPkl=[]
    for filename in os.listdir(directory):
        fname, extension = os.path.splitext(filename)
        if extension=='.pkl':
            fileListPkl.append(fname.replace(".raw",""))
        elif extension=='.gz':
            fileListGz.append(fname)
        else:
            None

    pkl = set(fileListPkl)
    gz= set(fileListGz)

    res=list(gz.difference(pkl))

    res[:] = [x+".gz" for x in res]

    return res


def loadPickle(year, month):

    yearsAvailable = getYears()
    if year not in yearsAvailable:
        raise ValueError('Year defined not in the list of available years')

    directory='data'
    flights_df_list=[]
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        fname, file_extension = os.path.splitext(f)
        if os.path.isfile(f) and file_extension=='.pkl' and "Flights_" in filename:
            res =filename.replace("Flights_", "")
            res=res.replace(".csv.raw.pkl", "")
            splitDates=res.split("_")
            date_time_obj1 = datetime.strptime(splitDates[0], '%Y%m%d')
            Fileyear = date_time_obj1.year
            Filemonth = date_time_obj1.month
            if Fileyear == year: # and Filemonth==month:
                temp_df = pd.read_pickle(f)
                flights_df_list.append(temp_df)

    flights_df = pd.concat(flights_df_list, ignore_index=True)
    return flights_df



# **************************************** #
# Constants for Fuel SAF Calculations
# all prices are in USD
# CostOfJetFuelPerKg = 0.61
# CostOfSafFuelPerKg = 3.66
# SafBlendingMandate = 0.02
# **************************************** #

def CalculateSAFCost(flights_df, costOfSafFuelPerKg = 3.66, safBlendingMandate = 0.02 ):

    # We only care for departure flight
    subSet = 'ADEP_SAF=="Y"'

    flights_df=flights_df.assign(SAF_COST=0.0)
    flights_df.loc[flights_df.eval(subSet),'SAF_COST'] = flights_df.query(subSet)['FUEL'] * safBlendingMandate * costOfSafFuelPerKg

    return flights_df

def CalculateFuelCost(flights_df, costOfJetFuelPerKg = 0.81, safBlendingMandate = 0.02):

    flights_df = flights_df.assign(FUEL_COST=0.0)
    flights_df['FUEL_COST'] = flights_df['FUEL'] * costOfJetFuelPerKg
    subSet = 'ADEP_SAF=="Y"'
    flights_df.loc[flights_df.eval(subSet),'FUEL_COST'] = flights_df.query(subSet)['FUEL']*(1-safBlendingMandate) * costOfJetFuelPerKg
    return flights_df

def CalculateTotalFuelCost(flights_df):

    flights_df = flights_df.assign(TOTAL_FUEL_COST=0.0)
    flights_df['TOTAL_FUEL_COST'] = flights_df['SAF_COST'] + flights_df['FUEL_COST']
    return flights_df


def getDFMonths(dtSeries):
    return set(dtSeries.dt.month.unique())


def getDFRatio(dfMonthsSet):
    summerIATA = {4, 5, 6, 7, 8, 9, 10}
    winterIATA = {1, 2, 3, 11, 12}

    reSum = summerIATA - dfMonthsSet
    reWin = winterIATA - dfMonthsSet

    sumMultiplier = len(summerIATA) - len(reSum)
    winMultiplier = len(winterIATA) - len(reWin)

    return sumMultiplier, winMultiplier


def getIATASeasons(setyear):
    startSummer = datetime(setyear, 3, 1) + relativedelta.relativedelta(day=31, weekday=relativedelta.SU(-1))

    endSummer = datetime(setyear, 10, 1) + relativedelta.relativedelta(day=31, hours=24,
                                                                    weekday=relativedelta.SA(-1)) + dt.timedelta(days=1)

    return startSummer, endSummer


def CalculateTaxCost(flights_df, FuelTaxRateEurosPerGJ = 0.00 , blendingMandate=0.00 ):
    # *************************************************** #
    # Constants for Fuel TAX Calculations
    # all prices are in Euros/GJ
    # 2023 = 0 Tax rate
    # 2024 = 1.075    2025 = 2.15 etc

    # Tax rate in 2033
    MaxFuelTaxRateEurosPerGJ = 10.75
    # Using rate for 2025 to match the SAF mandate



    # Tax rate in Euros/kg
    FuelTaxRateEurosPerKg = (46.4 / 1000) * FuelTaxRateEurosPerGJ
    FuelTaxRateUsdPerKg = FuelTaxRateEurosPerKg * EurosToUsdExchangeRate
    # *************************************************** #

    # Tax only for intra EU flights so ADEP and ADES must be Y
    subSet = '(ADEP_ETD=="Y" & ADES_ETD=="Y" & STATFOR_Market_Segment!="All-Cargo")'
    flights_df = flights_df.assign(TAX_COST= 0.0)
    flights_df.loc[flights_df.eval(subSet),'TAX_COST'] = flights_df.query(subSet)['FUEL'] * (1-blendingMandate) * FuelTaxRateUsdPerKg

    return flights_df

def CalculateETSCost(flights_df, safBlendingMandate=0.02, ETSCostpertonne = 62, ETSpercentage = 50 ):

    ETSPricePerKg = ETSCostpertonne/1000 * EurosToUsdExchangeRate

    # ETS only for intra EU flights so ADEP and ADES must be Y
    ETSsubSet = '(ADEP_ETS=="Y" & ADES_ETS=="Y")'
    flights_df = flights_df.assign(ETS_COST = 0.0 )
    flights_df.loc[flights_df.eval(ETSsubSet),'ETS_COST'] = flights_df.query(ETSsubSet)['FUEL'] * 3.15 * (1-safBlendingMandate) * ETSPricePerKg * ETSpercentage/100

    #ETS for flights from Outermost regions to home state
    OMSubset = '(ADEP_Region=="Canary Islands"  & ADES_COUNTRY=="Spain"             & ADES_Region != "Canary Islands") | ' \
               '(ADEP_COUNTRY=="Spain"          & ADEP_Region != "Canary Islands"   & ADES_Region == "Canary Islands") | ' \
               '(ADEP_Region=="Azores"          & ADES_COUNTRY == "Portugal"        & ADES_Region != "Azores" ) | ' \
               '(ADEP_COUNTRY=="Portugal"       & ADEP_Region !="Azores"            & ADES_Region == "Azores" ) | ' \
               '(ADEP_Region=="Madeira"         & ADES_COUNTRY == "Portugal"        & ADES_Region != "Madeira") | ' \
               '(ADEP_COUNTRY=="Portugal"       & ADEP_Region != "Madeira"          & ADES_Region == "Madeira") | ' \
               '(ADEP_Region=="French Guiana"   & ADES_COUNTRY == "France"          & ADES_Region != "French Guiana") | ' \
               '(ADEP_COUNTRY=="France"         & ADEP_Region != "French Guiana"    & ADES_Region == "French Guiana") | ' \
               '(ADEP_Region=="Réunion"         & ADES_COUNTRY == "France"          & ADES_Region != "Réunion") | ' \
               '(ADEP_COUNTRY=="France"         & ADEP_Region != "Réunion"          & ADES_Region == "Réunion") | ' \
               '(ADEP_Region=="West Indies"     & ADES_COUNTRY == "France"          & ADES_Region != "West Indies") |' \
               '(ADEP_COUNTRY=="France"         & ADEP_Region != "West Indies"      & ADES_Region == "West Indies") '

    flights_df.loc[flights_df.eval(OMSubset), 'ETS_COST'] = 0.0

    #ETS for flights from home state to outermost region
    OMSubset = '(ADEP_COUNTRY=="Canary Islands" & ADES_COUNTRY=="Canary Islands") | ' \
               '(ADEP_COUNTRY=="Azores" & ADES_COUNTRY=="Azores") | ' \
               '(ADEP_COUNTRY=="Madeira" & ADES_COUNTRY=="Madeira") | ' \
               '(ADEP_COUNTRY=="French Guiana" & ADES_COUNTRY=="French Guiana") | ' \
               '(ADEP_COUNTRY=="Réunion" & ADES_COUNTRY=="Réunion") | ' \
               '(ADEP_COUNTRY=="West Indies" & ADES_COUNTRY=="West Indies") '

    return flights_df

def calculateCustom(all_flights_df, custCriteria, custField, custValue):

    # (ADEP_COUNTRY=="Cyprus" & ADES_COUNTRY=="Greece") | (ADEP_COUNTRY=="Greece" & ADES_COUNTRY=="Cyprus")    ETS_COST
    if custCriteria:
        all_flights_df.loc[all_flights_df.eval(custCriteria), custField] = float(custValue)
        all_flights_df = CalculateTotalFuelCost(all_flights_df)
        all_flights_df['FIT55_COST'] = all_flights_df['SAF_COST'] + all_flights_df['TAX_COST'] + all_flights_df['ETS_COST']
        all_flights_df['TOTAL_COST'] = all_flights_df['SAF_COST'] + all_flights_df['TAX_COST'] + all_flights_df['ETS_COST'] + all_flights_df['FUEL_COST']


    return all_flights_df

def get_dd_selection(fromSelection, DepOrDes):
    fromSelection_value = fromSelection + ['!' + x for x in fromSelection]
    fromSelection_label = fromSelection + ['Outside ' + x for x in fromSelection]

    if DepOrDes =='ADEP':
        SDepOrDes = '(ADEP_'
    elif DepOrDes =='ADES':
        SDepOrDes = '(ADES_'
    else:
        raise ValueError('Invalid selection: ADEP or ADES')


    SelDict = []
    SelLength = len(fromSelection)

    for idx, label in enumerate(fromSelection_label):
        if idx < SelLength:
            SelDict.append({'label': fromSelection_label[idx], 'value': SDepOrDes + fromSelection_value[idx] + '=="Y")'})
        else:
            SelDict.append({'label': fromSelection_label[idx], 'value': SDepOrDes + fromSelection_value[idx][1:] + '=="N")'})

    return SelDict


def get_dd_selection(fromSelection, DepOrDes):
    fromSelection_value = fromSelection + ['!' + x for x in fromSelection]
    fromSelection_label = fromSelection + ['Outside ' + x for x in fromSelection]

    if DepOrDes =='ADEP':
        SDepOrDes = '(ADEP_'
    elif DepOrDes =='ADES':
        SDepOrDes = '(ADES_'
    else:
        raise ValueError('Invalid selection: ADEP or ADES')


    SelDict = []
    SelLength = len(fromSelection)

    for idx, label in enumerate(fromSelection_label):
        if idx < SelLength:
            SelDict.append({'label': fromSelection_label[idx], 'value': SDepOrDes + fromSelection_value[idx] + '=="Y")'})
        else:
            SelDict.append({'label': fromSelection_label[idx], 'value': SDepOrDes + fromSelection_value[idx][1:] + '=="N")'})

    return SelDict

def calculatePairs(dfRatio, endSummerIATA, groupSel, ms_filtered_df, startSummerIATA):
    # Calculate pairs for heatmap
    if groupSel == 'ADEP_COUNTRY':
        countryPairsSummer_df = ms_filtered_df[(ms_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
                ms_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
            .groupby([groupSel, groupSel.replace('ADEP', 'ADES')], observed=True).size().unstack(fill_value=0)
        countryPairsSummer_df = countryPairsSummer_df * 7 / dfRatio[0]

        countryPairsWinter_df = ms_filtered_df[(ms_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
                ms_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
            .groupby([groupSel, groupSel.replace('ADEP', 'ADES')], observed=True).size().unstack(fill_value=0)
        countryPairsWinter_df = countryPairsWinter_df * 5 / dfRatio[1]

        countryPairTotal_df = countryPairsSummer_df + countryPairsWinter_df
        countryPairTotal_df = countryPairTotal_df.dropna(how='all').fillna(0)
        return countryPairTotal_df

    elif groupSel == 'ADEP':
        airportPairsSummer_df = ms_filtered_df[(ms_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
                ms_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
            .groupby([groupSel, groupSel.replace('ADEP', 'ADES')], observed=True).size().unstack(fill_value=0)
        airportPairsSummer_df = airportPairsSummer_df * 7 / dfRatio[0]

        airportPairsWinter_df = ms_filtered_df[(ms_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
                ms_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
            .groupby([groupSel, groupSel.replace('ADEP', 'ADES')], observed=True).size().unstack(fill_value=0)
        airportPairsWinter_df = airportPairsWinter_df * 5 / dfRatio[1]

        airportPairsTotal = airportPairsSummer_df + airportPairsWinter_df
        airportPairsTotal= airportPairsTotal.dropna(how='all').fillna(0)

        return airportPairsTotal
    elif groupSel == 'AC_Operator':
        pass

    return None
    # TODO Country/Country Pair


def foldInOutermostWithMS(groupSel, outerCheck, per_group_annual):
    indexList = per_group_annual.index.tolist()
    if outerCheck == 'OUTER_CLOSE' and groupSel == 'ADEP_COUNTRY':
        if 'Canary Islands' in indexList:
            # Merge Spanish Outermost Regions
            multCa = per_group_annual.loc['Canary Islands', 'ECTRL_ID_size'] / \
                     (per_group_annual.loc['Canary Islands', 'ECTRL_ID_size'] + per_group_annual.loc['Spain', 'ECTRL_ID_size'])
            multSp = per_group_annual.loc['Spain', 'ECTRL_ID_size'] / \
                     (per_group_annual.loc['Canary Islands', 'ECTRL_ID_size'] + per_group_annual.loc['Spain', 'ECTRL_ID_size'])

            per_group_annual.loc['Spain', per_group_annual.columns.str.contains('mean|std|%')] = per_group_annual.loc['Spain', per_group_annual.columns.str.contains('mean|std|%')] * multSp
            caRow = per_group_annual.loc[['Canary Islands']]
            caRow.loc['Canary Islands', caRow.columns.str.contains('mean|std|%')] = caRow.loc['Canary Islands', caRow.columns.str.contains('mean|std|%')] * multCa
            per_group_annual.loc['Spain'] = per_group_annual.loc['Spain'] + caRow.loc['Canary Islands']

        if 'Azores' in indexList and 'Madeira' in indexList:
            # Merge Portugese Close regions
            multAz = per_group_annual.loc['Azores', 'ECTRL_ID_size'] / \
                     (per_group_annual.loc[['Azores', 'Madeira'], 'ECTRL_ID_size'].sum() + per_group_annual.loc['Portugal', 'ECTRL_ID_size'])
            multMa = per_group_annual.loc['Madeira', 'ECTRL_ID_size'] / \
                     (per_group_annual.loc[['Azores', 'Madeira'], 'ECTRL_ID_size'].sum() + per_group_annual.loc['Portugal', 'ECTRL_ID_size'])
            multPt = 1 - (multAz + multMa)

            per_group_annual.loc['Portugal', per_group_annual.columns.str.contains('mean|std|%')] = per_group_annual.loc['Portugal', per_group_annual.columns.str.contains('mean|std|%')] * multPt
            azmaRow = per_group_annual.loc[['Azores', 'Madeira']]

            azmaRow.loc['Azores', azmaRow.columns.str.contains('mean|std|%')] = azmaRow.loc['Azores', azmaRow.columns.str.contains('mean|std|%')] * multAz
            azmaRow.loc['Madeira', azmaRow.columns.str.contains('mean|std|%')] = azmaRow.loc['Madeira', azmaRow.columns.str.contains('mean|std|%')] * multMa
            per_group_annual.loc['Portugal'] = per_group_annual.loc['Portugal'] + azmaRow.loc['Azores'] + azmaRow.loc['Madeira']
    return per_group_annual


def Newcalculate_group_aggregates(dfRatio, emissionsGrowth, endSummerIATA, flightGrowth, flights_filtered_df, groupSel,  startSummerIATA, yearGDP, countries):

    #Adjust Groupsel
    if groupSel in ['ADEP_COUNTRY', 'ADEP', 'AC_Operator']:
        groupSel = [groupSel]
        tag = 'Selection'
    elif groupSel == 'ADEP_COUNTRY_PAIR':
        groupSel=[groupSel.replace('_PAIR',''), groupSel.replace('_PAIR','').replace('ADEP', 'ADES')]
        tag = ('Selection' , 'Selection')
    else:
        raise ValueError("Invalid grouping option")


    #countries = pd.concat([flights_filtered_df['ADEP_COUNTRY'] , flights_filtered_df['ADES_COUNTRY']]).unique()
    Summer= pd.DataFrame()
    Winter = pd.DataFrame()
    for country in countries:
        res = flights_filtered_df[
            (flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) &
            (flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA) &
            ((flights_filtered_df['ADEP_COUNTRY'] == country) | (flights_filtered_df['ADES_COUNTRY']==country))][['ECTRL_ID', 'Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'FIT55_COST', 'TOTAL_COST']] \
            .agg({'ECTRL_ID': 'size', 'Actual_Distance_Flown': ['mean', 'std', 'sum'], 'FUEL': 'sum', 'EMISSIONS': 'sum', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
                  'TOTAL_FUEL_COST': ['mean', 'std', 'sum'], 'TAX_COST': ['mean', 'std', 'sum'], 'ETS_COST': ['mean', 'std', 'sum'], 'FIT55_COST': ['mean', 'std', 'sum'], 'TOTAL_COST': ['mean', 'std', 'sum']}).unstack(fill_value=None)
        res = res.to_frame(name=country)
        Summer = pd.concat([Summer, res], axis =1)

        res = flights_filtered_df[
            ((flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)) &
            ((flights_filtered_df['ADEP_COUNTRY'] == country) | (flights_filtered_df['ADES_COUNTRY']==country))][['ECTRL_ID', 'Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'FIT55_COST', 'TOTAL_COST']] \
            .agg({'ECTRL_ID': 'size', 'Actual_Distance_Flown': ['mean', 'std', 'sum'], 'FUEL': 'sum', 'EMISSIONS': 'sum', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
                  'TOTAL_FUEL_COST': ['mean', 'std', 'sum'], 'TAX_COST': ['mean', 'std', 'sum'], 'ETS_COST': ['mean', 'std', 'sum'], 'FIT55_COST': ['mean', 'std', 'sum'], 'TOTAL_COST': ['mean', 'std', 'sum']}).unstack(fill_value=None)
        res = res.to_frame(name=country)
        Winter = pd.concat([Winter, res], axis =1)

    Winter = Winter.T
    Summer = Summer.T
    # Extrapolate each season, summer and winter, according to the determined ration of the dataset
    Summer.columns = ["_".join(a) for a in Summer.columns.to_flat_index()]
    Winter.columns = ["_".join(a) for a in Winter.columns.to_flat_index()]


    # exclude statistical components which cannot be extrapolated
    Summer.loc[:, ~Summer.columns.str.contains('mean|std|%')] = Summer.loc[:, ~Summer.columns.str.contains('mean|std|%')] / dfRatio[0]
    Winter.loc[:, ~Winter.columns.str.contains('mean|std|%')] = Winter.loc[:, ~Winter.columns.str.contains('mean|std|%')] / dfRatio[1]
    Annual = ((Summer * 7) + (Winter * 5))
    Annual.loc[:, Annual.columns.str.contains('mean|std|%')] = Annual.loc[:, Annual.columns.str.contains('mean|std|%')] / 12

    #determine statistics of selected region
    selSummer = flights_filtered_df[
        (flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) &
        (flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['ECTRL_ID', 'Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'FIT55_COST', 'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size', 'Actual_Distance_Flown': ['mean', 'std', 'sum'], 'FUEL': 'sum', 'EMISSIONS': 'sum', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
              'TOTAL_FUEL_COST': ['mean', 'std', 'sum'], 'TAX_COST': ['mean', 'std', 'sum'], 'ETS_COST': ['mean', 'std', 'sum'], 'FIT55_COST': ['mean', 'std', 'sum'], 'TOTAL_COST': ['mean', 'std', 'sum']}).unstack(fill_value=None)
    selSummer = selSummer.to_frame(name=tag).T

    selWinter = flights_filtered_df[
        ((flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
                flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA))][['ECTRL_ID', 'Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'FIT55_COST', 'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size', 'Actual_Distance_Flown': ['mean', 'std', 'sum'], 'FUEL': 'sum', 'EMISSIONS': 'sum', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
              'TOTAL_FUEL_COST': ['mean', 'std', 'sum'], 'TAX_COST': ['mean', 'std', 'sum'], 'ETS_COST': ['mean', 'std', 'sum'], 'FIT55_COST': ['mean', 'std', 'sum'], 'TOTAL_COST': ['mean', 'std', 'sum']}).unstack(fill_value=None)
    selWinter = selWinter.to_frame(name=tag).T

    # exclude statistical components which cannot be extrapolated
    selSummer.columns = ["_".join(a) for a in selSummer.columns.to_flat_index()]
    selWinter.columns = ["_".join(a) for a in selWinter.columns.to_flat_index()]
    selSummer.loc[:, ~selSummer.columns.str.contains('mean|std|%')] = selSummer.loc[:, ~selSummer.columns.str.contains('mean|std|%')] / dfRatio[0]
    selWinter.loc[:, ~selWinter.columns.str.contains('mean|std|%')] = selWinter.loc[:, ~selWinter.columns.str.contains('mean|std|%')] / dfRatio[1]
    selAnnual = ((selSummer * 7) + (selWinter * 5))
    selAnnual.loc[:, selAnnual.columns.str.contains('mean|std|%')] = selAnnual.loc[:, selAnnual.columns.str.contains('mean|std|%')] / 12

    Annual=pd.concat([Annual,selAnnual])


    Annual = Annual.dropna(axis=1, how='all')
    #per_group_annual = foldInOutermostWithMS(groupSel, outerCheck, per_group_annual)
    # Calculate Flight Growth. Use 2024 as the baseline which is the estimate time traffic will return to prepandemic levels
    if yearGDP > 2024:
        Annual.loc[:, ~Annual.columns.str.contains('mean|std|%|COUNTRY|EMISSIONS|Actual')] = Annual.loc[:, ~Annual.columns.str.contains('mean|std|%|COUNTRY|EMISSIONS|Actual')] * (1 + flightGrowth / 100) ** (yearGDP - 2024)
    # Calculate Emissions Growth
    Annual['EMISSIONS_sum'] = Annual["EMISSIONS_sum"] * (1 + emissionsGrowth / 100) ** (yearGDP - 2024)
    Annual['EMISSIONS_Percent'] = (Annual['EMISSIONS_sum'] /2.0) / Annual.loc[tag, 'EMISSIONS_sum'] * 100
    # prepare dataframe for presentation
    #per_group_annual = per_group_annual.reset_index()
    Annual = Annual.sort_values(by=['SAF_COST_mean'], ascending=False)
    Annual = Annual.round(2)
    Annual['ECTRL_ID_size'] = Annual['ECTRL_ID_size'].astype(int)
    Annual = Annual.rename(columns={'ECTRL_ID_size': 'Flights_size'})
    Annual.index.name = 'ADEP_COUNTRY'

    return Annual







def calculate_group_aggregates(dfRatio, emissionsGrowth, endSummerIATA, flightGrowth, flights_filtered_df, groupSel, startSummerIATA, yearGDP):

    #Adjust Groupsel
    if groupSel in ['ADEP_COUNTRY', 'ADEP', 'AC_Operator']:
        groupSel = [groupSel]
        tag = 'Selection'
    elif groupSel == 'ADEP_COUNTRY_PAIR':
        groupSel=[groupSel.replace('_PAIR',''), groupSel.replace('_PAIR','').replace('ADEP', 'ADES')]
        tag = ('Selection' , 'Selection')
    else:
        raise ValueError("Invalid grouping option")




    # Calculate the aggregates per IATA season basis
    # Summer
    per_group_summer = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
        .groupby(groupSel)[['ECTRL_ID', 'Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST','FIT55_COST' ,'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size', 'Actual_Distance_Flown': ['mean', 'std', 'sum'], 'FUEL': 'sum', 'EMISSIONS': 'sum', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
              'TOTAL_FUEL_COST': ['mean', 'std', 'sum'], 'TAX_COST': ['mean', 'std', 'sum'], 'ETS_COST': ['mean', 'std', 'sum'],'FIT55_COST' : ['mean', 'std', 'sum'], 'TOTAL_COST': ['mean', 'std', 'sum']})
    per_group_summer_quantiles = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)] \
        .groupby(groupSel)[['SAF_COST', 'TAX_COST', 'ETS_COST']] \
        .describe().filter(like='%')
    per_group_summer = pd.concat([per_group_summer, per_group_summer_quantiles], axis=1)
    # Winter
    per_group_winter = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
        .groupby(groupSel)[['ECTRL_ID', 'Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST','FIT55_COST', 'TOTAL_COST']] \
        .agg({'ECTRL_ID': 'size', 'Actual_Distance_Flown': ['mean', 'std', 'sum'], 'FUEL': 'sum', 'EMISSIONS': 'sum', 'SAF_COST': ['mean', 'std', 'sum'], 'FUEL_COST': ['mean', 'std', 'sum'],
              'TOTAL_FUEL_COST': ['mean', 'std', 'sum'], 'TAX_COST': ['mean', 'std', 'sum'], 'ETS_COST': ['mean', 'std', 'sum'],'FIT55_COST': ['mean', 'std', 'sum'], 'TOTAL_COST': ['mean', 'std', 'sum']})
    per_group_winter_quantiles = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)] \
        .groupby(groupSel)[['SAF_COST', 'TAX_COST', 'ETS_COST']] \
        .describe().filter(like='%')
    per_group_winter = pd.concat([per_group_winter, per_group_winter_quantiles], axis=1)
    # Extrapolate each season, summer and winter, according to the determined ration of the dataset
    per_group_summer.columns = ["_".join(a) for a in per_group_summer.columns.to_flat_index()]
    per_group_winter.columns = ["_".join(a) for a in per_group_winter.columns.to_flat_index()]
    # exclude statistical components which cannot be extrapolated
    per_group_summer.loc[:, ~per_group_summer.columns.str.contains('mean|std|%')] = per_group_summer.loc[:, ~per_group_summer.columns.str.contains('mean|std|%')] / dfRatio[0]
    per_group_winter.loc[:, ~per_group_winter.columns.str.contains('mean|std|%')] = per_group_winter.loc[:, ~per_group_winter.columns.str.contains('mean|std|%')] / dfRatio[1]
    per_group_annual = ((per_group_summer * 7) + (per_group_winter * 5))
    per_group_annual.loc[:, per_group_annual.columns.str.contains('mean|std|%')] = per_group_annual.loc[:, per_group_annual.columns.str.contains('mean|std|%')] / 12

    # Calculate from selected region averages, eg EU_EEA_EFTA
    sel_avg_quantiles_sum = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST','FIT55_COST', 'TOTAL_COST']].describe()
    sel_avg_sum_sum = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= startSummerIATA) & (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] < endSummerIATA)][['Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST','FIT55_COST', 'TOTAL_COST']].sum().reset_index(name='sum')
    selected_summer = sel_avg_quantiles_sum.T
    selected_summer['sum'] = (sel_avg_sum_sum.loc[:, 'sum'] / dfRatio[0]).tolist()
    sel_avg_quantiles_win = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)][['Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST','FIT55_COST', 'TOTAL_COST']].describe()
    sel_avg_sum_win = flights_filtered_df[(flights_filtered_df['FILED_OFF_BLOCK_TIME'] < startSummerIATA) | (
            flights_filtered_df['FILED_OFF_BLOCK_TIME'] >= endSummerIATA)][['Actual_Distance_Flown', 'FUEL', 'EMISSIONS', 'SAF_COST', 'FUEL_COST', 'TOTAL_FUEL_COST', 'TAX_COST', 'ETS_COST', 'FIT55_COST','TOTAL_COST']].sum().reset_index(name='sum')
    selected_winter = sel_avg_quantiles_win.T
    selected_winter['sum'] = (sel_avg_sum_win.loc[:, 'sum'] / dfRatio[1]).tolist()
    sel_ms_Annual = ((selected_summer * 7) + (selected_winter * 5))
    sel_ms_Annual = sel_ms_Annual.drop(columns=['min', 'max'])
    sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')] = sel_ms_Annual.loc[:, sel_ms_Annual.columns.str.contains('mean|std|%')] / 12

    # add record of selected region to dataframe
    per_group_annual.loc[tag,:] = (int(sel_ms_Annual.loc['SAF_COST', 'count']),
                                          sel_ms_Annual.loc['Actual_Distance_Flown', 'mean'],
                                          sel_ms_Annual.loc['Actual_Distance_Flown', 'std'],
                                          sel_ms_Annual.loc['Actual_Distance_Flown', 'sum'],
                                          sel_ms_Annual.loc['FUEL', 'sum'],
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
                                          sel_ms_Annual.loc['FIT55_COST', 'mean'],
                                          sel_ms_Annual.loc['FIT55_COST', 'std'],
                                          sel_ms_Annual.loc['FIT55_COST', 'sum'],
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

    per_group_annual = per_group_annual.dropna()
    #per_group_annual = foldInOutermostWithMS(groupSel, outerCheck, per_group_annual)
    # Calculate Flight Growth. Use 2024 as the baseline which is the estimate time traffic will return to prepandemic levels
    if yearGDP > 2024:
        per_group_annual.loc[:, ~per_group_annual.columns.str.contains('mean|std|%|COUNTRY|EMISSIONS|Actual')] = per_group_annual.loc[:, ~per_group_annual.columns.str.contains('mean|std|%|COUNTRY|EMISSIONS|Actual')] * (1 + flightGrowth / 100) ** (yearGDP - 2024)
    # Calculate Emissions Growth
    per_group_annual['EMISSIONS_sum'] = per_group_annual["EMISSIONS_sum"] * (1 + emissionsGrowth / 100) ** (yearGDP - 2024)
    per_group_annual['EMISSIONS_Percent'] = per_group_annual['EMISSIONS_sum'] / per_group_annual.loc[tag, 'EMISSIONS_sum'] * 100
    # prepare dataframe for presentation
    #per_group_annual = per_group_annual.reset_index()
    per_group_annual = per_group_annual.sort_values(by=['SAF_COST_mean'], ascending=False)
    per_group_annual = per_group_annual.round(2)
    per_group_annual['ECTRL_ID_size'] = per_group_annual['ECTRL_ID_size'].astype(int)
    per_group_annual = per_group_annual.rename(columns={'ECTRL_ID_size': 'Flights_size'})
    return per_group_annual
