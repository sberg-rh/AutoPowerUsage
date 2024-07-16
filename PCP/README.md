# Files and scripts useful for Perf Co-Pilot and power usage metrics
> Two new systemd services
> 1) rfchassis - retrieves Redfish metrics from Chassis endpoint
> 2) rfpdu - retrieves Redfish metrics from smartPDUs
>
> Each of these files will need edits specific to your environment
>   * rfchassis.envfile
>   * rfpdu.envfile
>
All these files should be put under /etc/systemd/system. \
Then load the new services and activate them:  
* 'sudo systemctl daemon-reload'  
* 'sudo systemctl start|stop|enable|disable ...'  
