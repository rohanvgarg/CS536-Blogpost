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

# Relative path of the configuration and logs directories
CFG_DIR = 'cfg'
LOGS_DIR = 'logs'

# Bridge ID and number of ports
BRIDGE_ID = 1

# Flows and logs threshold
NUM_ENTRIES_THRESHOLD = 10
NUM_LOGS_THRESHOLD = 10


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
def ProcPacketIn(bridge_name, mcast_group_id,
                 eth_to_port_map, num_entries_threshold, 
                 logs_dir, num_logs_threshold):
    try:
        mcast_group_id_in_bytes = mcast_group_id.to_bytes(2, byteorder='big')
        num_logs = 0
        while True:
            rep = p4sh.client.get_stream_packet("packet", timeout=1)
            if rep is not None:
                # Read the raw packet
                payload = rep.packet.payload




                ##################################################################################
                # Packet parsing logic - Begins ##################################################
                ##################################################################################
                
                # Parse Metadata
                ingress_port_in_bytes = rep.packet.metadata[0].value
                ingress_port = int.from_bytes(ingress_port_in_bytes, "big")

                # Parse Ethernet header (source and destination MAC)
                dst_mac_in_bytes = payload[0:6]
                dst_mac = mac2str(dst_mac_in_bytes)
                src_mac_in_bytes = payload[6:12]
                src_mac = mac2str(src_mac_in_bytes)

                print("PacketIn: dst={0} src={1} port={2}".format(
                    dst_mac, src_mac, ingress_port))

                ##################################################################################
                # Packet parsing logic - Ends ####################################################
                ##################################################################################
    



                # Decrement table entry's counter
                del_mac_list = []
                for mac in eth_to_port_map:
                    eth_to_port_map[mac]['count'] -= 1
                    if eth_to_port_map[mac]['count'] == 0:
                        print("INFO: Table entry deleted: mac={0} port={1}".format(
                              mac, eth_to_port_map[mac]['port']))
                        del_mac_list.append(mac)

                for mac in del_mac_list:
                    del eth_to_port_map[mac]




                ##################################################################################
                # Learning bridge logic - Begins #################################################
                ##################################################################################

                # Filter packets belonging to the same segment
                if dst_mac in eth_to_port_map:
                    if ingress_port != eth_to_port_map[dst_mac]['port']:
                        # Broadcast packet
                        ProcPacketOut(payload, mcast_group_id_in_bytes, ingress_port_in_bytes) 
                    else:
                        None  # ... drop the packet

                    eth_to_port_map[dst_mac]['count'] = num_entries_threshold  # ... reset the counter
                else:
                    # Broacast packet as-is, we haven't learned anything about it yet
                    ProcPacketOut(payload, mcast_group_id_in_bytes, ingress_port_in_bytes)

                # Learn Ethernet address to port mapping
                if src_mac not in eth_to_port_map:
                    eth_to_port_map[src_mac] = {'port': ingress_port,
                                                'count': num_entries_threshold}

                ##################################################################################
                # Learning bridge logic - Ends ###################################################
                ##################################################################################




            # Log the Ethernet address to port mapping
            num_logs += 1
            if num_logs == num_logs_threshold:
                num_logs = 0
                with open('{0}/{1}-table.json'.format(logs_dir, bridge_name), 'w') as outfile:
                    json.dump(eth_to_port_map, outfile)

                print(
                    "INFO: Log committed to {0}/{1}-table.json".format(logs_dir, bridge_name))
    except KeyboardInterrupt:
        return None

# Process outgoing packets
def ProcPacketOut(payload, mcast_grp_in_bytes=b'\00\00', ingress_port_in_bytes=None):
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

    # Send packet out
    p4sh.client.stream_out_q.put(req)


###############################################################################
# Main 
###############################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Learning Bridge Script')
    parser.add_argument('--grpc-port', help='GRPC Port', required=True,
                        type=str, action="store", default='50001')
    parser.add_argument('--topo-config', help='Topology Configuration File', required=True,
                        type=str, action="store")
    args = parser.parse_args()

    # Create a bridge name postfixed with the grpc port number
    bridge_name = 'bridge-{0}'.format(args.grpc_port)

    # Create a Ethernet address to port mapping
    eth_to_port_map = {}

    # Get Multicast to ports mapping
    with open(args.topo_config, 'r') as infile:
        topo_config = json.loads(infile.read())

    mcast_group_id = topo_config['switch'][args.grpc_port]['mcast']['id']
    mcast_group_ports = topo_config['switch'][args.grpc_port]['mcast']['ports']

    # Setup the P4Runtime connection with the bridge
    p4sh.setup(
        device_id=BRIDGE_ID, grpc_addr='127.0.0.1:{0}'.format(args.grpc_port), election_id=(0, 1),
        config=p4sh.FwdPipeConfig(
            '{0}/{1}-p4info.txt'.format(CFG_DIR, bridge_name),  # Path to P4Info file
            '{0}/{1}.json'.format(CFG_DIR, bridge_name)  # Path to config file
        )
    )

    print("Bridge Started @ Port: {0}".format(args.grpc_port))
    print("Press CTRL+C to stop ...")

    # Install broadcast rule
    InstallMcastGrpEntry(mcast_group_id, mcast_group_ports)

    # Start the packet-processing loop
    ProcPacketIn(bridge_name, mcast_group_id,
                 eth_to_port_map, NUM_ENTRIES_THRESHOLD, 
                 LOGS_DIR, NUM_LOGS_THRESHOLD)

    print("Bridge Stopped")

    # Delete the broadcast rule
    DeleteMcastGrpEntry(mcast_group_id)

    # Close the P4Runtime connection
    p4sh.teardown()
