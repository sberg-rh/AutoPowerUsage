# Scripts for working with Kepler
* testKepler.sh - executes workload phases, restarting kepler service prior to each one. Records 'curl' payloads and emits key metric readings to stdout along with Results directory.
* USAGE: ./testKepler.sh -r ${resdir} -t ${runtime} -n ${numcpus}
* EXAMPLE: ./testKepler.sh -r TEST600run2 -t 600 -n 4
* From the code comments:  
Run the workloads declared in $workload_arr and record KEPLER Metrics after
each stage. The default workload stages are:  
STAGE 1: restart.curl  
STAGE 2: sleep ${runtime}  
STAGE 3: sysbench cpu run --time ${runtime} --threads=${numcpus}  
STAGE 4: sysbench memory run --memory-scope=global --memory-total-size=2T --memory-access-mode=rnd --threads=${numcpus} --time=${runtime}  
STAGE 5: openssl speed -evp sha256 -bytes 16384 -seconds ${runtime} -multi ${numcpus}  
Then extract KEPLER Metrics from each curl results-file  
Workload throughput rates are recorded in '$resdir/workloads.log - $resfile  
  
* To download and install Kepler see "https://github.com/sustainable-computing-io/kepler"  
