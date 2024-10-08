# -*- coding: utf-8 -*-
from django.db import models

class Ligand(models.Model):
    ligand_id = models.AutoField(primary_key=True)
    ligand_from_key = models.CharField(max_length=255)
    ligand_smiles = models.CharField(max_length=255)

    def __str__(self):
        return f"Ligand ID: {self.ligand_id}, SMILES: {self.ligand_smiles}"