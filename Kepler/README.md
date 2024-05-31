# Scripts for working with Kepler
* testKepler.sh - executes workload phases (idle, 'sysbench cpu' and 'sysbench mem'), restarting kepler service prior to each one. Records 'curl' payloads and emits key metric readings to stdout along with Results directory.
* USAGE: ./testKepler.sh -r <resultsDir> -t <runtime> -n <numcpus>
* EXAMPLE: ./testKepler.sh -r TEST600run2 -t 600 -n 4

To download and install Kepler see "https://github.com/sustainable-computing-io/kepler"
