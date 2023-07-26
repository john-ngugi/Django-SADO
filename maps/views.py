from django.shortcuts import render
import folium 
import json 
import ee 
import time 
from . import L8
from . import precipitation as pt
from . import landsat
from . import VHI as vh
from colorama import init, Fore, Style
import pandas as pd
import plotly.express as px 

import geemap.foliumap as geemap


# Create your views here.
json_data = '''
{
  "type": "service_account",
  "project_id": "ee-muthamijohn",
  "private_key_id": "ba887a502e5b94d1c484429fb58de81fda8bf013",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCnBlXhl3LS4NDO\nO/32iManSz+kH+YFYfjqTIutkj+JUJ2CVywYIB85cJVGbQ0k23SVS1kx0wrhlA+b\nBzDwtsVBFev4/w6NeZ/YeqL4U/Ky9SP7t6wAmdDkijP9/EtP5IonxuVLYC5trGtw\nL5z6nWgfub0O+A6oTee1bdc3VSlgjt/wKcJwsHFMIr/Brg0lf3chwkBRh0+X1Ntd\np1l1hQVQCshLs32PoDds6ep3cEOpIf/X7diTT1uvprEPUQlNsQf4RzxPBvvqyRZb\nPo1Zv1JO+BAHntC8Z2L3aPmqot9Bq94BqLZm+pRzusoCRJ/Pe+V8J66rM1gR3jup\nEwI3K6abAgMBAAECggEABp5+DmY9sXtU8XdeXyplRQGUahRH8PREmw4H7KVpFmLQ\nrl1DoBXvZtiK8eZZQpnePhrLh0/0lG/7r/C4ncsaEhqksvkL28tzUqIf9A6cbAv1\nYYDFgXIwqkq+OLu9q4YRFSmqsjJp/jd6ooPtVd+hd4n/otvUKOAj5WrCJq03UJFu\n8NEP2aVF4OiVjYLhN5DaN1I+b7lsAA88ZcAYDYxOKiRvkIEyD2S3lJg46+cfIRKz\nbuNV65tWDsDWQL9djB8bRgmUnXjFmEfjiBxWyqv4JF2Xs4/bEuPmX3u06Zfy9UqE\nt/lhvXQ/s0Ou6ayrbDN7jd8yJuIl8EBDQAF6BWGSwQKBgQDWaroZc75ETtBEU401\nU8iBBSKI4YLY4RTvbCeaKBcmNGLzqk0nIdX4NxOwMm8P1LiDYJeOcKkxNTB05lNz\n526MomJ7rHx+vFjpi2a068+FuxczmVeEIbgDM8e2jttBjh6PauUxHEbcOsd7k2Je\nunDCHDUjjaCdRaMrWRT7m+qXywKBgQDHarRQ1pdNxmTjeAVyw1s8br6coVrL94Za\nPfBo6eFDcfsrPOdx7iq1NFuoOCWwZm1hBqhWJYWNqwbVS+G4ESaqnTY5LZTzR67X\n2LobeV/ZegpU7KWBt8Pes4ksMQZedNXuQmtZuKpNEXdAV5WKDgPeSIhdLNdevFJf\n99cv/8sycQKBgQCHy3wlVnpwBII+Y7QQzAk2PSxMCJa4CIUbxSGnrjBLD+6DZ54J\nZJKA61DazHYuToi1G92gZpWhBpCz2JON2krXYpiAvxLxqROehZz8hEQf7AebtEgK\n9Nf3nzmi0wLll76fEhIpckEmhUuFZihs2iNDrF2zMKVCNbJLZ9W0LGD81QKBgGEC\nzdmNq2mQnD/0gWIFG3tYvK3h6RPUxK1d+HhxXr660l+Eb2uDW49vey9osR0RlyBe\nZsIR2tjCXL6i/ZnX7iGN/XTvcciwFKS4sEDxWOmpbyFFRnbGeSj72j1/VAPbfr87\n3JF3PpHjb0oD0aGpk8QtMPly+QsDPmelYC/flnBhAoGBALqZ13BjABwBTKimTcmC\nQiI7LvdsAAdO9k4LjSKKSmCyUTAN4hCc5gqKPVxv62ao+rxbHzRqGNvouXePVb8z\nZbXzfXrWLJxci43wkq3UOoB3t5DTkTGQQveD1tFiVFwLrVZUahoDCerMSQRo449s\n1hx46+u8FvPA57M640V7arV8\n-----END PRIVATE KEY-----\n",
  "client_email": "kenya-environmental-dashboard@ee-muthamijohn.iam.gserviceaccount.com",
  "client_id": "101824526217381631179",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/kenya-environmental-dashboard%40ee-muthamijohn.iam.gserviceaccount.com"
}
'''

