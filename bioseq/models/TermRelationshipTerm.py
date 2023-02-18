from django.db import models

from bioseq.models.Term import Term
from bioseq.models.TermRelationship import TermRelationship


class TermRelationshipTerm(models.Model):
    term_relationship = models.OneToOneField(TermRelationship, models.DO_NOTHING, primary_key=True)
    term = models.OneToOneField(Term, models.DO_NOTHING, unique=True)

    class Meta:
        managed = True
        db_table = 'term_relationship_term'