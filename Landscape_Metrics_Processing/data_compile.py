from pathlib import Path
import os

from sqlalchemy import create_engine
import pandas as pd

""" 1. read landscape level metrics for each grid and compile all the data to wide table"""
columns=['ai', 'area_cv', 'area_mn', 'area_sd', 'cai_cv', 'cai_mn', 'cai_sd',
       'circle_cv', 'circle_mn', 'circle_sd', 'cohesion', 'condent', 'contag',
       'contig_cv', 'contig_mn', 'contig_sd', 'core_cv', 'core_mn', 'core_sd',
       'dcad', 'dcore_cv', 'dcore_mn', 'dcore_sd', 'division', 'ed', 'enn_cv',
       'enn_mn', 'enn_sd', 'ent', 'frac_cv', 'frac_mn', 'frac_sd', 'gyrate_cv',
       'gyrate_mn', 'gyrate_sd', 'iji', 'joinent', 'lpi', 'lsi', 'mesh',
       'msidi', 'msiei', 'mutinf', 'ndca', 'np', 'pafrac', 'para_cv',
       'para_mn', 'para_sd', 'pd', 'pladj', 'pr', 'prd', 'rpr', 'shape_cv',
       'shape_mn', 'shape_sd', 'shdi', 'shei', 'sidi', 'siei', 'split', 'ta',
       'tca', 'te']
grid_metrics_df = pd.DataFrame(columns=columns)
data_dir = Path('/Users/lianfeng/OneDrive - The University of Memphis/Research/analysis/data/lsm_landscape_results')
for result_path in data_dir.iterdir():
    if str(result_path).endswith('csv'):
        result = pd.read_csv(result_path)
        df = result.pivot(index='layer', columns='metric', values='value')
        grid = str(result_path).split('/')[-1][4:-4]
        df['grid_id'] = grid
        grid_metrics_df = grid_metrics_df.append(df)

""" 2. save to postgres or csv file"""
localhost = {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': 5432, 'db': 'fiadb'}
params = 'postgresql://{0}:{1}@{2}:{3}/{4}'
engine = create_engine(params.format(localhost['user'], localhost['password'], localhost['host'], localhost['port'], localhost['db']))
grid_metrics_df.to_sql('grid_sr_lsm', engine, schema='derived', if_exists='replace')

if os.path.isfile('../data/grid_lsm_sr.csv'):
    os.remove('../data/grid_lsm_sr.csv')
grid_metrics_df.to_csv('../data/grid_lsm_sr.csv')


""" 3. update grid geom and SR for the lsm table"""
update_grid_geom = """
                    alter table derived.grid_sr_lsm drop column if exists grid_geom; 
                    alter table derived.grid_sr_lsm add column grid_geom geometry(Polygon,4269);
                    update derived.grid_sr_lsm A set grid_geom = B.grid_geom from fs_fiadb.pergrid B
                    where A.grid_id = B.grid_id::TEXT;
"""
update_grid_sr = """
                    alter table derived.grid_sr_lsm drop column if exists tree_count; 
                    alter table derived.grid_sr_lsm add column tree_count bigint;
                    update derived.grid_sr_lsm A set tree_count = B.tree_count from fs_fiadb.pergrid B
                    where A.grid_id = B.grid_id::TEXT;
"""
connection = engine.connect()
connection.execute(update_grid_geom)
connection.execute(update_grid_sr)
connection.close


"""rename"""

data_dir = Path('/Users/lianfeng/OneDrive - The University of Memphis/Research/analysis/data/lsm_result2')
os.chdir(data_dir)
for result_path in data_dir.iterdir():
    if str(result_path).endswith('csv'):
        old_name= str(result_path).split('/')[-1]
        new_name = str(result_path).split('/')[-1][6:]
        os.rename(old_name, new_name)