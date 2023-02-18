import os
import sys
import warnings
from tqdm import tqdm
import subprocess as sp
import gzip

import Bio.SeqIO as bpio

from django.core.management.base import BaseCommand

from bioseq.io.BioIO import BioIO
from Bio import BiopythonWarning, BiopythonParserWarning, BiopythonDeprecationWarning, BiopythonExperimentalWarning

from bioseq.models.Ontology import Ontology

warnings.simplefilter('ignore', RuntimeWarning)
warnings.simplefilter('ignore', BiopythonWarning)
warnings.simplefilter('ignore', BiopythonParserWarning)
warnings.simplefilter('ignore', BiopythonDeprecationWarning)
warnings.simplefilter('ignore', BiopythonExperimentalWarning)


class Command(BaseCommand):
    help = 'Loads a genome in the database'

    def add_arguments(self, parser):
        parser.add_argument('--accession',  required=True)
        parser.add_argument('--taxon',  required=False)
        parser.add_argument('--overwrite',  action='store_true' )
        parser.add_argument('gbk')

        #parser.add_argument('--taxon', '-t', type=int, required=True)

    def handle(self, *args, **options):
        input_file = options['gbk']
        accession = options['accession']
        taxon = options['taxon']
        assert os.path.exists(input_file), "'%s' does not exists" % input_file
        io = BioIO(accession, taxon)

        grep_cmd = 'grep -c "FEATURES *Location/Qualifiers" "%s"' % input_file
        if input_file.endswith(".gz"):
            grep_cmd = 'z' + grep_cmd
            input_file = gzip.open(input_file, "rt")
        total = int(sp.check_output(grep_cmd, shell=True))

        if not Ontology.objects.filter(name=Ontology.SFS).exists():
            Ontology.load_ann_terms()
            Ontology.load_go_base()
        if io.exists() and options['overwrite']:
            self.stderr.write(f'"{accession}" database already exists: removing...')
            io.delete_db()
        elif io.exists():
            self.stderr.write(f'"{accession}" database already exists... use --overwrite to delete the existing one')
            sys.exit(1)

        io.create_db()
        io.process_record_list(bpio.parse(input_file, "gb"), total)

        self.stderr.write("genome imported!")
