# Changelog:

- runScript.py v0
    > Running in loe mode
    > Standard sweep going through arbitrary parameters and large sweep for
    > memory BW, capacity, intra-node and inter-node BW sweep
- runScript_updated.py v1
    > This script failed since I started two scripts updated and new :(
    > there are about 20k results available
    > Updated sweep parameters and combined memory tech
    > Sweep for single model as before
- runScript_new.py v2
    > Adding models for the sweep
    > Removed some ucie data rates
    > adding models from 175B to 125T, most of them might not work and log will
    > be like no possible solution found or error in divinding for TP
- runScript_v3.py
    > Added efficiency sweep but did not run this script
- runScript_v4.py
    > Going back to sensitivity sweeps
    > 


- test
    > test results to check calculon works or not, mostly with single config
    > with different model
- testRuns
    > runScript_updated.py results are here
- archive/testRuns
    > runScript.py file results
- results_workload
    > results for runScript_new.py


[![DOI](https://zenodo.org/badge/660734586.svg)](https://zenodo.org/badge/latestdoi/660734586)
# Calculon - Co-design for large scale parallel applications

## Running

Run Calculon like this:
``` sh
$> PYTHONPATH=. ./bin/ <args>
```

Calculon is a hierarchical command line. To see the commands it accepts, use `--help` or `-h`:
``` sh
$> PYTHONPATH=. ./bin/ -h
```

You can also see how to use any command specifically by using `--help` or `-h` on the command:
``` sh
$> PYTHONPATH=. ./bin/ llm -h
```

## LLM Example

Run a single calculation for LLM (~1 sec):
``` sh
$> PYTHONPATH=. ./bin/ llm models/megatron-1T.json examples/3072_t4_p64_d12_mbs4_full.json systems/a100_80g.json -
```

Run a system execution optimizer for LLM (~1 min):
``` sh
$> PYTHONPATH=. ./bin/ llm-optimal-execution models/turing-530B.json 5128 2520 float16 systems/a100_80g.json output.json -m
```
`opt_exe.json` will contain the optimal way to run Turing-530B across 5128 A100 GPUs.

To store results from all successful runs from the same experiment, run a special system optimizer (~1 min):
``` sh
$> PYTHONPATH=. ./bin/ llm-all-executions models/turing-530B.json 5128 2520 float16 systems/a100_80g.json all_output.csv
```

## Testing and validation (optional)
To make sure that the current build is working, use

``` sh
$> make test
```
To validate Calculon performance modeling against Megatron run on NVIDIA's Selene A100-based supercomputer with results published in ["Sequence parallelism" paper](https://arxiv.org/abs/2205.05198), use

``` sh
$> PYTHONPATH=. ./bin/calculon llm-validation
```

## Publications

* Calculon: A Methodology and Tool for High-Level Co-Design of Systems and Large Language Models\
Mikhail Isaev, Nic McDonald, Larry Dennison, Richard Vuduc\
[Paper](https://dl.acm.org/doi/pdf/10.1145/3581784.3607102)

* Scaling Infrastructure to Support Multi-Trillion Parameter LLM Training\
Mikhail Isaev, Nic McDonald, Richard Vuduc\
[Paper](https://openreview.net/pdf?id=rqn2v1Ltgn0)
