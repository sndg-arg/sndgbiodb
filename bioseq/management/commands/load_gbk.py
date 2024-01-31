import os
import shutil
import sys
import warnings
import subprocess as sp

from django.core.management.base import BaseCommand

from bioseq.io.BioIO import BioIO
from Bio import BiopythonWarning, BiopythonParserWarning, BiopythonDeprecationWarning, BiopythonExperimentalWarning

from bioseq.io.GenebankIO import GenebankIO
from bioseq.io.SeqStore import SeqStore
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
        parser.add_argument('--accession', default=None)
        parser.add_argument('--taxon', type=int, default=None)
        parser.add_argument('--overwrite', action='store_true')
        parser.add_argument('--datadir', default=os.environ.get("BIOSEQDATADIR","./data") )
        parser.add_argument('gbk')

    def handle(self, *args, **options):

        # initializes the gbio object 
        input_file = options['gbk']
        gbio = GenebankIO(input_file)
        assert gbio.check(), "'%s' does not exists" % input_file

        try:
            gbio.init(options["accession"])
        except:
            if not gbio.accession:
                self.stderr.write(f'no ACCESSION was found, use --accession parameter\n')
            else:
                raise
            sys.exit(1)

        # Esta parte parece estar chequeando que el path provisto sea correcto, preguntar.
        ss = SeqStore(options["datadir"])
        ss.create_idx_dir(gbio.accession)
        if ss.gbk(gbio.accession) != input_file:
            if input_file.endswith(".gz"):
                if os.path.abspath(input_file) != os.path.abspath(ss.gbk(gbio.accession)):
                    shutil.copy(input_file, ss.gbk(gbio.accession))
            else:
                sp.call(f'cat {input_file} | gzip > {ss.gbk(gbio.accession)}', shell=True)
        assert os.path.exists(ss.gbk(gbio.accession)),f'"{ss.gbk(gbio.accession)}" does not exists'

        # Tries to get the taxon from the file or from the arguments
        if not options['taxon']:
            if not gbio.taxon:
                self.stderr.write("taxon could not be obtained from input gbk, use --taxon option\n")
                sys.exit(2)
            else:
                taxon = gbio.taxon
        else:
            taxon = options['taxon']

        self.stderr.write(f'accession: {gbio.accession},taxon: {taxon},contigs: {gbio.total}\n')

        # Download the new taxon and initialized an BioIO object if the taxon is not in the db.
        tio = TaxIO()
        if not tio.id_exists_in_db(taxon):
            self.stderr.write(f"taxon {taxon} not in DB, downloading...\n")
            with transaction.atomic():
                tio.complete_tax(taxon)
            self.stderr.write(f"taxon {taxon} Download complete\n")

        io = BioIO(gbio.accession, taxon)

        # Check for base ontologies and overwrites the biodatabase if overwrite was provided
        if not Ontology.objects.filter(name=Ontology.SFS).exists():
            self.stderr.write(f'base ontologies not detecting, installing...')
            Ontology.load_ann_terms()
            Ontology.load_go_base()
            self.stderr.write(f'base ontologies installed!')
        if io.exists() and options['overwrite']:
            self.stderr.write(f'"{gbio.accession}" database already exists: removing...')
            io.delete_db()
        elif io.exists():
            self.stderr.write(f'"{gbio.accession}" database already exists... use --overwrite to delete the existing one')
            sys.exit(1)

        io.create_db()
        io.process_record_list(gbio.record_list(), gbio.total)

        self.stderr.write("genome imported!")
