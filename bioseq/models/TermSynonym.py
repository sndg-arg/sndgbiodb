from django.db import models

from bioseq.models.Term import Term


class TermSynonym(models.Model):
    term_synonym_id = models.AutoField(primary_key=True)
    synonym = models.CharField(max_length=255)
    term = models.ForeignKey(Term, models.CASCADE, related_name="synonyms")

    class Meta:
        managed = True
        db_table = 'term_synonym'
        unique_together = (('term', 'synonym'),)