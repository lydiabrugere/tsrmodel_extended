"""
This script calculate Mean frost day frequency (MFDF, days per month) as mean days per month for 1901 to 2009
Download Page:
http://www.cgiar-csi.org/data/uea-cru-ts-v3-10-01-historic-climate-database
Data size: GB
Method:
    1. Crop global AI to each 20 by 20 km grid;
    2. Sum up frost day per month from 1901 to 2009
    3. Calculate mean frost day per month of each grid
"""
import os
from pathlib import Path
import glob

from sqlalchemy import create_engine
import pandas as pd
import rasterio as rio
from rasterstats import zonal_stats
from shapely import wkb

from osgeo import gdal
import numpy as np

"""Preprocessing: Covert to tiff --> Define Projection"""
# 1. Convert to Tiff
# gdal_translate -of "GTiff" cru_ts_3_10.1901.2009.frs_1901_1.asc cru_ts_3_10.1901.2009.frs_1901_1.tif
asc2tif = 'for file in ./*asc; do gdal_translate -of "GTiff" $file ${file}.tif; done'
os.system(asc2tif)
# 2. Define Projection
# gdal_edit.py -a_srs EPSG:4269 cru_ts_3_10.1901.2009.frs_1901_1.tif
project_tif = 'for file in ./*tif; do gdal_edit.py -a_srs EPSG:4269 $file; done'
os.system(project_tif)
"""Done"""

# Calculate mean of all Tiff
mfdf_data_dir = Path('/Users/lianfeng/OneDrive - The University of Memphis/Research/species_richness_sdm/data/interim/mfdf_converted_tif')
os.chdir(mfdf_data_dir)

file_paths = glob.glob('./*.tif')
# We build one large np array of all images (this requires that all data fits in memory)
res = []
for f in file_paths:
    ds = gdal.Open(f)
    res.append(ds.GetRasterBand(1).ReadAsArray())  # assume that all rasters has a single band
stacked = np.dstack(res)  # assume that all rasters have the same dimensions
mean = np.mean(stacked, axis=-1)

# Finally save a new raster with the result.
# This assumes that all inputs have the same geotransform since we just copy the first
driver = gdal.GetDriverByName('GTiff')
result = driver.CreateCopy('../../processed/mfdf.tif', gdal.Open(file_paths[0]))
result.GetRasterBand(1).WriteArray(mean)
result = None

"""Extract mfdf for each grid"""
localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
geom_sql = """select distinct grid_id, centroid as geom from observation.all_pergrid_sr where grid_id is not null and centroid is not null"""
geom = pd.read_sql(geom_sql, engine)

col_names = ['grid_id', 'mfdf']
fdf_var = pd.DataFrame(columns=col_names)
fdf_var['grid_id'] = geom.grid_id
mfdf_layer = Path('/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/mfdf.tif')

for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    Index_label = fdf_var[fdf_var['grid_id'] == grid_id].index.tolist()[0]
    geom_polygon = wkb.loads(geom.geom[index], hex=True)
    pixel_count = zonal_stats(geom_polygon, mfdf_layer, stats="count mean")[0]['count']
    if pixel_count == 0:
        print('Grid {grid_id} does not intersect for non-zero value. Pass!'.format(grid_id=grid_id))
    else:
        grid_val = (zonal_stats(geom_polygon, mfdf_layer, stats="count mean")[0]['mean'])/100
        fdf_var.at[Index_label, 'mfdf'] = grid_val

fdf_var.to_sql(name='pergrid_mfdf', schema='observation', con=engine, if_exists='replace', index=False)