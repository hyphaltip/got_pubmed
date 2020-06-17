#!/usr/bin/env python3

import csv, re, sys, os
import xml.etree.ElementTree as ET
from Bio import Entrez
Entrez.email = 'ADD_YOUR_EMAIL'
insamples = "assemblies.tsv"
outsamples="assemblies_pubmed.tsv"

#Name   ASSEMBL_ID
#ID==STRAIN

if len(sys.argv) > 1:
    insamples = sys.argv[1]

if len(sys.argv) > 2:
    outsamples = sys.argv[2]

seen = {}
# to deal with crashes and re-running, this first reads in an existing
# sample.csv file and populates the dictionary with that info first
# so it can pick up where it left off or deal with hard-coded values
if os.path.exists(outsamples):
    with open(outsamples,"rU") as preprocess:
        incsv = csv.reader(preprocess,delimiter=",")
        h = next(incsv)
        for row in incsv:
            seen[row[0]] = row

# read the in_sample file and also set up the output
with open(insamples,"rU") as infh, open(outsamples,"w",newline='\n') as outfh:
    outcsv    = csv.writer(outfh,delimiter="\t")
    # the output columns will be the following
    outcsv.writerow(['SPECIES','ASSEMBLY','PUBMEDIDS'])

    samplescsv = csv.reader(infh,delimiter="\t")
    header = next(samplescsv)
    for row in samplescsv:
        if row[0].startswith("#"):
            continue
        outrow = [row[0],row[1], []]
        query = row[1]

        if row[0] in seen and len(seen[row[0]][2]) > 0:
            pmids = seen[row[0]][2]
            unique = {}
            for pmid in pmids.split(";"):
                unique[pmid] = 1
            seen[row[0]][2] = ";".join(unique.keys())
            outrow = seen[row[0]]
            outcsv.writerow(outrow)
            continue

        #print("query for assembly is %s"%(query))
        # This is the part that does the magic for Entrez (NCBI) lookup
        # we essentially leave it that a strain alone is sufficient
        # for a lookup.

        # this is not going to work for multiple strains in the BioSample
        # database

        handle = Entrez.esearch(db="assembly",retmax=10,term=query)
        record = Entrez.read(handle)
        handle.close()
        pubmeds = {}
        for assembly in record["IdList"]:
            print("assembly %s found for query '%s'"%(assembly,query))
            handle = Entrez.elink(dbfrom="assembly",db="pubmed",id=assembly)
            tree = ET.parse(handle)
            root = tree.getroot()
            #print(ET.tostring(root))
            for links in root.iter('LinkSetDb'):
                for link in links.iter("Link"):
                    for id in link.iter("Id"):
                        if id.text not in pubmeds:
                            outrow[2].append(id.text)
                            pubmeds[id.text] = 1

        outrow[2] = ";".join(outrow[2])
        outcsv.writerow(outrow)
