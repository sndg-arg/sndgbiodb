from django.db import models

from bioseq.models.Dbxref import Dbxref
from bioseq.models.Term import Term


class TermDbxref(models.Model):
    term_dbxref_id = models.AutoField(primary_key=True)
    term = models.ForeignKey(Term, models.CASCADE, related_name="dbxrefs")
    dbxref = models.ForeignKey(Dbxref, models.DO_NOTHING)
    rank = models.SmallIntegerField(default=1, null=True)

    class Meta:
        managed = True
        db_table = 'term_dbxref'
        unique_together = (('term', 'dbxref'),)
