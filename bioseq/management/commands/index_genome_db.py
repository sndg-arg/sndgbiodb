import warnings
from Bio import BiopythonWarning, BiopythonParserWarning, BiopythonDeprecationWarning, BiopythonExperimentalWarning
from django.core.management.base import BaseCommand
from tqdm import tqdm

from bioseq.io.BioIO import BioIO
from bioseq.io.IndexerIO import IndexerIO
from bioseq.models.Biodatabase import Biodatabase
from bioseq.models.BiodatabaseQualifierValue import BiodatabaseQualifierValue
from bioseq.models.BioentryQualifierValue import BioentryQualifierValue

warnings.simplefilter('ignore', RuntimeWarning)
warnings.simplefilter('ignore', BiopythonWarning)
warnings.simplefilter('ignore', BiopythonParserWarning)
warnings.simplefilter('ignore', BiopythonDeprecationWarning)
warnings.simplefilter('ignore', BiopythonExperimentalWarning)


class Command(BaseCommand):
    help = 'Index genome'

    def add_arguments(self, parser):
        parser.add_argument('accession')

    def handle(self, *args, **options):
        accession = options['accession']

        biodb = Biodatabase.objects.get(name=accession)
        bioprotdb = Biodatabase.objects.get(name=accession + BioIO.GENOME_PROT_POSTFIX)

        BiodatabaseQualifierValue.objects.filter(biodatabase=biodb).delete()
        BioentryQualifierValue.objects.filter(bioentry__biodatabase=biodb).delete()
        BioentryQualifierValue.objects.filter(bioentry__biodatabase=bioprotdb).delete()
        # Term.objects.filter(ontology__name=Ontology.BIOINDEX).delete()

        indexer = IndexerIO()
        indexer.init()

        indexer.index_entries(biodb)

        with tqdm(bioprotdb.entries.all()) as pbar:
            for i, p in enumerate(pbar):
                pbar.set_description(p.name)
                indexer.index_protein(p)
        self.stderr.write("genome indexed!")
