import pandas as pd
import sqlite3
import datetime
import math

monthLabels = {"1": "Januari",
               "2": "Februari",
               "3": "Maart",
               "4": "April",
               "5": "Mei",
               "6": "Juni",
               "7": "Juli",
               "8": "Augustus",
               "9": "September",
               "10": "Oktober",
               "11": "November",
               "12": "December"
               }

colorMap = {"Name": "#FF00FF"}

# load data WISSEL PATH VOOR SERVER VERSION
DB_PATH = "/app/data/data.db"
# DB_PATH = "dashboard/data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    conn.commit()
    return conn

def loadData(conn):
    return pd.read_sql("SELECT ActivityId, " \
                              "Date, " \
                              "Distance, " \
                              "Name " \
                        "FROM activities", 
                        conn)

def loadAndPrepareData():
    df = loadData(init_db())
    df["Date"] = pd.to_datetime(df["Date"])
    df = df[df["Date"].between("2026-01-01", "2026-12-31")]
    df["Date"] = df["Date"].dt.date
    return df

def labelMonth(df:pd.DataFrame):
    df["MonthName"] = df["Month"].astype(str)
    df["MonthName"] = df["MonthName"].map(monthLabels)
    return df
    
def getDataGroupedPerMonth(df:pd.DataFrame):
    df.sort_values(["Date", "Name"])
    df["Month"] = df["Date"].map(lambda x: x.month)
    dfGrouped = pd.DataFrame({"Distance": df.groupby(["Month", "Name"])["Distance"].sum().round(1)}).reset_index()

    return dfGrouped

def getMonthPivotTable(df:pd.DataFrame):
    pivotTable = df.pivot(index="Month", columns="Name", values="Distance").fillna(0)
    pivotTable = pivotTable[list(set(df["Name"].dropna()))]
    pivotTable.index = pivotTable.index.astype(str)
    pivotTable = pivotTable.rename(index = monthLabels)
    pivotTable["Totaal"] = pivotTable.sum(axis=1)
    pivotTable.loc["Totaal"] = pivotTable.sum(axis=0)
    pivotTable.index.names = ["Maand"]

    return pivotTable

def makeDataForMonthGraph(df:pd.DataFrame):
    dfMonths = getDataGroupedPerMonth(df)
    emptyMonths = pd.DataFrame({"Month": [int(i) for i in range(1, 13)],
                               "Distance": [0 for i in range(1,13)]
                               })
    
    newMonths = emptyMonths[~emptyMonths["Month"].isin(dfMonths["Month"])]
    dfMonths = pd.concat([dfMonths, newMonths], ignore_index=True)
    dfMonths = labelMonth(dfMonths)
    
    return dfMonths

def getNameList(df:pd.DataFrame):
    nameList = list(set(df["Name"].tolist()))
    nameList.append("Alles")
    nameList.sort()
    return nameList

def getCumulutiveDistancePerDay(df:pd.DataFrame, year=2026):
    start = pd.Timestamp(min(pd.Timestamp.today().year, year), 1, 1)
    end = min(pd.Timestamp.today().normalize(), pd.Timestamp(year, 12, 31))
    all_days = pd.date_range(start, end, freq='D')

    dfGrouped  = pd.DataFrame({"Distance": df.groupby(["Date"])["Distance"].sum().round(3)})
    dfGrouped = dfGrouped.reindex(all_days, fill_value=0)
    dfGrouped['CumulativeDistance'] = dfGrouped['Distance'].cumsum()

    return dfGrouped["CumulativeDistance"]

def getProjectedDistance(year=2026, distanceGoal=7500):
    start = pd.Timestamp(min(pd.Timestamp.today().year, year), 1, 1)
    end = pd.Timestamp(year, 12, 31)
    all_days = pd.date_range(start, end, freq='D')

    distancePerDay = distanceGoal / len(all_days)

    dfProjected = pd.DataFrame({'Date': all_days})
    dfProjected = dfProjected.reindex(all_days)
    dfProjected['DistancePerDay'] = distancePerDay

    dfProjected['ProjectedDistance'] = dfProjected['DistancePerDay'].cumsum()

    return dfProjected["ProjectedDistance"]

def getDataDistanceOverYear(df:pd.DataFrame, year=2026, distanceGoal=7500):
    dfRun = pd.DataFrame(getCumulutiveDistancePerDay(df, year=year))
    dfProjected = pd.DataFrame(getProjectedDistance(year=year, distanceGoal=distanceGoal))

    dfDistanceses = dfRun.join(dfProjected, how="outer")
    dfDistanceses.index.name = "Date"
    dfDistanceses = dfDistanceses.reset_index()

    dfDistanceses["Totale afstand"] = dfDistanceses["CumulativeDistance"]
    dfDistanceses["Doel"] = dfDistanceses["ProjectedDistance"]
    dfDistanceses["Datum"] = dfDistanceses["Date"]

    dfForPolot = dfDistanceses.melt(
        id_vars='Datum',
        value_vars=['Totale afstand', 'Doel'],
        var_name='Type',
        value_name='Afstand'
        )
           
    return dfForPolot

def getEddingtonDataForPerson(df:pd.DataFrame):
    dfGrouped = df.groupby('Date', as_index=False)['Distance'].sum()

    schema = {"EddingtonDistance": "int", "RunCount": "int"}
    dfEddingtonPerson = pd.DataFrame(columns=schema.keys()).astype(schema)
    maxDistance = math.floor(dfGrouped["Distance"].max())
    
    for iDistance in range(1, maxDistance + 1):
        dfEddingtonPerson.loc[len(dfEddingtonPerson)] = {"EddingtonDistance": iDistance, "RunCount": len(dfGrouped[dfGrouped["Distance"] >= iDistance])}

    return dfEddingtonPerson
