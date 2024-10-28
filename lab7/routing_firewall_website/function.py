import requests
import json

ip = "192.168.100.12"
port = "8080"

base_url = f"http://{ip}:{port}/wm/staticflowpusher/json"

def static_routing(name, dpid, priority, in_port, eth_type, dest_ip=None, floodport=None):
    
    flow_data = {
        "name": name,
        "switch": "00:00:00:00:00:00:00:0"+dpid,
        "priority": priority,
        "in_port": in_port,
        "eth_type": eth_type,
        "active": "true"
            }

    if dest_ip:
        flow_data["ipv4_dst"] = dest_ip
    if floodport:
        flow_data["actions"] = f"output={floodport}"
    else:
        flow_data["actions"] = "output=flood"

    response = requests.post(base_url, data=json.dumps(flow_data), headers={'Content-Type': 'application/json'})
    print(flow_data)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error", response.status_code)
        return None

def firewall(name, dpid, priority, in_port, eth_type, src_ip, dest_ip, l4_protocol):

    flow_data = {
        "switch": "00:00:00:00:00:00:00:0"+dpid,
        "name": name,
        "priority": priority,
        "in_port": in_port,
        "eth_type": eth_type,
        "ipv4_src": src_ip,
        "ipv4_dst": dest_ip,
        "ip_proto": l4_protocol,
        "active": "true"
    }

    # Allow action
    flow_data["actions"] = "output=flood"  # This will flood allowed packets; customize as needed.

    response = requests.post(base_url, data=json.dumps(flow_data), headers={'Content-Type': 'application/json'})
    print(flow_data)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error", response.status_code)
        return None

#print(static_routing("LOGANCHAYET","1","6969","3", "0x0800",None, None))
