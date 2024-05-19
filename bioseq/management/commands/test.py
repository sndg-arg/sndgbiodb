import gzip
import io
import shutil
import warnings
import os
from Bio import BiopythonWarning, BiopythonParserWarning, BiopythonDeprecationWarning, BiopythonExperimentalWarning, SeqIO
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
        parser.add_argument('--stdout', action="store_true")
        parser.add_argument('--datadir', default="./data")

    def handle(self, *args, **options):
        accession = 'NZ_AP023069.1'

        # Download the required GBK from the provided accesion code.
        h = GenebankIO.get_stream_from_accession(accession, options["email"])

        # Parse the GBK file into a SeqRecord object
        record = next(SeqIO.parse(h, "genbank"))

        # Extract the first 20 genes from the features of the SeqRecord
        record.features = record.features[:151]

        ss = SeqStore(options["datadir"])
        ss.create_idx_dir(accession)
        test_folder = ss.db_dir(accession)
        print(test_folder)

        # Define the output file path
        output_file_path = os.path.join(test_folder, f"{accession}.gbk")

        # Write the new SeqRecord with only the first 100 genes to a new GBK file
        SeqIO.write(record, output_file_path, "genbank")

        print(f"First 100 genes saved to {output_file_path}")
        # Gzip the file
        with open(output_file_path, 'rb') as f_in, gzip.open(output_file_path + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        h.close()

        self.stderr.write("genome imported!")
