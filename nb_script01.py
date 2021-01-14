#!/usr/bin/python3 

import pynetbox
import json
import argparse
import socket
from netmiko import ConnectHandler
import csv

def CreateParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-nb','--host', required = True, help = 'NetBOX instance url')
    parser.add_argument('-nbt','--token',required = True , help = 'token')
    parser.add_argument('-u','--username',required = True , help = 'user')
    parser.add_argument('-p','--password',required = True , help = 'pass')
    return parser


def getIP(ip_addr):
   if ip_addr:
      return ip_addr.split('/')[0]
   else:
      return False

def check_allow(ip_addr,port):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    if sock.connect_ex((str(ip_addr),port)) == 0:
        return True
    else:
        return False

def getConnectDriver(vendor,protocol):
    if vendor.lower() == 'cisco systems':
        if protocol.lower() == 'telnet':
             return 'cisco_ios_telnet'
        else:
             return 'cisco_ios'
    if vendor.lower() == 'allied':
        if protocol.lower() == 'ssh':
             return 'cisco_ios'
    if vendor.lower() == 'juniper':
        return 'juniper'
    return False


def getNetmikoDriver(nb,dev_id,vend):
    dev_srvc = nb.ipam.services.filter(device_id = dev_id)
    if not dev_srvc:
        res = {'device_type': getConnectDriver(vend,'ssh'), 'port' : 22,}
    for svc in dev_srvc:
       if svc.name == 'SSH':
           res = {'device_type': getConnectDriver(vend,'ssh'), 'port' : svc.ports[0],}
           return res       
       if svc.name == 'TELNET':
           res = {'device_type': getConnectDriver(vend,'telnet'), 'port' : svc.ports[0],}

    if res:
        return res
    else:
        res = {'device_type': getConnectDriver(vend,'ssh'), 'port' : 22,}
        return res



def getMacTable(host,vend):
    if vend.lower() == 'cisco systems':
        command = 'show mac addr'
    if vend.lower() == 'allied telesys':
        command = 'show mac addr'
    if vend.lower() == 'juniper':
        command = 'show ethernet-switching table brief'

    try:
        host1 = host
        if host['device_type'] == 'cisco_ios_telnet':      
            net_conn = ConnectHandler(**host1,fast_cli = False)
        else:
             net_conn = ConnectHandler(**host1)
        res = net_conn.send_command(command,use_textfsm = True)
    except:
        print ('Connect false')
        res = False
    return res    


if __name__ == "__main__":
    parser = CreateParser()
    prs = parser.parse_args()

    NB_URL = prs.host
    NB_TOKEN = prs.token
    
    username = prs.username
    password = prs.password
    
    nb = pynetbox.api(NB_URL, token = NB_TOKEN)
   
    devs = nb.dcim.devices.filter(role = 'access-switch',tag = TAG)
    csv_dict = []
    for dev in devs:
        print ('='*50)
        print (dev)
        print ('='*50)
        host_ip = getIP(dev.primary_ip.address)
        dev_port = getNetmikoDriver(nb,dev.id,dev.device_type.manufacturer.name)
        host = {
             'device_type' : dev_port['device_type'],
             'port' : dev_port['port'],
             'host': getIP(dev.primary_ip.address),
             'username' : username,
             'password' : password,
        }
        res = getMacTable(host,dev.device_type.manufacturer.name)
        if res:  
            for row in res:
               cute_mac = row['destination_address'].replace('.','').replace(':','')
               list = {
                   'device': dev,
                   'device_ip': getIP(dev.primary_ip.address),
                   'mac': row['destination_address'],
                   'port': row['destination_port'],
                   'vlan': row['vlan'],
                   'cute_mac': cute_mac,
                   'cute_mac2': cute_mac[2::],
               }
               csv_dict.append(list)
            print ('OK')
        else:
           print ('No data')    
    
    #print (csv_dict)
    field_names = ['device','device_ip','mac','port','vlan','cute_mac','cute_mac2']
    with open('macs.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(csv_dict)

