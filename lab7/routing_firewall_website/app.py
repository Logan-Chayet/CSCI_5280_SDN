from flask import Flask, render_template, request, redirect, url_for
import function


app = Flask(__name__)

# Home page with options
@app.route('/')
def index():
    return render_template('index.html')

# Static Routing page
@app.route('/static_routing', methods=['GET', 'POST'])
def static_routing():
    if request.method == 'POST':
        name = request.form.get('name')
        dpid = request.form.get('dpid')
        priority = request.form.get('priority')
        in_port = request.form.get('in_port')
        eth_type = request.form.get('eth_type')
        dest_ip = request.form.get('dest_ip')
        floodport = request.form.get('floodport')

        function.static_routing(name, dpid, priority, in_port, eth_type, dest_ip, floodport)

        print(f"Static routing entry: DPID={dpid}, Priority={priority}, In-Port={in_port}, "
              f"Eth-Type={eth_type}, Dest IP={dest_ip}, Action={floodport}")

        static_routing_data = {
            'name': name,
            'dpid': dpid,
            'priority': priority,
            'in_port': in_port,
            'eth_type': eth_type,
            'dest_ip': dest_ip,
            'floodport': floodport
        }

        return render_template('static_routing.html', static_routing_data=static_routing_data)
    return render_template('static_routing.html')

# Firewall page
@app.route('/firewall', methods=['GET', 'POST'])
def firewall():
    if request.method == 'POST':
        name = request.form.get('name')
        dpid = request.form.get('dpid')
        priority = request.form.get('priority')
        in_port = request.form.get('in_port')
        eth_type = request.form.get('eth_type')
        src_ip = request.form.get('src_ip')
        dest_ip = request.form.get('dest_ip')
        l4_protocol = request.form.get('l4_protocol')

        print(function.firewall(name, dpid, priority, in_port, eth_type, src_ip, dest_ip, l4_protocol))

        print(f"Firewall entry: DPID={dpid}, Priority={priority}, In-Port={in_port}, "
              f"Eth-Type={eth_type}, Src IP={src_ip}, Dest IP={dest_ip}, L4 Protocol={l4_protocol}")

        firewall_data = {
            'name': name,
            'dpid': dpid,
            'priority': priority,
            'in_port': in_port,
            'eth_type': eth_type,
            'src_ip': src_ip,
            'dest_ip': dest_ip,
            'l4_protocol': l4_protocol
        }

        return render_template('firewall.html', firewall_data=firewall_data)
    return render_template('firewall.html')

if __name__ == '__main__':
    app.run(debug=True)

