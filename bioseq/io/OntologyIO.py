from goatools.obo_parser import GODag
import re


class OntologyIO:
    """
    http://purl.obolibrary.org/obo/go.obo
    https://ftp.expasy.org/databases/enzyme/enzyme.dat
    https://ftp.expasy.org/databases/enzyme/enzclass.txt
    """

    def obo_ontology(self,  obo_file):
        obodag = GODag(obo_file, optional_attrs={"subset", "def"})
        idx = {}
        for term in obodag:

            text = (obodag[term].name + " " + obodag[term].id + " " +

                    obodag[term].defn + " " + " ".join(obodag[term].subset))

            for parent in obodag[term].get_all_parents():
                if parent not in ["GO:0008150", "GO:0005575", "GO:0003674"]:
                    text += (obodag[parent].name + " " + obodag[parent].id + " " +
                             obodag[parent].defn + " " + " ".join(obodag[parent].subset))
            idx[term] = text
            for syn in obodag[term].alt_ids:
                idx[syn] = text
        return obodag

    def ec_ontology(self, enzdata_file_path, enzclass_file_path):
        terms_dict = {}
        idx = {}
        with open(enzclass_file_path) as enzclass_handle:
            for line in enzclass_handle:
                if re.match(r'^[1-6][.]', line):
                    name = line.split(".-")[-1].strip()
                    term = "ec:" + line.replace(name, "").replace(" ", "").strip()
                    terms_dict[term] = name

        term = None
        with open(enzdata_file_path) as enzclass_handle:
            for line in enzclass_handle:
                if line.startswith("DE"):
                    terms_dict[term] = name
                elif line.startswith("ID"):
                    term = "ec:" + line.split("ID")[1].strip()
        return terms_dict
        """
        for term, name in terms_dict.items():
            idx[term] =  name
            #for x in term.replace(".-","").split("."):
        """



