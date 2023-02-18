from django.db import models

from bioseq.models.Seqfeature import Seqfeature


class SeqfeaturePath(models.Model):
    seqfeature_path_id = models.AutoField(primary_key=True)
    object_seqfeature = models.ForeignKey(Seqfeature, models.DO_NOTHING, related_name="object_paths")
    subject_seqfeature = models.ForeignKey(Seqfeature, models.DO_NOTHING, related_name="subject_paths") # parent
    term = models.ForeignKey('Term', models.DO_NOTHING)
    distance = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'seqfeature_path'
        unique_together = (('object_seqfeature', 'subject_seqfeature', 'term', 'distance'),)