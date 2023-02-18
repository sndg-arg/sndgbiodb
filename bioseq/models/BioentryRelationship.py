from django.db import models

class BioentryRelationship(models.Model):
    bioentry_relationship_id = models.AutoField(primary_key=True)
    object_bioentry = models.ForeignKey(Bioentry, models.DO_NOTHING, related_name="object_bioentry_relationship")
    subject_bioentry = models.ForeignKey(Bioentry, models.DO_NOTHING,
                                         related_name="subject_bioentry_relationship")  # parent
    term = models.ForeignKey('Term', models.DO_NOTHING)
    rank = models.IntegerField(default=1, null=True)

    class Meta:
        managed = True
        db_table = 'bioentry_relationship'
        unique_together = (('object_bioentry', 'subject_bioentry', 'term'),)