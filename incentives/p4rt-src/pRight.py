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

# Flows and logs threshold
NUM_ENTRIES_THRESHOLD = 100
NUM_LOGS_THRESHOLD = 10

# Ethernet type values (https://en.wikipedia.org/wiki/EtherType)
# - ARP: 0x0806
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
def ProcPacketIn(switch_name, mcast_group_id,
                 eth_to_port_map, num_entries_threshold, 
                 vlan_id_to_ports_map,
                 logs_dir, num_logs_threshold):


    try:
        flag = 0
        logs_count = 0
        while True:
            rep = p4sh.client.get_stream_packet("packet", timeout=1)
            if rep is not None:
                # Read the raw packet
                payload = rep.packet.payload



                
                ##################################################################################
                # Packet parsing logic - Begins ##################################################
                ##################################################################################
                
                # TODO: For each incoming packet, read the following fields:
                # - ingress port
                # - Ethernet header (source/destination MAC addresses and type)
                # - VLAN header (if present)
                
                # NOTE: please follow p4rt-src/bridge.py for a reference example


                #### ADD YOUR CODE HERE ... ####
                # - ingress port
                ingress_port_in_bytes = rep.packet.metadata[0].value
                ingress_port = int.from_bytes(ingress_port_in_bytes, "big")
                
                # - Ethernet header (source/destination MAC addresses and type)

                dst_mac_in_bytes = payload[0:6]
                dst_mac = mac2str(dst_mac_in_bytes)
                src_mac_in_bytes = payload[6:12]
                src_mac = mac2str(src_mac_in_bytes)


                eth_type_bytes = payload[12:14]
                
                arp  = False
                vlan = False

                if int.from_bytes(eth_type_bytes,'big') == ETH_TYPE_ARP:
                    arp = True
                elif int.from_bytes(eth_type_bytes,'big') == ETH_TYPE_VLAN:
                    # - VLAN header (if present)
                    vlan = True
                    print("payload[14:15][0] = ",payload[14:15][0], "payload[14:15]",payload[14:15])
                    vlan_id_bytes = bytes ([payload[14:15][0] & b'\x0f'[0] , payload[15:16][0] & b'\xff'[0]])
                    
                    
                    eth_type_bytes = payload[16:18]
                    if int.from_bytes(eth_type_bytes,'big') == ETH_TYPE_ARP:
                        arp = True



                ##################################################################################
                # Packet parsing logic - Ends ####################################################
                ##################################################################################


                '''

                # Decrement table entry's counter
                del_mac_list = []
                for mac in eth_to_port_map:
                    eth_to_port_map[mac]['count'] -= 1
                    if eth_to_port_map[mac]['count'] == 0:
                        print("INFO: Flow entry deleted: mac={0} port={1}".format(
                            mac, eth_to_port_map[mac]['port']))
                        del_mac_list.append(mac)

                for mac in del_mac_list:
                    del eth_to_port_map[mac]
                '''



                ##################################################################################
                # Learning switch logic - Begins #################################################
                ##################################################################################

                # TODO: For each packet, carryout the following tasks:
                # - If the packet is an ARP request, 
                #   - learn the Ethernet address to port mapping by updating the `eth_to_port_map` 
                #     table with the new source MAC and ingress port pair
                #   - broadcast the ARP packet; however, make sure only those hosts belonging to 
                #     a partuclar VLAN receive the packet (use `vlan_id_to_ports_map` table 
                #     for this)
                # - Else, for any other packet,
                #   - forward it using the learned Ethernet address to port mapping (i.e., 
                #     `eth_to_port_map` table)
                #   - if no mapping exists, drop the packet (we haven't received an ARP request for 
                #     it yet)

                
                #### ADD YOUR CODE HERE ... ####
                print("Ingress port type is:", type(ingress_port))

                if vlan:
                    print("Its VLAN", vlan_id_bytes, int.from_bytes(vlan_id_bytes,'big'))
                    group_id_in_bytes = vlan_id_bytes
                else:
                    print("Its not VLAN")
                    group_id_in_bytes = mcast_group_id.to_bytes(2, byteorder='big')
                if arp:
                    print("ARP")
                    if dst_mac in eth_to_port_map and eth_to_port_map[dst_mac]["port"] != ingress_port:
                        print("I know what to do")
                        egress_port_in_bytes = eth_to_port_map[dst_mac]["port"].to_bytes(2, byteorder='big')
                        ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                                             
                        eth_to_port_map[dst_mac]['count'] = num_entries_threshold

                    else:
                        print("I dont know so I broadcast")
                        ProcPacketOut(payload, group_id_in_bytes, ingress_port_in_bytes)
    
                    if src_mac not in eth_to_port_map:
                        print("this is where everithing stops")
                        eth_to_port_map[src_mac] = {'port': ingress_port,
                                            'count': num_entries_threshold}
                else:
                    if ingress_port == 2 or ingress_port == 3:
                        port = 1
                        egress_port_in_bytes = port.to_bytes(2, byteorder='big')
                        ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                    elif ingress_port == 1:
                        port = 4
                        egress_port_in_bytes = port.to_bytes(2, byteorder='big')
                        ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                    elif dst_mac in eth_to_port_map:
                        egress_port_in_bytes = eth_to_port_map[dst_mac]["port"].to_bytes(2, byteorder='big')
                        ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                        #eth_to_port_map[dst_mac]['count'] = num_entries_threshold
                '''

                if routing == 'OSPF' or routing=='SELFISH':
            
                    if arp == False:
                        if dst_mac in eth_to_port_map and eth_to_port_map[dst_mac]["port"] != ingress_port:
                            #print("Not arp and I know what to do")
                            egress_port_in_bytes = eth_to_port_map[dst_mac]["port"].to_bytes(2, byteorder='big')
                            ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)

                            eth_to_port_map[dst_mac]['count'] = num_entries_threshold
                elif routing == 'OPT':
                    if arp == False:
                        if switch_name == 'switch-50001':
                            if ingress_port == 1:
                                if flag==0:
                                    port = 2
                                    egress_port_in_bytes = port.to_bytes(2, byteorder='big')
                                    ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                                    flag = 1
                                else:
                                    port = 3
                                    egress_port_in_bytes = port.to_bytes(2, byteorder='big')
                                    ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                                    flag = 0
                            else:
                                if dst_mac in eth_to_port_map and eth_to_port_map[dst_mac]["port"] != ingress_port:
                                    #print("Not arp and I know what to do")
                                    egress_port_in_bytes = eth_to_port_map[dst_mac]["port"].to_bytes(2, byteorder='big')
                                    ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                                    eth_to_port_map[dst_mac]['count'] = num_entries_threshold
                        elif switch_name == 'switch-50002' or switch_name == 'switch-50003':
                            if ingress_port == 1:
                                port = 3
                                egress_port_in_bytes = port.to_bytes(2, byteorder='big')
                                ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                            else:
                                if dst_mac in eth_to_port_map and eth_to_port_map[dst_mac]["port"] != ingress_port:
                                    #print("Not arp and I know what to do")
                                    egress_port_in_bytes = eth_to_port_map[dst_mac]["port"].to_bytes(2, byteorder='big')
                                    ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                                    eth_to_port_map[dst_mac]['count'] = num_entries_threshold

                        else:
                             if dst_mac in eth_to_port_map and eth_to_port_map[dst_mac]["port"] != ingress_port:
                                #print("Not arp and I know what to do")
                                egress_port_in_bytes = eth_to_port_map[dst_mac]["port"].to_bytes(2, byteorder='big')
                                ProcPacketOut(payload, b'\00\00', ingress_port_in_bytes, egress_port_in_bytes)
                        
                                eth_to_port_map[dst_mac]['count'] = num_entries_threshold

                    '''
                ##################################################################################
                # Learning switch logic - Ends ###################################################
                ##################################################################################




            # Logs the Ethernet address to port mapping
            logs_count += 1
            if logs_count == num_logs_threshold:
                logs_count = 0
                with open('{0}/{1}-table.json'.format(logs_dir, switch_name), 'w') as outfile:
                    json.dump(eth_to_port_map, outfile)

                print(
                    "INFO: Logs committed to {0}/{1}-table.json".format(logs_dir, switch_name))
    except KeyboardInterrupt:
        return None

