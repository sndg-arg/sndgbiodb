from collections import defaultdict

from bioseq.models.Biodatabase import Biodatabase
from bioseq.models.BiodatabaseQualifierValue import BiodatabaseQualifierValue
from bioseq.models.Bioentry import Bioentry
from bioseq.models.BioentryQualifierValue import BioentryQualifierValue
from bioseq.models.Ontology import Ontology
from bioseq.models.Seqfeature import Seqfeature
from bioseq.models.Term import Term

from Bio.SeqUtils import molecular_weight, IsoelectricPoint, GC, CodonUsage
import numpy as np


class IndexerIO:

    def init(self):
        self.index_ontology = Ontology.objects.get_or_create(
            name=Ontology.BIOINDEX, definition="Pre calculated values")[0]

    def index_contig(self, bioentry: Bioentry, acc: dict):

        t = Term.objects.get_or_create(ontology=self.index_ontology,
                                       identifier="EntryLength")[0]
        v = bioentry.seq.length
        acc[t.identifier].append(v)
        bqv = BioentryQualifierValue(bioentry=bioentry, term=t, value=str(v))
        bqv.save()

        t = Term.objects.get_or_create(ontology=self.index_ontology,
                                       identifier="GC")[0]
        v = GC(bioentry.seq.seq)
        acc[t.identifier].append(v)
        bqv = BioentryQualifierValue(bioentry=bioentry, term=t, value=str(v))
        bqv.save()

        for k, v in bioentry.feature_counts().items():
            t = Term.objects.get_or_create(ontology=self.index_ontology, name=k,
                                           identifier=Seqfeature.BioentryCountTermPrefix + k)[0]
            bqv = BioentryQualifierValue(bioentry=bioentry, term=t, value=str(v))
            acc[t.identifier].append(int(v))
            bqv.save()

    def index_entries(self, biodatabase: Biodatabase):
        acc = defaultdict(list)
        for entry in biodatabase.entries.all():
            self.index_contig(entry, acc)

        for k, v in list(acc.items()):
            t = Term.objects.get_or_create(ontology=self.index_ontology,
                                           identifier=k)[0]
            bqv = BiodatabaseQualifierValue(biodatabase=biodatabase, term=t)
            # acc[t.identifier] = round(float(v) + float(acc[t.identifier]),2)
            if t.identifier == "GC":
                acc[t.identifier] = np.mean(acc[t.identifier])
            else:
                acc[t.identifier] = np.sum(acc[t.identifier])

            acc[t.identifier] = round(acc[t.identifier], 2)
            bqv.value = str(acc[t.identifier])
            bqv.save()

    def index_protein(self, bioentry: Bioentry):
        t = Term.objects.get_or_create(ontology=self.index_ontology,
                                       identifier="Length")[0]
        v = bioentry.seq.length
        bqv = BioentryQualifierValue(bioentry=bioentry, term=t, value=str(v))
        bqv.save()

        t = Term.objects.get_or_create(ontology=self.index_ontology,
                                       identifier="MW")[0]
        v = molecular_weight(bioentry.seq.seq, seq_type="protein")
        bqv = BioentryQualifierValue(bioentry=bioentry, term=t, value=str(v))
        bqv.save()

        t = Term.objects.get_or_create(ontology=self.index_ontology,
                                       identifier="IP")[0]
        v = IsoelectricPoint.IsoelectricPoint(bioentry.seq.seq).pi
        bqv = BioentryQualifierValue(bioentry=bioentry, term=t, value=str(v))
        bqv.save()
