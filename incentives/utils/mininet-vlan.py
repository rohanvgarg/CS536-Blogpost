############################################################################
##
##     This file is part of Purdue CS 536.
##
##     Purdue CS 536 is free software: you can redistribute it and/or modify
##     it under the terms of the GNU General Public License as published by
##     the Free Software Foundation, either version 3 of the License, or
##     (at your option) any later version.
##
##     Purdue CS 536 is distributed in the hope that it will be useful,
##     but WITHOUT ANY WARRANTY; without even the implied warranty of
##     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##     GNU General Public License for more details.
##
##     You should have received a copy of the GNU General Public License
##     along with Purdue CS 536. If not, see <https://www.gnu.org/licenses/>.
##
#############################################################################

import json
import argparse
import os

# Shell helper function
def cmdline(command):
    return os.popen(command).read()
    

# Enable VLAN interfaces on the Mininet hosts
def enable(scripts_dir, host_dict):
    for host in host_dict:
        vlan_id = host_dict[host]['vlan']

        ip_address = cmdline('{0}/utils/mn-stratum/exec-script {1} "hostname -I"'.format(
            scripts_dir, host)).strip()
        cmdline('{0}/utils/mn-stratum/exec-script {1} "ifconfig {1}-eth0 inet 0 && \
                                                       vconfig add {1}-eth0 {2} && \
                                                       ifconfig {1}-eth0.{2} inet {3}"'.format(
            scripts_dir, host, vlan_id, ip_address))
    print ("VLAN enabled")


# Disable VLAN interfaces on the Mininet hosts
def disable(scripts_dir, host_dict):
    for host in host_dict:
        vlan_id = host_dict[host]['vlan']

        ip_address = cmdline('{0}/utils/mn-stratum/exec-script {1} "hostname -I"'.format(
            scripts_dir, host)).strip()
        cmdline('{0}/utils/mn-stratum/exec-script {1} "vconfig rem {1}-eth0.{2} && \
                                                       ifconfig {1}-eth0 inet {3}"'.format(
            scripts_dir, host, vlan_id, ip_address))
    print ("VLAN disabled")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Vlan Utility Script')
    parser.add_argument('--scripts-dir', help='Scripts Directory', required=True,
                        type=str, action="store")
    parser.add_argument('--enable', help='Vlan Enable', action="store_true", default=False)
    parser.add_argument('--disable', help='Vlan Disable', action="store_true", default=False)
    parser.add_argument('--topo-config', help='Topology Configuration File', required=True,
                        type=str, action="store")
    args = parser.parse_args()

    with open(args.topo_config, 'r') as infile:
        topo_config = json.loads(infile.read())

    host_dict = topo_config['host']

    if args.enable:
        enable(args.scripts_dir, host_dict)
    elif args.disable:
        disable(args.scripts_dir, host_dict)
