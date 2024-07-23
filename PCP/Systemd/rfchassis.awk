#!/usr/bin/awk -f

/PowerConsumedWatts/ {printf "watts %.1f\n", $2}

