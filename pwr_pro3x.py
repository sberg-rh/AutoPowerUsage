#!/usr/bin/python3

import argparse, logging, requests, sys, time, statistics

# adding flush to ensure print() runs unbuffered mode
import functools
print = functools.partial(print, flush=True)

import sushy
from sushy.resources import common, base

# As long as sushy does not provide specialized classes for PowerEquipment,
# generic classes UniversalResource and UniversalCollection may be used.
# File 'universal_resources.py' required
from universal_resources import get_collection, get_resource

parser = argparse.ArgumentParser(sys.argv[0], description = "Redfish PRO3X per Outlet Power Monitor")
req_grp = parser.add_argument_group(title='Required Optional')
req_grp.add_argument('--ip', required=True, type=str, help='ip address')
req_grp.add_argument('--interval', required=True, type=str, help='delay in seconds between Readings')
req_grp.add_argument('--outlet', required=True, type=str, help='outlet number to monitor')
parser.add_argument('--user', type=str, help='user name', default="labuser")
parser.add_argument('--passwd', type=str, help='password', default="100Yard-")
args = parser.parse_args()

# Squelch insecure warnings - using basic auth
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Set log level
LOG = logging.getLogger('sushy')
LOG.setLevel(logging.WARNING)
LOG.addHandler(logging.StreamHandler())

# Use basic authentication method:
basic_auth = sushy.auth.BasicAuth(username=args.user, password=args.passwd)
try:
    root = sushy.Sushy(f'https://{args.ip}/redfish/v1', auth=basic_auth, verify=False)
except (sushy.exceptions.ConnectionError) as e:
    print("Connection Error, exiting...")
    print(e)
    exit()

# DEBUG get firmware version from the single manager
# Redfish on PRO3X requires Firmware Version 4.0.21 and later
##mgr_inst = root.get_manager()
##print("Firmware Version: ", mgr_inst.firmware_version)

pause_secs = args.interval              # user provided
outlets_uri = "/redfish/v1/PowerEquipment/RackPDUs/1/Outlets"
outlet_number = args.outlet             # user provided
outlet_fields = {
    "id": base.Field('Id'),
    "power": base.Field(['PowerWatts', 'Reading']),
    "energy": base.Field(['EnergykWh', 'Reading']),
}

print(f"Monitoring Outlet number: {outlet_number}. Pausing {pause_secs} seconds between readings")
print("Hit Control-C to end\n")

# Start by poking Redfish with the OUTLETS_URI
# Get the collection of Outlets - should have 36 members/Outlets
outlets_coll = get_collection(root, outlets_uri)
theoutlet_uri = outlets_uri + '/' + outlet_number

# Main Loop
loopctr = 1                   # counts number of samples
this_ptime = 0                # Time to probe Redfish (in sec)
total_rt = 0                  # Total runtime (in sec)
readings_list = []            # wattage readings
ptimes_list = []              # probe timing results

begin_ts = time.perf_counter()
try:
    while True:
        # Get Readings for the requested Outlet number
        # Measure time to probe and report in the Summary Report
        start_ts = time.perf_counter()
        svr_outlet = outlets_coll.get_member(theoutlet_uri, outlet_fields)
        end_ts = time.perf_counter()
        this_ptime = float(end_ts - start_ts)
##        print("  Sample#", loopctr)
        print("  Outlet#", svr_outlet.id, "Sample#", loopctr)
        print("    Power:   ", svr_outlet.power, "W\n")
        readings_list.append(float(svr_outlet.power))
        ptimes_list.append(float(this_ptime))
##        print("    Energy:   ", svr_outlet.energy, "kWh\n")
        time.sleep(int(pause_secs))
        loopctr = loopctr + 1
except KeyboardInterrupt:
    print('Interrupted!')

## REALLY Slow approach
##for outlet in outlets_coll.get_members(outlet_fields)[:4]:
##    print("    Outlet#", outlet.id)
##    print("      Power:   ", outlet.power, "W")
##    print("      Energy:  ", outlet.energy, "kWh")

final_ts = time.perf_counter()
basic_auth.close()
# Calculate the averages
avg_ptime = statistics.mean(ptimes_list)
avg_reading = statistics.mean(readings_list)
total_rt = float(final_ts - begin_ts)

# Print the Summary Report
print('SUMMARY REPORT')
print(f'  Number of samples: {loopctr}')
print(f'  Sample interval(in sec): {pause_secs}')
print(f'  Total runtime(in sec): {total_rt:.1f}')
print(f'  Average Probe time(in sec): {avg_ptime:.2f}')
print(f'  Average Reading(in Watts): {avg_reading:.2f}')
