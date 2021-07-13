"""Reprojecting clipped tiff to EPSG:102008 """
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pathlib import Path
import os

data_dir = Path('/Users/lianfeng/OneDrive - The University of Memphis/Research/analysis/data/NLCD_2016_Land_Cover_L48_20190424')
os.chdir(data_dir)
path = 'NLCD_2016_Land_Cover_L48_20190424.img'

"""
'EPSG:102008' (Equal Area Conic) to 'EPSG:4326' 
"""

dst_crs = 'EPSG:4326'
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
    dst_path = './NLCD_2016_Land_Cover_L48_clipped.tif'
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