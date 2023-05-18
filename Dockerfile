FROM python:3.10.11-slim-buster
WORKDIR /conflict_analytics
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8501
COPY . /conflict_analytics
#CMD streamlit run conflict_analytics.py
ENTRYPOINT ["streamlit", "run", "conflict_analytics.py", "--server.port=8501"] 