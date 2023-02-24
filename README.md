# sndgbiodb
./manage.py download_gbk NC_003047 | gzip > ./data/NC_003047.gbk.bgz
./manage.py load_gbk data/NC_003047.gbk.gz  --overwrite
./manage.py index_genome NC_003047
