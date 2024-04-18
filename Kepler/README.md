# Collection of scripts for working with Kepler
* runSysbench.sh - executes workload phases (idle, 'sysbench cpu' and 'sysbench mem'), restarting kepler service prior to each one. Records 'curl' payloads and emits key metric readings to stdout
* runOpenssl.sh - executes workload phases (idle and 'openssl speed'), restarting kepler service prior to each one. Records 'curl' payloads and emits key metric readings to stdout
