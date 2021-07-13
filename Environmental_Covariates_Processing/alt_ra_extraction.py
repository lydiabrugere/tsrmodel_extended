"""
This script calculate Range of Altitude (RA) variable for each grid
Method:
    1. Crop continental US topo to each 20 by 20 km grid;
    2. Calculate Min and Max value of each grid; then subtract for range
"""
from pathlib import Path

from sqlalchemy import create_engine
import pandas as pd
from shapely import wkb
import rasterio as rio
from rasterio.mask import mask

localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
geom_sql = """select distinct grid_id, grid_polygon_geom from observation.all_pergrid_sr where grid_id is not null and centroid is not null"""
geom = pd.read_sql(geom_sql, engine)

topo_layer = Path('/Users/lianfeng/Document/species_richness_sdm/data/interim/altitude/US_gtopo30_merged_4269.tif')
col_names = ['grid_id', 'alt', 'ra']
topo_var = pd.DataFrame(columns=col_names)
topo_var['grid_id'] = geom.grid_id

for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    Index_label = topo_var[topo_var['grid_id'] == grid_id].index.tolist()[0]
    polygon_geom = wkb.loads(geom.grid_polygon_geom[index], hex=True)

    # features = [polygon_geom]
    # try:
    #     with rio.open(topo_layer) as src:
    #         out_image, out_transform = mask(dataset=src, shapes=features, nodata=0, crop=True)
    #     non_zero_pixel_count = 0
    #     for i in range(2):
    #         non_zero_pixel_count = non_zero_pixel_count + out_image.nonzero()[i]
    #     if len(non_zero_pixel_count) != 0:
    #         topo_var.at[Index_label, 'alt'] = float(out_image.mean())
    #         topo_var.at[Index_label, 'ra'] = float(out_image.max() - out_image.min())
    #     else:
    #         print('Grid {grid_id} does not intersect with LULC. Pass!'.format(grid_id=grid_id))
    # except Exception as e:
    #     print("Cropping failed for grid {grid_id}".format(grid_id=grid_id))
    #     print(repr(e))

    stats = zonal_stats(polygon_geom, topo_layer, stats="count min max")
    if stats[0]['count'] == 0:
        print('Grid {grid_id} does not intersect for non-zero value. Pass!'.format(grid_id=grid_id))
    else:
        topo_var.at[Index_label, 'ra'] = stats[0]['max'] - stats[0]['min']

topo_var[['grid_id', 'ra']].to_sql(name='pergrid_ra', schema='observation', con=engine, if_exists='replace', index=False)
# topo_var[['grid_id', 'alt']].to_sql(name='pergrid_alt', schema='observation', con=engine, if_exists='replace', index=False)