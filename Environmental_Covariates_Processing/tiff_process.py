from sqlalchemy import create_engine
import pandas as pd
import rasterio as rio
import rasterio.mask
import shapely
from shapely import wkb
from pathlib import Path
import os
from PIL import Image


def get_grids():
    """Load grid id and geometry from pg"""
    localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
    params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
    engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
    # geom_sql = """select distinct grid_id, grid_polygon_geom as geom from observation.all_pergrid_sr where grid_id is not null and grid_polygon_geom is not null"""
    geom_sql = """select distinct grid_id, wkb_geometry as geom from predictor.pergrid_base where grid_id is not null and wkb_geometry is not null"""
    grids = pd.read_sql(geom_sql, engine)
    return grids


def crop2grid(rasterPath, predictor):
    """Crop nation-wide raster to grid-sized image"""
    # dest_dir = '/Users/lianfeng/Document/species_richness_sdm/data/processed/grid_level/tiff/' + predictor
    # Path(dest_dir).mkdir(parents=True, exist_ok=True)
    dest_dir ='/Users/lianfeng/Document/species_richness_sdm/src/notebooks/machine_learning/nlcd_base'
    os.chdir(dest_dir)
    grids = get_grids()

    with rio.open(rasterPath) as src:
        for index in range(grids.shape[0]):
            grid_id = int(grids.grid_id[index])
            geom_polygon = wkb.loads(grids.geom[index], hex=True)  # string to wkb

            # shapely polygon to feature list
            features = [{'type': 'Feature', 'properties': {}, 'geometry': shapely.geometry.mapping(geom_polygon)}]

            shapes = [feature["geometry"] for feature in features]

            out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
            out_meta = src.meta

            out_meta.update({"driver": "GTiff",
                             "height": out_image.shape[1],
                             "width": out_image.shape[2],
                             "transform": out_transform})

            with rio.open("{predictor}_{grid_id}.tif".format(predictor=predictor, grid_id=grid_id), "w", **out_meta) as dest:
                dest.write(out_image)
    return dest_dir


def tiff2jpeg(rasterPath, predictor):
    src_dir = crop2grid(rasterPath, predictor)
    data_dir = '/Users/lianfeng/Document/species_richness_sdm/src/notebooks/machine_learning/nlcd_jpg'
    dest_dir = data_dir
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(src_dir, topdown=False):
        for name in files:
            print(os.path.join(root, name))
            if os.path.splitext(os.path.join(root, name))[1].lower() == ".tif":
                if os.path.isfile(os.path.splitext(os.path.join(root, name))[0] + ".jpg"):
                    print("A jpeg file already exists for %s" % name)
                # If a jpeg with the name does *NOT* exist, convert one from the tif.
                else:
                    outputfile = dest_dir + '/' + name.split('.')[0] + ".jpg"
                    try:
                        im = Image.open(os.path.join(root, name))
                        print("Converting jpeg for %s" % name)
                        if im.mode != 'RGB':
                            new_im = im.convert('RGB')
                            new_im.thumbnail(im.size)
                            new_im.save(outputfile, "JPEG", quality=100)
                    except Exception as e:
                        print(e)

predictor='nlcd'
src_dir='/Volumes/data/data/processed/grid_level/tiff/nlcd'

tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_1.tif', predictor='mat')
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/raw/PET/et0_yr.tif', predictor="pet")
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_10.tif', predictor="mtwq")
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/raw/AET/MOD16A3_ET_2000_to_2013_mean.tif', predictor="aet")
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/processed/mfdf.tif', predictor="mfdf")
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_17.tif', predictor="mpdq")
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_11.tif', predictor="mtcq")
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/raw/AI/ai_et0.tif', predictor="ai")
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/interim/altitude/US_gtopo30_merged_4269.tif', predictor='alt_ra')
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_12.tif', predictor="map")
tiff2jpeg(rasterPath='/Volumes/research/raster_30m_hydrogrp/raster_30m_hydogrp.tif', predictor="soil")
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_7.tif', predictor='art')
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_15.tif', predictor='psn')
tiff2jpeg(rasterPath='/Users/lianfeng/Document/species_richness_sdm/data/processed/nation_wide/wc2.1_30s_bio_4.tif', predictor='tsn')
