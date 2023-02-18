from django.db import models

from bioseq.models.Bioentry import Bioentry


class BioentryQualifierValue(models.Model):



    bioentry_qualifiervalue_id = models.AutoField(primary_key=True)
    bioentry = models.ForeignKey(Bioentry, models.CASCADE, related_name="qualifiers")
    term = models.ForeignKey('Term', models.DO_NOTHING)
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField(default=1, null=True)

    class Meta:
        managed = True
        db_table = 'bioentry_qualifier_value'
        unique_together = (('bioentry', 'term', 'rank'),)
