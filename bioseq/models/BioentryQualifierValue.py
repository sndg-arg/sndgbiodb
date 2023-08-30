from django.db import models

from bioseq.models.Bioentry import Bioentry


class BioentryQualifierValue(models.Model):
    bioentry_qualifiervalue_id = models.AutoField(primary_key=True)
    bioentry = models.ForeignKey(Bioentry, models.CASCADE, related_name="qualifiers")
    term = models.ForeignKey('Term', models.DO_NOTHING)
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField(default=1, null=True)

    def __repr__(self):
        return f'BEQV(be={self.bioentry.bioentry_id} {self.term.identifier}: {self.value})'

    def __str__(self):
        return self.__repr__()

    class Meta:
        managed = True
        db_table = 'bioentry_qualifier_value'
        unique_together = (('bioentry', 'term', 'rank'),)
