# load librarys
import streamlit as st
import functionsForDashboard
import dashboardViews

st.set_page_config(
    page_title="Speedyboysss", 
    page_icon=":athletic_shoe:", 
    layout="wide"
)

df = functionsForDashboard.loadAndPrepareData()

st.title("Afstand tabel")
st.text("Hieronder is te zien hoeveel afstand er tot nu toe per persoon is afgelegd. Deze afstanden in deze tabel zijn " \
"afgerond per maand, per persoon. Hierdoor kan het totaal in deze tabel mogelijk iets verschillen van het totaal dat " \
"op een andere plek wordtd getoond. Berekeningen worden altijd gedaan op de gelopen afstanden in meters. " \
"Om de leesbaarheid van de data te verbeteren, wordt er voordat de data wordt getoond afgerond op 100 meter.")

# Group the data
dfGroupedMonth = functionsForDashboard.makeDataForMonthGraph(df)
dfGroupedMonthPivot = functionsForDashboard.getMonthPivotTable(dfGroupedMonth)

# Show the data
st.dataframe(dfGroupedMonthPivot[dfGroupedMonthPivot["Totaal"] > 0],
         width="stretch",
         height="content",
         column_order=(sorted(dfGroupedMonthPivot.columns.values.tolist()[0:-1]) + ["Totaal"]) #Sort columns alphabetically
)

st.subheader("Extra inzichten")

selectedView = st.selectbox("Selecteer hier welke informatie je wil tonen", options = dashboardViews.views)

dashboardViews.getView(selectedView, df)
