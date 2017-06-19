#!/usr/bin/env python
import os
import re
import time
import argparse
import subprocess


parser = argparse.ArgumentParser(description='UDEV Remap Script -- Rename interfaces using UDEV Rules')

parser.add_argument('-v','--verbose', action='store_true',
                   help='enables verbose logging mode')
parser.add_argument('-a','--add',  nargs=2, action='append',
                   help='Specify a mac address followed by an interface')
parser.add_argument('-d','--delete', action='append',
                   help='Specify a mac address to be removed from the exising UDEV rules.')
parser.add_argument('-s','--show', action='store_true',
                   help='Show the existing UDEV Rules.')
parser.add_argument('-nv','--no-vagrant-interface', action='store_true',
                   help='Using this option will not create a vagrant interface during the application of rules.')
parser.add_argument('-nd','--no-vagrant-default', action='store_true',
                   help='Using this option will not create a vagrant default route when applying the re-map.')
parser.add_argument('-vm','--vagrant_mapping', action='store_true',
                   help='Using this option will create the mapping for the vagrant interface that happens automatically during the apply option.')
parser.add_argument("--vagrant-name", default='vagrant',
                   help='The name of the vagrant interface (default "vagrant")')
parser.add_argument("--apply", action='store_true',
                   help='Apply the remap as it has been provided.')


def is_mac(mac):
    if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$",mac.lower()):
        mac=mac.lower().replace("-",":")
    elif re.match("[0-9a-f]{12}$",mac.lower()):
        mac=mac.lower()
        mac=':'.join(mac[i:i+2] for i in range(0,len(mac),2))
    else:
        print " ### ERROR: MAC address --> " + str(mac) + " is not valid."
        exit(1)
    return mac

def show_rules():
    #Show Existing Rules
    print "#### UDEV Rules (/etc/udev/rules.d/70-persistent-net.rules) ####"
    if not os.path.isfile(udev_file):
        if verbose: print " >>> No Rules Present or File Does Not Exist <<<"
        return
    rules=subprocess.check_output(["cat",udev_file]).split('\n')
    for line in rules: print line

def parse_interfaces():
    #Parse Interfaces
    output=subprocess.check_output(["ip","link","show"]).split('\n')

    ifindex=""
    interface=""
    mac=""
    index_map={}

    #parse ip link show output for interface, ifindex and MAC
    for line in output:
        if re.match("^.*LOOPBACK.*$",line): continue #skip loopbacks
        elif re.match("^[0-9]+:.*$",line): #look for lines that start with an ifindex
            cut_line=line.split()
            ifindex=cut_line[0][:-1]
            interface=cut_line[1][:-1]
        elif re.match("^.*link/ether.*$",line): #look for lines that have link/ether
            cut_line=line.split()
            mac=cut_line[1]
            if verbose: print "interface: " + interface + " index: " + str(ifindex) + " mac: " + mac
            index_map[interface]={"index":ifindex,"mac":mac}

    for interface in index_map:
        if verbose: print "determining driver for interface: " + interface
        success=False
        #Method1
        try:
            ethtool_output=subprocess.check_output(["ethtool","-i",interface]).split('\n')
            driver = ethtool_output[0].split(":")[1][1:]
        except (subprocess.CalledProcessError, OSError), e:
            #Method 2
            try:
                driver=subprocess.check_output(["basename $(readlink /sys/class/net/"+interface+"/device/driver/module) > /dev/null 2>&1"],shell=True).replace("\n","")
            except subprocess.CalledProcessError, e:
                try:
                    driver=subprocess.check_output(["basename $(readlink /sys/class/net/"+interface+"/device/driver) > /dev/null 2>&1"],shell=True).replace("\n","")
                except subprocess.CalledProcessError, e:
                    print " ### ERROR Tried 3 methods to determine device driver. All Failed."
                    exit(1)
        index_map[interface]["driver"]=driver
        if verbose: print "interface: " + interface + " driver: " + driver
    return index_map

def delete_rule(mac):
    if not os.path.isfile(udev_file):
        if verbose: print "WARN: delete of rule not possible, udev file does not exist."
        return
    #Delete rule with MAC address
    if verbose:
        print ">>> BEFORE"
        show_rules()
    remove_rule=subprocess.check_output(["sed -i '/"+mac+"/d' " + udev_file],shell=True).split('\n')
    if verbose:
        print "<<< AFTER"
        show_rules()

