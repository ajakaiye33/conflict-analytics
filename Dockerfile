FROM python:3.8.13-slim-buster
EXPOSE 8501
WORKDIR /conflict_analytics
COPY requirement.txt ./requirement.txt
RUN pip install -r requirement.txt
COPY . .
CMD streamlit run conflict_analytics.py 