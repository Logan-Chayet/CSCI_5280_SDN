import requests
import json

ip = "10.224.79.211"
port = "8080"

base_url = f"http://{ip}:{port}/wm/staticflowpusher/json"


def static_routing(dpid, name, priority, eth_type, ip_src, ip_dst, action, l4_protocol):

    flow_data = {
    "switch": "00:00:00:00:00:00:00:0"+dpid,
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


def get_path_data():
    url = "http://10.224.79.211:8080/wm/routing/paths/fast/00:00:00:00:00:00:00:01/00:00:00:00:00:00:00:05/3/json"
    
    try:
        # Send the GET request
        response = requests.get(url)
        
        # Check if the request was successful
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        # Parse the JSON data
        data = response.json()
        
        # Print the JSON data with indentation
        print("Path data:")
        print(json.dumps(data, indent=4))
        
        return data

    except requests.exceptions.RequestException as e:
        # Handle any errors (e.g., network problems, invalid JSON)
        print(f"An error occurred: {e}")
        return None


def best_delay():
    data = get_path_data()

        # Initialize variables to store the minimum latency and associated hop count
    min_latency = float('inf')
    min_hop_count = None

    # Iterate through each path in the data
    for path in data["results"]:
        # Convert latency and hop count to integers
        latency = int(path["latency"])
        hop_count = int(path["hop_count"])

        # Check if the current path has a lower latency
        if latency < min_latency:
            min_latency = latency
            min_hop_count = hop_count

    return min_latency, min_hop_count


def shortest_path():


    static_routing("1", "test_http1", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=3", "0x06")
    static_routing("1", "test_http2", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x06")
    static_routing("8", "test_http8", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x06")
    static_routing("8", "test_http9", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x06")
    static_routing("5", "test_http5", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=3", "0x06")
    static_routing("5", "test_http6", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=1", "0x06")

    static_routing("1", "test_http1v1", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=4", "0x01")
    static_routing("1", "test_http2v1", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x01")
    static_routing("6", "test_http8v1123", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x01")
    static_routing("6", "test_http9v1123", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x01")
    static_routing("7", "test_http8v1dq", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x01")
    static_routing("7", "test_http9v1dfad", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x01")
    static_routing("5", "test_http5v1dfasd", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=4", "0x01")
    static_routing("5", "test_http6v1dafasd", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=1", "0x01")

    arp_or_route("arp101b423b", "1", "1000", "1", "0x0806", None, None)
    arp_or_route("arp1011v12v1", "1", "1000", "4", "0x0806", None, None)
    arp_or_route("arp11b234b", "6", "1000", "1", "0x0806", None, None)
    arp_or_route("arp1011b234", "6", "1000", "2", "0x0806", None, None)
    arp_or_route("arpb2341", "7", "1000", "2", "0x0806", None, None)
    arp_or_route("arp1v2b43fd", "7", "1000", "1", "0x0806", None, None)
    arp_or_route("arp1v22b34", "5", "1000", "4", "0x0806", None, None)
    arp_or_route("arp1v12v41", "5", "1000", "1", "0x0806", None, None)

    return "Shortest Path Created"

def default_path():

    static_routing("1", "test_http1v1", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=4", "0x06")
    static_routing("1", "test_http2v1", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x06")
    static_routing("6", "test_http8v1123", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x06")
    static_routing("6", "test_http9v1123", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x06")
    static_routing("7", "test_http8v1dq", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x06")
    static_routing("7", "test_http9v1dfad", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x06")
    static_routing("5", "test_http5v1dfasd", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=4", "0x06")
    static_routing("5", "test_http6v1dafasd", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=1", "0x06")

    static_routing("1", "http1v1", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=4", "0x01")
    static_routing("1", "http2v1", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x01")
    static_routing("6", "http8v1123", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x01")
    static_routing("6", "http9v1123", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x01")
    static_routing("7", "http8v1dq", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x01")
    static_routing("7", "http9v1dfad", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x01")
    static_routing("5", "http5v1dfasd", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=4", "0x01")
    static_routing("5", "http6v1dafasd", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=1", "0x01")

    arp_or_route("arp101b423b", "1", "1000", "1", "0x0806", None, None)
    arp_or_route("arp1011v12v1", "1", "1000", "4", "0x0806", None, None)
    arp_or_route("arp11b234b", "6", "1000", "1", "0x0806", None, None)
    arp_or_route("arp1011b234", "6", "1000", "2", "0x0806", None, None)
    arp_or_route("arpb2341", "7", "1000", "2", "0x0806", None, None)
    arp_or_route("arp1v2b43fd", "7", "1000", "1", "0x0806", None, None)
    arp_or_route("arp1v22b34", "5", "1000", "4", "0x0806", None, None)
    arp_or_route("arp1v12v41", "5", "1000", "1", "0x0806", None, None)

    return "Default Path Created"

def longest_path():


    static_routing("1", "test_http1", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x06")
    static_routing("1", "test_http2", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x06")
    static_routing("2", "test_http8", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x06")
    static_routing("2", "test_http9", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x06")
    static_routing("3", "test_httpr123f8", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x06")
    static_routing("3", "test_httpv23vv9", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x06")
    static_routing("4", "test_http8fgh1", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x06")
    static_routing("4", "test_http9asddf1", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x06")
    static_routing("5", "test_http5", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=2", "0x06")
    static_routing("5", "test_http6", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=1", "0x06")

    static_routing("1", "test_http1v1", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=4", "0x01")
    static_routing("1", "test_http2v1", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x01")
    static_routing("6", "test_http8v1123", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x01")
    static_routing("6", "test_http9v1123", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x01")
    static_routing("7", "test_http8v1dq", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=2", "0x01")
    static_routing("7", "test_http9v1dfad", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=1", "0x01")
    static_routing("5", "test_http5v1dfasd", "1000", "0x0800", "1.1.1.1", "10.0.0.1", "output=4", "0x01")
    static_routing("5", "test_http6v1dafasd", "1000", "0x0800", "10.0.0.1", "1.1.1.1", "output=1", "0x01")

    arp_or_route("arp101b423b", "1", "1000", "1", "0x0806", None, None)
    arp_or_route("arp1011v12v1", "1", "1000", "4", "0x0806", None, None)
    arp_or_route("arp11b234b", "6", "1000", "1", "0x0806", None, None)
    arp_or_route("arp1011b234", "6", "1000", "2", "0x0806", None, None)
    arp_or_route("arpb2341", "7", "1000", "2", "0x0806", None, None)
    arp_or_route("arp1v2b43fd", "7", "1000", "1", "0x0806", None, None)
    arp_or_route("arp1v22b34", "5", "1000", "4", "0x0806", None, None)
    arp_or_route("arp1v12v41", "5", "1000", "1", "0x0806", None, None)

    return "Longest Path Created"

# Find and print the lowest latency and corresponding hop count
def best_delay_config():
    latency, hop_count = best_delay()
    if hop_count == 2:
        return shortest_path()
    elif hop_count == 3:
        return default_path()
    elif hop_count == 4:
        return longest_path()

