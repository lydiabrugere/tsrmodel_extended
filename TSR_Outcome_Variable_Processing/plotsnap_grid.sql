create table fs_fiadb.plotsnap_grid as
SELECT
  A.*,
  fishnet.grid_id AS grid_id,
  fishnet.geom AS grid_polygon_geom
FROM
(SELECT
  plotsnap.*
FROM fs_fiadb.plotsnap plotsnap, fs_fiadb.pop_eval_grp_most_recent most_recent
WHERE plotsnap.eval_grp_cn = most_recent.cn) A
JOIN geography.fishnet  AS fishnet
ON ST_Contains(fishnet.geom, A.geom);

SELECT COUNT(*) FROM fs_fiadb.plotsnap_grid -- "351396"
SELECT COUNT(distinct geom) FROM fs_fiadb.plotsnap_grid -- "351368"
SELECT COUNT(distinct grid_polygon_geom) FROM fs_fiadb.plotsnap_grid -- "20251"
SELECT COUNT(distinct grid_id) FROM fs_fiadb.plotsnap_grid -- "20251"
SELECT COUNT(distinct geom) FROM geography.fishnet -- "33033"
