from django.db import models




class SeqfeatureQualifierValue(models.Model):

    ProductValue = "product"
    NoteValue = "note"
    GeneValue = "gene"
    TranslationValue = "translation"
    GeneSymbolValue = "gene_symbol"
    OldLocusTagValue = "old_locus_tag"
    LocusTagValue = "locus_tag"
    AliasValue = "Alias"
    ProteinIDValue = "protein_id"
    PSEUDOValue = "pseudo"
    DBXREFValue = "db_xref"



    seqfeature_qualifiervalue_id = models.AutoField(primary_key=True)
    seqfeature = models.ForeignKey('Seqfeature', models.CASCADE, related_name="qualifiers")
    term = models.ForeignKey('Term', models.DO_NOTHING)
    rank = models.SmallIntegerField(default=1, null=True)
    value = models.TextField()

    class Meta:
        managed = True
        db_table = 'seqfeature_qualifier_value'
        unique_together = (('seqfeature', 'term', 'rank'),)
        indexes = [
            models.Index(fields=['term']),
        ]

    def __str__(self):
        return str(self.term.name) + ":" + self.value
