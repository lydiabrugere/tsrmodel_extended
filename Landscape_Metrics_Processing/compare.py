import pandas as pd
import os

tif_file = '../grids_result_list.txt'
txt_file = '../grids_tif_list.txt'

tif_pd = pd.read_table(tif_file, names=['path'])
tif_list = tif_pd['path'].tolist()
tif_list1 = [tif_path[:-4] for tif_path in tif_list]

txt_pd = pd.read_table(txt_file, names=['path'])
txt_list = txt_pd['path'].tolist()
txt_list1 = [txt_path[:-4] for txt_path in txt_list]

no_matches1 = list(set(txt_list1) - set(tif_list1))
# no_matches2 = list(set(tif_list1) - set(txt_list1))
# matches = set(tif_list1) & set(txt_list1)
# matches_list= list(matches)

redo_dir = "../redo"
for i in range(len(no_matches1)):
    match_file = no_matches1[i]
    mv_cmd = 'cp ../data/clipped2grid_projected/{}.tif {}'.format(match_file, redo_dir)
    os.system(mv_cmd)
