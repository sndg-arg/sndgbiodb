from django.db import models

from bioseq.models.Biodatabase import Biodatabase
from bioseq.models.Bioentry import Bioentry


class BiodatabaseQualifierValue(models.Model):



    biodatabase_qualifiervalue_id = models.AutoField(primary_key=True)
    biodatabase = models.ForeignKey(Biodatabase, models.CASCADE, related_name="qualifiers")
    term = models.ForeignKey('Term', models.DO_NOTHING)
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField(default=1, null=True)

    class Meta:
        managed = True
        db_table = 'bioedatabase_qualifier_value'
        unique_together = (('biodatabase', 'term', 'rank'),)

    def __repr__(self):
        return f'BdbQV {self.term.identifier}: {self.value}'