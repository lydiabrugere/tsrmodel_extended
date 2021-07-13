create table derived.plots_grid as
  SELECT
  plotsnap_grid.grid_id as grid_id,
  plotsnap_grid.grid_polygon_geom as grid_geom,
  pop_eval_grp_most_recent.cn as eval_grp_cn,
  pop_eval_grp_most_recent.eval_grp_descr as eval_grp_descr
FROM
  fs_fiadb.pop_eval_grp_most_recent,
  fs_fiadb.plotsnap_grid
WHERE
  plotsnap_grid.eval_grp_cn = pop_eval_grp_most_recent.cn
GROUP BY pop_eval_grp_most_recent.cn,pop_eval_grp_most_recent.eval_grp_descr;
alter table fs_fiadb.pop_eval_grp_most_recent add column grid_id integer
update fs_fiadb.pop_eval_grp_most_recent A set grid_id = B.grid_id
FROM fs_fiadb.plotsnap_grid B
WHERE A.cn = b.eval_grp_cn
