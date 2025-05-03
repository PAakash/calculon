#!/usr/bin/bash

declare -a models=("1" "2" "4" "11" "26" "53" "128")

for m in "${models[@]}"
do
    model="models/Test-${m}T.json"
    outputDir="results/Test-${m}T"
    mkdir -p ./$outputDir

    if ! python calculon_bin.py \
        llm \
        $model \
        examples/4096_t8_p2_d256_mbs4_full.json \
        systems/h100_80g_nvl8.json \
        $outputDir/calculon_stats.json \
        -l \
        -p $outputDir/calculon_peers.json > ./$outputDir/runLog.txt
    then
        echo "Failed to $m"
        continue
    fi
done
