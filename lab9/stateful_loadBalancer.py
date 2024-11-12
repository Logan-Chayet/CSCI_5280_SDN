# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import arp
from ryu.lib.mac import haddr_to_int
from ryu.lib.packet.ether_types import ETH_TYPE_IP
from ryu.lib.packet import ipv4

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    load_balancer_ip = '10.0.0.100'

    server1_ip = '10.0.0.1'
    server1_mac = '00:00:00:00:00:01'
    server1_port = 1
    server2_ip = '10.0.0.2'
    server2_mac = '00:00:00:00:00:02'
    server2_port = 2
    server3_ip = '10.0.0.3'
    server3_mac = '00:00:00:00:00:03'
    server3_port = 3

    current_server_index = 0
    servers = {
		's1': [],
		's2': [],
		's3': [],
	}
    server_list = list(servers.keys())

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 15, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 15, match, actions)
	        
        # ARP
        if eth.ethertype == ether_types.ETH_TYPE_ARP:
            arp_header = pkt.get_protocol(arp.arp)
            if arp_header.opcode == arp.ARP_REQUEST and arp_header.dst_ip == self.load_balancer_ip:
                self.logger.info("************* ARP PACKET *****************")
                arp_packet = self.arp_reply(arp_header.src_ip, arp_header.src_mac)
                actions = [parser.OFPActionOutput(in_port)]
                packet_out = parser.OFPPacketOut(datapath=datapath, in_port=ofproto.OFPP_ANY,data=arp_packet.data, actions=actions, buffer_id=0xffffffff)
                datapath.send_msg(packet_out)
                self.logger.info("ARP Reply Packet Sent")
                return	
        # TCP
        if eth.ethertype == ETH_TYPE_IP:
            self.logger.info("******************* TCP PACKET *****************")
            ip_pkt = pkt.get_protocol(ipv4.ipv4)
            packet_sent = self.tcp_handler(datapath, in_port, ip_pkt, parser, dst, src)
            self.logger.info("TCP Handler Packet: " + str(packet_sent))
            if packet_sent:
                return

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def add_ip(self, ip):
    
        server = self.server_list[self.current_server_index]

        if ip not in self.servers[server]:
            self.servers[server].append(ip)
            self.logger.info("Added IP "+ip+" to server "+server)
        else:
            self.logger.info("IP "+ip+" is already associated with server "+server)

        self.current_server_index = (self.current_server_index + 1) % len(self.server_list)	

    def find_ip(self, ip):
        for server, ips in self.servers.items():
            if ip in ips:
                return server
        return None

    def arp_reply(self, dst_ip, dst_mac):
        self.logger.info("ARP Reply Packet...")
        self.logger.info("ARP request client side IP: " + dst_ip + ", Client MAC: " + dst_mac)
        arp_target_ip = dst_ip  
        arp_target_mac = dst_mac
            
        src_ip = self.load_balancer_ip
        
        self.add_ip(dst_ip)
        server = self.find_ip(dst_ip)
        

        if server == 's1':
            src_mac = self.server1_mac
        elif server == 's2':
            src_mac = self.server2_mac
        elif server == 's3':
            src_mac = self.server3_mac	
        
        self.logger.info("Server MAC Address: " + src_mac)

        reply_packet = packet.Packet()
        reply_packet.add_protocol(ethernet.ethernet(dst=dst_mac, src=src_mac, ethertype=ether_types.ETH_TYPE_ARP))
        reply_packet.add_protocol(arp.arp(opcode=arp.ARP_REPLY, src_mac=src_mac, src_ip=src_ip,dst_mac=arp_target_mac, dst_ip=arp_target_ip))
        reply_packet.serialize()
        self.logger.info("ARP Reply packet processed...")
        return reply_packet

    def tcp_handler(self, datapath, in_port, ip_pkt, parser, dst_mac, src_mac):
        packet_processed = False
        if ip_pkt.dst == self.load_balancer_ip:
            if dst_mac == self.server1_mac:
                server_dst_ip = self.server1_ip
                server_out_port = self.server1_port
            elif dst_mac == self.server2_mac:
                server_dst_ip = self.server2_ip
                server_out_port = self.server2_port
            elif dst_mac == self.server3_mac:
                server_dst_ip = self.server3_ip
                server_out_port = self.server3_port

            match = parser.OFPMatch(in_port=in_port, eth_type=ETH_TYPE_IP, ip_proto=ip_pkt.proto,ipv4_dst=self.load_balancer_ip)

            actions = [parser.OFPActionSetField(ipv4_dst=server_dst_ip),parser.OFPActionOutput(server_out_port)]

            self.add_flow(datapath, 30, match, actions)
            self.logger.info("********* Client-Server Flow added: " + str(server_dst_ip) + " from Host :" + str(ip_pkt.src) + " on Switch Port:" + str(server_out_port) + "****************")

            match = parser.OFPMatch(in_port=server_out_port, eth_type=ETH_TYPE_IP,ip_proto=ip_pkt.proto,ipv4_src=server_dst_ip,eth_dst=src_mac)
            actions = [parser.OFPActionSetField(ipv4_src=self.load_balancer_ip),parser.OFPActionOutput(in_port)]

            self.add_flow(datapath, 30, match, actions)
            self.logger.info("******** Server-Client Flow added: " + str(server_dst_ip) + " to Host: " + str(src_mac) + " on Switch Port:" + str(in_port) + "*************")
            packet_processed = True
        return packet_processed
