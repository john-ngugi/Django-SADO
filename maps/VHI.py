import ee 



def getVHI(image,NIR,red,geometry,LST):
    NDVI = image.normalizedDifference([NIR,red]).rename("NDVI")
    
    #get minimum and maximum NDVI 
    min_val_ndvi = NDVI.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9).get('NDVI')
    max_val_ndvi = NDVI.reduceRegion(ee.Reducer.max(), geometry, 30, maxPixels=1e9).get('NDVI')
    min_value = ee.Number(min_val_ndvi)
    max_value = ee.Number(max_val_ndvi)
    
    #calculate vci 

    calc1 = NDVI.subtract(min_value)
    calc2 = max_value.subtract(min_value)

    global VCI
    VCI = calc1.divide(calc2)

    #get the minimum and mmaximum lst 

    min_val_lst = LST.reduceRegion(ee.Reducer.min(), geometry, 30, maxPixels=1e9).values().get(0)
    max_val_lst = LST.reduceRegion(ee.Reducer.max(), geometry, 30, maxPixels=1e9).values().get(0)
    min_val_lst = ee.Number(min_val_lst)
    max_val_lst = ee.Number(max_val_lst)
    
    global TCI 
    TCI = ee.Image(max_val_lst).subtract(LST).divide(max_val_lst.subtract(min_val_lst)) 

    VHI = VCI.multiply(ee.Image(0.5)).add(TCI.multiply(ee.Image(0.5)))

    return VHI,VCI,TCI