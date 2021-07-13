CREATE TABLE fs_fiadb.pop_eval_grp_most_recent as 
select A.* from fs_fiadb.pop_eval_grp A, fs_fiadb.most_recent_sample_year_by_state B
WHERE A.eval_grp_descr = B. eval_grp_descr

create table fs_fiadb.perplot as 
SELECT
  plotsnap.cn as plotsnap_cn,
  pop_eval_grp_most_recent.cn as eval_grp_cn,
  pop_eval_grp_most_recent.eval_grp_descr as eval_grp_descr,
  count(tree.cn) as tree_count
FROM
  fs_fiadb.cond,
  fs_fiadb.pop_eval_grp_most_recent,
  fs_fiadb.plotsnap,
  fs_fiadb.tree
WHERE
  cond.plt_cn = plotsnap.cn AND
  plotsnap.eval_grp_cn = pop_eval_grp_most_recent.cn AND
  tree.plt_cn = cond.plt_cn AND
  tree.condid = cond.condid
GROUP BY plotsnap.cn, pop_eval_grp_most_recent.cn, pop_eval_grp_most_recent.eval_grp_descr;

alter table fs_fiadb.perplot add column polt_geom geometry(Point,4269)
update fs_fiadb.perplot A set polt_geom = B.geom
from fs_fiadb.plotsnap B
WHERE A.plotsnap_cn = B.cn