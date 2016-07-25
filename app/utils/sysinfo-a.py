#!/usr/bin/python
# coding:utf-8
# author: rongjunfeng

import json
import subprocess
import psutil
import socket
import time
import re
import platform
import requests



device_white = ['eth1', 'eth2', 'eth3', 'bond0', 'bond1']

def get_hostname():
    return socket.gethostname()

def get_meminfo():
    ret = 0
    with open("/proc/meminfo") as f:
        for line in f:
            if "MemTotal" in line:
                ret = int(line.split()[1])
                break
    return ret / 1024

def get_device_info():
    ret = []
    for device, info in psutil.net_if_addrs().iteritems():
        if device in device_white:
            device_info = {'device': device}
            for snic in info:
                if snic.family == 2:
                    device_info['ip'] = snic.address
                elif snic.family == 17:
                    device_info['mac'] = snic.address
            ret.append(device_info)
    return ret

def get_cpuinfo():
    ret = {"cpu": '', 'num': 0}
    with open('/proc/cpuinfo') as f:
        for line in f:
            line_list = line.strip().split(':')
            key = line_list[0].rstrip()
            if key == "model name":
                ret['cpu'] = line_list[1].lstrip()
            if key == "processor":
                ret['num'] += 1
    return ret

def get_disk():
    #cmd = """/sbin/fdisk -l|grep Disk|egrep -v 'identifier|mapper|Disklabel'"""
    cmd = """/sbin/fdisk -l|grep Platte|egrep -v 'identifier|mapper|Disklabel'"""
    disk_data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    partition_size = []
    for dev in disk_data.stdout.readlines():
        size = int(dev.strip().split(', ')[1].split()[0]) / 1024 / 1024 / 1024
        partition_size.append(str(size))
    return " + ".join(partition_size)

def get_Manufacturer():
    cmd = """/usr/sbin/dmidecode | grep -A6 'System Information'"""
    ret = {}
    manufacturer_data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in manufacturer_data.stdout.readlines():
        if "Manufacturer" in line:
            ret['manufacturers'] = line.split(': ')[1].strip()
        elif "Product Name" in line:
            ret['server_type'] = line.split(': ')[1].strip()
        elif "Serial Number" in line:
            ret['st'] = line.split(': ')[1].strip().replace(' ','')
        elif "UUID" in line:
            ret['uuid'] = line.split(': ')[1].strip()
    return ret
    #return manufacturer_data.stdout.readline().split(': ')[1].strip()

# 出厂日期
def get_rel_date():
    cmd = """/usr/sbin/dmidecode | grep -i release"""
    data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    date = data.stdout.readline().split(': ')[1].strip()
    return re.sub(r'(\d+)/(\d+)/(\d+)',r'\3-\1-\2',date)  

def get_os_version():
    return " ".join(platform.linux_distribution())

def get_innerIp(ipinfo):
    inner_device = ["eth1", "bond0"]
    ret = {}
    for info in ipinfo:
        if info.has_key('ip') and info.get('device', None) in inner_device:
            ret['inner_ip'] = info['ip']
            ret['mac_address'] = info['mac']
            return  ret
    return {}
    

def run():
    data = {}
    data['hostname'] = get_hostname()
    device_info = get_device_info()
    data.update(get_innerIp(device_info))
    data['ipinfo'] = json.dumps(device_info)

    cpuinfo = get_cpuinfo()
    data['server_cpu'] = "{cpu} {num}".format(**cpuinfo)
    data['server_disk'] = get_disk()
    data['server_mem'] = get_meminfo()
    data.update( get_Manufacturer())
    data['manufacture_date'] = get_rel_date()
    data['os'] = get_os_version()
    #if "VMware" in data['manufacturers']:
    if 'VirtualBox' == data['server_type']:
        data['vm_status'] = 0
    else:
        data['vm_status'] = 1
    send(data)

def send(data):
    url = "http://192.168.1.220:5000/resources/server/report/"
    r = requests.post(url, data=data)


if __name__ == "__main__":
    run()

