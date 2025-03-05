#!/bin/bash
# Extends openmetrics-pmda to record R-Car S4 power readings
# Requires vars in 'auto_vars.cfg' to be configured for URLs and Credentials

# VARs - import from CFG file
#source /var/lib/pcp/pmdas/openmetrics/config.d/auto_vars.cfg

# Get Readings - R-Car S4
cat /sys/class/thermal/thermal_zone1/temp | \
    awk -v str="$rcar4_metric" '$0~str {
        print("# HELP CPU Temperature DegreesC")
        print("# TYPE hardware gauge")
        printf("DegreesC %.2f\n", $1 / 1000)
}'
