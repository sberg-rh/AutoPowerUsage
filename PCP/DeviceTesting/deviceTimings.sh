#!/bin/bash

# OUTER Loop - increase $delay
delay=10
for multiplier in {1..4}; do
        this_delay=$((delay*multiplier))
    echo "Delay between samples: ${this_delay} seconds"
    load="openssl speed -evp sha256 -bytes 16384 -seconds ${this_delay} \
          -multi $(nproc)"
    echo "Workload: ${load}"
    fname="${this_delay}sec.csv"

    # Start PMREP in backgrd and record PID
    pmrep -t 3 -o csv -F ${fname} \
        openmetrics.RFchassis openmetrics.RFpdu1 openmetrics.RFpdu2 \
        denki.rapl openmetrics.kepler.kepler_node_platform_joules_total \
        openmetrics.control.fetch_time &
    pmrepPID=$!
    
    # INNER Loop - repeat for 5 samples 
    echo -n "Sample "
    for sample_ctr in {1..5}; do
        echo -n "${sample_ctr}, "
        sleep $this_delay
##        $load &> /dev/null
    done
    kill ${pmrepPID}
    echo; echo "------------------"
    # Allow PMREP time to write CSV file
    sleep 5
    if [ -e $fname ]; then
        echo "Succesfully created $fname"
    else
        echo "Failed to create $fname, exiting"
        exit 1
    fi
done

