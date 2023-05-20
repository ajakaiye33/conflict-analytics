"""
Created on Tue Jun 17 00:59:25 2022
@author: Hedgar Ajakaiye
"""
# import  packages/module
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from scipy import stats
import warnings

warnings.simplefilter(action="ignore")
# import awswrangler as wr


# # universal data bucket
# def extract_country_data(country="Nigeria"):
#    raw_data ="s3://armed-conflict/conflictasat28-05-2023.csv"
#    loaded_data = wr.s3.read_csv(raw_data)
#    filter_country = loaded_data[loaded_data["country"] == country]
#    return filter_country


# data = extract_country_data()

#localize data for deployment
#data = data.to_csv("./data/armed_conflict_data_april2023.csv", index=False)

data = pd.read_csv("./data/armed_conflict_data_april2023.csv")


def clean_shape_data(df):
    """
    clean and transform data
    """
    df = df.drop(
        [
            "assoc_actor_1",
            "interaction",
            "admin3",
            "assoc_actor_2",
            "inter1",
            "inter2",
            "region",
            "geo_precision",
            "source",
            "source_scale",
        ],
        axis=1,
    )
    df["event_date"] = pd.to_datetime(df["event_date"])
    df["dayofweek"] = df["event_date"].dt.dayofweek
    df["day"] = df["event_date"].dt.day
    df["month"] = df["event_date"].dt.month
    df["weekofyear"] = df["event_date"].dt.isocalendar().week
    df["year"] = df["event_date"].dt.year
    df = df.rename(columns={"admin1": "state", "admin2": "lga"})
    df["daysofweek"] = df["dayofweek"].map(
        {
            0: "Sunday",
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
        }
    )
    df["months"] = df["month"].map(
        {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }
    )
    df["actor2"] = df["actor2"].fillna("Suicide Bombers")
    df = df[df["fatalities"] >= 1]
    df["norm_fatal"] = np.log(df["fatalities"])
    df["sharia_status"] = np.where(
        df["state"].isin(["Yobe", "Gombe", "Borno"]),
        "partial-sharia",
        np.where(
            df["state"].isin(
                [
                    "Bauchi",
                    "Jigawa",
                    "Kebbi",
                    "Zamfara",
                    "Kano",
                    "Katsina",
                    "Niger",
                    "Kaduna",
                    "Sokoto",
                ]
            ),
            "state_sharia",
            "No_sharia",
        ),
    )

    df["zscore_fatalities"] = stats.zscore(df["norm_fatal"])

    df["risk_status"] = np.where(
        stats.zscore(df["zscore_fatalities"]) >= 3, "high-risk", "low-risk"
    )
    return df


clean_data = clean_shape_data(data)


def df_cluster_data(df):
    model = KMeans(n_clusters=3, random_state=42)
    model.fit(df[["norm_fatal"]])
    df["clusters"] = model.predict(df[["norm_fatal"]])
    return df


clusters_data = df_cluster_data(clean_data)

# print(clusters_data['clusters'].value_counts())

# filter the data for where primary targets are innocent civilians

civilian_victims = clusters_data[
    clusters_data["event_type"] == "Violence against civilians"
]

# print(civilian_victims)


def cumu_deaths(df):
    df = df.iloc[::-1, [0, 1]]
    df = df.reset_index()
    df = df.drop(["index"], axis=1)
    df["fatalities"] = df["fatalities"].cumsum()
    return df


def civil_death_15():
    civil_deaths = civilian_victims[
        (civilian_victims["year"] >= 1999) & (civilian_victims["year"] <= 2015)
    ]
    filter_death = civil_deaths[["event_date", "fatalities"]]
    cumu_filter = cumu_deaths(filter_death)
    return cumu_filter


def civil_death_now():
    civil_death_n = civilian_victims[civilian_victims["year"] >= 2015]
    filter_death_n = civil_death_n[["event_date", "fatalities"]]
    cumu_filter_n = cumu_deaths(filter_death_n)
    return cumu_filter_n


def killers_15():
    civil_killers = civilian_victims[
        (civilian_victims["year"] >= 1999) & (civilian_victims["year"] <= 2015)
    ]
    return civil_killers


def killers_now():
    civil_killers_n = civilian_victims[civilian_victims["year"] >= 2015]
    return civil_killers_n


def sum_death_15():
    """
    Civilian victims from 1999 to 2015
    """
    filter_dates = civilian_victims[
        (civilian_victims["year"] >= 1999) & (civilian_victims["year"] <= 2015)
    ]
    sum_victim = (
        filter_dates.groupby("event_type").agg({"fatalities": "sum"}).reset_index()
    )
    sum_value = sum_victim.iloc[0, 1]
    return sum_value


def sum_death_now():
    """
    Civilian victims from 2015 till Date
    """
    filter_dates = civilian_victims[civilian_victims["year"] >= 2015]
    sum_victim = (
        filter_dates.groupby("event_type").agg({"fatalities": "sum"}).reset_index()
    )
    sum_value = sum_victim.iloc[0, 1]
    return sum_value


def geopolitical_zone():
    """
    group states into the six geopolitical zones
    """
    col = "state"
    condition = [
        civilian_victims[col].isin(
            [
                "Benue",
                "Kogi",
                "Kwara",
                "Nassarawa",
                "Niger",
                "Plateau",
                "Federal Capital Territory",
            ]
        ),
        civilian_victims[col].isin(
            ["Adamawa", "Bauchi", "Borno", "Gombe", "Taraba", "Yobe"]
        ),
        civilian_victims[col].isin(
            ["Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Sokoto", "Zamfara"]
        ),
        civilian_victims[col].isin(["Abia", "Anambra", "Ebonyi", "Enugu", "Imo"]),
        civilian_victims[col].isin(
            ["Akwa Ibom", "Bayelsa", "Cross River", "Delta", "Edo", "Rivers"]
        ),
        civilian_victims[col].isin(["Ekiti", "Lagos", "Ogun", "Ondo", "Osun", "Oyo"]),
    ]

    classes = [
        "North Central",
        "North East",
        "North West",
        "South East",
        "South South",
        "South West",
    ]

    civilian_victims["geopol_zones"] = np.select(condition, classes, default=np.nan)
    return civilian_victims


