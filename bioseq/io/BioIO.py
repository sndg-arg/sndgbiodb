import os
from tqdm import tqdm
from datetime import datetime
from typing import Iterable, Callable
import sys

from django.db import transaction

from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio.SeqFeature import SeqFeature as BSeqFeature

from bioseq.models.Taxon import Taxon
from bioseq.models.TaxonName import TaxonName
from bioseq.models.Ontology import Ontology
from bioseq.models.Term import Term
from bioseq.models.TermRelationship import TermRelationship
from bioseq.models.Biodatabase import Biodatabase
from bioseq.models.Bioentry import Bioentry
from bioseq.models.BioentryQualifierValue import BioentryQualifierValue
from bioseq.models.BioentryDbxref import BioentryDbxref
from bioseq.models.Biosequence import Biosequence
from bioseq.models.Seqfeature import Seqfeature
from bioseq.models.SeqfeatureDbxref import SeqfeatureDbxref
from bioseq.models.SeqfeatureQualifierValue import SeqfeatureQualifierValue
from bioseq.models.Location import Location
from bioseq.models.Dbxref import Dbxref, DbxrefQualifierValue


def bulk_save(iterator: Iterable, action: Callable[[BSeqFeature], Seqfeature], bulk_size: int = 1000,
              stderr=sys.stderr):
    data = []
    for obj in tqdm(iterator, file=stderr):
        data.append(obj)
        if (len(data) % bulk_size) == 0:
            with transaction.atomic():
                for x in data:
                    action(x)
            data = []
    if data:
        with transaction.atomic():
            for x in data:
                action(x)


