#!/usr/bin/python3
# Monitors power usage perf PDU Outlet using Redfish
# Writes JSON file in format ready for ingest in ElasticSearch
#
# Tested on RHEL 8.9 - Python 3.6.8
# DEPENDENCIES: # python3 -m pip install ??
#
# File 'universal_resources.py' required
# Redfish on PRO3X requires Firmware Version 4.0.21 and later
#
# USAGE:
# $ ./jsonJan30.py --ip 10.27.242.2 --interval 5 --outlet 3
##############################################################

##############################################################
# DICTIONARY Format - dicts initialized in main()
#
# testrun_dict = {
#     "start_ts": <curtime>,
#     "test_type": "power-usage",
#     "test_config": {
#         testcfg_dict{}
#     },
#     "test_results": {
#         testres_dict{}
#     },
#     "test_summary": {
#         "numsamples": <loopctr>,
#         "total_rt": <total_rt:.1f>,
#         "avg_pt": <avg_ptime:.2f>,
#         "avg_pwr": <avg_reading:.2f>
#     }
# }
###########
# testcfg_dict = {
#     "pdu_ip": <pduIP>,
#     "interval": <interval>,
#     "outlet": <outlet#>
# }
###########
# testres_dict = {
#     "sample": <sample#>,
#     "sample_data" = {
#         "timestamp": <curdate>,
#         "outlet": <outlet#>,
#         "power": <wattage>
#     }
# }


##############################################################
# IMPORTS
import argparse, logging, requests
import sys, time, statistics, datetime, json, io

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

def write_json(thedict, thefile):
    to_unicode = str
   # Write JSON file
    with io.open(thefile, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(thedict,
                          indent=4, sort_keys=False,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))
        outfile.write(to_unicode("\n"))

    print(f"Wrote file: {thefile}")

def init_rundict(the_curtime, the_type):
    # Initialize new dict{} for the test Run
    the_rundict = {}             # new empty dict

    the_rundict["start_ts"] = str(the_curtime.strip())
    the_rundict["test_type"] = str(the_type)

    return the_rundict

def init_cfgdict(the_pduIP, the_interval, the_outlet):
    # Initialize new dict{} for the test Config
    the_cfgdict = {}             # new empty dict

    the_cfgdict["pdu_ip"] = str(the_pduIP)
    the_cfgdict["interval"] = str(the_interval)
    the_cfgdict["outlet"] = str(the_outlet)

    return the_cfgdict

##def init_resdict(the_sample, the_ts, the_outlet, the_power):
def init_samdict(the_ts, the_outlet, the_power):
    # Initialize new dict{} for the test Results
    the_samdict = {}             # new empty dict

##    the_resdict["sample"] = int(the_sample)
    the_samdict["timestamp"] = str(the_ts.strip())
    the_samdict["outlet"] = str(the_outlet)
    the_samdict["power"] = float(the_power)

    return the_samdict

def init_sumdict(the_loopctr, the_runtime, the_avgPT, the_avgPWR):
    # Initialize new dict{} for the test Summary
    the_sumdict = {}             # new empty dict

    the_sumdict["numsamples"] = int(the_loopctr)
    the_sumdict["total_rt"] = float(the_runtime)
    the_sumdict["avg_ptime"] = float(the_avgPT)
    the_sumdict["avg_power"] = float(the_avgPWR)

    return the_sumdict

def get_curtime():
    # Provides a consistent method for recording the current timestamp
    the_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    return the_time

############
# BEGIN MAIN
def main():
    # Dictionaries
    testrun_dict = {}        # complete testrun results
    testcfg_dict = {}        # test Configuration
##    testres_dict = {}        # test Results (per Sample)
    results_list = []        # All Sample results - list of testres_dict(s)

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

    # Parse ARGs and define vars
    args = parseArgs(sys.argv[0])
    pdu_ip = args.ip                        # user provided
    pause_secs = args.interval              # user provided
    outlet_number = args.outlet             # user provided

    # Establish Connection using cmdline args
    conn, root = prepConn(args)

    # Get the collection of Outlets
    outlets_coll = get_collection(root, outlets_uri)
