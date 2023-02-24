#!/bin/bash
docker run -v $PWD/data:/jbrowse2/data --rm -u $(id -u ${USER}):$(id -g ${USER}) \
  -v $PWD:$PWD jbrowse jbrowse add-assembly data/${1}.genome.fna.bgz --load copy \
  --out data/jbrowse/${1}/ --type bgzipFasta -n "Ref"
docker run -v $PWD/data:/jbrowse2/data --rm -u $(id -u ${USER}):$(id -g ${USER}) \
  -v $PWD:$PWD jbrowse jbrowse add-track data/${1}.gff.bgz --load copy --out data/jbrowse/${1}/ -n Annotation --trackId=Annotation
rm data/jbrowse/${1}/${1}*
cp -l data/${1}.genome.fna.bgz* data/jbrowse/${1}/
cp -l data/${1}.gff.bgz* data/jbrowse/${1}/

#https://jbrowse.org/jb2/docs/urlparams/
#http://localhost:3000/?config=data/jbrowse/NC_003047/config.json&loc=NC_003047.1:1,808,037..1,855,678&assembly=Ref&tracks=Annotation,Ref-ReferenceSequenceTrack