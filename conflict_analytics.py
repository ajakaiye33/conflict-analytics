"""
Created on Tue Jun 17 00:59:25 2022
@author: Hedgar Ajakaiye
"""
from urllib.request import urlopen
import json
import streamlit as st
import matplotlib
import plotly.express as px

# import plotly.graph_objects as go
# import matplotlib.pyplot as plt
from millify import prettify
#from data_prep.data_wrang import clean_data
from data_prep.data_wrang import civil_death_15
from data_prep.data_wrang import civil_death_now
from data_prep.data_wrang import killers_15
from data_prep.data_wrang import killers_now
from data_prep.data_wrang import sum_death_15
from data_prep.data_wrang import sum_death_now
from data_prep.data_wrang import geo_zone_death_15
from data_prep.data_wrang import geo_zone_death_now

# import streamlit.components.v1 as components


matplotlib.use("agg")


st.set_page_config(
    page_icon=":bomb:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown("<style> body {color: white;}</style>", unsafe_allow_html=True)
st.markdown(
    "<h1 style='text-align: center; margin-top: 15px;'>Nigeria Armed Conflict Dashboard</h1>",  # noqa
    unsafe_allow_html=True,
)
st.markdown(
    "<style> .css-18c15ts {padding-top: 1rem; margin-top:-75px;} </style>",
    unsafe_allow_html=True,
)

st.markdown(
    """ <style>
# MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """,
    unsafe_allow_html=True,
)


#st.title("NSE Live Dashboard")
st.text(
    "Datat Source: ACLED https://acleddata.com/"
    )

death_cumu_civil = civil_death_15()
civilian_death_till_date = civil_death_now()
pre_bu = killers_15()
bubu = killers_now()
sixteen_years_death = sum_death_15()
eight_years_deaths = sum_death_now()
geo_15 = geo_zone_death_15()
geo_now = geo_zone_death_now()


def civilian_death_2015():
    pre_bubu, now_bubu = st.columns(2)
    with pre_bubu:
        fig = px.line(
            death_cumu_civil,
            x="event_date",
            y="fatalities",
            title="Civilian Deaths From Armed Conflict 1999-2015",
            labels={"event_date": "Date", "fatalities": "Deaths"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with now_bubu:
        fig = px.line(
            civilian_death_till_date,
            x="event_date",
            y="fatalities",
            title="Civilian Deaths From Armed Conflict 2015-2022",
            labels={"event_date": "Date", "fatalities": "Deaths"},
        )
        st.plotly_chart(fig, use_container_width=True)


def death_metric():
    death_metric1, death_metric2 = st.columns(2)
    death_metric1.metric(
        label="Civilian Deaths for the past 16 Years",
        value=f"{prettify(sixteen_years_death)}",
    )
    death_metric2.metric(
        label="Civilian Deaths for the past 7 Years",
        value=f"{prettify(eight_years_deaths)}",
    )


def killerz():
    (
        prebubu_kilers,
        bubu_killers,
    ) = st.columns(2)
    with prebubu_kilers:
        fig = px.sunburst(
            pre_bu,
            path=["state", "actor1"],
            values="norm_fatal",
            title="Civilian Killers By State 1999-2015",
        )
        st.plotly_chart(fig, use_container_width=True)
    with bubu_killers:
        fig = px.sunburst(
            bubu,
            path=["state", "actor1"],
            values="norm_fatal",
            title="Civilian Killers By State 2015-2022",
        )
        st.plotly_chart(fig, use_container_width=True)


def killers_sharia_state():
    pre_bubu_sharia, bubu_killers_sharia = st.columns(2)
    with pre_bubu_sharia:
        fig = px.sunburst(
            pre_bu,
            path=["sharia_status", "actor1"],
            values="norm_fatal",
            title="Civilian Killers By State's Sharia Status 1999-2015",
        )
        st.plotly_chart(fig, use_container_width=True)

    with bubu_killers_sharia:
        fig = px.sunburst(
            bubu,
            path=["sharia_status", "actor1"],
            values="norm_fatal",
            title="Civilian Killers By  State's Sharia Status 2015-2022",
        )
        st.plotly_chart(fig, use_container_width=True)


def geo_risk():
    """
    visualize civilian deaths from armed conflict by geopolitical zones and by risk status
    """
    geo_16, geo_8 = st.columns(2)

    with geo_16:
        fig = px.bar(
            geo_15,
            x="norm_fatal",
            y="geopol_zones",
            title="Civilian Death by Geopolitical Zone 1999-2015",
            labels={"geopol_zones": "Zones", "norm_fatal": "Civilian Deaths"},
            orientation="h",
        )
        st.plotly_chart(fig)
    with geo_8:
        fig = px.bar(
            geo_now,
            x="norm_fatal",
            y="geopol_zones",
            title="Civilian Death By Geopolitical Zone 2015-2022",
            labels={"geopol_zones": "Zones", "norm_fatal": " Civilian Deaths"},
            orientation="h",
        )
        st.plotly_chart(fig)


with urlopen(
    "https://gist.githubusercontent.com/sdwfrost/6c0ccf457e30963292522dc57ed1fe7a/raw/4023566e3b23d6a518d3c88d35b97ded46756544/nigeria_states.geojson"
) as response:
    states = json.load(response)

bycounties = pre_bu.groupby("state").agg({"norm_fatal": "sum"}).reset_index()
bycounties_bu = bubu.groupby("state").agg({"norm_fatal": "sum"}).reset_index()


def conflict_map():
    map_prebubu, map_bubu = st.columns(2)
    with map_prebubu:
        fig = px.choropleth(
            bycounties,
            geojson=states,
            locations="state",
            featureidkey="properties.name_1",
            color="norm_fatal",
            projection="mercator",
            color_continuous_scale="Reds",
            labels={"norm_fatal": "Civilian Deaths"},
            title="Total Civilian Deaths By State 1999-2015",
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig)
    with map_bubu:
        fig = px.choropleth(
            bycounties_bu,
            geojson=states,
            locations="state",
            featureidkey="properties.name_1",
            color="norm_fatal",
            projection="mercator",
            color_continuous_scale="Reds",
            labels={"norm_fatal": "Civilian Deaths"},
            title="Total Civilian Deaths By State 2015-2022",
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig)


if __name__ == "__main__":
    civilian_death_2015()
    death_metric()
    killerz()
    killers_sharia_state()
    geo_risk()
    conflict_map()
