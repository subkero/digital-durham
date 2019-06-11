import requests
import pandas as pd

import folium
import geopandas as gpd

import secrets1  # .gitignore, contains API key for Census

# "percent of households without internet access, you would calculate it by doing B28002_013 / B28002_001."
# https://acsdatacommunity.prb.org/acs-data-issues/acs-basics/f/10/t/451

def get_internetData(df):
    """
    Inputs: dataframe with Census tract column called 'NAMELSAD'
    Output: dataframe with Durham County, NC census data for internet usage added
    """
    base_url=('https://api.census.gov/data/2017/acs/acs5?get=B28002_013E,NAME'
    '&for=tract:*&in=state:37%20county:063&key='+secrets1.AppKey['Census'])
    
    base_url2=('https://api.census.gov/data/2017/acs/acs5?get=B28002_001E,NAME'
    '&for=tract:*&in=state:37%20county:063&key='+secrets1.AppKey['Census'])
 
    table2=census_query(base_url)  # Calls function below which does the heavy lifting
    table2.rename(columns={"B28002_013E":'NoIntrnt'}, inplace=True)
 
    table3=census_query(base_url2)  # Calls function below which does the heavy lifting
    table3.rename(columns={"B28002_001E":'Households'}, inplace=True)
 
    table2['IntrntRate']=(table2['NoIntrnt'].astype(int)*100).div(table3['Households'].astype(int),fill_value=1)
    table2['IntrntRate']=table2['IntrntRate'].astype(float).apply(lambda x:round(x,2))
    tables=pd.merge(table2,df, on='NAMELSAD')     
         
    return tables

    
def census_query(base_url):
    """
    Allows for different endpoints to be input for different queries to census API
    Input: URL
    Output: dataframe with relevant fields & values
    """# 
    r=requests.get(base_url)
    tables = pd.read_json(r.text)
    tables.columns=tables.iloc[0]
    tables.drop(tables.head(1).index, inplace=True)
    first_getter=lambda x: x.split(',')[0]
    tables['NAMELSAD']=tables['NAME'].apply(first_getter)
    tables.drop(['state', 'county'], axis=1, inplace=True)
    
    return tables

#Import NC tracts shapefiles
nc_tracts=gpd.read_file("zip://./Censustract_2017_37_tract.zip")

nc_tracts= gpd.GeoDataFrame(get_internetData(nc_tracts)) # adds columns with Data on households' internet 
durm_tracts=nc_tracts[nc_tracts['COUNTYFP']=='063'] # restrict to Durham tracts
durm_tracts.crs = {'init' :'epsg:4326'}

m = folium.Map(location=[36.04, -78.850], zoom_start=10.5) #basemap

folium.Choropleth(
    durm_tracts,
    name='choropleth',
    data=durm_tracts,
    columns=['NAMELSAD','IntrntRate'],
    key_on='feature.properties.NAMELSAD',
    fill_color='YlOrBr', 
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Durham County households without internet access (%)'
).add_to(m)

# Use transparent tracts with tooltips so data pops up on hover
folium.features.GeoJson(durm_tracts, name='Labels',
               style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
                tooltip=folium.features.GeoJsonTooltip(fields=['IntrntRate'],
                                              aliases = ['Households without internet (%):'],
                                              labels=True,
                                              sticky=False
                                             )
                       ).add_to(m)

folium.LayerControl().add_to(m)


m.save("mymap005.html")


