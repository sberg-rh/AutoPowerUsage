#!/bin/bash
# Run these workloads and record KEPLER Metrics after each stage:
# STAGE 1: restart.curl
# STAGE 2: sleep 120
# STAGE 3: sysbench cpu run --time 120 --threads={$numcpus}
# STAGE 4: sysbench memory --threads={$numcpus}
# And then extract KEPLER Metrics from each curl results-file
# USAGE:  
#######################################################################
declare -a curl_arr=(
    "curl_restart.log"
    "curl_sleep120.log"
    "curl_sysbenchCPU120.log"
    "curl_sysbenchMEM.log"
)
declare -a workload_arr=(
    "sleep 0"
    "sleep 120"
    "sysbench cpu run --time=120 --threads=144"
    "sysbench memory --memory-scope=global --memory-total-size=1T --memory-access-mode=rnd --threads=144 --time=120 run"
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
