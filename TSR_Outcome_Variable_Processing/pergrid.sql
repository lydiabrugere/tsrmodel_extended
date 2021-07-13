select count(*) from derived.pergrid
create table derived.pergrid as
  SELECT
  plotsnap_grid.grid_id as grid_id,
  plotsnap_grid.grid_polygon_geom as grid_geom,
  pop_eval_grp_most_recent.cn as eval_grp_cn,
  pop_eval_grp_most_recent.eval_grp_descr as eval_grp_descr,
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
GROUP BY plotsnap_grid.grid_id,plotsnap_grid.grid_polygon_geom, pop_eval_grp_most_recent.cn,pop_eval_grp_most_recent.eval_grp_descr;
