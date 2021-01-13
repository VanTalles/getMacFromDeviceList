#!/usr/bin/python3

import pynetbox
from netmiko import ConnectHandler
import argparse
import json


def CreateParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--host', required = True, help = 'device IP')
    parser.add_argument('-u','--username',required = True , help = 'username to connect to your device ')
    parser.add_argument('-p','--password',required = True, help = 'password to connect to your device')
#    parser.add_argument('-nbt','--token',required = True, help = 'netbox read token')

    return parser


def getMacTable(host,username,password,dev_type):
    host = {
        'ip' : host,
        'device_type' : dev_type,
        'username' : username,
        'password' : password,
    }
    net_connect = ConnectHandler(**host)
    mactable = net_connect.send_command('show mac address-table',use_textfsm = True)
    return mactable
 

if __name__ == "__main__":
    parser = CreateParser()
    prs = parser.parse_args()

    res = getMacTable(prs.host,prs.username,prs.password,'cisco_ios')
    print (res)
    

