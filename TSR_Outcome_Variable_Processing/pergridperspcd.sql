---------------------- One complete query
create table derived.pergridperspcd as
SELECT
  plotsnap_grid.grid_id as grid_id,
  plotsnap_grid.grid_polygon_geom as grid_geom,
  pop_eval_grp_most_recent.cn as eval_grp_cn,
  pop_eval_grp_most_recent.eval_grp_descr as eval_grp_descr,
  tree.spcd,
  ref_species.common_name,
  count(tree.cn) as tree_count
FROM
  fs_fiadb.cond,
  fs_fiadb.pop_eval_grp_most_recent,
  fs_fiadb.plotsnap_grid,
  fs_fiadb.tree,
  fs_fiadb.ref_species
WHERE
  cond.plt_cn = plotsnap_grid.plotsnap_cn AND
  plotsnap_grid.eval_grp_cn = pop_eval_grp_most_recent.cn AND
  tree.plt_cn = cond.plt_cn AND
  tree.condid = cond.condid
GROUP BY plotsnap_grid.grid_id,plotsnap_grid.grid_polygon_geom,
pop_eval_grp_most_recent.cn,pop_eval_grp_most_recent.eval_grp_descr, tree.spcd, ref_species.common_name;
---------------------- In case server connection is too short; breaking down
create table derived.pergridperspcd as
SELECT
  plotsnap_grid.grid_id as grid_id,
  pop_eval_grp_most_recent.cn as eval_grp_cn,
  pop_eval_grp_most_recent.eval_grp_descr as eval_grp_descr,
  tree.spcd,
  count(tree.cn) as tree_count
FROM
  fs_fiadb.cond,
  fs_fiadb.pop_eval_grp_most_recent,
  fs_fiadb.plotsnap_grid,
  fs_fiadb.tree
WHERE
  cond.plt_cn = plotsnap_grid.plotsnap_cn AND
  plotsnap_grid.eval_grp_cn = pop_eval_grp_most_recent.cn AND
  tree.plt_cn = cond.plt_cn AND
  tree.condid = cond.condid
GROUP BY plotsnap_grid.grid_id,
pop_eval_grp_most_recent.cn,pop_eval_grp_most_recent.eval_grp_descr, tree.spcd;

alter table derived.pergridperspcd add column grid_polygon_geom geometry(Polygon,4269);
update derived.pergridperspcd A set grid_polygon_geom = B.grid_polygon_geom
from fs_fiadb.plotsnap_grid B
where A.grid_id = B.grid_id;

alter table derived.pergridperspcd add column common_name character varying(100);
update derived.pergridperspcd A set common_name = B.common_name
from fs_fiadb.ref_species B
where A.spcd = B.spcd;
