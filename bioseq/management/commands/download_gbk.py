import gzip
import io
import shutil
import warnings
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

        try:
            if options["stdout"]:
                self.stdout.write(h.read())
            else:
                ss = SeqStore(options["datadir"])
                ss.create_idx_dir(options["accession"])
                with gzip.open(ss.gbk(options["accession"]), "wt") as hw:
                    shutil.copyfileobj(h, hw)
        finally:
            h.close()

        self.stderr.write("genome imported!")
