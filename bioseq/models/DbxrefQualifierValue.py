from django.db import models

from bioseq.models.Dbxref import Dbxref


class DbxrefQualifierValue(models.Model):
    dbxref = models.OneToOneField(Dbxref, models.DO_NOTHING, primary_key=True)
    term = models.ForeignKey('Term', models.DO_NOTHING)
    rank = models.SmallIntegerField(default=1, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dbxref_qualifier_value'
        unique_together = (('dbxref', 'term', 'rank'),)