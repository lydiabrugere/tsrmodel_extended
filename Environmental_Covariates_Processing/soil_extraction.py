"""
This script calculate the domainant soil type for each grid
Source Data:
https://www.nrcs.usda.gov/wps/portal/nrcs/detail/soils/home/?cid=nrcs142p2_053628
Reference:

Download Page:
https://figshare.com/articles/Global_Aridity_Index_and_Potential_Evapotranspiration_ET0_Climate_Database_v2/7504448/3
https://casoilresource.lawr.ucdavis.edu/soil_web/ssurgo.php?action=list_mapunits&areasymbol=la019
Method:
    1. Crop global Soil to each 20 by 20 km grid;
    2. Calculate the dominant soil type
Reconcile projection before extract pixel value:
    Soil layer is projected as Albers NorthAm; so reproject grid layer to 42303 before extract grid values
    -- in qgis open a new project; load soil layer, then load grid layer and save the grid layer to the projection of soil layer
"""

from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd
from rasterstats import zonal_stats
from shapely import wkb

localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
# geom_sql = """select distinct grid_id, wkb_geometry as geom from derived.pergrid_sr_combined_projected"""
geom_sql = """select distinct grid_id, wkb_geometry as geom from observation.all_pergrid_sr_projected where grid_id is not null and grid_polygon_geom is not null"""
geom = pd.read_sql(geom_sql, engine)

# /Volumes/research/raster_30m_hydrogrp/raster_30m_hydogrp.tif
input_layer = Path('/Volumes/research/raster_30m_hydrogrp/raster_30m_hydogrp.tif')
col_names = ['grid_id', 'soil']
soil_var = pd.DataFrame(columns=col_names)
soil_var['grid_id'] = geom.grid_id

for index in range(geom.shape[0]):
    grid_id = int(geom.grid_id[index])
    Index_label = soil_var[soil_var['grid_id'] == grid_id].index.tolist()[0]
    geom_polygon = wkb.loads(geom.geom[index], hex=True)
    # stats = zonal_stats(geom_polygon, soil_layer, stats="count mean majority")
    # if stats[0]['count'] == 0:
    #     print('Grid {grid_id} does not intersect for non-zero value. Pass!'.format(grid_id=grid_id))
    # else:
    #     grid_val = int(stats[0]['majority'])
    #     soil_var.at[Index_label, 'soil'] = grid_val

    features = [geom_polygon]
    try:
        with rio.open(input_layer) as src:
            # fill nodata area within a grid as np.nan
            out_image, out_transform = mask(dataset=src, shapes=features, nodata=np.nan, crop=True)

        # if all NaN within a grid, no data is extracted for now but will fill using KNN from neighbor grids
        if not np.isnan(out_image).all():
            # calculate stats for non-NaN pixels within bdry
            df.at[Index_label, vars[0]] = float(np.nanmean(out_image))/num


    except Exception as e:
        print("Cropping failed for grid {grid_id}".format(grid_id=grid_id))
        print(repr(e))

"""
(values,counts) = np.unique(a,return_counts=True)
ind=np.argmax(counts)
print values[ind] 
"""
# in total 253 out 15310 grids are null
soil_var.to_sql(name='pergrid_soil', schema='observation', con=engine, if_exists='replace', index=False)

update_geom = """
alter table observation.pergrid_soil add column wkb_geometry geometry(Polygon,4269);
update observation.pergrid_soil A SET wkb_geometry = B.grid_polygon_geom
FROM derived.pergrid_sr_combined B
WHERE A.grid_id = B.grid_id
"""
connection = engine.connect()
connection.execute(update_geom)

# update soil hydrological group
# muaggatt = pd.read_csv('/Users/lianfeng/Document/species_richness_sdm/data/raw/gssurgo/muaggatt.csv')
# muaggatt.to_sql(name='muaggatt', schema='predictor', con=engine, if_exists='replace', index=False)

update_soil_type = """alter table predictor.pergrid_soil add column hydgrpdcd text;
                        update predictor.pergrid_soil A set hydgrpdcd = B. hydgrpdcd
                        FROM predictor.muaggatt B
                        WHERE A.soil = B.mukey"""

connection = engine.connect()
connection.execute(update_soil_type)





