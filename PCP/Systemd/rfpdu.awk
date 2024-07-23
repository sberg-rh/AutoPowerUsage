#!/usr/bin/awk -f

/ApparentVA/ {printf "watts %.1f\n", $2}

