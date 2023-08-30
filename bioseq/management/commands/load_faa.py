import sys
import warnings



from django.core.management.base import BaseCommand

from bioseq.io.BioIO import BioIO
from Bio import BiopythonWarning, BiopythonParserWarning, BiopythonDeprecationWarning, BiopythonExperimentalWarning

from bioseq.io.GenebankIO import GenebankIO
from bioseq.io.TaxIO import TaxIO
from bioseq.models.Ontology import Ontology

warnings.simplefilter('ignore', RuntimeWarning)
warnings.simplefilter('ignore', BiopythonWarning)
warnings.simplefilter('ignore', BiopythonParserWarning)
warnings.simplefilter('ignore', BiopythonDeprecationWarning)
warnings.simplefilter('ignore', BiopythonExperimentalWarning)

from django.db import transaction


class Command(BaseCommand):
    help = 'Loads a genome in the database'

    def add_arguments(self, parser):
        parser.add_argument('accession', default=None)
        parser.add_argument('taxon', type=int, default=None)
        parser.add_argument('gbk')
        parser.add_argument('--overwrite', action='store_true')


    def handle(self, *args, **options):
        input_file = options['gbk']
        gbio = GenebankIO(input_file)
        assert gbio.check(), "'%s' does not exists" % input_file

        gbio.init()

        if not options['accession']:
            accession = gbio.accession
        else:
            accession = options['accession']

        if not options['taxon']:
            if not gbio.taxon:
                self.stderr.write("taxon could not be obtained from input gbk\n")
            else:
                taxon = gbio.taxon
        else:
            taxon = options['taxon']

        self.stderr.write(f'accession: {accession},taxon: {taxon},contigs: {gbio.total}\n')

        tio = TaxIO()
        if not tio.id_exists_in_db(taxon):
            self.stderr.write(f"taxon {taxon} not in DB, downloading...\n")
            with transaction.atomic():
                tio.complete_tax(taxon)
            self.stderr.write(f"taxon {taxon} Download complete\n")

        io = BioIO(accession, taxon)

        if not Ontology.objects.filter(name=Ontology.SFS).exists():
            self.stderr.write(f'base ontologies not detecting, installing...')
            Ontology.load_ann_terms()
            Ontology.load_go_base()
            self.stderr.write(f'base ontologies installed!')
        if io.exists() and options['overwrite']:
            self.stderr.write(f'"{accession}" database already exists: removing...')
            io.delete_db()
        elif io.exists():
            self.stderr.write(f'"{accession}" database already exists... use --overwrite to delete the existing one')
            sys.exit(1)

        io.create_db()
        io.process_record_list(gbio.record_list(), gbio.total)

        self.stderr.write("genome imported!")
