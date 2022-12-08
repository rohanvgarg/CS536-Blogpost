#!/usr/bin/env python

from scapy.all import *
import threading
import time

SEND_PACKET_SIZE = 4022272 # should be less than max packet size of 1500 bytes

# A client class for implementing TCP's three-way-handshake connection establishment and closing protocol,
# along with data transmission.


class Client3WH:

    def __init__(self, dip, dport):
        """Initializing variables"""
        self.dip = dip
        self.dport = dport
        # selecting a source port at random
        self.sport = random.randrange(0, 2**16)

        self.next_seq = 0                       # TCP's next sequence number
        self.next_ack = 0                       # TCP's next acknowledgement number

        self.ip = IP(dst=self.dip)              # IP header

        self.connected = False
        self.initiated_close = False
        self.timeout = 3

    def _start_sniffer(self):
        t = threading.Thread(target=self._sniffer)
        t.start()

    def _filter(self, pkt):
        if (IP in pkt) and (TCP in pkt):  # capture only IP and TCP packets
            return True
        return False

    def _sniffer(self):
        while self.connected:
            sniff(prn=lambda x: self._handle_packet(
                x), lfilter=lambda x: self._filter(x), count=1, timeout=self.timeout)

    def _handle_packet(self, pkt):
        """TODO(1): Handle incoming packets from the server and acknowledge them accordingly. Here are some pointers on
           what you need to do:
           1. If the incoming packet has data (or payload), send an acknowledgement (TCP) packet with correct 
              `sequence` and `acknowledgement` numbers.
           2. If the incoming packet is a FIN (or FINACK) packet, send an appropriate acknowledgement or FINACK packet
              to the server with correct `sequence` and `acknowledgement` numbers.
        """
        
        ### BEGIN: ADD YOUR CODE HERE ... ###
        if pkt[TCP].dport == self.sport  and pkt[TCP].flags & 0x01 == 0x01 and not self.initiated_close: # FIN OR FINACK
            
            self.connected = False
            #print("Received FIN from Server")
            self.next_ack += 1
            fin_ack = self.ip/TCP(sport=self.sport, dport=self.dport, flags='FA', seq=self.next_seq, ack=self.next_ack)
            ack = sr1(fin_ack, timeout=self.timeout)
            self.next_seq += 1

            assert ack.haslayer(TCP), 'TCP layer missing'
            assert ack[TCP].flags & 0x10 == 0x10 , 'No ACK flag'
            assert ack[TCP].ack == self.next_seq , 'Acknowledgment number error'
    

        if pkt.haslayer(Raw) and pkt[TCP].dport == self.sport:
            #print("Received Something Random from server")
            self.next_ack = pkt[TCP].seq + len(pkt[Raw])
            ack = self.ip/TCP(sport=self.sport, dport=self.dport, flags='A', seq=self.next_seq, ack=self.next_ack)
            send(ack)

        ### END: ADD YOUR CODE HERE ... #####

    def connect(self):
        """TODO(2): Implement TCP's three-way-handshake protocol for establishing a connection. Here are some
           pointers on what you need to do:
           1. Handle SYN -> SYNACK -> ACK packets.
           2. Make sure to update the `sequence` and `acknowledgement` numbers correctly, along with the 
              TCP `flags`.
        """

        ### BEGIN: ADD YOUR CODE HERE ... ###
        
        self.next_seq = random.randrange(0,(2**16)-1)

        syn = self.ip/TCP(sport=self.sport, dport=self.dport, seq=self.next_seq, flags='S')
        syn_ack = sr1(syn, timeout=self.timeout)
        self.next_seq += 1
      
        assert syn_ack.haslayer(TCP), 'TCP layer missing'
        assert syn_ack[TCP].flags & 0x12 == 0x12 , 'No SYN/ACK flags'
        assert syn_ack[TCP].ack == self.next_seq , 'Acknowledgment number error'
        
        #print("At connect received:", syn_ack)
        #print("Which has seq number:", syn_ack[TCP].seq)

        self.next_ack = syn_ack[TCP].seq + 1
        #print("Made ack:", self.next_ack)

        ack = self.ip/TCP(sport=self.sport, dport=self.dport, seq=self.next_seq, flags='A', ack=self.next_ack)
        send(ack)
        

        ### END: ADD YOUR CODE HERE ... #####

        self.connected = True
        self._start_sniffer()
        print('Connection Established')

    def close(self):
        """TODO(3): Implement TCP's three-way-handshake protocol for closing a connection. Here are some
           pointers on what you need to do:
           1. Handle FIN -> FINACK -> ACK packets.
           2. Make sure to update the `sequence` and `acknowledgement` numbers correctly, along with the 
              TCP `flags`.
        """

        ### BEGIN: ADD YOUR CODE HERE ... ###
        
        
        self.connected = False
        self.initiated_close = True


        fin = self.ip/TCP(sport=self.sport, dport=self.dport, flags='FA', seq=self.next_seq, ack=self.next_ack)
        fin_ack = sr1(fin, timeout=self.timeout)
        self.next_seq += 1

        assert fin_ack.haslayer(TCP), 'TCP layer missing'
        assert fin_ack[TCP].flags & 0x11 == 0x11 , 'No FIN/ACK flags'
        assert fin_ack[TCP].ack == self.next_seq , 'Acknowledgment number error'

        self.next_ack = fin_ack[TCP].seq + 1
        ack = self.ip/TCP(sport=self.sport, dport=self.dport, flags='A', seq=self.next_seq,  ack=self.next_ack)
        send(ack)

        print('Disconnected')
          

        ### END: ADD YOUR CODE HERE ... #####

        self.connected = False
        print('Connection Closed')

    def send(self, payload):
        """TODO(4): Create and send TCP's data packets for sharing the given message (or file):
           1. Make sure to update the `sequence` and `acknowledgement` numbers correctly, along with the 
              TCP `flags`.
        """
        #start = time.time()
        ### BEGIN: ADD YOUR CODE HERE ... ##
        #print("Trying to send")   
        packet = self.ip/TCP(sport=self.sport, dport=self.dport, flags = "PA", seq=self.next_seq, ack=self.next_ack)/payload
        self.next_seq += len(packet[Raw])

        ack = sr1(packet, timeout=self.timeout)
        #print("Sent it")
        
        #print("Received:", ack)

        assert ack.haslayer(TCP), 'TCP layer missing'
        assert ack[TCP].flags & 0x10 == 0x10, 'No ACK flag'
        assert ack[TCP].ack == self.next_seq , 'Acknowledgment number error'

        ### END: ADD YOUR CODE HERE ... #####
        #end = time.time()
        #print("time is:", end-start)


def main():
    """Parse command-line arguments and call client function """
    if len(sys.argv) != 3:
        sys.exit(
            "Usage: ./client-3wh.py [Server IP] [Server Port] < [message]")
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    client = Client3WH(server_ip, server_port)
    client.connect()
    
    message = sys.stdin.read(SEND_PACKET_SIZE)
    while message:
        client.send(message)
        message = sys.stdin.read(SEND_PACKET_SIZE)

    client.close()


if __name__ == "__main__":
    main()

