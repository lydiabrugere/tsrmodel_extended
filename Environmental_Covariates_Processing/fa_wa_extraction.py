import os
from pathlib import Path

from sqlalchemy import create_engine
import pandas as pd
import rasterio as rio
import math
import numpy as np
from rasterstats import zonal_stats


water_pixel_val = [11, 12]
forest_pixel_val = [41,42,43]
localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
# geom_sql = """select distinct grid_id, grid_geom from fs_fiadb.pergrid"""
geom_sql = """select distinct grid_id, grid_polygon_geom from observation.all_pergrid_sr where grid_id is not null and centroid is not null"""
geom = pd.read_sql(geom_sql, engine)

data_dir = Path('/Users/lianfeng/Document/species_richness_sdm/data/processed/grid_level/tiff/nlcd')
os.chdir(data_dir)
col_names = ['grid_id', 'fa', 'wa']
fa_wa_var = pd.DataFrame(columns=col_names)
fa_wa_var['grid_id'] = geom.grid_id

cell_size = 0.03
cell_size_2 = math.pow(cell_size, 2)

for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    Index_label = fa_wa_var[fa_wa_var['grid_id'] == grid_id].index.tolist()[0]
    tif_name = 'grid' + str(grid_id) + '.tif'
    if os.path.exists(tif_name):
        src = rio.open(tif_name)
        array = src.read(1)

        water_mask = np.isin(array, water_pixel_val)
        water_unique, water_count = np.unique(water_mask, return_counts=True)
        if water_unique.shape == (1,):
            fa_wa_var.at[Index_label, 'wa'] = 0
        else:
            fa_wa_var.at[Index_label, 'wa'] = float(cell_size_2 * int(water_count[1]))

        forest_mask = np.isin(array, forest_pixel_val)
        forest_unique, forest_count = np.unique(forest_mask, return_counts=True)
        if forest_unique.shape == (1,):
            fa_wa_var.at[Index_label, 'fa'] = 0
        else:
            fa_wa_var.at[Index_label, 'fa'] = float(cell_size_2 * int(forest_count[1]))

fa_wa_var = fa_wa_var.astype({'wa':'float', 'fa': 'float'})
fa_wa_var[['grid_id', 'fa']].to_sql(name='pergrid_fa', schema='observation', con=engine, if_exists='replace', index=False)