geo_dataframe = geopolitical_zone()


def geo_zone_death_15():
    civil_killers = geo_dataframe[
        (geo_dataframe["year"] >= 1999) & (geo_dataframe["year"] <= 2015)
    ]
    civil_killers = (
        civil_killers.groupby("geopol_zones")
        .agg({"norm_fatal": "sum"})
        .reset_index()
        .sort_values(by="norm_fatal", ascending=True)
    )
    return civil_killers


def geo_zone_death_now():
    civil_killers_n = geo_dataframe[geo_dataframe["year"] >= 2015]
    civil_killers_n = (
        civil_killers_n.groupby("geopol_zones")
        .agg({"norm_fatal": "sum"})
        .reset_index()
        .sort_values(by="norm_fatal", ascending=True)
    )
    return civil_killers_n


def state_forces():
    """
    filter state forces personel killed in armed conflict
    """
    state_forces_df = clusters_data[
        clusters_data["actor2"].isin(
            [
                "Military Forces of Nigeria (2015-)",
                "Police Forces of Nigeria (2015-)",
                "Police Forces of Niger (2021-)",
                "Private Security Forces (Nigeria)",
                "Police Forces of Nigeria (2015-) National Drug Law Enforcement Agency",
                "Police Forces of Nigeria (2015-) Ogun State Community, Social Orientation and Safety Corps",
                "Military Forces of Cameroon (1982-)",
                "Police Forces of Nigeria (2015-) Nigeria Customs Service",
                "Police Forces of Nigeria (2015-) Prison Guards",
                "Police Forces of Nigeria (2015-) Department of State Services",
                "Military Forces of Niger (2021-)",
                "Police Forces of Nigeria (2015-) Lagos State Environmental and Special Offences Task Force",
                "Military Forces of Nigeria (2015-) Joint Task Force",
                "Police Forces of Nigeria (2015-) Special Anti-Robbery Squad",
                "Police Forces of Nigeria (2015-) Customs Clearing Agents",
                "Military Forces of Chad (1990-2021)",
                "Police Forces of Nigeria (1999-2015)",
                "Military Forces of Nigeria (1999-2015)",
                "Military Forces of Nigeria (1999-2015) Joint Task Force",
                "Police Forces of Nigeria (1999-2015) Prison Guards",
                "Police Forces of Nigeria (1993-1999)",
                "Military Forces of Nigeria (1993-1999)",
            ]
        )
    ]
    return state_forces_df


state_forces_personnel = state_forces()


def state_forces_15():
    """
    state forces personnel killed in the past 16 years
    """
    state_forcess_killed = state_forces_personnel[
        (state_forces_personnel["year"] >= 1999)
        & (state_forces_personnel["year"] <= 2015)
    ]
    return state_forcess_killed


def state_forces_now():
    """
    state forces personel killed for the past 7 years
    """
    state_forces_killed = state_forces_personnel[state_forces_personnel["year"] >= 2015]
    return state_forces_killed


def military_expend():
    """
    Clean and process military expenditure data
    """
    mil_exp = pd.read_excel(
        "./data/SIPRI-Milex-data-1949-2021.xlsx", sheet_name=2, header=6
    )
    prepro0 = mil_exp.iloc[3:, :]
    prepro1 = prepro0.drop(
        [
            "Notes",
            "Currency",
            "Country",
            1949,
            1950,
            1951,
            1952,
            1953,
            1954,
            1955,
            1956,
            1957,
            1958,
            1959,
        ],
        axis=1,
    )
    tidy_data = prepro1.melt(var_name="calendar_year", value_name="amount")
    return tidy_data


mil_expend_data = military_expend()


def cumu_mil_expediture(df):
    """
    Military expenditur cumulative
    """
    df["amounts"] = df["amount"].cumsum()
    return df


cumulative_expend = cumu_mil_expediture(mil_expend_data)


def military_expend_15():
    """
    Military expenditure from 1999-2014
    """
    filter_data = cumulative_expend[
        (cumulative_expend["calendar_year"] >= 1999)
        & (cumulative_expend["calendar_year"] <= 2014)
    ]
    return filter_data


def military_expend_now():
    """
    Military expenditure from 2015-2021
    """
    filter_data = cumulative_expend[cumulative_expend["calendar_year"] >= 2015]
    return filter_data
    
    
# sum of civilians killed in the following states: Benue, Kaduna, Plateau
def bkp_deaths():
    bkp = civilian_victims[civilian_victims['state'].isin(['Benue','Kaduna','Plateau'])]
    bkp_by1 = bkp[bkp['year'] <= 2014]
    bkp_by2 = bkp[bkp['year'] >= 2015]
    bkp_grp1 = bkp_by1.groupby(['state']).agg({'fatalities':'sum'}).reset_index()
    bkp_grp2 = bkp_by2.groupby(['state']).agg({'fatalities':'sum'}).reset_index()
    return bkp_grp1,bkp_grp2

    # bkpb42015 = bkp_grp[bkp_grp['year'] <= 2014]
    # bkpfrm2016 = bkp_grp[bkp_grp['year'] >= 2015]
    # return bkpb42015, bkpfrm2016
if __name__ == "__main__":
    bkp_deaths()