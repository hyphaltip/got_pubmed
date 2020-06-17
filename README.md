got_pubmed
====

This set of scripts is helpful for retrieving pubmed and other NCBI IDs for resources.

The scripts depend on [https://biopython.org/](Biopython) (eg. `conda install biopython`).


Running the Tools
====

* Get Pubmed IDs for Genbank Assemblies
`./fetch_pubmed_for_asm.py examples/assemblies.tsv`

* Get BioProject, BioSamples, NCBI Locus Prefix, and SRA numbers
`./fetch_samples_prefix.py examples/bioproject.tsv`
