"""
This script calculate Range of Mean Annual Precipitation (Rmtcq) for each grid
Input:  bio12: Annual Precipitation (this is total annual precipitation): wc2.0_30s_bio/wc2.0_bio_30s_12.tif
Method
    1. Summarize raster dataset based on each grid's polygon geometry: min, max;
    2. Calculate Min and Max value of each grid; then subtract and average by 12 for range of mean annual precipitation
"""
from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd
from shapely import wkb
from rasterstats import zonal_stats

localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
geom_sql = """select distinct grid_id, grid_polygon_geom from observation.all_pergrid_sr where grid_id is not null and centroid is not null"""
geom = pd.read_sql(geom_sql, engine)

mtcq_layer = Path('/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_11.tif')
col_names = ['grid_id', 'mtcq']
mtcq_var = pd.DataFrame(columns=col_names)
mtcq_var['grid_id'] = geom.grid_id

for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    Index_label = mtcq_var[mtcq_var['grid_id'] == grid_id].index.tolist()[0]
    polygon_geom = wkb.loads(geom.grid_polygon_geom[index], hex=True)

    features = [polygon_geom]
    try:
        with rio.open(mtcq_layer) as src:
            out_image, out_transform = mask(dataset=src, shapes=features, nodata=0, crop=True)
        non_zero_pixel_count = 0
        for i in range(2):
            non_zero_pixel_count = non_zero_pixel_count + out_image.nonzero()[i]
        if len(non_zero_pixel_count) != 0:
            mtcq_var.at[Index_label, 'mtcq'] = float(out_image.mean())
        else:
            print('Grid {grid_id} does not intersect with LULC. Pass!'.format(grid_id=grid_id))
    except Exception as e:
        print("Cropping failed for grid {grid_id}".format(grid_id=grid_id))
        print(repr(e))

mtcq_var.to_sql(name='pergrid_mtcq', schema='observation', con=engine, if_exists='replace', index=False)
