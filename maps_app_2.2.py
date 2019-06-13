import pandas as pd
import folium
import geopandas as gpd

#Assumes Block groups shapefiles - 'cb_2017_37_bg_500k.zip' and 
# Data Excel Workbook - 'Data_sheets.xlsx' exist in folder-path set below
    
path_to_files='./' # set path to folder containing zip & xlsx file

nc_BlockGrp=gpd.read_file("zip://"+path_to_files+'cb_2017_37_bg_500k.zip')
durm_BlockGrps=nc_BlockGrp[nc_BlockGrp['COUNTYFP']=='063'] # restrict to Durham tracts
durm_BlockGrps[['TRACTCE','BLKGRPCE']]=durm_BlockGrps[['TRACTCE','BLKGRPCE']].astype(int)

df1 = pd.read_excel(path_to_files+'Data_sheets.xlsx', 'Households')
df2 = pd.read_excel(path_to_files+'Data_sheets.xlsx', 'Households without internet' )

durm_BlockGrps=pd.merge(durm_BlockGrps,df1, left_on=['TRACTCE','BLKGRPCE'], 
                                    right_on=['tract','block group']) 
durm_BlockGrps=durm_BlockGrps.merge(df2, on=['tract','block group']) 

durm_BlockGrps['IntrntRate']=(durm_BlockGrps['NoIntrnt']*100).div(
        durm_BlockGrps['Households'],fill_value=1)
durm_BlockGrps['IntrntRate']=durm_BlockGrps['IntrntRate'].astype(float).apply(lambda x:round(x,2))

durm_BlockGrps.crs = {'init' :'epsg:4326'} # set the projection 

m = folium.Map(location=[36.04, -78.850], zoom_start=10.5) #basemap

folium.Choropleth(
    durm_BlockGrps,
    name='choropleth',
    data=durm_BlockGrps,
    columns=['NAME','IntrntRate'],
    key_on='feature.properties.NAME',
    fill_color='YlOrBr', 
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Durham County households without internet access (%)'
).add_to(m)

# Use transparent tracts with tooltips so data pops up on hover
folium.features.GeoJson(durm_BlockGrps, name='Labels',
               style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
                tooltip=folium.features.GeoJsonTooltip(fields=['IntrntRate'],
                                              aliases = ['Households without internet (%):'],
                                              labels=True,
                                              sticky=False
                                             )
                       ).add_to(m)

folium.LayerControl().add_to(m)

m.save("mymap007.html")


