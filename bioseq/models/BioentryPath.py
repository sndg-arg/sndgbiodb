from django.db import models

from bioseq.models.Bioentry import Bioentry


class BioentryPath(models.Model):
    bioentry_path_id = models.AutoField(primary_key=True)
    object_bioentry = models.ForeignKey(Bioentry, models.DO_NOTHING, related_name="object_bioentry_path")
    subject_bioentry = models.ForeignKey(Bioentry, models.DO_NOTHING, related_name="subject_bioentry_path")  # parent
    term = models.ForeignKey('Term', models.DO_NOTHING)
    distance = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'bioentry_path'
        unique_together = (('object_bioentry', 'subject_bioentry', 'term', 'distance'),)