"""
This script calculate Range of Mean Annual Precipitation (RMAP) for each grid
Input:  bio12: Annual Precipitation (this is total annual precipitation): wc2.0_30s_bio/wc2.0_bio_30s_12.tif
Method
    1. Summarize raster dataset based on each grid's polygon geometry: min, max;
    2. Calculate Min and Max value of each grid; then subtract and average by 12 for range of mean annual precipitation
"""

from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd
from shapely import wkb
import rasterio as rio
from rasterio.mask import mask
from sklearn.impute import SimpleImputer
import numpy as np

localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
geom_sql = """select distinct grid_id, grid_polygon_geom from observation.all_pergrid_sr where grid_id is not null and centroid is not null"""
geom = pd.read_sql(geom_sql, engine)

map_layer = Path('/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_12.tif')
col_names = ['grid_id', 'map', 'rmap']
map_var = pd.DataFrame(columns=col_names)
map_var['grid_id'] = geom.grid_id

for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    Index_label = map_var[map_var['grid_id'] == grid_id].index.tolist()[0]
    polygon_geom = wkb.loads(geom.grid_polygon_geom[index], hex=True)

    features = [polygon_geom]
    try:
        with rio.open(map_layer) as src:
            # fill nodata area within a grid as -9999
            out_image, out_transform = mask(dataset=src, shapes=features, nodata=np.nan, crop=True)
            # out_image_reshape = out_image.reshape(out_image.shape[1], out_image.shape[2])
            # # fill these nodata area as numpy NaN
            # imp = SimpleImputer(missing_values=-9999, strategy='constant', fill_value=np.nan)
            # out_image_trans = imp.fit_transform(out_image_reshape)

            # if all NaN within a grid, no data is extracted for now but will fill using KNN from neighbor grids
            if np.isnan(out_image).all():
                print(index, grid_id)
            else:
                # calculate stats for non-NaN pixels within bdry
                map_var.at[Index_label, 'map'] = float(np.nanmean(out_image))
                map_var.at[Index_label, 'rmap'] = float(np.nanmax(out_image) - np.nanmin(out_image))

    except Exception as e:
        print("Cropping failed for grid {grid_id}".format(grid_id=grid_id))
        print(repr(e))

map_var[['grid_id', 'map']].to_sql(name='pergrid_map2', schema='observation', con=engine, if_exists='replace', index=False)
map_var[['grid_id', 'rmap']].to_sql(name='pergrid_rmap2', schema='observation', con=engine, if_exists='replace', index=False)