class BioIO:
    included_feature_qualifiers = [SeqfeatureQualifierValue.GeneValue, SeqfeatureQualifierValue.LocusTagValue,
                                   SeqfeatureQualifierValue.DBXREFValue]
    excluded_feature_qualifiers = [SeqfeatureQualifierValue.TranslationValue,
                                   #SeqfeatureQualifierValue.GeneValue,
                                   #SeqfeatureQualifierValue.LocusTagValue,
                                   "EC_number","GO_function","GO_process","GO_component",

                                   SeqfeatureQualifierValue.DBXREFValue,
                                   SeqfeatureQualifierValue.ProductValue]

    GENOME_PROT_POSTFIX = "_prots"
    GENOME_RNAS_POSTFIX = "_rnas"

    def __init__(self, biodb_name: str, ncbi_tax: int):
        self.biodb_name = biodb_name
        self.ncbi_tax = ncbi_tax
        self.stderr = sys.stderr

    def delete_db(self):
        Biodatabase.objects.filter(name=self.biodb_name).delete()
        Biodatabase.objects.filter(name=self.biodb_name + BioIO.GENOME_PROT_POSTFIX).delete()
        Biodatabase.objects.filter(name=self.biodb_name + BioIO.GENOME_RNAS_POSTFIX).delete()

    def exists(self):
        return Biodatabase.objects.filter(name=self.biodb_name).exists()

    def create_db(self):
        self.genomedb = Biodatabase(name=self.biodb_name)
        self.genomedb.save()
        self.proteindb = Biodatabase(name=self.biodb_name + BioIO.GENOME_PROT_POSTFIX)
        self.proteindb.save()
        self.rnadb = Biodatabase(name=self.biodb_name + BioIO.GENOME_RNAS_POSTFIX)
        self.rnadb.save()

        self.sfk_ontology = Ontology.objects.get(name=Ontology.SFK)
        self.sfs_ontology = Ontology.objects.get(name=Ontology.SFS)
        self.ann_ontology = Ontology.objects.get(name=Ontology.ANNTAGS)
        self.feature_term = (
            Term.objects.get_or_create(ontology=self.ann_ontology, identifier=Seqfeature.GFeatureIdTerm)[0])
        self.bioentry_term = Term.objects.get_or_create(ontology=self.ann_ontology, identifier=Bioentry.BioentryIdTerm)[
            0]

    def process_feature(self, be: Bioentry, feature: BSeqFeature):
        type_term = Term.objects.get_or_create(ontology=self.sfk_ontology, identifier=feature.type)[0]
        source_term = Term.objects.get_or_create(ontology=self.sfk_ontology, identifier="calculated")[0]

        display_name = (feature.qualifiersq[SeqfeatureQualifierValue.GeneValue][
                            0] if SeqfeatureQualifierValue.GeneValue in feature.qualifiers else (
            feature.qualifiers[SeqfeatureQualifierValue.LocusTagValue][
                0] if SeqfeatureQualifierValue.LocusTagValue in feature.qualifiers else feature.type))
        sf = Seqfeature(bioentry=be, type_term=type_term, source_term=source_term, display_name=display_name)
        sf.save()

        for key, value in feature.qualifiers.items():
            value = value[0]
            if not (feature.type == Seqfeature.CDS_ENTRY_TYPE or "RNA" in feature.type) or (
                    key in BioIO.included_feature_qualifiers):
                term = Term.objects.get_or_create(identifier=key, ontology=self.ann_ontology)[0]
                sfqv = SeqfeatureQualifierValue.objects.create(seqfeature=sf, term=term, value=value)
                sfqv.save()
        # sub_features

        for rank, location in enumerate(feature.location.parts):
            loc = Location(seqfeature=sf, start_pos=location.start, end_pos=location.end,
                           strand=location.strand, rank=rank)
            loc.save()

        if SeqfeatureQualifierValue.PSEUDOValue in feature.qualifiers:
            return

        if feature.type == Seqfeature.CDS_ENTRY_TYPE or "RNA" in feature.type:
            self.bioentry_from_feature(be, feature, sf)

    def bioentry_from_feature(self, be, feature, sf):
        description = (
            feature.qualifiers[SeqfeatureQualifierValue.ProductValue][0] if SeqfeatureQualifierValue.ProductValue else (
                feature.qualifiers[SeqfeatureQualifierValue.NoteValue][
                    0] if SeqfeatureQualifierValue.NoteValue in feature.qualifiers else ""))
        gene = feature.qualifiers[SeqfeatureQualifierValue.GeneValue][
            0] if SeqfeatureQualifierValue.GeneValue in feature.qualifiers else feature.qualifiers["locus_tag"][0]
        locus_tag = feature.qualifiers[SeqfeatureQualifierValue.LocusTagValue][
            0] if SeqfeatureQualifierValue.LocusTagValue in feature.qualifiers else gene
        if Seqfeature.CDS_ENTRY_TYPE == feature.type:
            seq = feature.qualifiers["translation"][0]
            db = self.proteindb
        else:
            db = self.rnadb
            seq = str(feature.extract(Seq(be.seq.seq)))
        be_count = Bioentry.objects.filter(biodatabase=db, accession=locus_tag).count()
        if be_count:
            be_count = Bioentry.objects.filter(biodatabase=db, accession__startswith=locus_tag + "_").count() + 1
            locus_tag = locus_tag + "_" + str(be_count)
        prot = Bioentry.objects.create(biodatabase=db,
                                       description=description, name=gene,
                                       accession=locus_tag)
        BioentryQualifierValue.objects.create(bioentry=prot, term=self.feature_term, value=sf.seqfeature_id)
        SeqfeatureQualifierValue.objects.create(seqfeature=sf, term=self.bioentry_term, value=prot.bioentry_id)
        Biosequence.objects.create(bioentry=prot, seq=seq, length=len(seq))
        # unip = Dbxref.objects.create(dbname="Uniprot", accession="P9WHW3")
        # BioentryDbxref.objects.create(bioentry=prot, dbxref=unip)
        #print(feature.qualifiers)
        for key, value in feature.qualifiers.items():
            value = value[0]
            if key not in BioIO.excluded_feature_qualifiers:
                term = Term.objects.get_or_create(identifier=key, ontology=self.ann_ontology)[0]
                BioentryQualifierValue.objects.create(bioentry=prot, term=term,
                                                      value=value)
        if "EC_number" in feature.qualifiers:
            for term in feature.qualifiers["EC_number"]:
                term = "EC:" + term
                qs = Dbxref.objects.filter(dbname=Ontology.EC,accession=term)
                if qs.exists():
                    dbxref = qs.get()
                    BioentryDbxref.objects.get_or_create(bioentry=be,dbxref=dbxref)
                else:
                    self.stderr.write(f"EC term {term} not found\n")

        for k,v in {k:v for k,v in feature.qualifiers.items()
                    if k in ["GO_function","GO_process","GO_component"]}.items():
            if isinstance(v,str):
                gos = [v]
            else:
                gos = v
            for go in gos:
                #GO_function="GO:0004853 - uroporphyrinogen decarboxylase
                term = go.split()[0].upper()
                qs = Dbxref.objects.filter(dbname=Ontology.GO,accession=term)
                if qs.exists():
                    dbxref = qs.get()
                    BioentryDbxref.objects.get_or_create(bioentry=be,dbxref=dbxref)
                else:
                    self.stderr.write(f"go term {v} not found\n")


    def process_seqrecord(self, seqrecord):
        be = Bioentry(biodatabase=self.genomedb,
                      name=seqrecord.name, accession=seqrecord.id,
                      identifier=seqrecord.id)
        if self.ncbi_tax:
            be.taxon = Taxon.objects.get(ncbi_taxon_id=self.ncbi_tax)
        be.save()

        seq = Biosequence(bioentry=be, seq="", length=len(seqrecord.seq))
        seq.save()

        bulk_save(seqrecord.features, action=lambda f: self.process_feature(be, f), stderr=self.stderr)

    def process_record_list(self, seq_record_iterator: Iterable[SeqRecord], contig_count: int):
        first = True
        with tqdm(seq_record_iterator, total=contig_count, file=self.stderr) as pbar:
            for seqrecord in pbar:
                if first:
                    first = False
                    self.genomedb.description = seqrecord.description
                    self.genomedb.save()

                pbar.set_description(seqrecord.id)
                self.process_seqrecord(seqrecord)

