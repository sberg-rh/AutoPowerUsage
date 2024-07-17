#!/usr/bin/awk -f

/ApparentVA/ {printf "watts %s %.1f\n", id, $2}

