import socket
import requests
import json

# Floodlight Controller REST API URL
CONTROLLER_URL = "http://172.16.10.22:8080"

# Function to add a flow to a switch
def add_flow(switch, flow):
    url = f"{CONTROLLER_URL}/wm/staticflowentrypusher/json"
    response = requests.post(url, data=json.dumps(flow), headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        print(f"Flow - {flow['name']} -  added successfully to switch {switch}")
    else:
        print(f"Error adding Flow - {flow['name']} to switch {switch}: {response.status_code}")

# Function to resolve a domain name to an IP address
def resolve_domain(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception as e:
        print(f"Error resolving domain {domain}: {e}")
        return None

# Function to setup DNS flows for allowed and blocked domains
def setup_dns_flows():
    #switches = ["00:00:00:00:00:00:00:03", "00:00:00:00:00:00:00:04", "00:00:00:00:00:00:00:05"]
    switches = ["00:14:00:1c:2e:15:1a:c0"]
    # DNS flow for youtube.com (allowed domain)
    youtube_ip = resolve_domain("youtube.com")
    if youtube_ip:
        # Static Flow Entry for DNS Request (Host1 -> OVS3 -> OVS4 -> OVS5 -> Host2)
        dns_request_flows = [
            {
                "switch": "00:00:00:00:00:00:00:03",  # OVS3 DPID
                "name": "dns-request-ovs3-to-ovs4",
                "cookie":"0",
                "priority": 1000,
                "ip_proto": "17",  # UDP
                "in_port": 2,  # DNS request from Host1 on OVS3 Port 2
                "eth_type": 0x0800,  # IPv4
                "ipv4_dst": youtube_ip,  # DNS server (example youtube.com)
                "udp_dst": 53,  # DNS port
                "actions": "output=4",  # Forward out to OVS4 Port 4
            },
            {
                "switch": "00:00:00:00:00:00:00:04",  # OVS4 DPID
                "name": "dns-request-ovs4-to-ovs5",
                "priority": 1000,
                "ip_proto": "17",  # UDP
                "cookie":"0",
                "in_port": 3,  # DNS request from OVS3 Port 4 to OVS4 Port 3
                "eth_type": 0x0800,  # IPv4
                "ipv4_dst": youtube_ip,  # DNS server (example youtube.com)
                "udp_dst": 53,  # DNS port
                "actions": "output=4",  # Forward out to OVS5 Port 4
            },
            {
                "switch": "00:00:00:00:00:00:00:05",  # OVS5 DPID
                "name": "dns-request-ovs5-to-host2",
                "priority": 1000,
                "ip_proto": "17",  # UDP
                "cookie":"0",
                "in_port": 3,  # DNS request from OVS4 Port 4 to OVS5 Port 3
                "eth_type": 0x0800,  # IPv4
                "ipv4_dst": youtube_ip,  # DNS server (example youtube.com)
                "udp_dst": 53,  # DNS port
                "actions": "output=2",  # Forward out to Host2 via OVS5 Port 2
            },
        ]
        
        # Static Flow Entry for DNS Reply (Host2 -> OVS5 -> OVS4 -> OVS3 -> Host1)
        dns_reply_flows = [
            {
                "switch": "00:00:00:00:00:00:00:05",  # OVS5 DPID
                "name": "dns-reply-ovs5-to-ovs4",
                "priority": 1000,
                "ip_proto": "17",  # UDP
                "cookie":"0",
                "in_port": 2,  # DNS reply from Host2 to OVS5 Port 2
                "eth_type": 0x0800,  # IPv4
                "ipv4_src": youtube_ip,  # DNS server (example youtube.com)
                "udp_src": 53,  # DNS port
                "actions": "output=3",  # Forward out to OVS4 Port 3
            },
            {
                "switch": "00:00:00:00:00:00:00:04",  # OVS4 DPID
                "name": "dns-reply-ovs4-to-ovs3",
                "priority": 1000,
                "cookie":"0",
                "ip_proto": "17",  # UDP
                "in_port": 4,  # DNS reply from OVS5 Port 3 to OVS4 Port 4
                "eth_type": 0x0800,  # IPv4
                "ipv4_src": youtube_ip,  # DNS server (example youtube.com)
                "udp_src": 53,  # DNS port
                "actions": "output=3",  # Forward out to OVS3 Port 3
            },
            {
                "switch": "00:00:00:00:00:00:00:03",  # OVS3 DPID
                "name": "dns-reply-ovs3-to-host1",
                "priority": 1000,
                "ip_proto": "17",  # UDP
                "cookie":"0",
                "in_port": 4,  # DNS reply from OVS4 Port 3 to OVS3 Port 4
                "eth_type": 0x0800,  # IPv4
                "ipv4_src": youtube_ip,  # DNS server (example youtube.com)
                "udp_src": 53,  # DNS port
                "actions": "output=2",  # Forward out to Host1 via OVS3 Port 2
            },
        ]
        # Send DNS reply flows only to the appropriate switches
        # Send DNS REQ flows:
     #   for flow_entry in dns_request_flows:
     #       if flow_entry["switch"] in switches:
     #           print(flow_entry)
     #           add_flow(flow_entry["switch"], flow_entry)
     #   for flow_entry in dns_reply_flows:
     #       if flow_entry["switch"] in switches:
     #           add_flow(flow_entry["switch"], flow_entry)
       

    # Block DNS flows for facebook.com and wells.fargo.com
    for domain in ["www.facebook.com", "www.wellsfargo.com"]:
        domain_ip = resolve_domain(domain)
        if domain_ip:
            print(f'Resolved Ip for {domain}: {domain_ip}')
            for switch in switches:
                flow_name = f"block_{domain}_{switch}"
                block_flow = {
                    "switch": switch,
                    "name": flow_name,
                    "cookie":"0",
                    "priority": "1000",
                    "ip_proto": "17",  # UDP
                    "in_port": "4",  # DNS request from H1
                    "eth_type": "0x0800",  # IPv4
                    "ipv4_dst": "57.144.174.1",  # DNS server IP
                    "udp_dst": "53",  # DNS port
                    "actions": "",  # Drop the packet
                }
                add_flow(switch, block_flow)

# Main function to run the DNS application
def main():
    print("Setting up DNS flows...")
    setup_dns_flows()
    print("DNS flows setup complete.")

if __name__ == "__main__":
    main()
