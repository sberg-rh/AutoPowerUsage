#!/bin/bash
# Extends openmetrics-pmda to record R-Car S4 power readings
# Requires vars in 'auto_vars.cfg' to be configured for URLs and Credentials

# VARs - import from CFG file
source /var/lib/pcp/pmdas/openmetrics/config.d/auto_vars.cfg

# Get Readings - R-Car S4
ssh root@renesas-rcar-s4-sidekick-$rcar4_number.auto.eng.bost2.dc.redhat.com "stdbuf -oL powermeter -p /dev/i2c-1 | \
    awk -v str="$rcar4_metric" '$0~str {
        print("# HELP Rensas R-Car S4 watts")
        print("# TYPE hardware gauge")
        printf("watts %.1f\n", $3)
}'"
