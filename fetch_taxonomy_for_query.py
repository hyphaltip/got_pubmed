#!/usr/bin/env python3

import csv, re, sys, os
import xml.etree.ElementTree as ET
from Bio import Entrez
Entrez.email = 'YOUR_EMAIL'
insamples = "names.tsv"
outsamples="names_taxonomy.csv"

if len(sys.argv) > 1:
    insamples = sys.argv[1]

if len(sys.argv) > 2:
    outsamples = sys.argv[2]

seen = {}
if os.path.exists(outsamples):
    with open(outsamples,"rU") as preprocess:
        incsv = csv.reader(preprocess,delimiter=",")
        h = next(incsv)
        for row in incsv:
            seen[row[1]] = row

expected_ranks = ['kingdom','phylum','subphylum','class', 'order','family','genus']
with open(insamples,"rU") as infh, open(outsamples,"w") as outfh:
    outcsv    = csv.writer(outfh,delimiter=",")
    outcsv.writerow(['PREFIX','NAME','KINGDOM','PHYLUM','SUBPHYLUM','CLASS','ORDER','FAMILY','GENUS','LINEAGE'])

    namescsv = csv.reader(infh,delimiter="\t")
    for row in namescsv:
        prefix= row[0]
        name  = row[1]
        if name.startswith("#"):
            continue

        outrow = [prefix,name]
        if name in seen:
            outrow = seen[name]
            outcsv.writerow(outrow)
            continue

        query_fields  = name.split("_")[0:2]
        query  = "%s+%s"%(query_fields[0],query_fields[1])

        handle = Entrez.esearch(db="taxonomy",retmax=10,term=query)
        record = Entrez.read(handle)
        handle.close()
        for taxon in record["IdList"]:
            print("taxon was %s for query=%s"%(taxon,query))
            handle = Entrez.efetch(db="taxonomy", id=taxon)
            tree = ET.parse(handle)
            root = tree.getroot()
            taxonomy = {}
            full_lineage = ""
            for l in root.iter('Lineage'):
                full_lineage = l.text

            for lineage in root.iter('LineageEx'):
                for taxnode in lineage.iter('Taxon'):
                    rank = ""
                    sciname = ""
                    taaxid = ""
                    for taxdat in taxnode:
                        if taxdat.tag == "Rank":
                            rank = taxdat.text
                        elif taxdat.tag ==  "ScientificName":
                            sciname = taxdat.text
                        elif taxdat.tag == "TaxId":
                            taxid = taxdat.text

                    #print("Taxon node %s is called '%s' (%s) "%(rank,sciname,taxid))
                    if rank != 'no rank':
                        taxonomy[rank] = [sciname,taxid]

        for rank in expected_ranks:
            if rank in taxonomy:
                outrow.append(taxonomy[rank][0])
            else:
                outrow.append("")
        outrow.append(full_lineage)
        outcsv.writerow(outrow)
