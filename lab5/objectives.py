from netmiko import ConnectHandler
from napalm import get_network_driver
import re,paramiko,time

def sendConfig(ip,fileName):
    device = {
        'device_type': "cisco_ios",
        'host': ip,
        'username': "admin",
        'password': "password"
    }
    cfg_file = fileName
    with ConnectHandler(**device) as connection:
        connection.enable()
        output = connection.send_config_from_file(cfg_file)
    #print(output)
    return output
def find_mininet_ip():
    output = sendConfig("192.168.100.1", "config.txt")
    # Regular expression to match IPv4 addresses
    ipv4_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    # Find all matches in the output
    ipv4_addresses = re.findall(ipv4_pattern, output)

    # Print the extracted IP addresses
    return ipv4_addresses[0]
def mininet_init(ip):
    hostname = ip
    port = 22
    username = 'mininet'
    password = 'mininet'
    
    client = paramiko.SSHClient()
    
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(hostname, port, username, password)

    shell = client.invoke_shell()

    shell.send("sudo mn --mac --controller=remote,ip=10.20.30.2,port=6653 --switch ovsk,protocols=OpenFlow13\n")
    time.sleep(1)
    shell.send(password + "\n")
    time.sleep(1)
    shell.send("pingall\n")
    time.sleep(1)


    output = shell.recv(1024).decode()
    print(output)

    client.close()
def send_routing_configs():
    ip = ["192.168.100.1", "192.168.200.2", "172.16.100.1"]
    fileName = ["R1.txt", "R2.txt", "R3.txt"]
    for i in range(3):
        print(sendConfig(ip[i], fileName[i]))
def mininet_check(ip):
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
    print(output)

#mininet_check(find_mininet_ip())


def handle_choice(choice):
    if choice == 1:
        print(find_mininet_ip())
        # Implement Option 1 functionality here
    elif choice == 2:
        mininet_init(find_mininet_ip()) 
        # Implement Option 2 functionality here
    elif choice == 3:
        send_routing_configs()
        # Implement Option 3 functionality here
    elif choice == 4:
        mininet_check(find_mininet_ip())
        # Implement Option 3 functionality here
    elif choice == 0:
        print("Exiting...")
    else:
        print("Invalid choice. Please try again.")

while True:
    try:
        choice = int(input("Enter your choice: "))
        if choice == 0:
            break
        else:
            handle_choice(choice)
    except ValueError:
        print("Invalid input. Please enter a number.")
