# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
import json

# +
with open('YEG_Neighbourhood_Boundaries.geojson','r') as fid:
    df_places = json.load(fid)

df = pd.read_csv('Pet__Licenses_by_Neighbourhood.csv')
df = df.dropna()
df.head()

# -

df_20 = df[df['YEAR']==2020]
print (df.shape, df_20.shape)

# -

df_20_cats = df_20[df_20['PET_TYPE']=='Cat']
df_20_dogs = df_20[df_20['PET_TYPE']=='Dog']
print(df_20_cats.shape[0],df_20_dogs.shape[0])


count_cats = df_20_cats.groupby(
    ['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],as_index=False).sum()[
    ['COUNT','NEIGHBOURHOOD','NEIGHBOURHOOD_ID']].sort_values(['NEIGHBOURHOOD_ID']).reset_index(drop=True)
max_value = count_cats['COUNT'].max()
fig = px.choropleth_mapbox(count_cats, geojson=df_places, locations='NEIGHBOURHOOD_ID',       
                           color='COUNT',
                           featureidkey="properties.number",
                           color_continuous_scale="jet",
                           mapbox_style="carto-positron",
                          zoom=9, center = {"lat":53.5461, "lon":-113.4938},
                           opacity=0.5)
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

count_cats = df_20_cats.groupby(
    ['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],as_index=False).sum()[
    ['COUNT','NEIGHBOURHOOD','NEIGHBOURHOOD_ID']].sort_values(['NEIGHBOURHOOD_ID']).reset_index(drop=True)
max_value = count_cats['COUNT'].max()
fig = px.choropleth(count_cats, geojson=df_places, locations='NEIGHBOURHOOD_ID',       
                           color='COUNT',
                           color_continuous_scale="Viridis",
#                            range_color=(0, max_value),
                           featureidkey="properties.number",
                           projection="mercator"
                          )
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

count_dogs = df_20_dogs.groupby(
    ['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],as_index=False).sum()[
    ['COUNT','NEIGHBOURHOOD','NEIGHBOURHOOD_ID']].sort_values(['NEIGHBOURHOOD_ID']).reset_index(drop=True)
max_value = count_dogs['COUNT'].max()
fig = px.choropleth(count_dogs, geojson=df_places, locations='NEIGHBOURHOOD_ID',       
                           color='COUNT',
                           color_continuous_scale="Viridis",
#                            range_color=(0, max_value),
                           featureidkey="properties.number",
                           projection="mercator"
                          )
fig.update_geos(fitbounds="locations", visible=False)
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()



# +
count_series = df_20.groupby(
    ['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],as_index=False)['PET_TYPE'].agg(
    pd.Series.mode).sort_values(['NEIGHBOURHOOD_ID']).reset_index(drop=True)



final_df = count_series.copy()#[['NEIGHBOURHOOD','NEIGHBOURHOOD_ID']]
final_df = final_df.merge(count_cats, how='left', 
               on=['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],
                sort=False, suffixes=('', '_cats')) 
final_df['Cats'] = final_df['COUNT']

final_df.drop(columns=['COUNT'], inplace=True)


final_df = final_df.merge(count_dogs, how='left', 
               on=['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],
                sort=False, suffixes=('', '_dogs')) 
final_df['Dogs'] = final_df['COUNT']

final_df.drop(columns=['COUNT'], inplace=True)
final_df['Winner'] = df_20.groupby(
    ['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],as_index=False)['PET_TYPE'].agg(
    lambda x:x.value_counts(normalize=True).mul(100).round(2)[0].astype(str) + '%')['PET_TYPE']
final_df.fillna(0, inplace=True)
final_df.to_csv('pet_type.csv', index=False)

# -

pet_type_df = pd.read_csv('pet_type.csv')
fig = px.choropleth(pet_type_df, geojson=df_places, locations='NEIGHBOURHOOD_ID',       
                           color='PET_TYPE',
#                            color_continuous_scale="Viridis",
                           featureidkey="properties.number",
                                               projection="mercator", 
                    hover_data=["Cats", "Dogs", 'Winner'])
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()


# # Cat Type

# +
count_series = df_20_cats.groupby(
    ['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],as_index=False)['BREED'].agg(
    pd.Series.mode).sort_values(['NEIGHBOURHOOD_ID']).reset_index(drop=True)



final_df = count_series.copy()#[['NEIGHBOURHOOD','NEIGHBOURHOOD_ID']]
final_df = final_df.merge(count_cats, how='left', 
               on=['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],
                sort=False, suffixes=('', '_cats')) 
final_df['Cats'] = final_df['COUNT']

final_df.drop(columns=['COUNT'], inplace=True)

final_df['Percent of total'] = df_20.groupby(
    ['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],as_index=False)['BREED'].agg(
    lambda x:x.value_counts(normalize=True).mul(100).round(2)[0].astype(str) + '%')['BREED']
final_df.fillna(0, inplace=True)
final_df.to_csv('cat_type.csv', index=False)

# -

pet_type_df = pd.read_csv('cat_type.csv')
fig = px.choropleth(pet_type_df, geojson=df_places, locations='NEIGHBOURHOOD_ID',       
                           color='BREED',
#                            color_continuous_scale="Viridis",
                        color_continuous_scale='Reds',

                           featureidkey="properties.number",
                                               projection="mercator", 
                    hover_data=['Percent of total'])
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()


# # Dog Type

# +
count_series = df_20_dogs.groupby(
    ['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],as_index=False)['BREED'].agg(
    lambda x:x.value_counts().index[0]).sort_values(['NEIGHBOURHOOD_ID']).reset_index(drop=True)

final_df = count_series.copy()#[['NEIGHBOURHOOD','NEIGHBOURHOOD_ID']]
final_df['Percent of total'] = df_20.groupby(
    ['NEIGHBOURHOOD','NEIGHBOURHOOD_ID'],as_index=False)['BREED'].agg(
    lambda x:x.value_counts(normalize=True).mul(100).round(2)[0].astype(str) + '%')['BREED']
final_df.fillna(0, inplace=True)
final_df.to_csv('dog_type.csv', index=False)

# -

pet_type_df = pd.read_csv('dog_type.csv')
fig = px.choropleth(pet_type_df, geojson=df_places, locations='NEIGHBOURHOOD_ID',       
                           color='BREED',
#                            color_continuous_scale="Viridis",
                           featureidkey="properties.number",
                                               projection="mercator", 
                    hover_data=['Percent of total'])
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()




to_remove = list(df_20_dogs['BREED'].value_counts(normalize=True).index[16:])
df_20_dogs['BREED'].replace(to_remove, 'OTHERS', inplace=True)
