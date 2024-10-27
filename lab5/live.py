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

    shell.send("sudo tcpdump tcp port 6633 or tcp port 6653 -i enp0s8 -w /home/sdn/midterm.pcap\n")
    time.sleep(1)
    shell.send(password + "\n")
    time.sleep(6)

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
    
    shell.send("scp /home/sdn/midterm.pcap student@192.168.100.13:/home/student/Documents/midterm.pcap\n")
    time.sleep(1)
    shell.send("admin\n")
    time.sleep(1)

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
    with open("/home/student/Documents/data.txt", "a") as doc:
        doc.write(str(count)+"\n")
while True:
    sdn_pcap("10.20.30.2")
    time.sleep(2)
    host_pcap("10.20.30.2")
    get_pcap("midterm.pcap")

