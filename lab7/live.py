import re,paramiko,time,subprocess,pyshark

def sdn_pcap(ip):
    hostname = ip
    port = 22
    username = 'sdn'
    password = 'sdn'

    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname, port, username, password)

    shell = client.invoke_shell()
    
    print("Checking for Packet_IN packets...\n")
    shell.send("sudo tcpdump tcp port 6633 or tcp port 6653 -i enp0s8 -w /home/sdn/midterm.pcap\n")
    time.sleep(1)
    shell.send(password + "\n")
    time.sleep(5)

    output = shell.recv(1024).decode()
    print(output)
    client.close()
def host_pcap(ip):
    hostname = ip
    port = 22
    username = 'sdn'
    password = 'sdn'

    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname, port, username, password)

    shell = client.invoke_shell()
    
    shell.send("scp /home/sdn/midterm.pcap student@192.168.100.13:/home/student/CSCI_5280_SDN/lab7/midterm.pcap\n")
    time.sleep(1)
    shell.send("admin\n")
    time.sleep(1)

    output = shell.recv(1024).decode()
    print(output)
    client.close()
def block_attack(ip):
    hostname = ip
    port = 22
    username = 'sdn'
    password = 'sdn'

    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname, port, username, password)

    shell = client.invoke_shell()
    
    print("Blocking attack...")
    shell.send("sudo iptables -i enp0s8 -A INPUT -s 192.168.1.13 -d 192.168.1.12 -p tcp --dport 6653 --sport 1:100 -j DROP\n")
    time.sleep(1)
    shell.send(password + "\n")
    time.sleep(5)

    output = shell.recv(1024).decode()
    print(output)
    client.close()


def get_pcap(file):
    cap = pyshark.FileCapture(file)
    count=0
    for packet in cap:
        if 'openflow_v4' in packet:
            if packet.openflow_v4.type == "10":
                count+=1
                print(packet)
    print(count)
    with open("/home/student/CSCI_5280_SDN/lab7/data.txt", "a") as doc:
        doc.write(str(count)+"\n")

    return count

def defend():
    count = get_pcap("midterm.pcap")
    if count > 80:
        print("DDOS ATTACK DETECTED, MITIGATING THREAT")
        block_attack("192.168.100.12")

while True:
    sdn_pcap("192.168.100.12")
    host_pcap("192.168.100.12")
    defend()

