import paramiko
import time
import requests

# Define switches with their IDs and desired cookie values (including both old and new switches)
switches_with_cookies = {
    "sw1_long": {"id": "00:14:00:1c:2e:98:12:80", "cookie": "45035996671791186"},
    "sw2_long": {"id": "00:14:00:17:a4:7f:21:00", "cookie": "49539595694466892"},
    "sw3_long": {"id": "00:14:00:1c:2e:15:1a:c0", "cookie": "45035996671746662"},
    "sw4_long": {"id": "00:14:78:ac:c0:14:b4:80", "cookie": "49539593988529346"},
    "sw5_long": {"id": "00:14:00:17:a4:7f:51:40", "cookie": "49539593988529348"},
    "sw3_short": {"id": "00:14:00:1c:2e:15:1a:c0", "cookie": "45035998211325771"},
    "sw4_short": {"id": "00:14:78:ac:c0:14:b4:80", "cookie": "45035998211325778"},
    "sw5_short": {"id": "00:14:00:17:a4:7f:51:40", "cookie": "45035998211325775"},
}

# Base URL for the API
base_url = "http://198.11.21.22:8080/wm/core/switch/{}/flow/json"

# Store previous packet counts to compare with next iteration
previous_packet_counts = {}

def ssh_ping(src_ip, dst_ip):
    """SSH into the source IP and run a ping command to the destination IP."""
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # If the src_ip is 192.168.1.3, SSH into 172.16.10.30
        if src_ip == "192.168.1.3":
            src_ip = "172.16.10.30"
        
        ssh_client.connect(src_ip, username='admin123', password='admin123')
        
        # Run the ping command
        stdin, stdout, stderr = ssh_client.exec_command(f'ping {dst_ip} -c 10')
        output = stdout.read().decode()
        ssh_client.close()
        
        # Check if ping was successful
        if "100% packet loss" in output:
            return False, output
        else:
            return True, output
    except Exception as e:
        return False, f"SSH connection failed: {str(e)}"

def fetch_packet_counts():
    """Fetch packet counts for the switches and detect any path increase."""
    path_increased = []
    
    for switch_name, switch_data in switches_with_cookies.items():
        switch_id = switch_data["id"]
        target_cookie = switch_data["cookie"]
        url = base_url.format(switch_id)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()  # Parse JSON response
            
            # Extract "flows" array and filter for matching cookies
            flows = data.get("flows", [])
            matching_flows = [flow for flow in flows if flow.get("cookie") == target_cookie]

            if matching_flows:
                # Get the packet count
                packet_count = int(matching_flows[0].get("packet_count", 0))
                
                # Check if we have a previous count to compare with
                if switch_name in previous_packet_counts:
                    prev_count = previous_packet_counts[switch_name]
                    if packet_count > prev_count:
                        path_increased.append(switch_name)
                
                # Store the current packet count for future comparison
                previous_packet_counts[switch_name] = packet_count
            else:
                print(f"No matching flows found for {switch_name} with cookie {target_cookie}.")
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching flows for {switch_name} ({switch_id}): {e}")
        except ValueError as e:
            print(f"Unexpected response format for {switch_name} ({switch_id}): {e}")
    
    # Return the switches whose path increased
    return path_increased

def main():
    # Ask the user for the source and destination IP addresses
    src_ip = input("Enter the source IP address: ")
    dst_ip = input("Enter the destination IP address: ")
    
    # Perform SSH login and ping the destination IP
    print(f"Attempting to ping {dst_ip} from {src_ip}...")
    ping_successful, ping_output = ssh_ping(src_ip, dst_ip)
    
    if ping_successful:
        print("Ping successful!")
        print(ping_output)
        
        # If ping is successful, monitor packet counts every 15 seconds
        print("Starting to fetch packet counts every 20 seconds...")
        
        # Run fetch_packet_counts every 15 seconds until a change is detected
        while True:
            path_increased = fetch_packet_counts()
            
            if path_increased:
                print(f"Trace complete:")
                for switch in path_increased:
                    print(f" - {switch}")
                break  # Exit the loop if a change is detected
            else:
                print("Still detecting packet trace...")
            
            # Wait for 15 seconds before the next check
            time.sleep(20)
    
    else:
        print("Ping failed.")
        print(ping_output)

if __name__ == "__main__":
    main()
