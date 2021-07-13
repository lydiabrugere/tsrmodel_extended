create table derived.perplotperspcd_seedling as (
SELECT
  plotsnap.cn as plotsnap_cn,
  pop_eval_grp_most_recent.cn as eval_grp_cn,
  pop_eval_grp_most_recent.eval_grp_descr as eval_grp_descr,
  seedling.spcd,
  count(seedling.cn) as seedling_count
FROM
  fs_fiadb.cond,
  fs_fiadb.pop_eval_grp_most_recent,
  fs_fiadb.plotsnap,
  fs_fiadb.seedling
WHERE
  cond.plt_cn = plotsnap.cn AND
  plotsnap.eval_grp_cn = pop_eval_grp_most_recent.cn AND
  seedling.plt_cn = cond.plt_cn AND
  seedling.condid = cond.condid
GROUP BY plotsnap.cn, pop_eval_grp_most_recent.cn, pop_eval_grp_most_recent.eval_grp_descr, seedling.spcd);

alter table derived.perplotperspcd_seedling add column polt_geom geometry(Point,4269);
update derived.perplotperspcd_seedling A set polt_geom = B.geom
from fs_fiadb.plotsnap B
WHERE A.plotsnap_cn = B.cn
