/*****************************************************************************
 *
 *     This file is part of Purdue CS 536.
 *
 *     Purdue CS 536 is free software: you can redistribute it and/or modify
 *     it under the terms of the GNU General Public License as published by
 *     the Free Software Foundation, either version 3 of the License, or
 *     (at your option) any later version.
 *
 *     Purdue CS 536 is distributed in the hope that it will be useful,
 *     but WITHOUT ANY WARRANTY; without even the implied warranty of
 *     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *     GNU General Public License for more details.
 *
 *     You should have received a copy of the GNU General Public License
 *     along with Purdue CS 536. If not, see <https://www.gnu.org/licenses/>.
 *
 *****************************************************************************/

/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#define CPU_PORT 255
/*
  255 is confirmed for opennetworking/p4mn　(Mininet/Stratum on docker)
  192 is confirmed for WEDGE-100BF-32X (2 pipes device)
  320 is probably good for 4 pipes devices
*/

/**************************************************************************/
/**************************  Headers  *************************************/
/**************************************************************************/

@controller_header("packet_out")
header packet_out_header_t {
    bit<16> mcast_grp;
    bit<9> ingress_port;
    bit<7> _pad;
}

@controller_header("packet_in")
header packet_in_header_t {
    bit<9> ingress_port;
    bit<7> _pad;
}

struct metadata {
    bit<9> ingress_port;
    bit<7> _pad;
}

struct headers {
    packet_out_header_t packet_out;
    packet_in_header_t packet_in;
}

/**************************************************************************/
/***************************  Parser  *************************************/
/**************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition select(standard_metadata.ingress_port) {
            CPU_PORT: parse_packet_out;
            default: accept;
        }
    }

    state parse_packet_out {
        packet.extract(hdr.packet_out);
        transition accept;
    }
}

/**************************************************************************/
/*********************  Checksum Verification  *****************************/
/**************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

/**************************************************************************/
/***********************  Ingress Processing  *****************************/
/**************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action to_controller() {
        standard_metadata.egress_spec = CPU_PORT;
        hdr.packet_in.setValid();
        hdr.packet_in.ingress_port = standard_metadata.ingress_port;
    }
    
    apply {
        if (standard_metadata.ingress_port == CPU_PORT) {
            // Broadcast packets to all ports
            standard_metadata.mcast_grp = hdr.packet_out.mcast_grp;
            meta.ingress_port = hdr.packet_out.ingress_port;
            hdr.packet_out.setInvalid();
        } else {
            // Send packets to the CPU, otherwise
            to_controller();
        }
    }
}

/**************************************************************************/
/************************  Egress Processing  *****************************/
/**************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    apply {
        // Prune multicast packets going to ingress port to prevent loops
        if (standard_metadata.egress_port == meta.ingress_port)
            drop();
    }
}

/**************************************************************************/
/*********************  Checksum Computation  *****************************/
/**************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

/**************************************************************************/
/**************************  Deparser  ************************************/
/**************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.packet_out);
        packet.emit(hdr.packet_in);
    }
}

/**************************************************************************/
/***************************  Bridge  *************************************/
/**************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
