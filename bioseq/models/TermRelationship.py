from django.db import models

from bioseq.models.Ontology import Ontology
from bioseq.models.Term import Term


class TermRelationship(models.Model):
    term_relationship_id = models.AutoField(primary_key=True)
    subject_term = models.ForeignKey(Term, models.DO_NOTHING, related_name="subject_termrelationships")  # parent
    predicate_term = models.ForeignKey(Term, models.DO_NOTHING, related_name="predicate_termrelationships")
    object_term = models.ForeignKey(Term, models.DO_NOTHING, related_name="object_termrelationships")  # child
    ontology = models.ForeignKey(Ontology, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'term_relationship'
        unique_together = (('subject_term', 'predicate_term', 'object_term', 'ontology'),)