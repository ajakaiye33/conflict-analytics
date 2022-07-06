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
#import awswrangler as wr

# universal data bucket
# def extract_country_data(country="Nigeria"):
# raw_data = (
#     "s3://armed-conflict/1997-01-01-2022-06-20-Middle_Africa-Western_Africa.csv"
# )
# loaded_data = wr.s3.read_csv(raw_data)
# filter_country = loaded_data[loaded_data["country"] == country]
# return filter_country


# data = extract_country_data()

# localize data for deployment
# data = data.to_csv("./data/armed_conflict_data_june2022.csv", index=False)

data = pd.read_csv("./data/armed_conflict_data_june2022.csv")


def clean_shape_data(df):
    df = df.drop(
        [
            "data_id",
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
    df["weekofyear"] = df["event_date"].dt.weekofyear
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
    # df['norm_fatal'] = (df['fatalities'] - df['fatalities'].min())/ (df['fatalities'].max() - df['fatalities'].min())
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
