# Systemd services which provide Redfish power usage metrics to Perf Co-Pilot
> Two new systemd services
> 1) rfchassis - retrieves Redfish metrics from Chassis endpoint
> 2) rfpdu - retrieves Redfish metrics from smartPDUs
>
> Each of these files will need edits specific to your environment
>   * rfchassis.envfile
>   * rfpdu.envfile
>
All these files should be moved under /etc/systemd/system, \
and owned by root. Also be sure to set '*.awk' as executable:
* 'sudo chmod 755 *.awk'
>  
Then load the new services and activate them:  
* 'sudo systemctl daemon-reload'  
* 'sudo systemctl start|stop rfchassis.timer'
* 'sudo systemctl start|stop rfpdu.timer'
>
> To verify:  
* 'fswatch -t /tmp/openmetrics_RFchassis.txt'  
* 'fswatch -t /tmp/openmetrics_RFpdu.txt'  
