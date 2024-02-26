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
from bioseq.models.Ontology import Ontology
from bioseq.models.SeqfeatureQualifierValue import SeqfeatureQualifierValue
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
    help = 'gets uniprot'

    def add_arguments(self, parser):
        parser.add_argument('accession')
        parser.add_argument('--batch_size', type=int, default=1000)
        parser.add_argument('--polling_interval', type=int, default=5)
        parser.add_argument('--mapping_tmp', type=str)
        parser.add_argument('--not_mapped', type=str, default="not_mapped.lst")
        parser.add_argument('--datadir', default="./data")

    def handle(self, *args, **options):
        accession = options['accession'] + BioIO.GENOME_PROT_POSTFIX
        batch_size = options['batch_size']
        polling_interval = options['polling_interval']

        assert Biodatabase.objects.filter(name=accession).exists(), "'%s' does not exists" % accession
        ss = SeqStore(options["datadir"])
        protein_ids_qs = BioentryQualifierValue.objects.filter(
            bioentry__biodatabase__name=accession,
            term__identifier="protein_id").values_list("bioentry__bioentry_id", "value")
        
        # Extraction of the protein_id and locus_tag from db
        protein_ids_loc = BioentryQualifierValue.objects.filter(
            bioentry__biodatabase__name=accession,
            term__identifier="protein_id").values_list("bioentry__accession", "value") 

        fd, path = tempfile.mkstemp()
        temperr = open(fd, "w")

        if not options["mapping_tmp"]:
            options["mapping_tmp"] = ss.db_dir(options["accession"]) + "/unips_mapping.csv"



        prot_id_bioentry = {}
        prot_id_loc_tag = {}

        # Creation of the dict
        for a, b in protein_ids_loc:
            prot_id_loc_tag[b]=a

        if not os.path.exists(options["mapping_tmp"]):
            txttable = ""
            with tqdm(range(0, len(protein_ids_qs), batch_size)) as pbar:
                for i in pbar:
                    batch = protein_ids_qs[i:i + batch_size]
                    for bioentry_id, protein_id in batch:
                        prot_id_bioentry[protein_id] = bioentry_id


                    ids = ",".join(prot_id_bioentry.keys())
                    cmd = f'''curl --request POST 'https://rest.uniprot.org/idmapping/run' --form 'ids="{ids}"' --form 'from="RefSeq_Protein"' --form 'to="UniProtKB"' '''
                    jobid = json.loads(sp.check_output(cmd, shell=True, stderr=temperr).decode("utf-8"))["jobId"]

                    finished = False

                    while not finished:
                        cmd = f'''curl 'https://rest.uniprot.org/idmapping/status/{jobid}' '''
                        jobstatus_raw = sp.check_output(cmd, shell=True, stderr=temperr).decode("utf-8")
                        jobstatus_dict = json.loads(jobstatus_raw)

                        jobstatus = jobstatus_dict["jobStatus"]
                        if jobstatus == "RUNNING":
                            pbar.set_description(f"Retrying in {polling_interval}s")
                            time.sleep(polling_interval)
                        elif jobstatus == "ERROR":
                            self.stderr.write(f"job has finished with errors {jobstatus}")
                            self.stderr.write(jobstatus_dict)
                            sys.exit(2)
                        elif jobstatus == "FINISHED":
                            cmd = f'curl "https://rest.uniprot.org/idmapping/uniprotkb/results/stream/{jobid}?format=tsv&compressed=true"  | gunzip'
                            jobresult_raw = sp.check_output(cmd, shell=True, stderr=temperr).decode("utf-8")
                            finished = True

                        else:
                            self.stderr.write(f"unknown status {jobstatus}")
                            sys.exit(1)

                    txttable += "\n".join(jobresult_raw.split("\n")[1:])

            csvStringIO = StringIO(txttable)
            df = pd.read_csv(csvStringIO, sep="\t",
                             names="From\tEntry\tEntry Name\tReviewed\tProtein names\tGene Names\tOrganism\tLength".split(
                                 "\t"))
            
            # Transform dict to df and merge of the locus_tag based on 'From' (protein_id)
            merge_df = pd.DataFrame(list(prot_id_loc_tag.items()), columns=['From', 'LocusTag'])
            merged_df = pd.merge(df, merge_df, on='From')

            with open(options["mapping_tmp"], "w") as h:
                merged_df.to_csv(h, index=False)
            self.stderr.write("------------------------\n")
        else:

            df = pd.read_csv(options.get("mapping_tmp",options["mapping_tmp"] ))
            for bioentry_id, protein_id in protein_ids_qs:
                prot_id_bioentry[protein_id] = bioentry_id

        with transaction.atomic():
            qs = BioentryDbxref.objects.filter(bioentry__biodatabase__name=accession,
                                               dbxref__dbname__in=["UnipSp", "UnipTr", "UnipGene"])
            qs.delete()
            BioentryQualifierValue.objects.filter(bioentry__biodatabase__name=accession,
                                                  term__identifier="UnipProtName").delete()
        unip_list = []
        for protein_id, df_prot in tqdm(df.fillna("").groupby("From")): 
            df_prot = df_prot.sort_values("Reviewed")
            unip_list.append(df_prot.iloc[0]["Entry"] + " " + df_prot.iloc[0]["LocusTag"])
            bioentry_id = prot_id_bioentry[protein_id]
            with transaction.atomic():

                # be = Bioentry.objects.filter(bioentry_id=prot_id_bioentry[protein_id]).get()
                genes = []
                unips = []
                for idx, r in df_prot.iterrows():
                    db = "UnipSp" if r["Reviewed"] == "reviewed" else "UnipTr"
                    unips.append([db, r["Entry"]])
                    if r["Gene Names"].split():
                        genes += r["Gene Names"].split()
                    unip_protein_name = Term.objects.get_or_create(identifier="UnipProtName",
                                                                   ontology=Ontology.objects.get_or_create(
                                                                       name=Ontology.ANNTAGS)[0])[0]
                    qualunipname = BioentryQualifierValue(term=unip_protein_name, bioentry_id=bioentry_id,
                                                          value=r["Protein names"], rank=idx)

                    qualunipname.save()
                unip_dict = {}
                for db, unip in unips:
                    if unip not in unip_dict:
                        dbxrefdb = Dbxref.objects.get_or_create(dbname=db, accession=unip)[0]
                        dbx = BioentryDbxref(dbxref=dbxrefdb, bioentry_id=bioentry_id)
                        dbx.save()
                        unip_dict[unip] = 1

                for genename in set(genes):
                    dbxrefdb = Dbxref.objects.get_or_create(
                        dbname=Dbxref.UnipGene, accession=genename)[0]
                    dbx = BioentryDbxref(dbxref=dbxrefdb, bioentry_id=bioentry_id)
                    dbx.save()

        temperr.close()

        self.stdout.write("\n".join(unip_list) + "\n")

        not_mapped = set(prot_id_bioentry) - set(df["From"])
        if not_mapped:
            if not options["not_mapped"]:
                options["not_mapped"] = ss.db_dir(options["accession"]) + "/unips_not_mapped.csv"
            self.stderr.write(f'({len(not_mapped)}) ids were not found: {options["not_mapped"]}\n')
            with open(options["not_mapped"], "w") as h:
                h.write("\n".join(not_mapped))
        self.stderr.write("\nuniprot data imported!\n")
