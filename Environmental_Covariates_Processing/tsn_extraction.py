"""
This script calculate mean Actual evapotranspiration for each grid
Source Data:
http://www.ntsg.umt.edu/project/modis/mod16.php
Reference:
Download Page:
http://files.ntsg.umt.edu/data/NTSG_Products/MOD16/MOD16A3.105_MERRAGMAO/Geotiff/MOD16A3_ET_2000_to_2013_mean.tif

Data size: 1.59 GB
Method:
    1. Crop global PE to each 20 by 20 km grid;
    2. Calculate Mean of each grid
"""

from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd
from rasterstats import zonal_stats
from shapely import wkb


localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
geom_sql = """select distinct grid_id, grid_polygon_geom from observation.all_pergrid_sr where grid_id is not null and centroid is not null"""
geom = pd.read_sql(geom_sql, engine)

tsn_layer = Path('/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_4.tif')
col_names = ['grid_id', 'tsn']
tsn_var = pd.DataFrame(columns=col_names)
tsn_var['grid_id'] = geom.grid_id

for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    Index_label = tsn_var[tsn_var['grid_id'] == grid_id].index.tolist()[0]
    polygon_geom = wkb.loads(geom.grid_polygon_geom[index], hex=True)

    features = [polygon_geom]
    try:
        with rio.open(tsn_layer) as src:
            out_image, out_transform = mask(dataset=src, shapes=features, nodata=0, crop=True)
        non_zero_pixel_count = 0
        for i in range(2):
            non_zero_pixel_count = non_zero_pixel_count + out_image.nonzero()[i]
        if len(non_zero_pixel_count) != 0:
            tsn_var.at[Index_label, 'tsn'] = float(out_image.mean())
        else:
            print('Grid {grid_id} does not intersect with LULC. Pass!'.format(grid_id=grid_id))
    except Exception as e:
        print("Cropping failed for grid {grid_id}".format(grid_id=grid_id))
        print(repr(e))

tsn_var.to_sql(name='pergrid_tsn', schema='observation', con=engine, if_exists='replace', index=False)