# Preparing values
json_object = json.loads(json_data, strict=False)
service_account = json_object['client_email']
json_object = json.dumps(json_object)
#Authorising the app
credentials = ee.ServiceAccountCredentials(service_account, key_data=json_object)
ee.Initialize(credentials)


def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)

# Add the method to the folium Map class
folium.Map.add_ee_layer = add_ee_layer

def getLayers(request,year_start,year_end,monthRange,startMonth,endMonth):
    process_start = time.time()
     # Create a map centered at Nakuru, Kenya
    m = folium.Map(location=[-2.3746, 37.9715],tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)', zoom_start=9,height="80%",name='terrainOSM')
    worldImagery= folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr= 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',name='ESRI world Imagery')
    # basemapOSM =folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)')
   
    worldImagery.add_to(m)

   

    # Update the values
    YEAR_START = year_start
    YEAR_END = year_end
    monthRangeGetLayersFunction = monthRange
    startMonth = startMonth
    endMonth = endMonth
    # Define the area of interest (AOI) as a shapefile
    geometry = ee.FeatureCollection('projects/ee-muthamijohn/assets/arthi-galana')

    # Visualization Palette
    # vis = ['d7191c', 'fdae61', 'ffffc0', 'a6d96a', '1a9641']
    vis = ['red','yellow','green']

  
    
    # get precipitation Data
    precipitation = pt.precipitation(YEAR_START,YEAR_END,startMonth,endMonth) 

    

