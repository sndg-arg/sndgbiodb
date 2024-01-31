import os
import sys
import warnings
from Bio.SeqFeature import CompoundLocation, FeatureLocation, ExactPosition, SeqFeature
from Bio.bgzf import BgzfWriter
from tqdm import tqdm
import subprocess as sp
import gzip
import bgzip
from BCBio.GFF.GFFOutput import GFF3Writer, _IdHandler

import Bio.SeqIO as bpio

from django.core.management.base import BaseCommand

from Bio import BiopythonWarning, BiopythonParserWarning, BiopythonDeprecationWarning, BiopythonExperimentalWarning

from SNDG.Annotation.GenebankUtils import GenebankUtils
from bioseq.io.SeqStore import SeqStore
from bioseq.io.GenebankIO import GenebankIO

warnings.simplefilter('ignore', RuntimeWarning)
warnings.simplefilter('ignore', BiopythonWarning)
warnings.simplefilter('ignore', BiopythonParserWarning)
warnings.simplefilter('ignore', BiopythonDeprecationWarning)
warnings.simplefilter('ignore', BiopythonExperimentalWarning)


class _CircularLocation(FeatureLocation):

    def __init__(self, start, end, strand=None, ref=None, ref_db=None):
        self._start = ExactPosition(start)
        self._end = ExactPosition(end)

        self.strand = strand
        self.ref = ref
        self.ref_db = ref_db


class Command(BaseCommand):
    help = 'Index genome'

    def add_arguments(self, parser):
        parser.add_argument('--datadir', default=os.environ.get("BIOSEQDATADIR","./data") )
        parser.add_argument('accession')

    def handle(self, *args, **options):
        acc = options['accession']
        seqstore = SeqStore(options['datadir'])
        gbk = seqstore.gbk(acc)

        gbio = GenebankIO(gbk)
        utils = GenebankUtils()
        assert gbio.check(), f"'{gbk}' does not exists!"

        gbio.init(acc)
        """genome_fna = gbk.replace(".gbk.gz", ".genome.fna.bgz")
        genes_fna = gbk.replace(".gbk.gz", ".genes.fna.gz")
        faa = gbk.replace(".gbk.gz", ".faa.gz")
        gff = gbk.replace(".gbk.gz", ".gff.bgz")
        """
        genome_fna = seqstore.genome_fna(acc)
        genes_fna = seqstore.genes_fna(acc)
        faa = seqstore.faa(acc)
        gff = seqstore.gff(acc)

        with BgzfWriter(genome_fna) as hf, gzip.open(faa, "wt") as hp, gzip.open(
                genes_fna, "wt") as hge, BgzfWriter(gff) as hg:
            id_handler, writer = self.create_gff_writter(hg)
            for contig in tqdm(gbio.record_list(), total=gbio.total):
                # order is important, since write_gff_contig changes features
                bpio.write(utils.proteins_from_sequence(contig), hp, "fasta")
                bpio.write(utils.proteins_from_sequence(contig, otype="nucl"), hge, "fasta")
                bpio.write(contig, hf, "fasta")
                self.write_gff_contig(contig, hg, id_handler, writer)

        cmd = f'tabix -p gff {gff}'
        print(f'Command: {cmd}')
        sys.stderr.write(sp.check_output(cmd, shell=True).decode("utf-8"))
        cmd = f'samtools faidx {genome_fna}'
        sys.stderr.write(sp.check_output(cmd, shell=True).decode("utf-8"))
        cmd = f'zcat {genome_fna} | makeblastdb -dbtype nucl -in - -title {genome_fna} -out {genome_fna}'
        sys.stderr.write(sp.check_output(cmd, shell=True).decode("utf-8"))
        cmd = f'zcat {genes_fna} | makeblastdb -dbtype nucl -in - -title {genes_fna} -out {genes_fna}'
        sys.stderr.write(sp.check_output(cmd, shell=True).decode("utf-8"))
        cmd = f'zcat {faa} | makeblastdb -dbtype prot -in - -title {faa} -out {faa}'
        sys.stderr.write(sp.check_output(cmd, shell=True).decode("utf-8"))

        self.stderr.write("genome sequences indexed!")

    def write_gff_contig(self, contig, hg, id_handler, writer):
        writer._write_rec(contig, hg)
        #writer._write_annotations(contig.annotations, contig.id, len(contig.seq), hg)
        for sf in contig.features:

            sf = writer._clean_feature(sf)
            if "note" in sf.qualifiers:
                sf.qualifiers["note"] =  sf.qualifiers.get("gene", sf.qualifiers.get("locus_tag",[""]))[0]
            for ssf in sf.sub_features:
                if "note" in ssf.qualifiers:
                    ssf.qualifiers["note"] =  ssf.qualifiers.get("gene", ssf.qualifiers.get("locus_tag",[""]))[0]
            if isinstance(sf.location, CompoundLocation) and int(sf.location.start) == 0 and int(
                    sf.location.end) == len(contig) and "locus_tag" in sf.qualifiers:
                """for idx, part in enumerate(sf.location.parts):
                    sf2 = SeqFeature(location=part,
                                     type=sf.type,
                                     strand=sf.strand,
                                     id=sf.id,
                                     qualifiers={k: v for k, v in sf.qualifiers.items()},
                                     ref=sf.ref,
                                     ref_db=sf.ref_db)
                    sf2.sub_features = []

                    sf2.qualifiers["locus_tag"][0] = sf.qualifiers["locus_tag"][0] + f"_part_{idx}"
                    id_handler = writer._write_feature(sf2, contig.id, hg, id_handler)
                """
            elif sf.type not in ["source", "remark"]:
                id_handler = writer._write_feature(sf, contig.id, hg, id_handler)

    def create_gff_writter(self, hg):
        writer = GFF3Writer()
        writer._write_header(hg)
        id_handler = _IdHandler()
        return id_handler, writer
