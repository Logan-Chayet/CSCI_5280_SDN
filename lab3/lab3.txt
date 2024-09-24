import os
import pyshark
import json

def create_pcap():
        os.system('sudo tcpdump tcp port 6633 or tcp port 6653 -i ens192 -w lab3.pcap -c 100')

def write_json(data):
    json_object = json.dumps(data, indent=4)

    with open("connected.txt", "w") as outfile:
        outfile.write(json_object)

def identify_switch():
        #create_pcap()
        data = {}
        file = "test.pcap"
        cap = pyshark.FileCapture("lab3.pcap")
        for packet in cap:
            if 'openflow_v4' in packet:
                if packet.openflow_v4.type == "6":
                    ip_address = packet.ip.src
                    dpid = packet.openflow_v4.switch_features_datapath_id
                    data[dpid] = { "ip_address": ip_address, "status": "connected"}
        print(data)
        write_json(data)
identify_switch()
