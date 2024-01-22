import os
import Bio.SeqIO as bpio
import subprocess as sp
import gzip
from Bio import Entrez


class GenebankIO:

    def __init__(self, gbk_path, *args, **kwargs):
        super(GenebankIO, self).__init__(*args, **kwargs)
        self.gbk_path = gbk_path
        self.accession = None
        self.total = None
        self.taxon = None

    @staticmethod
    def get_stream_from_accession(accession, email="something@adomain.com"):
        Entrez.email = email

        return Entrez.efetch(
            db="nucleotide",
            id=accession,
            rettype="gbwithparts",
            retmode="text",
        )

    def check(self):
        return os.path.exists(self.gbk_path)

    def init(self,accession=None):
        if not accession:
            grep_cmd = f'cat "{self.gbk_path}" |  head  | grep "VERSION "'
            if self.gbk_path.endswith(".gz"):
                grep_cmd = 'z' + grep_cmd
            self.accession = sp.check_output(grep_cmd, shell=True).decode("utf-8").strip().split()
            if len(self.accession)>1:
                self.accession = self.accession[1]
            else:
                self.accession =None
                raise Exception("Empty ACCESSION")
        else:
            self.accession = accession

        print("hola")
        print(self.accession)
        grep_cmd = f'grep -c "FEATURES *Location/Qualifiers" "{self.gbk_path}"'
        if self.gbk_path.endswith(".gz"):
            grep_cmd = 'z' + grep_cmd
        self.total = int(sp.check_output(grep_cmd, shell=True))

        grep_cmd = f"cat {self.gbk_path} | grep 'db_xref=\"taxon:'|head -n1"
        if self.gbk_path.endswith(".gz"):
            grep_cmd = 'z' + grep_cmd
        try:
            taxon = sp.check_output(grep_cmd, shell=True).decode("utf-8").strip()
            taxon = taxon.split('/db_xref="taxon:')[1][:-1]
            self.taxon = int(taxon)
        except:
            pass

    def record_list(self, mode="t"):
        if self.gbk_path.endswith(".gz"):
            input_file_handle = gzip.open(self.gbk_path, "r" + mode)
        else:
            input_file_handle = open(self.gbk_path)
        try:
            for contig in bpio.parse(input_file_handle, "gb"):
                yield contig
        finally:
            input_file_handle.close()