def add_rule(mac,interface):
    index_map=parse_interfaces()
    print "  INFO: Adding UDEV Rule: " + mac + " --> " + interface
    mac_found=False
    for interface_1 in index_map:
        if index_map[interface_1]['mac'] == mac: mac_found = True
    if not mac_found:
        print " WARNING: this MAC address presently does not belong to any device on the system."

    if verbose:
        print "deleting any matching rules to be safe..."
    delete_rule(mac)

    with open("/etc/udev/rules.d/70-persistent-net.rules","a") as udev_file:
        udev_file.write("""ACTION=="add", SUBSYSTEM=="net", ATTR{address}==\"""" + mac +"\", NAME=\""+interface+"\", SUBSYSTEMS==\"pci\" \n")
    if verbose: show_rules()

def apply_remap():
    global just_vagrant
    index_map=parse_interfaces()
    if not just_vagrant:
        print "  INFO: Applying new UDEV Rules..."
    drivers={}
    lowest_index=""
    lowest_index_interface=""
    #Determine Driver and lowest index
    for interface in index_map:
        if lowest_index == "":
            lowest_index = index_map[interface]["index"]
            lowest_index_interface = interface
        elif int(index_map[interface]["index"]) < int(lowest_index):
            #Confirm that it is a physical interface and not a logical device
            try:
                subprocess.check_call(["udevadm info -a -p /sys/class/net/"+interface+""" | grep 'SUBSYSTEMS=="pci"' > /dev/null"""],shell=True)
            except subprocess.CalledProcessError, e:
                continue
            lowest_index = index_map[interface]["index"]
            lowest_index_interface = interface
        if verbose:
            print interface
            print "    lowest_index: + " + str(lowest_index) + "  --> " + str(lowest_index_interface)
            print "        index: " + index_map[interface]["index"]
            print "        mac: " + index_map[interface]["mac"]
            print "        driver: " + index_map[interface]["driver"]
        if index_map[interface]["driver"] not in drivers: drivers[index_map[interface]["driver"]]= True

    #Leave tunnel and bridge devices alone
    if "tun" in drivers: del drivers["tun"]
    if "bridge" in drivers: del drivers["bridge"]
    if "vxlan" in drivers: del drivers["vxlan"]
    if "bond" in drivers: del drivers["bond"]

    if verbose:
        print "lowest_index_interface: " + lowest_index_interface
        print "lowest_index: " + str(lowest_index)
        print drivers

    global vagrant_name
    if use_vagrant_interface:
        add_rule(index_map[lowest_index_interface]["mac"], vagrant_name)
        print "          FYI: "+lowest_index_interface + " will become the vagrant interface"

    if just_vagrant: return 0
    for driver in drivers:
        dead_drop=subprocess.check_output(["modprobe","-r",driver])


    dead_drop=subprocess.check_output(["udevadm","control","--reload-rules"])
    dead_drop=subprocess.check_output(["udevadm","trigger"])
    time.sleep(4)
    if use_vagrant_interface:
        dead_drop=subprocess.check_output(["ifup vagrant"],shell=True)
        time.sleep(1)
        if use_vagrant_default:
            dead_drop=subprocess.check_output(["ip route delete default dev vagrant"],shell=True)
    output=subprocess.check_output(["ip","link","show"]).split('\n')
    print "### PRESENT INTERFACES ###"
    for line in output:
        print line

def main():

    global verbose
    verbose=False
    global udev_file
    udev_file="/etc/udev/rules.d/70-persistent-net.rules"
    global use_vagrant_interface
    use_vagrant_interface=True
    global use_vagrant_default
    use_vagrant_default=True
    add=False
    show=False
    delete=False
    global just_vagrant
    just_vagrant=False
    global vagrant_name
    apply=False
    additions=[]
    removals=[]

    args = parser.parse_args()
    if args.verbose: verbose=args.verbose
    if args.add:
        add=True
        for mac,interface in args.add: additions.append([is_mac(mac),interface])
    if args.delete:
        delete=True
        for mac in args.delete: removals.append(is_mac(mac))
    if args.show: show=True
    if args.no_vagrant_interface: use_vagrant_interface=False
    if args.vagrant_mapping:
        apply=True
        just_vagrant=True
    if args.no_vagrant_default: use_vagrant_default=False
    if args.apply: apply=True
    vagrant_name = args.vagrant_name

    if verbose:
        print "Arguments:"
        print args

    if show: show_rules()
    elif delete == True:
        for mac in removals: delete_rule(mac)
    elif add == False: apply_remap()
    elif add == True:
        for mac,interface in additions: add_rule(mac,interface)


if __name__ == "__main__":
    main()

exit(0)
