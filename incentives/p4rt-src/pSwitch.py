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
import contextlib
import p4runtime_sh.shell as p4sh
from p4.v1 import p4runtime_pb2 as p4rt

###############################################################################
# Default parameters
###############################################################################

# Relative path of the configuration, logs, and topo directories
CFG_DIR = 'cfg'
LOGS_DIR = 'logs'

# Bridge ID and number of ports
BRIDGE_ID = 1
BRIDGE_CPU_PORT = 255

# Logs threshold
NUM_LOGS_THRESHOLD = 10

# Ethernet type values (https://en.wikipedia.org/wiki/EtherType)
ETH_TYPE_ARP = 0x0806
ETH_TYPE_VLAN = 0x8100


###############################################################################
# Helper functions
###############################################################################

# MAC address in bytes to string
def mac2str(mac):
    return ':'.join('{:02x}'.format(b) for b in mac)


###############################################################################
# Multicast group functions
###############################################################################

# Create a multicast group entry
def InstallMcastGrpEntry(mcast_group_id, bridge_ports):
    mcast_entry = p4sh.MulticastGroupEntry(mcast_group_id)
    for port in bridge_ports:
        mcast_entry.add(port)
    mcast_entry.insert()

# Delete a multicast group entry
def DeleteMcastGrpEntry(mcast_group_id):
    mcast_entry = p4sh.MulticastGroupEntry(mcast_group_id)
    mcast_entry.delete()


###############################################################################
# Packet processing functions
###############################################################################

# Process incoming packets
def ProcPacketIn(switch_name, logs_dir, num_logs_threshold):
    try:
        num_logs = 0
        while True:
            rep = p4sh.client.get_stream_packet("packet", timeout=1)
            if rep is not None:
                # Read the raw packet
                payload = rep.packet.payload
                
                 # Parse Metadata
                ingress_port_in_bytes = rep.packet.metadata[0].value
                ingress_port = int.from_bytes(ingress_port_in_bytes, "big")


                print("Got packet from ", ingress_port)


            '''
            # Log the Ethernet address to port mapping
            num_logs += 1
            if num_logs == num_logs_threshold:
                num_logs = 0
                with open('{0}/{1}-table.json'.format(logs_dir, switch_name), 'w') as outfile:
                    with contextlib.redirect_stdout(outfile):
                        p4sh.TableEntry('MyIngress.switch_table').read(lambda te: print(te))
                print(
                    "INFO: Log committed to {0}/{1}-table.json".format(logs_dir, switch_name))
            '''
    except KeyboardInterrupt:
        return None


###############################################################################
# Main 
###############################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Switch Script')
    parser.add_argument('--grpc-port', help='GRPC Port', required=True,
                        type=str, action="store", default='50001')
    parser.add_argument('--topo-config', help='Topology Configuration File', required=True,
                        type=str, action="store")
    args = parser.parse_args()

    # Create a bridge name postfixed with the grpc port number
    if (args.grpc_port == '50001'):
        switch_name = 'pLeft-{0}'.format(args.grpc_port)
    else:
        switch_name = 'pRight-{0}'.format(args.grpc_port)


    # Get Multicast/VLAN ID to ports mapping
    with open(args.topo_config, 'r') as infile:
        topo_config = json.loads(infile.read())

    mcast_group_id = topo_config['switch'][args.grpc_port]['mcast']['id']
    mcast_group_ports = topo_config['switch'][args.grpc_port]['mcast']['ports']

    vlan_id_to_ports_map = {}
    for vlan_id, ports in topo_config['switch'][args.grpc_port]['vlan_id_to_ports'].items():
        vlan_id_to_ports_map[int(vlan_id)] = ports

    # Setup the P4Runtime connection with the bridge
    p4sh.setup(
        device_id=BRIDGE_ID, grpc_addr='127.0.0.1:{0}'.format(args.grpc_port), election_id=(0, 1),
        config=p4sh.FwdPipeConfig(
            '{0}/{1}-p4info.txt'.format(CFG_DIR, switch_name),  # Path to P4Info file
            '{0}/{1}.json'.format(CFG_DIR, switch_name)  # Path to config file
        )
    )

    print("Switch Started @ Port: {0}".format(args.grpc_port))
    print("Press CTRL+C to stop ...")

    # Install broadcast rule
    InstallMcastGrpEntry(mcast_group_id, mcast_group_ports + [BRIDGE_CPU_PORT])

    # Install VLAN rules
    with contextlib.redirect_stdout(None):  # A hack to suppress print statements 
        # within the table_entry.match get/set objects




        ##################################################################################
        # Install VLAN Rules - Begins ####################################################
        ##################################################################################

        # TODO: Install flow entries to let packets traverse only those egress ports that 
        # match its VLAN ID.
        # Install flow entries in the VLAN table (as specified in the P4 program):
        #   - Match fields: `standard_metadata.egress_port`, VLAN ID
        #   - Action: `MyEgress.noop`
        #
        # NOTE: please follow p4rt-src/bridge.py for a reference example on how to install
        # table entries.

        '''
        #### ADD YOUR CODE HERE ... ####
        for vid in vlan_id_to_ports_map:
            for port in vlan_id_to_ports_map[vid]:
                table_entry = p4sh.TableEntry('MyEgress.vlan_table')(action='MyEgress.noop')
                table_entry.match['meta.vid'] = str(vid)
                table_entry.match['standard_metadata.egress_port'] = str(port)
                table_entry.insert()
        '''


        ##################################################################################
        # Install VLAN Rules - Ends ######################################################
        ##################################################################################



    '''
    with open('{0}/{1}-vlan-table.json'.format(LOGS_DIR, switch_name), 'w') as outfile:
        with contextlib.redirect_stdout(outfile):
            p4sh.TableEntry('MyEgress.vlan_table').read(lambda te: print(te))
        print("INFO: Log committed to {0}/{1}-vlan-table.json".format(LOGS_DIR, switch_name))
    '''
    # Start the packet-processing loop
    ProcPacketIn(switch_name, LOGS_DIR, NUM_LOGS_THRESHOLD)

    print("Switch Stopped")

    # Delete broadcast rule
    DeleteMcastGrpEntry(mcast_group_id)

    # Delete VLAN rules
    with contextlib.redirect_stdout(None):  # A hack to suppress print statements 
        # within the table_entry.match get/set objects




        ##################################################################################
        # Delete VLAN Rules - Begins #####################################################
        ##################################################################################

        # TODO: Delete VLAN flow entries.
        # Delete flow entries from the VLAN table (as specified in the P4 program):
        #   - Match fields: `standard_metadata.egress_port`, VLAN ID
        #   - Action: `MyEgress.noop`
        #
        # NOTE: please follow p4rt-src/bridge.py for a reference example on how to install
        # table entries.


        #### ADD YOUR CODE HERE ... ####

        p4sh.TableEntry('MyEgress.vlan_table').read(function=lambda x: x.delete())


        ##################################################################################
        # Delete VLAN Rules - Ends #######################################################
        ##################################################################################




    # Close the P4Runtime connection
    p4sh.teardown()
