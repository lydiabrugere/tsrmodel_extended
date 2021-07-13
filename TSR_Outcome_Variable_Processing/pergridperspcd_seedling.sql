---------------------- One complete query
create table derived.pergridperspcd_seedling as
SELECT
  plotsnap_grid.grid_id as grid_id,
  plotsnap_grid.grid_polygon_geom as grid_geom,
  pop_eval_grp_most_recent.cn as eval_grp_cn,
  pop_eval_grp_most_recent.eval_grp_descr as eval_grp_descr,
  seedling.spcd,
  ref_species.common_name,
  count(seedling.cn) as seedlings_count
FROM
  fs_fiadb.cond,
  fs_fiadb.pop_eval_grp_most_recent,
  fs_fiadb.plotsnap_grid,
  fs_fiadb.seedling,
  fs_fiadb.ref_species
WHERE
  cond.plt_cn = plotsnap_grid.cn AND
  plotsnap_grid.eval_grp_cn = pop_eval_grp_most_recent.cn AND
  seedling.plt_cn = cond.plt_cn AND
  seedling.condid = cond.condid
GROUP BY plotsnap_grid.grid_id, plotsnap_grid.grid_polygon_geom,
pop_eval_grp_most_recent.cn, pop_eval_grp_most_recent.eval_grp_descr, seedling.spcd, ref_species.common_name;
---------------------- In case server connection is too short; breaking down
create table derived.pergridperspcd_seedling as
SELECT
  plotsnap_grid.grid_id as grid_id,
  pop_eval_grp_most_recent.cn as eval_grp_cn,
  pop_eval_grp_most_recent.eval_grp_descr as eval_grp_descr,
  seedling.spcd,
  count(seedling.cn) as seedlings_count
FROM
  fs_fiadb.cond,
  fs_fiadb.pop_eval_grp_most_recent,
  fs_fiadb.plotsnap_grid,
  fs_fiadb.seedling
WHERE
  cond.plt_cn = plotsnap_grid.cn AND
  plotsnap_grid.eval_grp_cn = pop_eval_grp_most_recent.cn AND
  seedling.plt_cn = cond.plt_cn AND
  seedling.condid = cond.condid
GROUP BY plotsnap_grid.grid_id,
pop_eval_grp_most_recent.cn,pop_eval_grp_most_recent.eval_grp_descr, seedling.spcd;

alter table derived.pergridperspcd_seedling add column grid_polygon_geom geometry(Polygon,4269);
update derived.pergridperspcd_seedling A set grid_polygon_geom = B.grid_polygon_geom
from fs_fiadb.plotsnap_grid B
where A.grid_id = B.grid_id;

alter table derived.pergridperspcd_seedling add column common_name character varying(100);
update derived.pergridperspcd_seedling A set common_name = B.common_name
from fs_fiadb.ref_species B
where A.spcd = B.spcd;
