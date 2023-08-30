# sndgbiodb

```console
conda create -n tpv2 -c conda-forge -c bioconda python=3.10 samtools blast bedtools bcftools
conda activate tpv2

./manage.py download_gbk NC_003047 | gzip 
./manage.py load_gbk data/003/NC_003047.gbk.gz  --overwrite
./manage.py index_genome_db NC_003047
./manage.py index_genome_seq NC_003047

# interproscan usualy wont be runned locally
# zcat data/003/NC_003047.faa.gz | interproscan.sh --pathways --goterms --cpu 10 -iprlookup --formats tsv -i - --output-dir ./ -o data/003/NC_003047.faa.tsv
# gzip data/003/NC_003047.faa.tsv

./manage.py load_interpro NC_003047 data/003/NC_003047.faa.tsv.gz


./manage.py gbk2uniprot_map NC_003047 --mapping_tmp data/003/NC_003047_unips_mapping.csv \
    --not_mapped data/003/NC_003047_unips_not_mapped.lst > data/003/NC_003047_unips.lst

cat data/003/NC_003047_unips.lst | head -n 2|  python -m "TP.alphafold" -pr /opt/p2rank_2.4/prank -o data/003/NC_003047/ -T 10 -nc

docker --rm -it -v $PWD:$PWD ezequieljsosa/fpocket fpocket -f data/003/NC_003047/SM_RS15270/SM_RS15270.pdb_out/

./manage.py load_af_model SM_RS15270 "data/003/NC_003047/Q92LQ0/Q92LQ0_AF.pdb" SM_RS15270 --overwrite
python -m "SNDG.Structure.FPocket" 2json data/003/NC_003047/SM_RS15270/SM_RS15270.pdb_out| gzip >  data/003/NC_003047/SM_RS15270/fpocket.json.gz
echo -e "\n" | gzip >> data/003/NC_003047/SM_RS15270/SM_RS15270.pdb.gz
# we should filter only pockets with druggability > 0.2
grep "^HETATM"  data/003/NC_003047/SM_RS15270/SM_RS15270.pdb_out/SM_RS15270.pdb_out.pdb  | grep "STP" | grep "POL" | gzip >> data/003/NC_003047/SM_RS15270/SM_RS15270.pdb.gz
    


```