FROM python:3.8.13-slim-buster
EXPOSE 8501
WORKDIR /conf_viz
COPY requirement.txt ./requirement.txt
RUN pip install -r requirements.txt
COPY . .
CMD streamlit run conflict_analytics.py 