# Image logic and getting image from the landsat class in the landsat module 
    
    if YEAR_START > 2000 and YEAR_END <= 2014:
        landsat8=  landsat.landsat(YEAR_START,YEAR_END,startMonth,endMonth,"LANDSAT/LE07/C02/T1_L2",monthRangeGetLayersFunction)
        landsatImage=landsat8.getImage()
        landsatCollection=landsat8.dataset()
        ndviL8 = landsat8.getNDVI("SR_B4","SR_B3")
        lst = landsat8.calcLSTL5L4L7("LANDSAT/LE07/C02/T1",ndviL8,geometry).clip(geometry)
        # def clippedLandSurfaceTemp1(startDate,endDate):
        #     clippedLandSurfaceTemp =landsat8.getLSTDroughtIndexL5L7("LANDSAT/LC07/C02/T1",startDate,endDate)
        #     return clippedLandSurfaceTemp
        
    if YEAR_START >2014 and YEAR_END<= 2029:
            landsat8 = landsat.landsat(YEAR_START,YEAR_END,startMonth,endMonth,"LANDSAT/LC08/C02/T1_L2",monthRangeGetLayersFunction)
            landsatImage=landsat8.getImage()
            landsatCollection=landsat8.dataset()
            ndviL8 = landsat8.getNDVI("SR_B5","SR_B4")
            lst = landsat8.calcLSTL8("LANDSAT/LC08/C02/T1",ndviL8,geometry).clip(geometry)
            # def clippedLandSurfaceTemp1(startDate,endDate):
            #     clippedLandSurfaceTemp = landsat8.getLSTDroughtIndexL8("LANDSAT/LC08/C02/T1",startDate,endDate)
            #     return clippedLandSurfaceTemp


    if YEAR_START > 2016:
        def maskS2clouds(image):
            return image.updateMask(image.select('QA60').eq(0));

            # Load Sentinel-2 data for the region of interest
        sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filter(ee.Filter.calendarRange(YEAR_START,YEAR_END, 'year')).filter(ee.Filter.calendarRange(startMonth, endMonth, 'month'))\
            .filterBounds(geometry)\
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE',5))\
            .map(maskS2clouds).median().clip(geometry)

        # Calculate NDVI
        ndvi = sentinel2.normalizedDifference(['B8', 'B4'])

    # Define visualization parameters for NDVI
    ndvi_vis_params = {
        'min': 0,
        'max': 1,
        'palette': ['red', 'yellow', '#006400','green']
    }

    
    image = landsat8.dataset().median()
    # ************************* check logic *****************
    VHI,VCI,TCI = vh.getVHI(image,'SR_B5','SR_B4',geometry,lst)
    

    # VHI classification into classes based on threshold values to calculate Drought Index
    image02 = VHI.lt(0.1).And(VHI.gte(-1))
    image04 = ((VHI.gte(0.1)).And(VHI.lt(0.2))).multiply(2)
    image06 = ((VHI.gte(0.2)).And(VHI.lt(0.3))).multiply(3)
    image08 = ((VHI.gte(0.3)).And(VHI.lt(0.4))).multiply(4)
    image10 = (VHI.gte(0.4)).multiply(5)
    Drought_Index = (image02.add(image04).add(image06).add(image08).add(image10)).float()
    Drought_Index_Mean = Drought_Index.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, bestEffort=True,scale=30)



    visualization = {
        'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
        'min': 1,
        'max': 65455,
        'gamma': 1.4,
    }
    
    ndvi_params = {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}


    # Add the layer to the map
    start = time.time()
    # TCI display to map
    m.add_ee_layer(TCI, {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}, 'TCI')
    # # VCI display to map
    m.add_ee_layer(VCI.clip(geometry), {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}, 'VCI')
    # # VHI display to map
    m.add_ee_layer(VHI, {'min': -1, 'max': 1, 'palette': ['red', 'yellow', 'green']}, 'VHI')
    # # Drought display to map
    m.add_ee_layer(Drought_Index, {'min': 1, 'max': 5, 'palette': vis}, 'Drought Index')
        # m.add_ee_layer(Drought_Index, {'min': 1, 'max': 5, 'palette': vis}, 'Drought Index')
    end = time.time()
    rslt = end - start

    if float(rslt) >= 30.00:
        print("major layers load time: " + Fore.RED + str(rslt) + Style.RESET_ALL)
    elif float(rslt) >=20.00:
        print("major layers load time: " + Fore.YELLOW + str(rslt) + Style.RESET_ALL)    
    else:
        print("major layers load time: " + Fore.BLUE + str(rslt) + Style.RESET_ALL)

    m.add_ee_layer(landsatImage.clip(geometry), visualization, 'True Color (432)')
    start=time.time()
    m.add_ee_layer(lst, {'min': 2,'max': 45,'palette': ['040274', '040281', '0502a3', '0502b8', '0502ce', '0502e6',
'0602ff', '235cb1', '307ef3', '269db1', '30c8e2', '32d3ef',
'3be285', '3ff38f', '86e26f', '3ae237', 'b5e22e', 'd6e21f',
'fff705', 'ffd611', 'ffb613', 'ff8b13', 'ff6e08', 'ff500d',
'ff0000', 'de0101', 'c21301', 'a71001', '911003' ]},'LST')
    end= time.time()

    minrslt= end - start
    if float(minrslt) >= 20.00:
        print("lst display process finished within " + Fore.RED + str(minrslt) + Style.RESET_ALL)
    else:
        print("lst display process finished within " + Fore.BLUE + str(minrslt) + Style.RESET_ALL)


    m.add_ee_layer(precipitation.first().clip(geometry),{
    'min': 1.0,
    'max': 17.0,
    'palette' : ['001137', '0aab1e', 'e7eb05', 'ff4a2d', 'e90000'],
    }, 'Precipitation')

    m.add_ee_layer(ndviL8.clip(geometry),ndvi_params,'NDVI L8')

    try:
        # Add the NDVI layer to the map
        m.add_ee_layer(ndvi, ndvi_vis_params, 'NDVI')
    except:
         print("sentinel not yet Discovered")    

    # Add a layer control to the map
    m.add_child(folium.LayerControl())

    ## **************** important ******************






    VHI_mean = VHI.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
    VHI_mean = ee.Number(VHI_mean.get('NDVI')).float().getInfo()
    TCI_mean = TCI.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
    TCI_mean = ee.Number(TCI_mean.get('constant')).float().getInfo()
    VCI_mean = VCI.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
    VCI_mean = ee.Number(VCI_mean.get('NDVI')).float().getInfo()
    Drought_Index_mean = Drought_Index.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
    Drought_Index_mean = ee.Number(Drought_Index_mean.get('NDVI')).float().getInfo()

    indeces = [VCI_mean,VHI_mean,TCI_mean,Drought_Index_mean]
    def maskL8sr(image):
        # Select the pixel QA band.
        qa = image.select('QA_PIXEL')
        
        # Define the bitmasks for cloud and cloud shadow.
        cloudBitMask = 1 << 3
        cloudShadowBitMask = 1 << 4
        
        # Create the mask for clear conditions.
        mask = qa.bitwiseAnd(cloudBitMask).eq(0) \
            .And(qa.bitwiseAnd(cloudShadowBitMask).eq(0))
        
        # Apply the mask to the image.
        return image.updateMask(mask)

    startYearVHI = year_start
    endYearVHI = year_end



    def compute_veg_indices(start_date, end_date):
            geometry = ee.FeatureCollection('projects/ee-muthamijohn/assets/arthi-galana')
            # Drought_Index=Drought_Index.select('NDVI')
            # NDVI_mean = ndviL8.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9)
            # NDVI_mean = ee.Number(NDVI_mean.get('NDVI')).float().getInfo()
            
            def calculate_drought_index(geometry, start_date_index, end_date_index):
                    
                    if YEAR_START >= 2000 and YEAR_END < 2014:
                        col1 = ee.ImageCollection("LANDSAT/LE07/C02/T1") \
                        .map(maskL8sr) \
                        .filterDate(start_date_index,end_date_index) \
                        .filterBounds(geometry)    

                        col1 =col1.mean().clip(geometry)

                        # Calculate TOA spectral radiance
                        ML = 0.055375
                        AL = 1.18243
                        TOA_radiance = col1.expression('ML * B6 + AL', {
                            'ML': ML,
                            'AL': AL,
                            'B6': col1.select('B6_VCID_1')
                        })
                        
                        # Convert TOA spectral radiance to brightness temperature
                        K1 = 607.76
                        K2 = 1260.56
                        brightnessTemp = TOA_radiance.expression(
                            '(K2 / (log(K1 / L) + 1)) - 273.15', {
                                'K1': K1,
                                'K2': K2,
                                'L': TOA_radiance
                        })
                        
                        clippedbrightnessTemp = brightnessTemp.clip(geometry)
                        
                        # Median
                        ndvi = col1.normalizedDifference(['B4', 'B3']).rename('NDVI')
                        ndviParams = {'min': -1, 'max': 1, 'palette': ['blue', 'white', 'green']}
                        
                        # Find the min and max of NDVI
                        min_val = ndvi.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9).get('NDVI')
                        max_val = ndvi.reduceRegion(ee.Reducer.max(), geometry, 30, maxPixels=1e9).get('NDVI')
                        min = ee.Number(min_val)
                        max = ee.Number(max_val)
                        
                        # Fractional vegetation
                        fv = ndvi.subtract(min).divide(max.subtract(min)).pow(ee.Number(2)).rename('FV')
                        VCI = (ndvi.subtract(min)).divide(max.subtract(min))
                        
                        # Emissivity
                        a = ee.Number(0.004)
                        b = ee.Number(0.986)
                        EM = fv.multiply(a).add(b).rename('EMM')
                        
                        # Calculate land surface temperature
                        landSurfaceTemp = brightnessTemp.expression(
                            '(BT / (1 + (0.00115 * BT / 1.4388) * log(epsilon)))', {
                                'BT': brightnessTemp,
                                'epsilon': EM.select('EMM')
                        })
                        
                        # Clip the land surface temperature image to the geometry
                        clippedLandSurfaceTemp = landSurfaceTemp.clip(geometry)
                        

                    if YEAR_START > 2014:
                            col = ee.ImageCollection("LANDSAT/LC08/C02/T1") \
                            .map(maskL8sr) \
                            .filterDate(start_date_index,end_date_index) \
                            .filterBounds(geometry)

                            # image = self.dataset().median()
                            # Image reduction
                            image = col.mean()

                            # Calculate TOA spectral radiance
                            ML = 0.0003342
                            AL = 0.10000
                            Oi = 0.29

                            TOA_radiance = image.expression('ML * B10 + AL - Oi', {
                                'ML': ML,
                                'AL': AL,
                                'B10': image.select('B10'),
                                'Oi': Oi
                            })

                            # Convert TOA spectral radiance to brightness temperature
                            K1 = 774.8853
                            K2 = 1321.0789

                            brightnessTemp = TOA_radiance.expression(
                                '(K2 / (log((K1 / L) + 1))) - 273.15', {
                                    'K1': K1,
                                    'K2': K2,
                                    'L': TOA_radiance
                                })

                            # Median
                            ndvi = image.normalizedDifference(['B5', 'B4']).rename('NDVI')

                            # Find the min and max of NDVI
                            min_val = ndvi.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9).values().get(0)
                            max_val = ndvi.reduceRegion(ee.Reducer.max(), geometry, 30, maxPixels=1e9).values().get(0)
                            min_value = ee.Number(min_val)
                            max_value = ee.Number(max_val)

                            # Fractional vegetation
                            fv = ndvi.subtract(min_value).divide(max_value.subtract(min_value)).pow(2).rename('FV')
                            VCI = (ndvi.subtract(min_value)).divide(max_value.subtract(min_value))


                            # Emissivity
                            a = 0.004
                            b = 0.986
                            EM = fv.multiply(a).add(b).rename('EMM')
                        
                            # Calculate land surface temperature
                            landSurfaceTemp = brightnessTemp.expression(
                                '(BT / (1 + (10.60 * BT / 14388) * log(epsilon)))', {
                                    'BT': brightnessTemp,
                                    'epsilon': EM.select('EMM')
                                })
                            clippedLandSurfaceTemp = landSurfaceTemp .clip(geometry)


                    # Find the min and max of LST
                    min_v = clippedLandSurfaceTemp.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9).values().get(0)
                    max_v = clippedLandSurfaceTemp.reduceRegion(ee.Reducer.max(), geometry, 30, maxPixels=1e9).values().get(0)
                    min_LST = ee.Number(min_v)
                    max_LST = ee.Number(max_v)
                    
                    max_LST_1 = ee.Image(max_LST)
                    #Obtain TCI
                    TCI = max_LST_1.subtract(clippedLandSurfaceTemp).divide(max_LST.subtract(min_LST))
                    
                    #Calculate VCI
                    VHI = (VCI.multiply(0.5)).add(TCI.multiply(0.5))
                    
                    # VHI classification into classes based on threshold values to calculate Drought Index
                    image02 = VHI.lt(0.1).And(VHI.gte(-1))
                    image04 = ((VHI.gte(0.1)).And(VHI.lt(0.2))).multiply(2)
                    image06 = ((VHI.gte(0.2)).And(VHI.lt(0.3))).multiply(3)
                    image08 = ((VHI.gte(0.3)).And(VHI.lt(0.4))).multiply(4)
                    image10 = (VHI.gte(0.4)).multiply(5)
                    Drought_Index = (image02.add(image04).add(image06).add(image08).add(image10)).float()
                    
                    return Drought_Index, TCI, VCI, VHI
            
            Drought_Index, TCI, VCI, VHI = calculate_drought_index(geometry, start_date, end_date)

            # imageVHI =ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").filterDate(date,date).filterBounds(geometry).map(maskL8sr).median().clip(geometry)
            # VHI,VCI,TCI = vh.getVHI(imageVHI,'SR_B5','SR_B4',geometry,lst)
            VHI_mean = VHI.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
            VHI_mean = ee.Number(VHI_mean.get('NDVI')).float().getInfo()
            TCI_mean = TCI.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
            TCI_mean = ee.Number(TCI_mean.get('constant')).float().getInfo()
            VCI_mean = VCI.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
            VCI_mean = ee.Number(VCI_mean.get('NDVI')).float().getInfo()
            Drought_Index_mean = Drought_Index.reduceRegion(ee.Reducer.mean(), geometry, 30, maxPixels=1e9)
            Drought_Index_mean = ee.Number(Drought_Index_mean.get('NDVI')).float().getInfo()

            return {'start_date': start_date, 'end_date': end_date, 'VHI_mean': VHI_mean, 'Drought_index_mean': Drought_Index_mean, 'TCI_mean': TCI_mean, 'VCI_mean': VCI_mean}
        

    dates = ee.List(landsatCollection.distinct('system:time_start').aggregate_array('system:time_start')).map(
        lambda time_start: ee.Date(time_start).format('YYYY-MM-dd')).getInfo()

    # Retrieve the first sequence of dates
    first_sequence = []
    current_sequence = []

    for i, date in enumerate(dates):
        if i == 0 or int(date.split('-')[0]) >= int(dates[i-1].split('-')[0]):
            current_sequence.append(date)
        else:
            break

    first_sequence = current_sequence

    print(first_sequence)

    # First, convert the date strings in the first_sequence list to datetime objects
    from datetime import datetime, timedelta

    date_format = "%Y-%m-%d"
    first_sequence = [datetime.strptime(date_str, date_format) for date_str in first_sequence]

    # Create date pairs by picking each date as the start date and adding 16 days to obtain the end date
    date_pairs = []
    for i in range(len(first_sequence)):
        start_date = first_sequence[i]
        end_date = start_date + timedelta(days=16)
        date_pairs.append((start_date.strftime(date_format), end_date.strftime(date_format)))

    print(date_pairs)

    # Perform computations for each date pair and store the results in a list
    data = []

    for start_date, end_date in date_pairs:
        result = compute_veg_indices(start_date, end_date)
        data.append(result)

    # Convert the list of dictionaries to a pandas DataFrame and set 'start_date' and 'end_date' as the MultiIndex
    df= pd.DataFrame(data).drop(['end_date'], axis=1).set_index(['start_date'])
    print(df)



    # Step 1: Initialize an empty DataFrame to store the standardized values
    standardized_df = pd.DataFrame()

    # Step 2: Loop through each season and calculate the mean and standard deviation
    for season in df.index.get_level_values('start_date').str[:2].unique():
        seasonal_data = df.loc[df.index.get_level_values('start_date').str[:2] == season]
        min_of_season = seasonal_data['Drought_index_mean'].min()
        max_of_season = seasonal_data['Drought_index_mean'].max()
        range_of_season = max_of_season - min_of_season
        
        # Step 3: Compute the standardized values for the 'Drought_index_mean' column
        standardized_values = (seasonal_data['Drought_index_mean'] - min_of_season) / range_of_season * 2 - 1
        
        # Step 4: Assign the standardized values to the 'Standardized_Drought_Index' column
        seasonal_data['Standardized_Drought_Index'] = standardized_values
        
        # Append the seasonal data to the empty DataFrame
        standardized_df = pd.concat([standardized_df, seasonal_data])
        standardized_df=standardized_df.drop('Drought_index_mean',axis=1)
        print(standardized_df.keys())
    print(standardized_df)
    

    graph = px.line(
        standardized_df
    )

    context = {'map': m._repr_html_(),'VHI_mean':VHI_mean,'Drought_index_mean':Drought_Index_mean,'TCI_mean':TCI_mean,'VCI_mean':VCI_mean,'graph':graph.to_html()}
    # return render(request, 'map.html', context)
    process_end = time.time()
    process_time_rslt = process_end - process_start
    print("process finished within: " + Fore.MAGENTA + str(process_time_rslt) + Style.RESET_ALL)
    return context


