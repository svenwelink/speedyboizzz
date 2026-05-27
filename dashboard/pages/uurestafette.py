import streamlit as st
import pandas as pd
import pages.helpers.uurestafetteFunctions as func
import pages.helpers.uurestafetteViews as view
import plotly.express as px

st.set_page_config(
    page_title="uurestafette", 
    page_icon=":athletic_shoe:", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* Hele sidebar */
section[data-testid="stSidebar"] {
    display: none;
}
/* Navigatie in sidebar */
[data-testid="stSidebarNav"] {
    display: none;
}
/* Toggle knop (driehoekjes / hamburger) */
button[kind="header"] {
    display: none;
}
/* Extra header spacing opruimen */
[data-testid="stHeader"] {
    height: 0rem;
}
</style>
""", unsafe_allow_html=True)

st.title("Uurestafette")

st.write("Hieronder zijn de resultaten van de uurestafette te zien.")

df = pd.read_csv("dashboard/pages/helpers/uurestafetteData.csv")

dfSummaryTable = func.prepSummaryTable(df)
st.table(dfSummaryTable)

namesSelected = st.multiselect("Verglijk ronde tijden", options=func.getNameList(df), max_selections = 6)
st.table(func.getPivotForSelected(df, namesSelected))