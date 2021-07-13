
select count(*) from derived.perplotperspcd_seedling -- "436257"
select count(*) from derived.perplotperspcd -- ""714805""
select count(*) from derived.perplotperspcd_combined -- "1151062"
select count(distinct A.*) from derived.perplotperspcd_combined A

-- 877737
create table derived.perplot_spcd as 
select distinct plotsnap_cn, eval_grp_cn, eval_grp_descr, spcd, plot_geom from derived.perplotperspcd_combined

alter table derived.perplot_spcd add column ogc_fid_eco integer
update derived.perplot_spcd A set ogc_fid_eco = B.ogc_fid
FROM geography.ecoregion B
where st_contains(B.wkb_geometry,A.plot_geom)

alter table derived.perplot_spcd add column province character varying(100); 
update derived.perplot_spcd A set province = B.province
FROM geography.ecoregion B
Where A.ogc_fid_eco = B.ogc_fid

alter table derived.perplot_spcd drop column eco_wkb_geometry;

alter table derived.perplot_spcd add column eco_wkb_geometry geometry(MultiPolygon,4269)
update derived.perplot_spcd A set eco_wkb_geometry = B.wkb_geometry
FROM geography.ecoregion B
Where A.ogc_fid_eco = B.ogc_fid

create table derived.ecoregion_sr as
select A.ogc_fid_eco, A.province, count(distinct A.spcd) AS SR_COUNT from derived.perplot_spcd A
group by A.ogc_fid_eco, A.province

alter table derived.ecoregion_sr add column wkb_geometry geometry(MultiPolygon,4269);

update derived.ecoregion_sr A set wkb_geometry = B.wkb_geometry
FROM geography.ecoregion B
Where A.ogc_fid_eco = B.ogc_fid
