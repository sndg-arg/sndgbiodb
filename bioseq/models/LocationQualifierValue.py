from django.db import models

from bioseq.models.Location import Location


class LocationQualifierValue(models.Model):
    location = models.OneToOneField(Location, models.DO_NOTHING, primary_key=True)
    term = models.ForeignKey('Term', models.DO_NOTHING)
    value = models.CharField(max_length=255)
    int_value = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'location_qualifier_value'
        unique_together = (('location', 'term'),)