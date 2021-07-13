import numpy as np
from scipy import ndimage
import rasterio
import math
from sqlalchemy import create_engine
import pandas as pd
# clip landcover map with the geom and output a raster
import rasterio as rio
from rasterio.mask import mask
from shapely import wkb

raster_path = "./data/se_mixed_forest_lu_4269.tif"
dataset_raw = rasterio.open(str(raster_path))
localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
# sqlalchemy dialect: username:password@host:port/database
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
# entire  state: 15,256 grids; SE mixed forest: 1,475 grids
geom_sql = """select distinct grid_id, grid_geom from fs_fiadb.pergridperspcd_se_mixed_forest"""
geom = pd.read_sql(geom_sql, engine)
for index in range(geom.shape[0]):
    grid_id = geom.grid_id[index]
    geom_polygon = wkb.loads(geom.grid_geom[index], hex=True)
    features = [geom_polygon]
    print("Attempting to crop for grid {grid_id}".format(grid_id=grid_id))
    try:
        with rio.open(raster_raw) as src:
            out_image, out_transform = mask(src, features, all_touched=True, crop=True)
            out_meta = src.meta.copy()
        print("Grid {grid_id} is cropped successfully".format(grid_id=grid_id))
    except Exception as e:
        print("Cropping failed for grid {grid_id}".format(grid_id=grid_id))
        print(repr(e))
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})
    cropped_raster = "./data/clipped2grid/se_mixed_forest_lu_" + str(grid_id) + '.tif'
    with rasterio.open(cropped_raster, "w", **out_meta) as dest:
        dest.write(out_image)

raster_path = "./data/clipped2grid/se_mixed_forest_lu_5669.tif"
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
lulc_test = mpimg.imread(raster_path)
lulc_test_img = plt.imshow(lulc_test)
type(lulc_test)
num_row, num_col = lulc_test.shape  # define hight and width of input matrix
with_borders = np.ones((num_row + 2, num_col + 2)) * 0  # set the border to borderValue
with_borders[1:num_row + 1, 1:num_col + 1] = lulc_test  # set the interior region to the input matrix

# TotalPerimeter = np.sum(labeled_array[:, 1:] != labeled_array[:, :-1]) + np.sum(labeled_array[1:, :] != labeled_array[:-1, :])
peri1 = np.sum(with_borders[:, 1:] != with_borders[:, :-1]) + np.sum(with_borders[1:, :] != with_borders[:-1, :])
peri_min = np.minimum(with_borders[with_borders[:, 1:] != with_borders[:, :-1]]) + np.minimum(with_borders[1:, :] != with_borders[:-1, :])
_, occ_count1 = np.unique((with_borders[:, 1:] != with_borders[:, :-1]), return_counts=True)
_, occ_count2 = np.unique((with_borders[1:, :] != with_borders[:-1, :]), return_counts=True)

s = ndimage.generate_binary_structure(2, 1)
labeled_array, num_patches = ndimage.label(lulc_test, s)

plt.imshow(with_borders)


"""Reprojection"""
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pathlib import Path

dst_crs = 'EPSG:102008'

src_dir = './clipped2grid'
dst_dir = './clipped2grid_projected'

pathlist = Path(src_dir).glob('**/*.tif')
for path in pathlist:
    print(str(path))

    with rasterio.open(path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        dst_path = dst_dir + '/' + str(path).split('/')[-1]
        with rasterio.open(dst_path, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)