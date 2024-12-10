import requests
import json

ip = "10.224.78.149"
port = "8080"

base_url = f"http://{ip}:{port}/wm/staticflowpusher/json"

s10 = "00:00:00:00:00:45:64:91"
s20 = "00:00:00:00:00:05:44:67"

def static_routing(dpid, name, priority, eth_type, ip_src, ip_dst, action, l4_protocol):

    flow_data = {
    "switch": dpid,
    "name": name,
    "priority": priority,
    "eth_type": eth_type,
    "ipv4_src": ip_src,
    "ipv4_dst": ip_dst,
    "active": "true",
    "actions": action,
    "ip_proto": l4_protocol
    }

    response = requests.post(base_url, data=json.dumps(flow_data), headers={'Content-Type': 'application/json'})
    print(flow_data)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error", response.status_code)
        return None

def block_icmp_http():
    static_routing(s20, "test_http10", "2000", "0x0800", "10.0.0.2", "10.0.0.3", "output=", "0x06")

    static_routing(s20, "test_ping_1", "2000", "0x0800", "10.0.0.2", "10.0.0.3", "output=", "0x01")
    static_routing(s20, "test_ping_2", "2000", "0x0800", "10.0.0.3", "10.0.0.2", "output=", "0x01")
    static_routing(s20, "test_ping_3", "2000", "0x0800", "10.0.0.3", "10.0.0.1", "output=", "0x01")
    static_routing(s10, "test_ping_4", "2000", "0x0800", "10.0.0.1", "10.0.0.3", "output=", "0x01")

    return "Blocked Traffic"

print(block_icmp_http())
