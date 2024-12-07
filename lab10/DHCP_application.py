import requests
import json

ip = "198.11.21.22"
port = "8080"

base_url = f"http://{ip}:{port}/wm/staticflowpusher/json"

s1 = "00:14:00:1c:2e:98:12:80"
s2 = "00:14:00:17:a4:7f:21:00"
s3 = "00:14:00:1c:2e:15:1a:c0"
s4 = "00:14:78:ac:c0:14:b4:80"
s5 = "00:14:00:17:a4:7f:51:40"

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
    
def arp_or_route(name, dpid, priority, in_port, eth_type, dest_ip=None, floodport=None):

    flow_data = {
        "name": name,
        "switch": dpid,
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

def dhcp_routing(dpid, name, priority, eth_type, udp_src, udp_dst, in_port, action, ip_proto):

    flow_data = {
    "switch": dpid,
    "name": name,
    "priority": priority,
    "eth_type": eth_type,
    "udp_src": udp_src,
    "udp_dst": udp_dst,
    "active": "true",
    "in_port": in_port,
    "actions": action,
    "ip_proto": ip_proto
    }

    response = requests.post(base_url, data=json.dumps(flow_data), headers={'Content-Type': 'application/json'})
    print(flow_data)

    if response.status_code == 200:
        return response.json()
    else:
        print("Error", response.status_code)
        return None

def dhcp_routing_path():
    dhcp_routing(s3, "asfh222", "1000", "0x0800", "68", "67", "4", "output=3", "17")
    dhcp_routing(s4, "asfh2232", "1000", "0x0800", "68", "67", "2", "output=4", "17")
    dhcp_routing(s5, "asfh2242", "1000", "0x0800", "68", "67", "2", "output=3", "17")

    dhcp_routing(s3, "asfh5222", "1000", "0x0800", "67", "68", "3", "output=4", "17")
    dhcp_routing(s4, "asfh2262", "1000", "0x0800", "67", "68", "4", "output=2", "17")
    dhcp_routing(s5, "asfh2722", "1000", "0x0800", "67", "68", "3", "output=2", "17")

def dhcp_routing_path_long():
    dhcp_routing(s3, "asfhf222", "500", "0x0800", "68", "67", "4", "output=2", "17")
    dhcp_routing(s1, "asfdah2232", "500", "0x0800", "68", "67", "3", "output=2", "17")
    dhcp_routing(s2, "asfadh2242", "500", "0x0800", "68", "67", "2", "output=3", "17")
    dhcp_routing(s4, "asffdh2242", "500", "0x0800", "68", "67", "3", "output=4", "17")
    dhcp_routing(s5, "asfsadh2242", "500", "0x0800", "68", "67", "2", "output=3", "17")

    dhcp_routing(s3, "asffdah5222", "500", "0x0800", "67", "68", "2", "output=4", "17")
    dhcp_routing(s1, "asfdfh2262", "500", "0x0800", "67", "68", "2", "output=3", "17")
    dhcp_routing(s2, "asfdfh2722", "500", "0x0800", "67", "68", "3", "output=2", "17")
    dhcp_routing(s4, "asfhdf2722", "500", "0x0800", "67", "68", "4", "output=3", "17")
    dhcp_routing(s5, "asfdfh2722", "500", "0x0800", "67", "68", "3", "output=2", "17")

def shortest_path():
    static_routing(s3, "test_http1", "1000", "0x0800", "192.168.1.3", "192.168.1.1", "output=3", "0x01")
    static_routing(s3, "test_http2", "1000", "0x0800", "192.168.1.1", "192.168.1.3", "output=4", "0x01")
    static_routing(s4, "test_http8", "1000", "0x0800", "192.168.1.3", "192.168.1.1", "output=4", "0x01")
    static_routing(s4, "test_http9", "1000", "0x0800", "192.168.1.1", "192.168.1.3", "output=2", "0x01")
    static_routing(s5, "test_http5", "1000", "0x0800", "192.168.1.1", "192.168.1.3", "output=2", "0x01")
    static_routing(s5, "test_http6", "1000", "0x0800", "192.168.1.3", "192.168.1.1", "output=3", "0x01")

    arp_or_route("arp101b423b", s3, "1000", "3", "0x0806", None, None)
    arp_or_route("arp1011v12v1", s3, "1000", "4", "0x0806", None, None)
    arp_or_route("arp11b234b", s4, "1000", "2", "0x0806", None, None)
    arp_or_route("arp1011b234", s4, "1000", "4", "0x0806", None, None)
    arp_or_route("arpb2341", s5, "1000", "2", "0x0806", None, None)
    arp_or_route("arp1v2b43fd", s5, "1000", "3", "0x0806", None, None)

def longest_path():
    static_routing(s3, "test_http231", "500", "0x0800", "192.168.1.3", "192.168.1.1", "output=2", "0x01")
    static_routing(s3, "test_http23", "500", "0x0800", "192.168.1.1", "192.168.1.3", "output=4", "0x01")
    static_routing(s1, "test_http334", "500", "0x0800", "192.168.1.3", "192.168.1.1", "output=2", "0x01")
    static_routing(s1, "test_http4122", "500", "0x0800", "192.168.1.1", "192.168.1.3", "output=3", "0x01")
    static_routing(s2, "test_http532134", "500", "0x0800", "192.168.1.3", "192.168.1.1", "output=3", "0x01")
    static_routing(s2, "test_http634", "500", "0x0800", "192.168.1.1", "192.168.1.3", "output=2", "0x01")
    static_routing(s4, "test_http2347", "500", "0x0800", "192.168.1.3", "192.168.1.1", "output=4", "0x01")
    static_routing(s4, "test_http2348", "500", "0x0800", "192.168.1.1", "192.168.1.3", "output=3", "0x01")
    static_routing(s5, "test_http2349", "500", "0x0800", "192.168.1.3", "192.168.1.1", "output=3", "0x01")
    static_routing(s5, "test_http12340", "500", "0x0800", "192.168.1.1", "192.168.1.3", "output=2", "0x01")

    arp_or_route("2arp101b423b", s3, "500", "2", "0x0806", None, None)
    arp_or_route("23arp1011v12v1", s3, "500", "4", "0x0806", None, None)
    arp_or_route("a33rp101b423b", s1, "500", "2", "0x0806", None, None)
    arp_or_route("ar43p1011v12v1", s1, "500", "3", "0x0806", None, None)
    arp_or_route("arp5101b423b", s2, "500", "3", "0x0806", None, None)
    arp_or_route("ar6p1011v12v1", s2, "500", "2", "0x0806", None, None)
    arp_or_route("ar44p11b234b", s4, "500", "4", "0x0806", None, None)
    arp_or_route("ar56p1011b234", s4, "500", "3", "0x0806", None, None)
    arp_or_route("arp65b2341", s5, "500", "3", "0x0806", None, None)
    arp_or_route("arp44121v2b43fd", s5, "500", "2", "0x0806", None, None)

def dhcp_application():
    print("\n Creating Shortest Path Routing:\n")
    shortest_path()
    print("\n Creating Longest Path Routing:\n")
    longest_path()
    print("\n Creating Shortest Path DHCP:\n")
    dhcp_routing_path()
    print("\n Creating Longest Path DHCP:\n")
    dhcp_routing_path_long()

dhcp_application()


