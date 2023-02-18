from django.db import models

from bioseq.models.Dbxref import Dbxref
from bioseq.models.Seqfeature import Seqfeature


class SeqfeatureDbxref(models.Model):
    seqfeature_dbxref_id = models.AutoField(primary_key=True)
    seqfeature = models.ForeignKey(Seqfeature, models.DO_NOTHING, related_name="dbxrefs")
    dbxref = models.ForeignKey(Dbxref, models.DO_NOTHING)
    rank = models.SmallIntegerField(default=1, null=True)

    class Meta:
        managed = True
        db_table = 'seqfeature_dbxref'
        unique_together = (('seqfeature', 'dbxref'),)
