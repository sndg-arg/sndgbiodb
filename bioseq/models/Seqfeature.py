# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import gettext_lazy as __
from django.db import models
from django.shortcuts import reverse


from ..models.Bioentry import Bioentry
from ..models.Dbxref import Dbxref

from ..managers.SeqfeatureManager import SeqfeatureManager

from .SeqfeatureQualifierValue import SeqfeatureQualifierValue

class Seqfeature(models.Model):
    GFeatureIdTerm = "GFeatureId"

    BioentryCountTermPrefix = "COUNT_"
    CDS_ENTRY_TYPE = "CDS"
    RRNA_ENTRY_TYPE = "rRNA"
    TRNA_ENTRY_TYPE = "tRNA"
    REGULATORY_ENTRY_TYPE = "regulatory"
    NCRNA_ENTRY_TYPE = "ncRNA"
    MRNA_ENTRY_TYPE = "mRNA"
    REPEAT_ENTRY_TYPE = "repeat"

    ENTRY_TYPES = [CDS_ENTRY_TYPE, RRNA_ENTRY_TYPE, TRNA_ENTRY_TYPE, REGULATORY_ENTRY_TYPE,
                   NCRNA_ENTRY_TYPE, MRNA_ENTRY_TYPE, REPEAT_ENTRY_TYPE]

    seqfeature_id = models.AutoField(primary_key=True)
    bioentry = models.ForeignKey('Bioentry', models.CASCADE, related_name="features")
    type_term = models.ForeignKey('Term', models.DO_NOTHING, related_name="features_of_type")
    source_term = models.ForeignKey('Term', models.DO_NOTHING, related_name="source_of")
    display_name = models.CharField(max_length=64, blank=True, null=True)
    rank = models.PositiveSmallIntegerField(default=1, null=True)

    index_updated = models.BooleanField(default=False)

    def qualifiers_dict(self):
        return {x.term.identifier: x.value for x in self.qualifiers.all()}

    objects = SeqfeatureManager()

    def __str__(self):
        ls = list(self.locations.all())
        """return "%s:%i-%i %s" % (self.bioentry.name, ls[0].start_pos, ls[-1].end_pos,
                       
                                "|".join([k + ":" + v for k, v in self.qualifiers_dict().items()]))
                                """
        return f'SeqF {self.display_name} {self.bioentry.name}:{ ls[0].start_pos}-{ls[-1].end_pos,}'

    class Meta:
        managed = True
        db_table = 'seqfeature'
        # unique_together = (('bioentry', 'type_term', 'source_term', 'rank'),)

    def strand(self):
        return "+" if self.locations.all()[0].strand > 0 else "-"

    def locus_tag(self):
        return self.qualifiers.get(term__name=SeqfeatureQualifierValue.LocusTagValue).value

    def genes(self):
        return [x.value for x in
                self.qualifiers.filter(term_name__in=[
                    SeqfeatureQualifierValue.GeneSymbolValue,
                    SeqfeatureQualifierValue.OldLocusTagValue,
                    SeqfeatureQualifierValue.ProteinIDValue,
                    SeqfeatureQualifierValue.AliasValue,
                    SeqfeatureQualifierValue.GeneValue])]

    def description(self):
        qs = self.qualifiers.filter(term__name=SeqfeatureQualifierValue.ProductValue)
        if qs.exists():
            return qs.get().value
        return self.type_term.name

    def length(self):
        return sum([abs(x.end_pos - x.start_pos) for x in self.locations])

    def subfeatures(self):
        return [x.object_seqfeature for x in self.object_relationships.all()]

    def is_pseudo(self):
        # count = Seqfeature.objects.filter(qualifiers__term__identifier="pseudo",
        #                                                 bioentry=self.bioentry,
        #                                                 type_term__identifier="gene").count()
        # [x for x in self.bioentry.features.filter(qualifiers__term__identifier="pseudo").all()][0]

        f = [f for f in self.bioentry.features.filter(type_term__identifier=SeqfeatureQualifierValue.GeneValue,
                                                      qualifiers__value=self.locus_tag())]
        if f:
            f = f[0]
            return "pseudo" in f.qualifiers_dict()
        return False
