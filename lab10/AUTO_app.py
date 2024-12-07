from netmiko import ConnectHandler
import requests
import json
import re

ip = "198.11.21.22"
port = "8080"

base_url = f"http://{ip}:{port}/wm/core/controller/switches/json"

switches = {"s1": "172.16.10.201", "s2": "172.16.10.202", "s3": "172.16.10.203", "s4": "172.16.10.204", "s5": "172.16.10.205"}


def get_device_info():

    response = requests.get(base_url)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error", response.status_code)
        return None

def print_device_info(info):
    print("\nDevice info: \n")
    for i in info:
        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', i['inetAddress'])

        if match:
            ip_address = match.group(1)
            for j in switches:
                if switches[j] == ip_address:
                    print(j+" at IP: "+ip_address+" is conntected to the controller")
                    print("DPID is: "+i['switchDPID']+"\n")

def configure_devices():
    for i in switches:
        # Define the connection parameters for the HP ProCurve
        hp_procurve = {
            'device_type': 'hp_procurve',
            'host': switches[i],  # Replace with the IP address of your switch
            'username': 'manager',     # Replace with your username
            'password': 'admin',  # Replace with your password
        }

        # Establish the connection
        try:
            # Connect to the switch
            connection = ConnectHandler(**hp_procurve)

            # If an enable mode is required, enter it
            connection.enable()

            # Send the 'show run' command

            print("\nNow configuring device: "+i)
            output = connection.send_config_from_file('NSOT/'+i+'_openflow.txt')

            # Print the output
            print(output)

            # Disconnect from the device
            connection.disconnect()

        except Exception as e:
            print(f"An error occurred: {e}")

configure_devices()
print_device_info(get_device_info())
