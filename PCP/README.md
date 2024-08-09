# Files and scripts useful for Perf Co-Pilot and power usage metrics
 
**Openmetrics PMDA Files**
> These files extend the openmetrics PMDA to access the Redfish power usage
> metrics, from Chassis and Smart PDUs
> 
> The values in **'RFvars.cfg'** must be set for your environment:
> 1) Redfish device IP addresses
> 2) Redfish server User account name and password
> 3) Redfish URLs for both Chassis Power and Smart PDU readings 
> 
> The files should be copied to /var/lib/pcp/pmdas/openmetrics/config.d
> and the '.sh' files should be made executable
>    
**These can be verified and Readings viewed**  
> $ pminfo openmetrics | grep watts  
> $ pmrep openmetrics.RFchassis openmetrics.RFpdu1 openmetrics.RFpdu2  
