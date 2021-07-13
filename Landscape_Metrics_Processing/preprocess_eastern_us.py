"""SE mixed forest"""
import rasterio
from sqlalchemy import create_engine
import pandas as pd
import rasterio as rio
from rasterio.mask import mask
from shapely import wkb

"""clip SE mixed forest LULC map to 20*20 grids; In total 1,042 grids"""
raster_path = "../data/se_mixed_forest_lu.tif"
localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
# sqlalchemy dialect: username:password@host:port/database
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
# this table contains all the grids which are completely within SE mixed forest (in total 1,042)
geom_sql = """select distinct grid_id, wkb_geometry from geography.fishnet_se_mixed_forest"""
geom = pd.read_sql(geom_sql, engine)
for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    geom_polygon = wkb.loads(geom.wkb_geometry[index], hex=True)
    features = [geom_polygon]
    #  print("Attempting to crop for grid {grid_id}".format(grid_id=grid_id))
    try:
        with rio.open(raster_path) as src:
            out_image, out_transform = mask(src, features, all_touched=True, crop=True)
            out_meta = src.meta.copy()
        print("Grid {grid_id} is cropped successfully".format(grid_id=grid_id))
        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        cropped_raster = "./clipped2grid_entire_us/grid" + str(grid_id) + '.tif'
        with rasterio.open(cropped_raster, "w", **out_meta) as dest:
            dest.write(out_image)
    except Exception as e:
        print(repr(e))
