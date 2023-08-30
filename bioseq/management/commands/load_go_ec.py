import sys
import warnings
import subprocess as sp
from tqdm import tqdm
from django.core.management.base import BaseCommand
import os

from bioseq.io.BioIO import BioIO
from Bio import BiopythonWarning, BiopythonParserWarning, BiopythonDeprecationWarning, BiopythonExperimentalWarning

from bioseq.io.GenebankIO import GenebankIO
from bioseq.io.OntologyIO import OntologyIO
from bioseq.io.TaxIO import TaxIO
from bioseq.models.Dbxref import Dbxref
from bioseq.models.Ontology import Ontology
from bioseq.models.Term import Term
from bioseq.models.TermDbxref import TermDbxref

warnings.simplefilter('ignore', RuntimeWarning)
warnings.simplefilter('ignore', BiopythonWarning)
warnings.simplefilter('ignore', BiopythonParserWarning)
warnings.simplefilter('ignore', BiopythonDeprecationWarning)
warnings.simplefilter('ignore', BiopythonExperimentalWarning)

from django.db import transaction


class Command(BaseCommand):
    help = 'Loads a genome in the database'

    def add_arguments(self, parser):

        parser.add_argument('--go', type=str, default=None)
        parser.add_argument('--ec_enzyme', type=str, default=None)
        parser.add_argument('--ec_enzclass', type=str, default=None)
        parser.add_argument('--datadir', type=str, default="./data")

    def handle(self, *args, **options):
        obo_go = options['go']
        datadir = options['datadir']
        ec_enzyme = options['ec_enzyme']
        ec_enzclass = options['ec_enzclass']
        oio = OntologyIO()

        if not obo_go:
            obo_go = f'{datadir}/go.obo'
            if not os.path.exists(obo_go):
                sp.call(f'curl "http://current.geneontology.org/ontology/go.obo" > {obo_go}', shell=True)

        if not ec_enzyme:
            ec_enzyme = f'{datadir}/enzyme.dat'
            ec_enzclass = f'{datadir}/enzclass.txt'
            if not os.path.exists(ec_enzyme):
                sp.call(f'curl "https://ftp.expasy.org/databases/enzyme/enzyme.dat" > {ec_enzyme}', shell=True)
            if not os.path.exists(ec_enzclass):
                sp.call(f'curl "https://ftp.expasy.org/databases/enzyme/enzclass.txt" > {ec_enzclass}', shell=True)

        obodag = oio.obo_ontology(obo_go)
        Ontology.load_go_base()

        ontology = Ontology.objects.get_or_create(name=Ontology.GO)[0]

        TermDbxref.objects.filter(dbxref__dbname=Ontology.GO).delete()
        Dbxref.objects.filter(dbname=Ontology.GO).delete()
        Term.objects.filter(ontology=ontology).delete()

        def partition_array(array, n):
            return [array[i:i + n] for i in range(0, len(array), n)]

        batchs = partition_array(list(obodag), 1000)
        with tqdm(obodag, total=len(obodag)) as pbar:
            for batch in batchs:
                with transaction.atomic():
                    for termid in batch:
                        pbar.update(1)
                        term = obodag[termid]

                        termobj = Term.objects.get_or_create(name=term.name, identifier=termid,
                                                   definition=term.defn, is_obsolete="Y" if term.is_obsolete else "N",
                                                   ontology=ontology)[0]
                        dbxref = Dbxref.objects.get_or_create(dbname=Ontology.GO, accession=termid)[0]
                        TermDbxref(term=termobj,dbxref=dbxref).save()
                        for x in term.alt_ids:
                            termobj = Term.objects.get_or_create(name=term.name, identifier=x, definition=term.defn,
                                                       is_obsolete="Y" if term.is_obsolete else "N",
                                                       ontology=ontology)[0]
                            dbxref = Dbxref.objects.get_or_create(dbname=Ontology.GO, accession=termid)[0]
                            TermDbxref.objects.get_or_create(term=termobj,dbxref=dbxref)

        ontology = Ontology.objects.get_or_create(name=Ontology.EC)[0]
        TermDbxref.objects.filter(dbxref__dbname=Ontology.EC).delete()
        Dbxref.objects.filter(dbname=Ontology.EC).delete()
        Term.objects.filter(ontology=ontology).delete()
        terms_dict = oio.ec_ontology(ec_enzyme, ec_enzclass)
        for k, v in tqdm(terms_dict.items()):
            k = k.upper()
            term = Term.objects.get_or_create(name=v, identifier=k,
                                       is_obsolete="N",
                                       ontology=ontology)[0]
            dbxref = Dbxref.objects.get_or_create(dbname=Ontology.EC, accession=k)[0]
            TermDbxref.objects.get_or_create(term=term,dbxref=dbxref)

        self.stderr.write("go and ec terms imported!")
