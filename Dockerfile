FROM python:3.8.13-slim-buster
EXPOSE 8501
WORKDIR /conflict_analytics
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD streamlit run conflict_analytics.py 