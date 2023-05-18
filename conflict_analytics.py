"""
Created on Tue June 30 00:59:25 2022
@author: Hedgar Ajakaiye
"""
from urllib.request import urlopen
import json
import streamlit as st
import matplotlib
import plotly.express as px
from millify import prettify
from data_prep.data_wrang import civil_death_15
from data_prep.data_wrang import civil_death_now
from data_prep.data_wrang import killers_15
from data_prep.data_wrang import killers_now
from data_prep.data_wrang import sum_death_15
from data_prep.data_wrang import sum_death_now
from data_prep.data_wrang import geo_zone_death_15
from data_prep.data_wrang import geo_zone_death_now
from data_prep.data_wrang import state_forces_15
from data_prep.data_wrang import state_forces_now
from data_prep.data_wrang import military_expend_15
from data_prep.data_wrang import military_expend_now


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


# st.title("NSE Live Dashboard")
st.text(
    "Datat Sources:1.ACLED https://acleddata.com/, 2.https://sipri.org/databases/milex; Last updated:28-04-2023"
)


def civilian_death_2015():
    """
    Visualize innocent citizen murdered over the years
    """
    death_cumu_civil = civil_death_15()
    civilian_death_till_date = civil_death_now()
    pre_bubu, now_bubu = st.columns(2)
    with pre_bubu:
        fig = px.line(
            death_cumu_civil,
            x="event_date",
            y="fatalities",
            title="Innocent Civilians Deaths Trend 1999-2015",
            labels={"event_date": "Date", "fatalities": "Deaths"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with now_bubu:
        fig = px.line(
            civilian_death_till_date,
            x="event_date",
            y="fatalities",
            title="Innocent Civilians Deaths Trend 2015-2022",
            labels={"event_date": "Date", "fatalities": "Deaths"},
        )
        st.plotly_chart(fig, use_container_width=True)


def death_metric():
    """
    Number of innocent citizens murdered over the years
    """
    sixteen_years_death = sum_death_15()
    eight_years_deaths = sum_death_now()
    death_metric1, death_metric2 = st.columns(2)
    death_metric1.metric(
        label="Innocent Civilians Murdered in the past 16 Years",
        value=f"{prettify(sixteen_years_death)}",
    )
    death_metric2.metric(
        label="Innocent Civilian Murdered in the past 7 Years",
        value=f"{prettify(eight_years_deaths)}",
    )


def state_forces_killed_metric():
    """
    Number of state forces-military and police that have been murdered over the  years
    """
    force_15 = state_forces_15()
    force_now = state_forces_now()
    metric_force_15 = force_15["fatalities"].sum()
    metric_force_now = force_now["fatalities"].sum()
    state_force_16, state_force_7 = st.columns(2)
    state_force_16.metric(
        label="State Forces(Military & Police) Murdered in the past 16 years",
        value=f"{prettify(metric_force_15)}",
    )
    state_force_7.metric(
        label="State Forces(Military & Police) Murdered in the past 7 years",
        value=f"{prettify(metric_force_now)}",
    )


def military_expenditure_viz():
    """
    Visualize Military expenditure over the years
    """
    pre_buhari_regime = military_expend_15()
    buhari_regime = military_expend_now()
    then_expen, now_expend = st.columns(2)
    with then_expen:
        fig = px.line(
            pre_buhari_regime,
            x="calendar_year",
            y="amounts",
            title="Expenditure on the Military 1999-2014",
            labels={"amounts": "Amount", "calendar_year": "Year"},
        )
        st.plotly_chart(fig)
    with now_expend:
        fig = px.line(
            buhari_regime,
            x="calendar_year",
            y="amounts",
            title="Expenditure on the Military 2015-2021",
            labels={"amounts": "Amount", "calendar_year": "Year"},
        )
        st.plotly_chart(fig)


def military_expend_metric():
    """
    Military expenditure metrics
    """
    pre_buhari_regime = military_expend_15()
    buhari_regime = military_expend_now()
    sum_prev_regime_data = pre_buhari_regime["amount"].sum()/1000000000000
    sum_current_regime_data = buhari_regime["amount"].sum()/1000000000000
    military_spend_metric1, military_spend_metric_2 = st.columns(2)
    military_spend_metric1.metric(
        label="Amount spent on Military 1999-2014",
        value=f"{prettify(round(sum_prev_regime_data,3))} Trillion Naira",
    )
    military_spend_metric_2.metric(
        label="Amount spent on Miliary 2015-2021",
        value=f"{prettify(round(sum_current_regime_data,3))} Trillion Naira",
    )


def killerz():
    """
    Visualize the actors-killers of innocent citizens
    """
    pre_bu = killers_15()
    bubu = killers_now()
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


def state_forces_killers():
    """
    visualize state forces- miliitary and police deaths in  armed conflict
    """
    force_15 = state_forces_15()
    force_now = state_forces_now()
    pre_state_killers, now_state_killers = st.columns(2)
    with pre_state_killers:
        fig = px.sunburst(
            force_15,
            path=["state", "actor1"],
            values="norm_fatal",
            title="State Forces Killers by State 1999-2015",
        )
        st.plotly_chart(fig, use_container_width=True)
    with now_state_killers:
        fig = px.sunburst(
            force_now,
            path=["state", "actor1"],
            values="norm_fatal",
            title="State Forces Killers by State 2015-2022",
        )
        st.plotly_chart(fig, use_container_width=True)


def killers_sharia_state():
    """
    Visualize the impact of sharia status on Fatalities across states
    """
    pre_bu = killers_15()
    bubu = killers_now()
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
    geo_15 = geo_zone_death_15()
    geo_now = geo_zone_death_now()
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


def conflict_map():
    """
    Visualize fatalities across states on the  Nigeria Map
    """
    pre_bu = killers_15()
    bubu = killers_now()
    bycounties = pre_bu.groupby("state").agg({"norm_fatal": "sum"}).reset_index()
    bycounties_bu = bubu.groupby("state").agg({"norm_fatal": "sum"}).reset_index()
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
    military_expenditure_viz()
    military_expend_metric()
    state_forces_killed_metric()
    killerz()
    state_forces_killers()
    killers_sharia_state()
    geo_risk()
    conflict_map()
