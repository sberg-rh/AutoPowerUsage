#!/bin/bash
# Run these workloads and record KEPLER Metrics after each stage:
# STAGE 1: restart.curl
# STAGE 2: sleep 120
# STAGE 3: openssl speed -evp sha256 -bytes 16384 -seconds 120 -multi 144
# And then extract KEPLER Metrics from each curl results-file
# USAGE:  
#######################################################################
declare -a curl_arr=(
    "curl_restart.log"
    "curl_sleep120.log"
    "curl_openssl.log"
)
declare -a workload_arr=(
    "sleep 0"
    "sleep 120"
    "openssl speed -evp sha256 -bytes 16384 -seconds 120 -multi 144"
)
declare -a km_arr=(
    "^kepler_node_package_joules_total"
    "^kepler_node_platform_joules_total"
    "^kepler_node_core_joules_total"
    "^kepler_node_dram_joules_total"
)

###################################
# Perform Workload Stages
wl_cntr=0                     # initialize loop counter
for cmd in "${workload_arr[@]}"; do
    # Restart Kepler svc
    systemctl restart container-kepler --now
    sleep 5s                  # delay for restart
    # Execute workload
    echo "> Executing: $cmd"        # DEBUG
    $cmd
    # Read Kepler Metrics and record to curl file
    curl localhost:8888/metrics 2>/devnull 1>"${curl_arr[$wl_cntr]}"
    sleep 5s                  # arbitrary delay
    wl_cntr=$((wl_cntr+1))    # incr loop counter
done

###################################
# Search for and Report Key Metrics
for cfile in "${curl_arr[@]}"; do
    echo "==============================="
    echo "METRICS from file $cfile:"
    for kmetric in "${km_arr[@]}"; do
        echo -n "${kmetric:1}"             # strip preceeding "^"
        cat $cfile | awk '/'"$kmetric"'/{printf " , %s", $NF} END {print ""}'
    done
done
echo "==============================="
