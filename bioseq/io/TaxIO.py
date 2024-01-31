from bioseq.models.Taxon import Taxon

import requests
import urllib.parse

from bioseq.models.TaxonName import TaxonName


class TaxException(Exception):
    pass


class TaxIO:

    def get_tax_from_name(self, taxname):
        query = f'https://www.ebi.ac.uk/ena/taxonomy/rest/scientific-name/{urllib.parse.quote(taxname)}?binomialOnly=false'
        r = requests.get(query)
        if r.ok:
            return r.json()[0]
        else:
            raise TaxException(f"could not find tax name '{taxname}'")

    def get_tax_from_id(self, ncbi_taxid: int):
        r = requests.get(f'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/{ncbi_taxid}?binomialOnly=false')
        if r.ok:
            return r.json()
        else:
            raise TaxException(f"could not find tax id '{ncbi_taxid}'")

    def id_exists_in_db(self, ncbi_taxid: int):
        return Taxon.objects.filter(ncbi_taxon_id=ncbi_taxid).exists()

    def get_by_id_from_db(self, ncbi_taxid: int):
        return Taxon.objects.filter(ncbi_taxon_id=ncbi_taxid).get()

    def get_by_name_from_db(self, taxname: str):
        return Taxon.objects.filter(scientificName=taxname).get()

    def name_exists_in_db(self, taxname: str):
        return Taxon.objects.filter(scientificName=taxname).exists()

    def complete_tax(self, ncbi_tax: int):
        if self.id_exists_in_db(ncbi_tax):
            return
        taxdto = self.get_tax_from_id(ncbi_tax)
        lineages = [x.strip() for x in taxdto["lineage"].strip().split(";") if x.strip()]

        parent = None
        for taxname in lineages:
            if not self.name_exists_in_db(taxname):
                taxdto_parent = self.get_tax_from_name(taxname)
                parent = self.save(taxdto_parent, parent)
        if not parent:
            parent = self.get_by_name_from_db(taxname)

        self.save(taxdto, parent)

    def save(self, taxdto: dict, parent: int):

        """
              "taxId" : "1280",
              "scientificName" : "Staphylococcus aureus",
              "formalName" : "true",
              "rank" : "species",
              "division" : "PRO",
              "lineage" : "Bacteria; Bacillota; Bacilli; Bacillales; Staphylococcaceae; Staphylococcus; ",
              "geneticCode" : "11",
              "submittable" : "true",
              "binomial" : "true"
              # commonName
                # mitochondrialGeneticCode
            """
        print(taxdto)
        taxon = Taxon(ncbi_taxon_id=int(taxdto["taxId"]),
                      parent_taxon=parent,
                      node_rank=taxdto["rank"],
                      node_division=taxdto["division"],
                      scientificName=taxdto["scientificName"],
                      genetic_code=taxdto["geneticCode"],
                      )

        if "mitochondrialGeneticCode" in taxdto:
            taxon.mito_genetic_code = taxdto["mitochondrialGeneticCode"]
        taxon.save()
        if "commonName" in taxdto:
            tn = TaxonName(taxon=taxon, name=taxdto["commonName"], name_class="commonName")
            tn.save()
        tn = TaxonName(taxon=taxon, name=taxdto["scientificName"], name_class="scientificName")
        tn.save()
        return taxon
