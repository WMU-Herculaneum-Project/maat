# Machine-Actionable Ancient Text Corpus (MAAT)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12553283.svg)](https://doi.org/10.5281/zenodo.12553283)

This is code to create the [Machine-Actionable Ancient Text Corpus (MAAT)](https://zenodo.org/records/12553283).

## Installation

This code uses the `poetry` system to install Python dependencies. To install, clone this
repository, and then:

```sh
$ poetry install
$ poetry shell
```

## Use

First, you need to install the TEI XML files that you want to convert to MAAT.

The first corpora added to the MAAT corpus are the following:

1. [The Duke Databank of Documentary Papyri](https://papyri.info/docs/ddbdp) data can be cloned from [here](https://github.com/papyri/idp.data).
2. [The Digital Corpus of Literary Papyri] (https://papyri.info/browse/dclp) data can be cloned from [here] (https://github.com/papyri/idp.data).
3. [Epigraphic Database Heidelberg](https://edh.ub.uni-heidelberg.de/home) data can be downloaded from [here](https://edh.ub.uni-heidelberg.de/data/download).

The `script/convert` script is used to convert the TEI XML files to MAAT. The script takes one or more directories as input, and writes the MAAT JSON-LD to standard output.

This is how the first files were converted:

```sh
$ script/convert /Volumes/general/corpora/papyri/idp.data/DDB_EpiDoc_XML  /Volumes/general/corpora/papyri/idp.data/DCLP /Volumes/general/corpora/inscriptions | tee /tmp/results.json | jq .id
```

This places the results in `/tmp/results.json`, and prints the `id` field of each document to standard output.

A log file is also created in the current directory, with the name ` convert_errors.json`. This file contains the errors that occurred during the conversion process. It is also in JSON-LD format.

## Citation

If you use this code, please cite the following:

```bibtex
@software{maat,
  author = {Fitzgerald, Will AND Barney, Justin},
  title = {Machine-Actionable Ancient Text Corpus (MAAT)},
  url = {https://github.com/WMU-Herculaneum-Project/maat},
  version = {1.0.0},
  date = {2024-07-15},
}
```
