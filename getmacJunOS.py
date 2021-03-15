#!/usr/bin/python3

from netmiko import juniper

import device_info as dinf
from netmiko import ConnectHandler
host = {
    'device_type' : 'juniper_junos',
    'host': dinf.host,
    'username': dinf.username,
    'password': dinf.password,
}

ncon = ConnectHandler(**host)
res = ncon.send_command('show ethernet-switching table', use_textfsm = True)
res2 = ncon.send_command('show ethernet-switching interface | match "tagged" | match e- | except "untagged"')

tagged_interfaces = []

# Add trunk interfaces from the res2 to the list aka "tagged_interfaces"
for line in res2.split('\n'):
    if len(line) > 1:
        tagged_interfaces.append(str(line).split()[0])

# work with data from the res. Exclude row where a field "logical_interfacse" in the tagged_interfaces
for row in res:
    if row['logical_interface'] not in tagged_interfaces:
        print (row)

