from django.db import models

from bioseq.models.Seqfeature import Seqfeature


class SeqfeatureRelationship(models.Model):
    seqfeature_relationship_id = models.AutoField(primary_key=True)
    object_seqfeature = models.ForeignKey(Seqfeature, models.DO_NOTHING, related_name="object_relationships")
    subject_seqfeature = models.ForeignKey(Seqfeature, models.CASCADE, related_name="subject_relationships") # parent
    term = models.ForeignKey('Term', models.DO_NOTHING)
    rank = models.IntegerField(default=1, null=True)

    class Meta:
        managed = True
        db_table = 'seqfeature_relationship'
        unique_together = (('object_seqfeature', 'subject_seqfeature', 'term'),)