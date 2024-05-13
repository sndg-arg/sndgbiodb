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
        i= 0
        for feature in record.features:
            i += 1
            
            print(feature)
            if i > 20:
                break
        # Extract the first 20 genes from the features of the SeqRecord
        record.features = record.features[:101]


        # Define the output file path
        output_file_path = os.path.join(options["datadir"], f"{accession}.gbk")

        # Write the new SeqRecord with only the first 20 genes to a new GBK file
        SeqIO.write(record, output_file_path, "genbank")

        print(f"First 20 genes saved to {output_file_path}")


        ## If asked, the content is printed as stdout and the file isn't saved
        #try:

        #    ss = SeqStore(options["datadir"])
        #    test_folder =  ss.test()
        #    print(test_folder)
        #    if os.path.exists(test_folder):
        #        shutil.rmtree(test_folder)

            #Creates the test directory
         #   os.makedirs(test_folder)
            
            # Creates the test_file
         #   test_file = accession + '.gz'
          #  with gzip.open(test_file, "wt") as hw:
           #     shutil.copyfileobj(h, hw)

           # shutil.move(test_file, test_folder)
            


        h.close()

        self.stderr.write("genome imported!")
