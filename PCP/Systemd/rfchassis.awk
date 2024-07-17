#!/usr/bin/awk -f

/PowerConsumedWatts/ {printf "watts chassis %.1f\n", $2}

