from django.db import models

from bioseq.models.Taxon import Taxon


class TaxonName(models.Model):
    id = models.AutoField(primary_key=True)
    taxon = models.ForeignKey(Taxon, models.DO_NOTHING, related_name="names")
    name = models.CharField(max_length=255)
    name_class = models.CharField(max_length=32)

    class Meta:
        managed = True
        db_table = 'taxon_name'
        unique_together = (('taxon', 'name', 'name_class'),)