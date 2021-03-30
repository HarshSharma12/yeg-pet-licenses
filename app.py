# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import requests
import datetime
import json
import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

EDM_LAT = 53.5461
EDM_LON = -113.4938

with open("YEG_Neighbourhood_Boundaries.geojson", "r") as fid:
    df_places = json.load(fid)
# with open('full_data.json', 'w') as fid:
#     r = requests.get(url = 'https://data.edmonton.ca/resource/5squ-mg4w.json')
#     data = r.json()
#     json.dump(data, fid)

# +
df = pd.read_csv("Pet__Licenses_by_Neighbourhood.csv")
df = df.dropna()
df_20 = df[df["YEAR"] == 2020]
# df_20_cats = df_20[df_20["PET_TYPE"] == "Cat"]
# df_20_dogs = df_20[df_20["PET_TYPE"] == "Dog"]

count_cats = (
    df_20[df_20["PET_TYPE"] == "Cat"]
    .groupby(["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False)
    .sum()[["COUNT", "NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"]]
    .sort_values(["NEIGHBOURHOOD_ID"])
    .reset_index(drop=True)
)

count_dogs = (
    df_20[df_20["PET_TYPE"] == "Dog"]
    .groupby(["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False)
    .sum()[["COUNT", "NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"]]
    .sort_values(["NEIGHBOURHOOD_ID"])
    .reset_index(drop=True)
)
pet_types = sorted(list(df_20["PET_TYPE"].unique()))
# -

# app = dash.Dash(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# +
print("Plotting fig_pet_hood")
winner_df = (
    df_20.groupby(["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False)["PET_TYPE"]
    .agg(pd.Series.mode)
    .sort_values(["NEIGHBOURHOOD_ID"])
    .reset_index(drop=True)
)


count_pets = winner_df.copy()  # [['NEIGHBOURHOOD','NEIGHBOURHOOD_ID']]
count_pets = count_pets.merge(
    count_cats,
    how="left",
    on=["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"],
    sort=False,
    suffixes=("", "_cats"),
)
count_pets["Cats"] = count_pets["COUNT"]

count_pets.drop(columns=["COUNT"], inplace=True)


count_pets = count_pets.merge(
    count_dogs,
    how="left",
    on=["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"],
    sort=False,
    suffixes=("", "_dogs"),
)
count_pets["Dogs"] = count_pets["COUNT"]

count_pets.drop(columns=["COUNT"], inplace=True)
count_pets["Winner"] = df_20.groupby(
    ["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False
)["PET_TYPE"].agg(
    lambda x: x.value_counts(normalize=True).mul(100).round(2)[0].astype(str) + "%"
)[
    "PET_TYPE"
]
count_pets.fillna(0, inplace=True)
count_pets.to_csv("pet_type.csv", index=False)

# -


pet_type_df = pd.read_csv("pet_type.csv")
fig_pet_hood = px.choropleth_mapbox(
    pet_type_df,
    geojson=df_places,
    locations="NEIGHBOURHOOD",
    color="PET_TYPE",
    featureidkey="properties.name",
    hover_data=["Cats", "Dogs", "Winner"],
    mapbox_style="carto-positron",
    zoom=9,
    center={"lat": EDM_LAT, "lon": EDM_LON},
    opacity=0.5,
)
fig_pet_hood.update_geos(fitbounds="locations", visible=False)
fig_pet_hood.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


# +


@app.callback(
    [Output("choropleth_count", "figure"), Output("choropleth_type", "figure")],
    [Input("pet_type", "value")],
)
def display_choropleth(pet_type):
    filtered_df = df_20[df_20["PET_TYPE"] == pet_type]
    count_df = (
        filtered_df.groupby(["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False)
        .sum()[["COUNT", "NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"]]
        .sort_values(["NEIGHBOURHOOD_ID"])
        .reset_index(drop=True)
    )

    type_df = (
        filtered_df.groupby(["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False)[
            "BREED"
        ]
        .agg(lambda x: x.value_counts().index[0])
        .sort_values(["NEIGHBOURHOOD_ID"])
        .reset_index(drop=True)
    )

    max_value = count_df["COUNT"].max()
    fig_count = px.choropleth_mapbox(
        count_df,
        geojson=df_places,
        locations="NEIGHBOURHOOD",
        color="COUNT",
        color_continuous_scale="jet",
        range_color=(0, max_value),
        featureidkey="properties.name",
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat": EDM_LAT, "lon": EDM_LON},
        opacity=0.5,
    )
    fig_count.update_geos(fitbounds="locations", visible=False)
    fig_count.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    type_df["Percent of total"] = df_20.groupby(
        ["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False
    )["BREED"].agg(
        lambda x: x.value_counts(normalize=True).mul(100).round(2)[0].astype(str) + "%"
    )[
        "BREED"
    ]
    type_df.fillna(0, inplace=True)
    type_df.to_csv(f"{pet_type}_type.csv", index=False)

    type_df = pd.read_csv(f"{pet_type}_type.csv")
    fig_type = px.choropleth_mapbox(
        type_df,
        geojson=df_places,
        locations="NEIGHBOURHOOD",
        color="BREED",
        color_continuous_scale="Reds",
        featureidkey="properties.name",
        hover_data=["Percent of total"],
        mapbox_style="carto-positron",
        zoom=9,
        center={"lat": EDM_LAT, "lon": EDM_LON},
        opacity=0.5,
    )
    fig_type.update_geos(fitbounds="locations", visible=False)
    fig_type.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return [fig_count, fig_type]


# +
# print("Plotting fig_cat_count")
# max_value = count_cats["COUNT"].max()
# fig_cat_count = px.choropleth_mapbox(
#     count_cats,
#     geojson=df_places,
#     locations="NEIGHBOURHOOD",
#     color="COUNT",
#     color_continuous_scale="jet",
#     range_color=(0, max_value),
#     featureidkey="properties.name",
#     mapbox_style="carto-positron",
#     zoom=9,
#     center={"lat": EDM_LAT, "lon": EDM_LON},
#     opacity=0.5,
# )
# fig_cat_count.update_geos(fitbounds="locations", visible=False)
# fig_cat_count.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


# +
# print("Plotting fig_cat_hood")

# cat_type_df = (
#     df_20_cats.groupby(["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False)["BREED"]
#     .agg(pd.Series.mode)
#     .sort_values(["NEIGHBOURHOOD_ID"])
#     .reset_index(drop=True)
# )


# cat_type_df["Percent of total"] = df_20.groupby(
#     ["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False
# )["BREED"].agg(
#     lambda x: x.value_counts(normalize=True).mul(100).round(2)[0].astype(str) + "%"
# )[
#     "BREED"
# ]
# cat_type_df.fillna(0, inplace=True)
# cat_type_df.to_csv("cat_type.csv", index=False)


# cat_type_df = pd.read_csv("cat_type.csv")
# fig_cat_hood = px.choropleth_mapbox(
#     cat_type_df,
#     geojson=df_places,
#     locations="NEIGHBOURHOOD",
#     color="BREED",
#     color_continuous_scale="Reds",
#     featureidkey="properties.name",
#     hover_data=["Percent of total"],
#     mapbox_style="carto-positron",
#     zoom=9,
#     center={"lat": EDM_LAT, "lon": EDM_LON},
#     opacity=0.5,
# )
# fig_cat_hood.update_geos(fitbounds="locations", visible=False)
# fig_cat_hood.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


# +
# print("Plotting fig_dog_count")
# max_value = count_dogs["COUNT"].max()
# fig_dog_count = px.choropleth_mapbox(
#     count_dogs,
#     geojson=df_places,
#     locations="NEIGHBOURHOOD",
#     color="COUNT",
#     color_continuous_scale="jet",
#     range_color=(0, max_value),
#     featureidkey="properties.name",
#     mapbox_style="carto-positron",
#     zoom=9,
#     center={"lat": EDM_LAT, "lon": EDM_LON},
#     opacity=0.5,
# )
# fig_dog_count.update_geos(fitbounds="locations", visible=False)
# fig_dog_count.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


# +
# print("Plotting fig_dog_hood")

# dog_type_df = (
#     df_20_dogs.groupby(["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False)["BREED"]
#     .agg(lambda x: x.value_counts().index[0])
#     .sort_values(["NEIGHBOURHOOD_ID"])
#     .reset_index(drop=True)
# )

# dog_type_df["Percent of total"] = df_20.groupby(
#     ["NEIGHBOURHOOD", "NEIGHBOURHOOD_ID"], as_index=False
# )["BREED"].agg(
#     lambda x: x.value_counts(normalize=True).mul(100).round(2)[0].astype(str) + "%"
# )[
#     "BREED"
# ]
# dog_type_df.fillna(0, inplace=True)
# dog_type_df.to_csv("dog_type.csv", index=False)

# dog_type_df = pd.read_csv("dog_type.csv")
# fig_dog_hood = px.choropleth_mapbox(
#     dog_type_df,
#     geojson=df_places,
#     locations="NEIGHBOURHOOD",
#     color="BREED",
#     featureidkey="properties.name",
#     hover_data=["Percent of total"],
#     mapbox_style="carto-positron",
#     zoom=9,
#     center={"lat": EDM_LAT, "lon": EDM_LON},
#     opacity=0.5,
# )
# fig_dog_hood.update_geos(fitbounds="locations", visible=False)
# fig_dog_hood.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})


# +
maj_pet_type = pet_type_df["PET_TYPE"].value_counts().index[0]
min_pet_type = pet_type_df["PET_TYPE"].value_counts().index[1]

maj_pet_type_cnt = pet_type_df["PET_TYPE"].value_counts()[0]
min_pet_type_cnt = pet_type_df["PET_TYPE"].value_counts()[1]

maj_pet_type_pct = round(
    pet_type_df["PET_TYPE"].value_counts(normalize=True)[0] * 100, 2
)
min_pet_type_pct = round(
    pet_type_df["PET_TYPE"].value_counts(normalize=True)[1] * 100, 2
)
# -

print("Creating app layout")
app.layout = html.Div(
    children=[
        html.H1(
            children="Cats 🐈 or Dogs 🐕?\n",
            style={"text-align": "center", "margin": "5rem"},
        ),
        html.H3(
            children="Are you in a cat majority neighborhood?",
            style={"margin-bottom": "3rem"},
        ),
        html.Div(
            children=f"""
              
              Ever wondered if there are more cats or more dogs in your neighborhood? According to the data from City of Edmonton {maj_pet_type_cnt} neighbouhoods have more {maj_pet_type}s than {min_pet_type}s. That is {maj_pet_type_pct} % of the neighborhoods in the city
              
              Check out the map below to find out if you belong to the elite neighbourhood with more {min_pet_type}s than {maj_pet_type}s
              
              """,
            style={"font-size": "1.7rem"},
        ),
        html.Div([dcc.Graph(figure=fig_pet_hood)]),
        html.H3(
            children="Some other stats about pets in your hood",
            style={"margin-top": "3rem", "margin-bottom": "3rem"},
        ),
        html.H4("Pet Type:"),
        dcc.RadioItems(
            id="pet_type",
            options=[{"value": x, "label": x} for x in pet_types],
            value=pet_types[0],
            labelStyle={"display": "inline-block"},
        ),
        html.Div(
            [
                html.H6(
                    children="Number of licensed pets",
                    style={"text-align": "center", "margin-top": "3rem"},
                ),
                html.Div([dcc.Graph(id="choropleth_count")]),
            ],
        ),
        html.Div(
            [
                html.H6(
                    children="Which breed is most common?",
                    style={"text-align": "center", "margin-top": "3rem"},
                ),
                html.Div([dcc.Graph(id="choropleth_type")]),
            ],
        ),
        html.Div(
            dcc.Link("Created with ❤️ by Harsh Sharma", href="http://hsharma.xyz"),
            style={
                "font-size": "1.5rem",
                "text-align": "center",
                "margin-top": "5rem",
            },
        ),
    ]
)


# +
# app.run_server(debug=True, use_reloader=False)  # Turn off reloader if inside Jupyter

# +

if __name__ == "__main__":
    app.run_server(debug=True)
