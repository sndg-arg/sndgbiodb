from django.db import models

from bioseq.models.Ontology import Ontology
from bioseq.models.Term import Term


class TermPath(models.Model):
    term_path_id = models.AutoField(primary_key=True)
    subject_term = models.ForeignKey(Term, models.DO_NOTHING, related_name="subject_termpaths") # parent
    predicate_term = models.ForeignKey(Term, models.DO_NOTHING, related_name="predicate_termpaths")
    object_term = models.ForeignKey(Term, models.DO_NOTHING, related_name="object_termpaths")
    ontology = models.ForeignKey(Ontology, models.DO_NOTHING)
    distance = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'term_path'
        unique_together = (('subject_term', 'predicate_term', 'object_term', 'ontology', 'distance'),)

