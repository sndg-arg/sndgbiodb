import gzip
import io
import shutil
import warnings
import os
from Bio import BiopythonWarning, BiopythonParserWarning, BiopythonDeprecationWarning, BiopythonExperimentalWarning
from django.core.management.base import BaseCommand

from bioseq.io.GenebankIO import GenebankIO
from bioseq.io.SeqStore import SeqStore

warnings.simplefilter('ignore', RuntimeWarning)
warnings.simplefilter('ignore', BiopythonWarning)
warnings.simplefilter('ignore', BiopythonParserWarning)
warnings.simplefilter('ignore', BiopythonDeprecationWarning)
warnings.simplefilter('ignore', BiopythonExperimentalWarning)


class Command(BaseCommand):
    help = 'Downloads a genebank file from accession number'

    def add_arguments(self, parser):
        parser.add_argument('--email', default="something@adomain.com")
        parser.add_argument('accession')
        parser.add_argument('--stdout', action="store_true")
        parser.add_argument('--datadir', default="./data")

    def handle(self, *args, **options):
        h = GenebankIO.get_stream_from_accession(options["accession"], options["email"])
        if not os.path.exists(options['datadir'] + '/tmp'):
            os.makedirs(options['datadir'] + '/tmp')
        try:
            if options["stdout"]:
                self.stdout.write(h.read())
            else:
                tmp_file = options['datadir'] + '/tmp/' + options["accession"] + '.gz'
                with gzip.open(tmp_file, "wt") as hw:
                    shutil.copyfileobj(h, hw)
                gbio = GenebankIO(tmp_file)
                gbio.init()
                ss = SeqStore(options["datadir"])
                ss.create_idx_dir(gbio.accession)
                shutil.move(tmp_file, ss.gbk(gbio.accession))

        finally:
            h.close()

        self.stderr.write("genome imported!")
