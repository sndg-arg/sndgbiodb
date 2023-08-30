# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import defaultdict
from django.db.models import Count

from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

from django.utils.translation import gettext_lazy as __
from django.db import models
from django.shortcuts import reverse

from .Dbxref import Dbxref
from .SeqfeatureQualifierValue import SeqfeatureQualifierValue
from ..managers.BioentryManager import BioentryManager
from ..models.Biodatabase import Biodatabase


class Bioentry(models.Model):
    BioentryIdTerm = "BioentryId"

    bioentry_id = models.AutoField(primary_key=True)
    biodatabase = models.ForeignKey(Biodatabase, models.CASCADE, "entries")
    taxon = models.ForeignKey('Taxon', models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=40)
    accession = models.CharField(max_length=128,unique=True)
    identifier = models.CharField(max_length=40, blank=True, null=True)
    division = models.CharField(max_length=6, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    version = models.PositiveSmallIntegerField(default=1, null=True)

    index_updated = models.BooleanField(default=False)

    objects = BioentryManager()

    def __str__(self):
        return self.identifier + " " + self.biodatabase.name

    class Meta:
        managed = True
        db_table = 'bioentry'
        unique_together = (('accession', 'biodatabase', 'version'), ('identifier', 'biodatabase'),)

    def get_absolute_url(self):
        return reverse(
            'bioresources:' + (
                'protein_view' if self.biodatabase.name.endswith(Biodatabase.PROT_POSTFIX) else "nucleotide_view"),
            args=[str(self.bioentry_id)])  # TODO: parametrizar la app del link

    def groupedFeatures(self):
        group = defaultdict(lambda: [])
        for f in self.features.all():
            group[f.type_term.identifier].append(f.locations.first())

        return dict(group)

    def feature_counts(self):
        return {x["type_term__identifier"]: x["total"] for x in
                self.features.values('type_term__identifier').annotate(total=Count("type_term")) if
                x["type_term__identifier"] != "source"}

        # data = defaultdict(lambda: 0)
        # for f in self.features.all():
        #     data[f.type_term.name] += 1
        # return dict(data)

    def genes(self):
        # from ..models.Seqfeature import Seqfeature
        # beg = Biodatabase.objects.get(name=self.biodatabase.name.replace("_prots", ""))
        # feature = Seqfeature.objects.seqfeature_from_locus_tag(beg.biodatabase_id, self.accession)
        # feature = list(feature)[0]
        return list(set([x.value for x in
                         self.qualifiers.all() if x.term.identifier in
                         [SeqfeatureQualifierValue.GeneSymbolValue,
                          SeqfeatureQualifierValue.OldLocusTagValue,
                          SeqfeatureQualifierValue.ProteinIDValue,
                          SeqfeatureQualifierValue.AliasValue,
                          SeqfeatureQualifierValue.GeneValue
                          ]] +
                        [x.dbxref.accession for x in self.dbxrefs.all() if x.dbxref.dbname in [Dbxref.UnipGene]]))

    def product_description(self):
        qs = self.qualifiers.filter(term__name="product")
        return qs.value if qs.exists() else None

    def molecular_weight(self):
        qs = self.qualifiers.filter(term__name="molecular_weight")
        return qs.value if qs.exists() else None

    def go_terms(self, database):
        return self.qualifiers.filter(term__dbxrefs__dbxref__dbname="go",
                                      term__dbxrefs__dbxref__accession=database)
        # term__dbxrefs__dbxref__accession="goslim_generic",

    def biological_process(self):
        return self.go_terms("biological_process")

    def idx_biological_process(self):
        return [x.term.identifier for x in self.biological_process()]

    def txt_biological_process(self):
        return [x.term.keywords.text for x in self.biological_process()]

    def molecular_function(self):
        return self.go_terms("molecular_function")

    def cellular_component(self):
        return self.go_terms("cellular_component")

    def ftype(self):
        return 40  # "protein"

    def qualifiers_dict(self):
        return {qual.term.identifier: qual.value for qual in self.qualifiers.all()}

    def __str__(self):
        return "BioEntry('%s')" % self.accession

    def __repr__(self):
        return str(self)

    def to_seq_record(self, addDesc=True):
        desc = self.description if addDesc else ""
        r = SeqRecord(id=self.accession, name=desc, seq=Seq(self.seq.seq))
        return r

# class BioentryReference(models.Model):
#     bioentry_relationship_id = models.AutoField(primary_key=True)
#     bioentry = models.ForeignKey(Bioentry, models.CASCADE)
#     reference = models.ForeignKey('Reference', models.DO_NOTHING)
#     start_pos = models.IntegerField(blank=True, null=True)
#     end_pos = models.IntegerField(blank=True, null=True)
#     rank = models.SmallIntegerField(default=1, null=True)
#
#     class Meta:
#         managed = True
#         db_table = 'bioentry_reference'
#         unique_together = (('bioentry', 'reference', 'rank'),)
