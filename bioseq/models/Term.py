# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import gettext_lazy as __
from django.db import models
from django.shortcuts import reverse

from .Ontology import Ontology
from .Dbxref import Dbxref

class Term(models.Model):
    term_id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=False)
    definition = models.TextField(blank=True, null=True)
    identifier = models.CharField(max_length=255, blank=False, null=False)
    is_obsolete = models.CharField(max_length=1, blank=True, null=True)
    ontology = models.ForeignKey(Ontology, models.DO_NOTHING,related_name="terms")
    version = models.PositiveSmallIntegerField(default=1, null=True)

    class Meta:
        managed = True
        db_table = 'term'
        unique_together = (('identifier', 'ontology', 'is_obsolete'),)

    def __str__(self):
        return "%s - %s (%s)" % (self.identifier, self.name, self.ontology.name)




class TermIdx(models.Model):
    """
    Created for indexing purposes
    """
    term = models.OneToOneField(Term, models.CASCADE, primary_key=True, db_column="term_id", related_name="keywords")
    text = models.TextField()

    class Meta:
        managed = True
        db_table = 'term_idx'
