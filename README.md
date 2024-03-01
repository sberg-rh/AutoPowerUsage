# PowerUsage
Collection of scripts for monitoring system power usage  
Comments in Python code include USAGE details  

## POWER SCRIPTS
rfChassis.py - probes Redfish URI /redfish/v1/Chassis for PowerConsumedWatts property  
PRO3Xmultiple.py - probes Redfish URI /redfish/v1/PowerEquipment for per Outlet Wattage used  
universal_resources.py - include script with functiond definitions for PRO3Xmultiple.py  
<br>
Ansible/ - folder with playbook and supporting scripts. Coordinates Power Script and Workload processes  
