import pandas as pd

def timeToCentiseconds(t):
    minuten, seconden = t.split(":")
    s = float(seconden)
    return int(minuten) * 6000 + int(round(s * 100))

def timeToFormat(cs):
    min = cs // 6000
    rest = cs % 6000
    seconden = rest / 100

    if min > 0:
        return f"{int(min)}:{seconden:05.2f}"

    if seconden < 1:
        return f"{seconden:.1f}"

    return f"{seconden:.2f}"

def calculateRestTime(row, df):
    if pd.isna(row["prev_runId"]):
        return None

    team = row["Team"]
    start = int(row["prev_runId"] + 1)
    end = int(row["runId"] - 1)

    subset = df[
        (df["Team"] == team) &
        (df["runId"].between(start, end))
    ]

    return subset["Tijd_cs"].sum()

def getNameList(df:pd.DataFrame):
    nameList = list(set(df["Naam"].tolist()))
    nameList.append("Alles")
    nameList.sort()
    return nameList

def prepSummaryTable(df):
    df["Tijd_cs"] = df["Tijd"].apply(timeToCentiseconds)
    df = df.sort_values(["Naam", "Ronde"])

    df["Verschil"] = df.groupby("Naam")["Tijd_cs"].diff().abs()

    summaryTable = (
        df.groupby("Naam")
        .agg(
            Gemiddelde_Tijd=("Tijd_cs", "mean"),
            Standaarddeviatie=("Tijd_cs", "std"),
            Snelste_Ronde=("Tijd_cs", "min"),
            Traagste_Ronde=("Tijd_cs", "max"),
            Grootste_Verschil=("Verschil", "max"),
        ).reset_index())
    
    summaryTable["Verschil_Snelste_Traagste"] = summaryTable["Traagste_Ronde"] - summaryTable["Snelste_Ronde"]
    summaryRest = prepRestTime(df)

    summaryTable = summaryTable.merge(summaryRest, on="Naam", how="left")
    return formatSummaryTable(summaryTable)

def prepRestTime(df):
    df = df.sort_values(["Team", "runId", "Naam"])
    df["prev_runId"] = df.groupby("Naam")["runId"].shift()

    df["Rusttijd_cs"] = df.apply(lambda x: calculateRestTime(x, df), axis=1)

    dfRest = df.groupby("Naam").agg(Gemiddelde_Rusttijd=("Rusttijd_cs", "mean")).reset_index()
    return dfRest

def formatSummaryTable(summaryTable):
    columns = [
        "Gemiddelde_Tijd",
        "Standaarddeviatie",
        "Snelste_Ronde",
        "Traagste_Ronde",
        "Grootste_Verschil",
        "Verschil_Snelste_Traagste",
        "Gemiddelde_Rusttijd"
    ]

    for column in columns:
        summaryTable[column] = summaryTable[column].apply(timeToFormat)

    summaryTable.columns = ["Naam", "Gemiddelde ronde tijd", "Standaarddeviatie", "Snelste ronde", "Traagste ronde", "Grootste verschil tussen twee rondes", "Totaal verschil", "Gemiddelde rusttijd"]
    return summaryTable

def getPivotForSelected(df, names):
    dfFilterd = df[df["Naam"].isin(list(names))]
    pivotTable = pd.pivot_table(
        dfFilterd,
        values="Tijd",
        index="Ronde",
        columns="Naam",
        aggfunc="sum"
    )

    return pivotTable