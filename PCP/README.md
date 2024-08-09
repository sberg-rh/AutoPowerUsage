# Files and scripts useful for Perf Co-Pilot and power usage metrics
 
**Openmetrics PMDA Files**
> These files extend the openmetrics PMDA to access the Redfish power usage
> metrics, freom Chassis and Smart PDUs
> which
> are written by the two new systemd services.
> The values in 'RFvars.cfg' must be set for your environment:
> 1) Redfish device IP addresses
> 2) Redfish server User account name and password
> 3) Redfish URLs for both Chassis Power and Smart PDU readings 
> 
> The files should be copied to /var/lib/pcp/pmdas/openmetrics/config.d
> and the '.sh' files should be executable
>    
**These can be verified using '$pminfo openmetrics | grep watts'
