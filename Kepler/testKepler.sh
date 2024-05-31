#!/bin/bash
# Run the workloads declared in $workload_arr and record KEPLER Metrics after
# each stage. The default workloads are:
# STAGE 1: restart.curl
# STAGE 2: sleep ${runtime}
# STAGE 3: sysbench cpu run --time ${runtime} --threads=${numcpus}
# STAGE 4: sysbench memory run --memory-scope=global --memory-total-size=2T --memory-access-mode=rnd --threads=${numcpus} --time=${runtime}
# STAGE 5: openssl speed -evp sha256 -bytes 16384 -seconds ${runtime} -multi ${numcpus}
# Then extract KEPLER Metrics from each curl results-file
# Workload throughput rates are recorded in '$resdir/workloads.log - $resfile
#############
# USAGE: $ ./script.sh -r $resdir -t $runtime -n $numcpus  
#      All three args are required
#
# Example: $ ./script -r TEST -t 300 -n 8
#
#######################################################################

###################################
# Parse args
unset -v resdir
unset -v runtime
unset -v numcpus
usage() {  echo "required args <-r resDir -t runtime(in seconds) -n numcpus>"; exit 1; }

while getopts "r:t:n:" arg; do
    case "${arg}" in
        r) # Required. Specify results directory.
          resdir=${OPTARG}
          ;;
        t) # Required. Specify workload runtime.
          runtime=${OPTARG}
          ;;
        n) # Required. Specify numcpus.
          numcpus=${OPTARG}
          ;;
        ?) # Display help.
          usage
          ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${resdir}" ] || [ -z "${runtime}" ] || [ -z "${numcpus}" ]; then
    usage
fi

##echo $resdir $runtime $numcpus           # DEBUG

###################################
# Declare arrays
# NOTE: these two arrays (curl_arr and workload_arr) must be aligned.
#       in other words, they must have the same number of elements.
declare -a curl_arr=(
    "${resdir}/curl_restart.log"
    "${resdir}/curl_sleep${runtime}.log"
    "${resdir}/curl_sysbenchCPU${runtime}.log"
    "${resdir}/curl_sysbenchMEM${runtime}.log"
    "${resdir}/curl_opensslEVP${runtime}.log"
)
declare -a workload_arr=(
    "sleep 0"
    "sleep ${runtime}"
    "sysbench cpu run --time=${runtime} --threads=${numcpus} | grep 'events per second:' "
    "sysbench memory run --time=${runtime} --threads=${numcpus} --memory-scope=global --memory-total-size=2T --memory-access-mode=rnd | grep '^Total operations:' "
    "openssl speed -evp sha256 -bytes 16384 -seconds ${runtime} -multi ${numcpus} 2>/dev/null | grep '^sha256' "
)
declare -a km_arr=(
    "^kepler_node_package_joules_total"
    "^kepler_node_platform_joules_total"
    "^kepler_node_core_joules_total"
    "^kepler_node_dram_joules_total"
)

###################################
# Create RESULTS Directory and RESULTS summary file
if [ -d "$resdir" ]; then
	echo "Directory $resdir exists, exiting."
	exit 1
fi

mkdir $resdir
if [ $? -eq 0 ]; then
    echo "Created directory $resdir, continuing with test."
else
    echo "FAILED to create directory $resdir, exiting."
    exit 1
fi

resfile="${resdir}/workloads.log"
touch $resfile
if [ $? -ne 0 ]; then
    echo "FAILED to create workload summary file $resfile, exiting."
    exit 1
fi

###################################
# Record SUT facts
# lscpu
# ??
# cstates
# pstates
# tuned profile


###################################
# Perform Workload Stages
wl_cntr=0                     # initialize loop counter
for cmd in "${workload_arr[@]}"; do
    # Restart Kepler svc
    systemctl restart container-kepler --now
    sleep 5s                  # delay for restart
    # Execute workload
    echo "> Executing: $cmd" | tee -a $resfile
    eval "$cmd" | tee -a $resfile 
    if [ $? -ne 0 ]; then
       echo "Workload failed to run, exiting."
       exit 1
    fi
    # Read Kepler Metrics and record to associated curl file
##    curl localhost:8888/metrics 2>/dev/null 1>"${curl_arr[$wl_cntr]}"
    curl localhost:8888/metrics 2>/dev/null | grep kepler_node >"${curl_arr[$wl_cntr]}"
##    sleep 5s                  # arbitrary delay REMOVED
    wl_cntr=$((wl_cntr+1))    # incr loop counter
done

##################################
# Search for and Report Key Metrics
for cfile in "${curl_arr[@]}"; do
    echo "==============================="
    echo "Kepler METRICS from file $cfile:"
    for kmetric in "${km_arr[@]}"; do
        echo -n "${kmetric:1}"             # strip preceeding "^"
##        cat $cfile | awk '/'"$kmetric"'/{printf "\t%s", $NF} END {print ""}'
        cat $cfile | awk '/'"$kmetric"'/ && /idle/ {printf "\tIDLE: %s", $NF} END {printf ""}'
        cat $cfile | awk '/'"$kmetric"'/ && /dynamic/ {printf "\tDYNAMIC: %s", $NF} END {print ""}'
##        awk -v regx="$kmetric" 'BEGIN if ( $0 ~ regx ){printf "\t%s", $NF} END {print ""}' $cfile
    done
done
echo "==============================="

##################################
# Print workload summary file
echo "$resfile contains: "
if [ -f $resfile ]; then
	cat $resfile
else
	echo "ERROR: workload summary file does not exist"
fi

echo "==============================="
