import os.path
import sys
import tempfile
import warnings
from io import StringIO

from django.core.management.base import BaseCommand

from bioseq.io.BioIO import BioIO
from Bio import BiopythonWarning, BiopythonParserWarning, BiopythonDeprecationWarning, BiopythonExperimentalWarning

from bioseq.io.GenebankIO import GenebankIO
from bioseq.io.SeqStore import SeqStore
from bioseq.io.TaxIO import TaxIO
from bioseq.models.Biodatabase import Biodatabase
from bioseq.models.Bioentry import Bioentry
from bioseq.models.BioentryDbxref import BioentryDbxref
from bioseq.models.BioentryQualifierValue import BioentryQualifierValue
from bioseq.models.Dbxref import Dbxref
from bioseq.models.Location import Location
from bioseq.models.Ontology import Ontology
from bioseq.models.Seqfeature import Seqfeature
from bioseq.models.Term import Term

warnings.simplefilter('ignore', RuntimeWarning)
warnings.simplefilter('ignore', BiopythonWarning)
warnings.simplefilter('ignore', BiopythonParserWarning)
warnings.simplefilter('ignore', BiopythonDeprecationWarning)
warnings.simplefilter('ignore', BiopythonExperimentalWarning)

from django.db import transaction
from tqdm import tqdm
import subprocess as sp
import json
import time
import pandas as pd
from django.db import transaction


class Command(BaseCommand):
    help = 'loads interprot annotation'

    def add_arguments(self, parser):
        parser.add_argument('accession')
        parser.add_argument('--interpro_tsv', help="Interpro results file",default=None)
        parser.add_argument('--datadir', default="./data")
        """parser.add_argument('--polling_interval', type=int, default=5)
        parser.add_argument('--mapping_tmp', type=str)
        parser.add_argument('--not_mapped', type=str,default="not_mapped.lst")"""

    def handle(self, *args, **options):
        seqstore = SeqStore(options['datadir'])
        accession = options['accession'] + BioIO.GENOME_PROT_POSTFIX
        interpro_tsv = options['interpro_tsv']
        if not interpro_tsv:
            interpro_tsv = seqstore.faa(options['accession']).replace(".gz",".tsv.gz")

        assert os.path.exists(interpro_tsv), f'"{interpro_tsv}" does not exists'
        assert Biodatabase.objects.filter(name=accession).exists(), "'%s' does not exists" % accession

        ipcols = "acc MD5 length analysis accession description start stop score status date IPAcc IPDesc gos pws".split()
        if interpro_tsv.endswith(".gz"):
            df = pd.read_csv(interpro_tsv, sep="\t", compression='gzip', names=ipcols).fillna("")
        else:
            df = pd.read_csv(interpro_tsv, sep="\t", names=ipcols).fillna("")

        ontologies = list(df.analysis.unique())
        ontologies = {x: Ontology.objects.get_or_create(name=x)[0] for x in ontologies}
        ontologies[Ontology.GO] = Ontology.objects.filter(name=Ontology.GO).get()
        ontologies["InterProScan"] = Ontology.objects.get_or_create(
            name="InterProScan")[0]
        ontologies["InterPro"] = Ontology.objects.get_or_create(
            name="InterPro")[0]

        terms = {}
        for _, r in tqdm(df.iterrows(), total=len(df)):

            key = r.analysis + "||" + r.accession
            if key not in terms:
                t = Term.objects.filter(ontology=ontologies[r.analysis], identifier=r.accession)
                if t.exists():
                    terms[key] = t.get()
                else:
                    t = Term.objects.create(ontology=ontologies[r.analysis], identifier=r.accession,
                                            name=r.description)
                    terms[key] = t
            if r.IPAcc and r.IPAcc not in terms and r.IPAcc != "-":
                t = Term.objects.get_or_create(ontology=ontologies["InterPro"], identifier=r.IPAcc,
                                               name=r.IPDesc)[0]
                terms[r.IPAcc] = t
            for go in r.gos.split("|"):
                if go not in terms:
                    goterm = Term.objects.filter(ontology=ontologies[Ontology.GO], identifier=go)
                    if goterm.exists():
                        terms[go] = goterm.get()

        terms["InterProScan"] = Term.objects.get_or_create(ontology=Ontology.objects.get(name=Ontology.ANNTAGS),
                                                           identifier="InterProScan")[0]

        for acc, df_prot in tqdm(df.groupby("acc")):
            try:
                be = Bioentry.objects.filter(accession=acc).get()

                gos = []
                with transaction.atomic():

                    for idx, r in df_prot.iterrows():
                        """
                        
                        
                        source_term = models.ForeignKey('Term', models.DO_NOTHING, related_name="source_of")
                        display_name = models.CharField(max_length=64, blank=True, null=True)
                        rank = models.PositiveSmallIntegerField(default=1, null=True)
                        """
                        key = r.analysis + "||" + r.accession
                        sf = Seqfeature(bioentry=be, type_term=terms[key], source_term=terms["InterProScan"],
                                        display_name=key)
                        sf.save()
                        Location(seqfeature=sf, start_pos=r.start, end_pos=r.stop, strand=1).save()

                        if r.IPAcc and (r.IPAcc != "-"):
                            sf = Seqfeature(bioentry=be, type_term=terms[r.IPAcc], source_term=terms[key],
                                            display_name=key)
                            sf.save()
                            Location(seqfeature=sf, start_pos=r.start, end_pos=r.stop, strand=1).save()

                        if r.gos:
                            gos += r.gos.split("|")

                    for go in set(gos) - set(["-"]):
                        dbxrefdbqs = Dbxref.objects.filter(dbname=Ontology.GO, accession=go)
                        if dbxrefdbqs.exists():
                            BioentryDbxref.objects.get_or_create(dbxref=dbxrefdbqs.get(), bioentry=be)
                        else:
                            self.stderr.write(f'GO term {go} was not found in DB')
            except Exception as e:
                print(e)

        self.stderr.write("\nInterPro data imported!\n")
