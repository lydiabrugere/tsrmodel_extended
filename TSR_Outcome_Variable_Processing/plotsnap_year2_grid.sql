SELECT 
  plotsnap_year2.eval_grp_descr as eval_grp_descr, 
  plotsnap_year2.eval_grp_cn as eval_grp_cn, 
  plotsnap_year2.plotsnap_cn as plotsnap_cn, 
  plotsnap_year2.lat as lat, 
  plotsnap_year2.lon as lon, 
  plotsnap_grid.grid_id as grid_id
FROM 
  public.plotsnap_grid, 
  public.plotsnap_year2
WHERE 
  plotsnap_grid.plotsnap_cn = plotsnap_year2.plotsnap_cn;
