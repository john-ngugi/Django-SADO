import ee
import time 

class landsat:
    def __init__(self,startYear,endYear,startMonth,endMonth,imageCollection,monthRange):
       
       self.startYear=startYear
       self.endYear = endYear
       self.startMonth = startMonth
       self.endMonth =endMonth
       self.imageCollection = imageCollection
       self.monthRange = monthRange
       
    
    def maskL8sr(self,image):
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

    def dataset(self):
        dataset = ee.ImageCollection(self.imageCollection).filter(ee.Filter.calendarRange(self.startYear, self.endYear, 'year')).filter(self.monthRange)

        return dataset.map(self.maskL8sr)
       
    geometry = ee.FeatureCollection('projects/ee-muthamijohn/assets/arthi-galana')
    


    def getImage(self):
        dataset = self.dataset()
        return dataset.median()
    

    def getNDVI(self,NIR,red):
        # Calculate NDVI
        datasetNdvi= self.dataset().median()
        ndvi = datasetNdvi.normalizedDifference([NIR, red]).rename('NDVI')
        return ndvi
    
    def getNDVIInset(self,image):
        # Calculate NDVI
        datasetNdvi= self.dataset().median()
        ndvi = datasetNdvi.normalizedDifference(['SR_B5','SR_B4']) 
        datsetNdvi = datasetNdvi.addBands(ndvi.rename('nd'))
        return datsetNdvi

    def calcLSTL8(self,collection,ndvi,geometry):
        start = time.time()
        col = ee.ImageCollection(collection).filter(ee.Filter.calendarRange(self.startYear, self.endYear, 'year')).filter(self.monthRange).map(self.maskL8sr)
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


        end = time.time()
        return landSurfaceTemp
                

    def calcLSTL5L4L7(self,collection,ndvi,geometry):
        col1 = ee.ImageCollection(collection) \
        .map(self.maskL8sr) \
        .filter(ee.Filter.calendarRange(self.startYear, self.endYear, 'year')).filter(self.monthRange) \
        .filterBounds(self.geometry).median().clip(self.geometry)
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
        
        clippedbrightnessTemp = brightnessTemp.clip(self.geometry)
        
        # Median
        ndvi = col1.normalizedDifference(['B4', 'B3']).rename('NDVI')
        ndviParams = {'min': -1, 'max': 1, 'palette': ['blue', 'white', 'green']}
        
        # Find the min and max of NDVI
        min_val = ndvi.reduceRegion(ee.Reducer.min(), self.geometry, 30, maxPixels=1e9).get('NDVI')
        max_val = ndvi.reduceRegion(ee.Reducer.max(), self.geometry, 30, maxPixels=1e9).get('NDVI')
        min = ee.Number(min_val)
        max = ee.Number(max_val)
        
        # Fractional vegetation
        fv = ndvi.subtract(min).divide(max.subtract(min)).pow(ee.Number(2)).rename('FV')
        
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
        clippedLandSurfaceTemp = landSurfaceTemp.clip(self.geometry)
        

        return clippedLandSurfaceTemp
    

    def getLSTDroughtIndexL8(self,collection,startDate,endDate):
        start = time.time()
        col = ee.ImageCollection(collection) \
        .map(self.maskL8sr) \
        .filterDate(startDate,endDate) \
        .filterBounds(self.geometry)

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
        min_val = ndvi.reduceRegion(ee.Reducer.min(), self.geometry, 30, maxPixels=1e9).values().get(0)
        max_val = ndvi.reduceRegion(ee.Reducer.max(), self.geometry, 30, maxPixels=1e9).values().get(0)
        min_value = ee.Number(min_val)
        max_value = ee.Number(max_val)

        # Fractional vegetation
        fv = ndvi.subtract(min_value).divide(max_value.subtract(min_value)).pow(2).rename('FV')


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


        end = time.time()
        return landSurfaceTemp
        
    def getLSTDroughtIndexL5L7(self,collection,startDate,endDate):
        col1 = ee.ImageCollection(collection) \
        .map(self.maskL8sr) \
        .filterDate(startDate,endDate) \
        .filterBounds(self.geometry)    

        col1 =col1.mean().clip()

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
        
        clippedbrightnessTemp = brightnessTemp.clip(self.geometry)
        
        # Median
        ndvi = col1.normalizedDifference(['B4', 'B3']).rename('NDVI')
        ndviParams = {'min': -1, 'max': 1, 'palette': ['blue', 'white', 'green']}
        
        # Find the min and max of NDVI
        min_val = ndvi.reduceRegion(ee.Reducer.min(), self.geometry, 30, maxPixels=1e9).get('NDVI')
        max_val = ndvi.reduceRegion(ee.Reducer.max(), self.geometry, 30, maxPixels=1e9).get('NDVI')
        min = ee.Number(min_val)
        max = ee.Number(max_val)
        
        # Fractional vegetation
        fv = ndvi.subtract(min).divide(max.subtract(min)).pow(ee.Number(2)).rename('FV')
        
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
        clippedLandSurfaceTemp = landSurfaceTemp.clip(self.geometry)
        

        return clippedLandSurfaceTemp
    
    def getImageLST(self,startDate,endDate):
        pass
                


