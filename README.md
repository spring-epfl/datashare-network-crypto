# DatashareNetwork proof of concept
This repository accompanies the paper *DatashareNetwork: A Decentralized
Privacy-Preserving Search Engine for Investigative Journalists* by Kasra
EdalatNejad (SPRING Lab, EPFL), Wouter Lueks (SPRING Lab, EPFL), Julien Pierre
Martin, Soline Ledésert (ICIJ), Anne L'Hôte (ICIJ), Bruno Thomas (ICIJ), Laurent
Girod (SPRING Lab, EPFL) and Carmela Troncoso (SPRING Lab, EPFL), which will be
presented at USENIX 2020.

This repository contains a proof of concept implementation of cryptographic
primitives of DatashareNetwork and aims to enable reproducibility
of measurements in the paper.

You can find the extended edition of the DatashareNetwork paper at [https://arxiv.org/abs/2005.14645].


## Installation

Install petlib's requirements

    sudo apt-get install python3-dev libssl-dev libffi-dev

(Optional) Create a virtual environment

    python3 -m venv venv
    source venv/bin/activate

Install the requirements.

    pip3 install -r requirements.txt

To run the tests, run the following command.

    python3 -m pytest -s

## Anonymous Credentials
Anonymous credentials have been moved to the [SSCred library](https://github.com/spring-epfl/SSCred).

## Evaluation

Two benchmarks are provided

- `benchmark-mspsi.py`: Benchmark for interacting with one journalist. This benchmark aims to measure the time to make and reply to a query.
- `benchmark-mspsi-many-journalist.py`: Benchmark for searching the corpora of many journalists. 

These benchmarks run the protocol and record the timing in the `benchmark-mspsi-{time-stamp}.json` file.

A jupyter notebook (`notebooks\benchmark_plotting_mspsi.ipynb`) is provided to visualize the single journalist data.

To use the notebook:
    jupyter lab notebooks\benchmark_plotting_mspsi.ipynb

Then open the notebook with Jupyter's interface. Run all cells to generate the performance plots of mspsi.