# Process outgoing packets
def ProcPacketOut(payload, mcast_grp_in_bytes=b'\00\00', ingress_port_in_bytes=None, egress_port_in_bytes=None):
    req = p4rt.StreamMessageRequest()
    packet = req.packet
    packet.payload = payload

    metadata = p4rt.PacketMetadata()
    # Append multicast group ID
    metadata.metadata_id = 1
    metadata.value = mcast_grp_in_bytes
    packet.metadata.append(metadata)
    if ingress_port_in_bytes is not None:
        # Append ingress port
        metadata.metadata_id = 2
        metadata.value = ingress_port_in_bytes
        packet.metadata.append(metadata)
    if egress_port_in_bytes is not None:
        # Append egress port
        metadata.metadata_id = 4
        metadata.value = egress_port_in_bytes
        packet.metadata.append(metadata)

    # Send packet out
    p4sh.client.stream_out_q.put(req)


###############################################################################
# Main 
###############################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Switch Script')
    parser.add_argument('--grpc-port', help='GRPC Port', required=True,
                        type=str, action="store", default='50001')
    parser.add_argument('--topo-config', help='Topology Configuration File', required=True,
                        type=str, action="store")
    #parser.add_argument('--routing', help='Routing options', required=True,
     #                   type=str, action="store", default = 'OSPF')


    args = parser.parse_args()

    # Create a bridge name postfixed with the grpc port number
    switch_name = 'switch-{0}'.format(args.grpc_port)

    routing = 'OPT'
    #print(routing)

    # Create a Ethernet address to port mapping
    eth_to_port_map = {}

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
    InstallMcastGrpEntry(mcast_group_id, mcast_group_ports)




    ##################################################################################
    # Install VLAN Broadcast Rules - Begins ##########################################
    ##################################################################################

    # TODO: Install VLAN-specific broadcast rules (use `vlan_id_to_ports_map` table for 
    # this)

    #### ADD YOUR CODE HERE ... ####
    for vlanid in vlan_id_to_ports_map:
        InstallMcastGrpEntry(vlanid,vlan_id_to_ports_map[vlanid])

    ##################################################################################
    # Install VLAN Broadcast Rules - Ends ############################################
    ##################################################################################




    # Start the packet-processing loop
    ProcPacketIn(switch_name, mcast_group_id, 
                 eth_to_port_map, NUM_ENTRIES_THRESHOLD, 
                 vlan_id_to_ports_map,
                 LOGS_DIR, NUM_LOGS_THRESHOLD)

    print("Switch Stopped")

    # Delete broadcast rule
    DeleteMcastGrpEntry(mcast_group_id)




    ##################################################################################
    # Delete VLAN Broadcast Rules - Begins ###########################################
    ##################################################################################

    # TODO: Delete VLAN-specific broadcast rules (use `vlan_id_to_ports_map` table for 
    # this)

    #### ADD YOUR CODE HERE ... ####

    for vlanid in vlan_id_to_ports_map:
        DeleteMcastGrpEntry(vlanid)

    ##################################################################################
    # Delete VLAN Broadcast Rules - Ends #############################################
    ##################################################################################




    # Close the P4Runtime connection
    p4sh.teardown()