#    # Verify requested Outlet is available
#    numOutlets = len(outlets_coll.get_members())   # SLOW
#    if ( int(outlet_number) > int(numOutlets) ):
#        print('Invalid Outlet Number requested, exiting\n')
#        exit()

    theoutlet_uri = outlets_uri + '/' + outlet_number

    # Record Start Time
    start_curtime = get_curtime()

    # Basename for JSON output file
    outfilename = str("Results" + "_" + str(start_curtime))

    # Initialize Test Run and Test Config dicts
    testrun_dict = init_rundict(get_curtime(), "power-usage")
    testcfg_dict = init_cfgdict(pdu_ip, pause_secs, outlet_number)
    testrun_dict["test_config"] = testcfg_dict

    # Print opening message
    print(f"Monitoring Outlet number: {outlet_number}. Pausing {pause_secs} seconds between readings")
    print("Hit Control-C <SIGINT> to end\n")

    #######################################
    # Main Monitoring Loop - Record Samples
    begin_ts = time.perf_counter()

    try:
        while True:
            # Get Readings for the requested Outlet number
            # Measure time to probe and report in the Summary Report
            start_ts = time.perf_counter()
            svr_outlet = outlets_coll.get_member(theoutlet_uri, outlet_fields)
            end_ts = time.perf_counter()
            this_ptime = round((end_ts - start_ts), 2)
            this_curtime = get_curtime()
            outlet_id = svr_outlet.id
            power_W = svr_outlet.power
            print(f'  Outlet# {outlet_id} Sample# {loopctr}')  # DEBUG
##            print(f'    Timestamp:   {this_curtime}')
##            print(f'    ProbeTime:   {this_ptime} sec')
##            print(f'    Power:       {power_W} W\n')

            # Append to Summary stats for this Sample
            readings_list.append(float(power_W))
            ptimes_list.append(float(this_ptime))

            # Initialize Test Result dict for this Sample
            # Per Sample (sample_dict) is nested within Test Result dict
            testres_dict = {}        # test Results (per Sample)
            sample_dict = {}         # Sample data

            testres_dict["sample"] = int(loopctr)
            sample_dict = init_samdict(this_curtime, outlet_id, power_W)
            testres_dict["sample_data"] = sample_dict

            # Append this Sample's Test Result dict to results_list
            results_list.append(testres_dict)

            # Pause and incr loopctr
            time.sleep(int(pause_secs))
            loopctr = loopctr + 1

    except KeyboardInterrupt:
        print('Interrupted!')

    #######################################
    # Monitoring loop Interrupted - cleanup and write JSON Output
    final_ts = time.perf_counter()
    conn.close()

    # Calculate the Averages
    avg_ptime = round(statistics.mean(ptimes_list), 2)
    avg_reading = round(statistics.mean(readings_list), 2)
    total_rt = round((final_ts - begin_ts), 1)

    # Print the Summary Report
##    print('SUMMARY REPORT')
##    print(f'  Number of samples: {loopctr}')
##    print(f'  Sample interval(in sec): {pause_secs}')
##    print(f'  Total runtime(in sec): {total_rt}')
##    print(f'  Average Probe time(in sec): {avg_ptime}')
##    print(f'  Average Reading(in Watts): {avg_reading}')

    # Insert complete samples_dict{} into testrun_dict (final dict)
##    testrun_dict["test_results"] = samples_dict
    testrun_dict["test_results"] = results_list

    # Initialize Test Summary dict
    testsum_dict = init_sumdict(loopctr, total_rt, avg_ptime, avg_reading)
    testrun_dict["test_summary"] = testsum_dict

    # Write JSON output file
    write_json(testrun_dict, outfilename + ".json")

# END MAIN
##########

if __name__ == "__main__":
    main()

##############################################################
