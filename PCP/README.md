# Files and scripts useful for Perf Co-Pilot and power usage metrics
## Systemd/
> Two new systemd services
> 1) rfchassis - retrieves Redfish metrics from Chassis endpoint
> 2) rfpdu - retrieves Redfish metrics from smartPDUs  
**see Systemd/README.md**  
 
## URL Files
> These files extend the openmetrics PDMA to access the Redfish metric files, which
> are written by the two new systemd services.
> The URL files should be copied to /var/lib/pcp/pmdas/openmetrics/config.d
> 1) RFchassis.url
> 2) RFpdu1.url
> 3) RFpdu2.url
**These can be verified using '$pminfo openmetrics | grep watts'
