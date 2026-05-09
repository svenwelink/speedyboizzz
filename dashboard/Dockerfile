FROM python:3.14

WORKDIR /app

COPY main.py .
COPY functionsForDashboard.py .
COPY dashboardViews.py .

RUN pip install streamlit pandas plotly_express

EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]