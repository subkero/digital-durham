import requests
import pandas as pd

import folium
import geopandas as gpd

import secrets1  # .gitignore, contains API key for Census

def get_internetData(df):
    """
    Inputs: dataframe with Census tract column called 'NAMELSAD'
    Output: dataframe with Durham County, NC census data for internet usage added
    """
    base_url=('https://api.census.gov/data/2017/acs/acs5?get=B28003_001E,NAME'
    '&for=tract:*&in=state:37%20county:063&key='+secrets1.AppKey['Census'])
 
    table2=census_query(base_url)  # Calls function below which does the heavy lifting
    table2.rename(columns={"B28003_001E":'CmptrIntrnt'}, inplace=True)
    table2['IntrntRate']=(table2['CmptrIntrnt'].astype(int)*100).div(df['POP'].astype(int),fill_value=1)
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

def census_countyPop_getter(df): #df=pd.read_csv('pivot_table_chloro_updated.csv', header=0)
    """
    Input: dataframe with 'Principal County Served:' column
    Output: Population by tract column, 'POP', merged to input df
    """
    base_url=('https://api.census.gov/data/2017/acs/acs5?get=B01001_001E,NAME'
    '&for=tract:*&in=state:37%20county:063&key='+secrets1.AppKey['Census'])
    table=census_query(base_url)
    table.rename(columns={"B01001_001E":'POP'}, inplace=True)
    table=get_internetData(table)
    tables=pd.merge(table,df, on='NAMELSAD')

    return tables

#Import NC tracts shapefiles
nc_tracts=gpd.read_file("zip://./Censustract_2017_37_tract.zip")
nc_tracts= gpd.GeoDataFrame(census_countyPop_getter(nc_tracts))
durm_tracts=nc_tracts[nc_tracts['COUNTYFP']=='063'] # restrict to Durham tracts
durm_tracts.crs = {'init' :'epsg:4326'}

m = folium.Map(location=[36.04, -78.850], zoom_start=10.5) #basemap

folium.Choropleth(
    durm_tracts,
    name='choropleth',
    data=durm_tracts,
    columns=['NAMELSAD','IntrntRate'],
    key_on='feature.properties.NAMELSAD',
    fill_color='YlOrBr_r', 
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Residents with internet access (%)'
).add_to(m)

# Use transparent tracts with tooltips so data pops up on hover
folium.features.GeoJson(durm_tracts, name='Labels',
               style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
                tooltip=folium.features.GeoJsonTooltip(fields=['IntrntRate'],
                                              aliases = ['Internet Access Rate (%):'],
                                              labels=True,
                                              sticky=False
                                             )
                       ).add_to(m)

folium.LayerControl().add_to(m)


m.save("mymap003.html")


