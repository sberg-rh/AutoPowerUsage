#!/usr/bin/python3
#
# Tested on RHEL 8.9 - Python 3.6.8
# DEPENDENCIES: # python3 -m pip install sushy
#
# File 'universal_resources.py' required
# Redfish on PRO3X requires Firmware Version 4.0.21 and later
#
# USAGE:
# $ ./testJan29.py --ip 10.27.242.2 --interval 5 --outlet 3
##############################################################

##############################################################
# IMPORTS
import argparse, logging, requests, sys, time, statistics, datetime

# adding flush=True' to ensure print() runs unbuffered mode
import functools
print = functools.partial(print, flush=True)

import sushy
from sushy.resources import common, base

# As long as sushy does not provide specialized classes for PowerEquipment,
# generic classes UniversalResource and UniversalCollection may be used.
from universal_resources import get_collection, get_resource

##############################################################
# GLOBAL VARS

##############################################################
# FUNCTIONS
def parseArgs(argv0):
    # Parse ARGs and return them
    parser = argparse.ArgumentParser(argv0, 
            description = "Redfish PRO3X per Outlet Power Monitor")
    req_grp = parser.add_argument_group(title='Required Optional')
    req_grp.add_argument('--ip', required=True, type=str, 
                         help='ip address (Redfish Server)')
    req_grp.add_argument('--interval', required=True, type=str,
                         help='delay in seconds between Readings')
    req_grp.add_argument('--outlet', required=True, type=str,
                         help='PDU outlet number to monitor')
    parser.add_argument('--user', type=str, 
                        help='user name (Redfish Server)', default="labuser")
    parser.add_argument('--passwd', type=str, 
                        help='password (Redfish Server)', default="100Yard-")
    theArgs = parser.parse_args()

    return theArgs

def prepConn(the_args):
    # Prepare the Redfish connection

    # Squelch insecure warnings - using basic auth
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

    # Set log level
    LOG = logging.getLogger('sushy')
    LOG.setLevel(logging.WARNING)
    LOG.addHandler(logging.StreamHandler())

    # Verify Redfish Connection using basic authentication method
    theConn = sushy.auth.BasicAuth(username=the_args.user, 
                                      password=the_args.passwd)
    try:
        theRoot = sushy.Sushy(f'https://{the_args.ip}/redfish/v1',
                               auth=theConn, verify=False)
    except (sushy.exceptions.ConnectionError) as e:
        print("Connection Error, exiting...")
        print(e)
        exit()

    # Return the Connection and Root 
    return (theConn, theRoot)

# BEGIN MAIN
def main():
    # Dictionaries
    testrun_dict = {}        # complete testrun results
    testcfg_dict = {}        # test Configuration
    testres_dict = {}        # test Results

    # Define VARs
    loopctr = 1                   # counts number of samples
    this_ptime = 0                # Time to probe Redfish (in sec)
    total_rt = 0                  # Total runtime (in sec)
    readings_list = []            # wattage readings
    ptimes_list = []              # probe timing results
    outlets_uri = "/redfish/v1/PowerEquipment/RackPDUs/1/Outlets"
    outlet_fields = {
        "id": base.Field('Id'),
        "power": base.Field(['PowerWatts', 'Reading']),
##        "energy": base.Field(['EnergykWh', 'Reading']),
    }

    # Parse ARGs
    args = parseArgs(sys.argv[0])
    pause_secs = args.interval              # user provided
    outlet_number = args.outlet             # user provided

    # Establish Connection
    conn, root = prepConn(args)

    # Get the collection of Outlets
    outlets_coll = get_collection(root, outlets_uri)
#    # Verify requested Outlet is available
#    numOutlets = len(outlets_coll.get_members())   # SLOW
#    if ( int(outlet_number) > int(numOutlets) ):
#        print('Invalid Outlet Number requested, exiting\n')
#        exit()

    theoutlet_uri = outlets_uri + '/' + outlet_number

    # Print opening message
    print(f"Monitoring Outlet number: {outlet_number}. Pausing {pause_secs} seconds between readings")
    print("Hit Control-C to end\n")

    ################
    # Main Monitoring Loop
    begin_ts = time.perf_counter()

    try:
        while True:
            # Get Readings for the requested Outlet number
            # Measure time to probe and report in the Summary Report
            start_ts = time.perf_counter()
            svr_outlet = outlets_coll.get_member(theoutlet_uri, outlet_fields)
            end_ts = time.perf_counter()
            this_ptime = float(end_ts - start_ts)
            curtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            print(f'  Outlet# {svr_outlet.id} Sample# {loopctr}')
            print(f'    Timestamp:   {curtime}')
            print(f'    ProbeTime:   {this_ptime:.2f} sec')
            print(f'    Power:       {svr_outlet.power} W\n')
            # Add to Summary stats
            readings_list.append(float(svr_outlet.power))
            ptimes_list.append(float(this_ptime))
            # Pause and incr loopctr
            time.sleep(int(pause_secs))
            loopctr = loopctr + 1

    except KeyboardInterrupt:
        print('Interrupted!')

    # Monitoring loop Interrupted - cleanup and print Summary
    final_ts = time.perf_counter()
    conn.close()
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

# END MAIN

if __name__ == "__main__":
    main()

##############################################################
