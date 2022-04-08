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

    flights_df['SAF_COST'] = flights_df['FUEL'] * safBlendingMandate * costOfSafFuelPerKg
    return flights_df

def CalculateFuelCost(flights_df, costOfJetFuelPerKg = 0.61, safBlendingMandate = 0.02 ):
    flights_df['FUEL_COST'] = flights_df['FUEL']*(1-safBlendingMandate) * costOfJetFuelPerKg
    return flights_df

def CalculateTotalFuelCost(flights_df):
    flights_df['TOTAL_FUEL_COST'] = flights_df['SAF_COST'] + flights_df['FUEL_COST']
    return flights_df


def getDFMonths(dtSeries):
    return set(dtSeries.dt.month.unique())


def getDFRatio(dfMonthsSet):
    summerIATA = set([4, 5, 6, 7, 8, 9, 10])
    winterIATA = set([1, 2, 3, 11, 12])

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


def CalculateTaxCost(flights_df, FuelTaxRateEurosPerGJ = 2.15 , blendingMandate=0.02 ):
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

    flights_df['TAX_COST'] = flights_df['FUEL'] * (1-blendingMandate) * FuelTaxRateUsdPerKg

    return flights_df

def CalculateETSCost(flights_df, safBlendingMandate=0.02, ETSCostpertonne = 62, ETSpercentage = 50):

    ETSPricePerKg = ETSCostpertonne/1000 * EurosToUsdExchangeRate

    flights_df['ETS_COST'] = flights_df['FUEL']* 3.15 * (1-safBlendingMandate) * ETSPricePerKg * ETSpercentage/100

    return flights_df


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
        return airportPairsTotal,
    elif groupSel == 'AC_Operator':
        pass

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
