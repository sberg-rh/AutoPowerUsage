#!/bin/bash

load="openssl speed -evp sha256 -bytes 16384 -seconds ${delay} -multi $(nproc)"

echo "Workload: ${load}"

for delay in {10, 20, 40, 80}; do
    echo "Delay between samples: ${delay} seconds"
    echo "Workload: ${load}"
    fname="${delay}sec.csv"

    # Start PMREP in backgrd and record PID
    pmrep -t 3 -o csv -F ${fname} \
        openmetrics.RFchassis openmetrics.RFpdu1 openmetrics.RFpdu2 \
        denki.rapl openmetrics.kepler.kepler_node_platform_joules_total \
        openmetrics.control.fetch_time &
    pmrepPID=$!

    echo -n "Sample "
    for sample_ctr in {1..5}; do
        echo -n "${sample_ctr} "
        sleep $delay
        $load &> /dev/null
    done
    kill ${pmrepPID}
    echo "------------------"
    # Allow PMREP time to write CSV file
    sleep 5
    if -e $fname
        echo "Succesfully created $fname"
    else
        echo "Failed to create $fname, exiting"
        exit 1
    fi
done
