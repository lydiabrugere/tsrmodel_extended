"""NCLD national Tiff: 15256 grids"""
from pathlib import Path
import os

import rasterio
from sqlalchemy import create_engine
import pandas as pd
import rasterio as rio
from rasterio.mask import mask
from shapely import wkb

"""clip SE mixed forest LULC map to 20*20 grids; In total 1,042 grids"""
data_dir = Path('/Users/lianfeng/OneDrive - The University of Memphis/Research/analysis/data/NLCD_2016_Land_Cover_L48_20190424')
os.chdir(data_dir)
raster_path = 'NLCD_2016_Land_Cover_L48_20190424.img'
dataset = rasterio.open(raster_path)
dataset.crs

localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
# geom_sql = """select distinct grid_id, grid_geom from fs_fiadb.pergrid"""
geom_sql = """select distinct grid_id, wkb_geometry from geography.fishnet"""
geom = pd.read_sql(geom_sql, engine)

for index in range(100):
# for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    geom_polygon = wkb.loads(geom.wkb_geometry[index], hex=True)
    features = [geom_polygon]
    # print("Attempting to crop for grid {grid_id}".format(grid_id=grid_id))
    try:
        with rio.open(raster_path) as src:
            out_image, out_transform = mask(src, features, all_touched=True, crop=True)
            out_meta = src.meta.copy()
        non_zero_pixel_count = 0
        for i in range(2):
            non_zero_pixel_count = non_zero_pixel_count + out_image.nonzero()[i]
        if len(non_zero_pixel_count) != 0:
            out_meta.update({"driver": "GTiff",
                             "height": out_image.shape[1],
                             "width": out_image.shape[2],
                             "transform": out_transform})
            cropped_raster = "./clipped2grid_entire_us/grid" + str(grid_id) + '.tif'
            with rasterio.open(cropped_raster, "w", **out_meta) as dest:
                dest.write(out_image)
            print("Grid {grid_id} is cropped successfully".format(grid_id=grid_id))
        else:
            print('Grid {grid_id} doesn not intersects with LULC. Pass!'.format(grid_id=grid_id))
    except Exception as e:
        print("Cropping failed for grid {grid_id}".format(grid_id=grid_id))
        print(repr(e))
