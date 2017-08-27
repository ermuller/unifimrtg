# unifimrtg
poll unifi user stats for mrtg

You'll want to customize the global settings at the top (device list,
community, mib path).  You'll also need to make sure you have the UBNT MIB
files available in your local snmp search path.


You can use it like this in your mrtg config:
```
Target[wifi_clients]: `/usr/local/bin/unifiusers.py --mrtg`
Options[wifi_clients]: gauge, nopercent, growright
MaxBytes[wifi_clients]: 32
YLegend[wifi_clients]: WiFi Clients by Band
ShortLegend[wifi_clients]: clients
Legend1[wifi_clients]: Active WiFi Clients by Band
LegendI[wifi_clients]: Clients 5GHz:
LegendO[wifi_clients]: Clients 2.4GHz:
Title[wifi_clients]: Clients on WiFi by Bands
```

