create table predictor.pergrid_base as
select a.grid_id,a.aet,b.ai,c.art,d.ewd,e.fa,f.map,g.mat,h.mpdq,i.mtcq,j.pet,k.psn,l.ra,m.rmap,n.rmat,o.tsn,p.mfdf,q.alt, r.hydgrpdcd_num as shg, s.mtwq, t.wa from
observation.pergrid_aet a,
observation.pergrid_ai b,
observation.pergrid_art c,
observation.pergrid_ewd d,
observation.pergrid_fa e,
observation.pergrid_map f,
observation.pergrid_mat g,
observation.pergrid_mpdq h,
observation.pergrid_mtcq i,
observation.pergrid_pet2 j,
observation.pergrid_psn k,
observation.pergrid_ra l,
observation.pergrid_rmap m,
observation.pergrid_rmat n,
observation.pergrid_tsn o,
observation.pergrid_mfdf p,
observation.pergrid_alt q,
observation.pergrid_soil r,
observation.pergrid_mtwq s,
predictor.pergrid_wa t
where a.grid_id=b.grid_id
and a.grid_id=c.grid_id
and a.grid_id=d.grid_id
and a.grid_id=e.grid_id
and a.grid_id=f.grid_id
and a.grid_id=g.grid_id
and a.grid_id=h.grid_id
and a.grid_id=i.grid_id
and a.grid_id=j.grid_id
and a.grid_id=k.grid_id
and a.grid_id=l.grid_id
and a.grid_id=m.grid_id
and a.grid_id=n.grid_id
and a.grid_id=o.grid_id
and a.grid_id=p.grid_id
and a.grid_id=q.grid_id
and a.grid_id=r.grid_id
and a.grid_id=s.grid_id
and a.grid_id=t.grid_id;

select * from predictor.pergrid_base 

alter table predictor.pergrid_base add column wkb_geometry geometry(Polygon,4269);
update predictor.pergrid_base A SET wkb_geometry = B.grid_polygon_geom
FROM observation.all_pergrid_sr B
WHERE A.grid_id = B.grid_id;

alter table predictor.pergrid_base add column tsr bigint;
update predictor.pergrid_base A set tsr = B.sr_count
from observation.all_pergrid_sr B
WHERE A.grid_id = B.grid_id;

alter table predictor.pergrid_base
alter column tsr set data type double precision USING tsr::double precision;

select distinct grid_id, tsr from predictor.pergrid_base 
where fa<=0.0 -- 310

select distinct grid_id, tsr from predictor.pergrid_base 
where tsr =0 -- 0

create table observation.pergrid_base_cleaned as 
select * from observation.pergrid_base 
where fa >0.0 and tsr > 0.0

select count(*) from observation.all_pergrid_sr 
where grid_id is not null and centroid is not null
