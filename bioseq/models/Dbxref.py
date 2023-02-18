# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.translation import gettext_lazy as __
from django.db import models
from django.shortcuts import reverse



class Dbxref(models.Model):
    dbxref_id = models.AutoField(primary_key=True)
    dbname = models.CharField(max_length=40)
    accession = models.CharField(max_length=128)
    version = models.PositiveSmallIntegerField(default=1, null=True)

    class Meta:
        managed = True
        db_table = 'dbxref'
        unique_together = (('accession', 'dbname', 'version'),)

    def __str__(self):
        return self.dbname + ":" + self.accession + "." + str(self.version)


class DbxrefQualifierValue(models.Model):
    dbxref = models.OneToOneField(Dbxref, models.DO_NOTHING, primary_key=True)
    term = models.ForeignKey('Term', models.DO_NOTHING)
    rank = models.SmallIntegerField(default=1, null=True)
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dbxref_qualifier_value'
        unique_together = (('dbxref', 'term', 'rank'),)