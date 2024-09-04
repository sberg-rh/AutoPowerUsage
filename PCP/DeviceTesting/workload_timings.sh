#!/bin/bash

declare -a load_arr=(
    "sysbench cpu run --time=10 --threads=$(nproc)"
    "openssl speed -evp sha256 -bytes 16384 -seconds 10 -multi $(nproc)"
)


for load in "${load_arr[@]}"; do
    echo "Workload: ${load}"
    for ctr in {1..10}; do
##        RESfile = "loop$ctr"
        echo -n "Sample ${ctr}"
        time $load &> /dev/null
        echo
    done
    echo "------------------"
done
