"""
This script calculate mean Aridity Index for each grid
Source Data:
https://cgiarcsi.community/2019/01/24/global-aridity-index-and-potential-evapotranspiration-climate-database-v2/
Reference:
Trabucco, Antonio; Zomer, Robert (2019): Global Aridity Index and Potential Evapotranspiration (ET0) Climate Database v2. figshare. Fileset. https://doi.org/10.6084/m9.figshare.7504448.v3
Download Page:
https://figshare.com/articles/Global_Aridity_Index_and_Potential_Evapotranspiration_ET0_Climate_Database_v2/7504448/3
Data size: 1.59 GB
Method:
    1. Crop global AI to each 20 by 20 km grid;
    2. Calculate Mean of each grid

Be cautious!!!: original dataset is multiplied by a factor of 10,000
"""

from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd
import rasterio as rio
from rasterio.mask import mask
from shapely import wkb


localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
geom_sql = """select distinct grid_id, grid_polygon_geom from observation.all_pergrid_sr where grid_id is not null and centroid is not null"""
geom = pd.read_sql(geom_sql, engine)

ai_layer = Path('/Users/lianfeng/Document/species_richness_sdm/data/raw/AI/ai_et0.tif')
col_names = ['grid_id', 'ai']
ai_var = pd.DataFrame(columns=col_names)
ai_var['grid_id'] = geom.grid_id

for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    Index_label = ai_var[ai_var['grid_id'] == grid_id].index.tolist()[0]
    polygon_geom = wkb.loads(geom.grid_polygon_geom[index], hex=True)

    features = [polygon_geom]
    try:
        with rio.open(ai_layer) as src:
            out_image, out_transform = mask(dataset=src, shapes=features, nodata=0, crop=True)
        non_zero_pixel_count = 0
        for i in range(2):
            non_zero_pixel_count = non_zero_pixel_count + out_image.nonzero()[i]
        if len(non_zero_pixel_count) != 0:
            ai_var.at[Index_label, 'ai'] = float(out_image.mean()/10000)
        else:
            print('Grid {grid_id} does not intersect with LULC. Pass!'.format(grid_id=grid_id))
    except Exception as e:
        print("Cropping failed for grid {grid_id}".format(grid_id=grid_id))
        print(repr(e))

ai_var.to_sql(name='pergrid_ai', schema='observation', con=engine, if_exists='replace', index=False)
