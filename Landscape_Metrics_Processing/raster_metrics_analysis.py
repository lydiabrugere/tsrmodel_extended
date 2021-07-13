from osgeo import gdal, osr
import numpy as np

# Read first band of tiff to array
lu_tif = "./data/se_mixed_forest_lu.tif"
raster = gdal.Open(lu_tif)
band = raster.GetRasterBand(1)
array = band.ReadAsArray()  # Convert first band to array

# mask non-target classes as 0 -- example: mixed_forest (pixel val = 43)
class_array = np.copy(array)
class_array[class_array != 43] = 0

geo_transform = raster.GetGeoTransform()
projection = raster.GetProjection()
cols = raster.RasterXSize
rows = raster.RasterYSize

lu_tif_masked = "./data/se_mixed_forest_lu_class43.tif"
driver = gdal.GetDriverByName('GTiff')
dataset = driver.Create(lu_tif_masked, cols, rows, 1, gdal.GDT_Byte)
dataset.SetGeoTransform(geo_transform)
dataset.SetProjection(projection)
band = dataset.GetRasterBand(1)
band.WriteArray(class_array)
dataset = None