def index(request):
    # Create a map centered at Nakuru, Kenya
    m = folium.Map(location=[-1.2921, 36.8219], zoom_start=15,tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr= 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',name='ESRI world Imagery')
    worldImagery= folium.TileLayer(tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)', zoom_start=9,height="80%",name='terrainOSM')
    # basemapOSM =folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)')
    worldImagery.add_to(m)
    if request.method == 'POST':
            
        # # Define the area of interest (AOI) as a shapefile
        # geometry = ee.FeatureCollection('projects/ee-muthamijohn/assets/arthi-galana')
        # Get the form data
        year_start = int(request.POST.get('year_start'))
        year_end = int(request.POST.get('year_end'))
        month = int(request.POST.get('month'))

        if month == 1:
            monthRange = ee.Filter.calendarRange(1, 3, 'month')
            startMonth = 1
            endMonth = 3

        if month == 2:
            monthRange = ee.Filter.calendarRange(4, 6, 'month')    
            startMonth = 4
            endMonth = 6

        if month == 3:
            monthRange = ee.Filter.calendarRange(7, 9, 'month')   
            startMonth = 7
            endMonth = 9

        if month == 4:
            monthRange = ee.Filter.calendarRange(10, 12, 'month') 
            startMonth = 10
            endMonth = 12

        context = getLayers(request,year_start,year_end,monthRange,startMonth,endMonth)

        return render(request, 'map.html', context)
    else:     
        m.add_child(folium.LayerControl())
        context = {'map': m._repr_html_()} 
        
        return render(request, 'map.html', context)
    