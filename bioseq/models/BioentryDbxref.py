from django.db import models

from bioseq.models.Bioentry import Bioentry


class BioentryDbxref(models.Model):
    bioentry_dbxref_id = models.AutoField(primary_key=True)
    bioentry = models.ForeignKey(Bioentry, models.CASCADE, related_name="dbxrefs")
    dbxref = models.ForeignKey('Dbxref', models.DO_NOTHING)
    rank = models.SmallIntegerField(default=1, null=True)

    class Meta:
        managed = True
        db_table = 'bioentry_dbxref'
        unique_together = (('bioentry', 'dbxref', 'rank'),)

    def __repr__(self):
        return f'BioentryDbxref({self.bioentry.accession} - {self.dbxref.accession})'

    def __str__(self):
        return self.__repr__()