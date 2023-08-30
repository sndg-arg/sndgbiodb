import os.path

from math import floor


class SeqStore:

    def __init__(self, datadir):
        self.datadir = datadir

    def idx_dir(self, accession):
        acclen = len(accession)
        return accession[floor(acclen / 2 - 1):floor(acclen / 2 + 2)]

    def db_dir(self,accession):
        return f'{self.datadir}/{self.idx_dir(accession)}/{accession}'

    def create_idx_dir(self, accession):
        idx_dir = f'{self.datadir}/{self.idx_dir(accession)}/{accession}'
        if not os.path.exists(idx_dir):
            os.makedirs(idx_dir)
        assert os.path.exists(idx_dir), f'"{idx_dir}" could not be created'

    def gbk(self, accession):
        return f'{self.datadir}/{self.idx_dir(accession)}/{accession}/{accession}.gbk.gz'

    def genome_fna(self, accession):
        return f'{self.datadir}/{self.idx_dir(accession)}/{accession}/{accession}.genome.fna.bgz'

    def genes_fna(self, accession):
        return f'{self.datadir}/{self.idx_dir(accession)}/{accession}/{accession}.genes.fna.gz'

    def gff(self, accession):
        return f'{self.datadir}/{self.idx_dir(accession)}/{accession}/{accession}.gff.bgz'

    def faa(self, accession):
        return f'{self.datadir}/{self.idx_dir(accession)}/{accession}/{accession}.faa.gz'

    def structure(self, biodbacc, bioentryacc, structacc):
        return f'{self.datadir}/{self.idx_dir(biodbacc)}/{biodbacc}/{bioentryacc}/{structacc}.pdb.gz'

    def structure_dir(self, biodbacc, bioentryacc):
        return f'{self.datadir}/{self.idx_dir(biodbacc)}/{biodbacc}/{bioentryacc}'
