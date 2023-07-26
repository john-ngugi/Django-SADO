import ee
import json 




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








# def maskL8sr(image):
#     # Bits 3 and 5 are cloud shadow and cloud, respectively.
#     cloudShadowBitMask = 1 << 3
#     cloudsBitMask = 1 << 5
#     # Get the pixel QA band.
#     qa = image.select('QA_PIXEL')
#     # Both flags should be set to zero, indicating clear conditions.
#     mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0) \
#         .And(qa.bitwiseAnd(cloudsBitMask).eq(0))
#     # Return the masked image, scaled to reflectance, without the QA bands.
#     return image.updateMask(mask).divide(10000) \
#         .select("B[0-9]*") \
#         .copyProperties(image, ["system:time_start"])

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


def getImageL8(startYear, endYear,startMonth, endMonth):
    dataset = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").filter(ee.Filter.calendarRange(startYear, endYear, 'year')).filter(ee.Filter.calendarRange(startMonth, endMonth, 'month'))
    # # Applies scaling factors.
    # def applyScaleFactors(image):
    #     opticalBands = image.select('B.').multiply(0.0000275).add(-0.2)
    #     thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    #     return image.addBands(opticalBands, None, True) \
    #                 .addBands(thermalBands, None, True)
    dataset = dataset.map(maskL8sr)
    return dataset.median()


def getNDVI(startYear, endYear,startMonth, endMonth):
    dataset = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2").filter(ee.Filter.calendarRange(startYear, endYear, 'year')).filter(ee.Filter.calendarRange(startMonth, endMonth, 'month'))
    # Calculate NDVI
    datasetNdvi= dataset.median()
    ndvi = datasetNdvi.normalizedDifference(['SR_B5', 'SR_B4']) 
    #st.write(ndvi)  
    # Map.centerObject(ndvi, 10)
    return ndvi
    # Map.to_streamlit()
    



