#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)

    info( '*** Add links\n')
    s3s1 = {'bw':20}
    net.addLink(s3, s1, cls=TCLink , **s3s1)
    s1s4 = {'bw':20}
    net.addLink(s1, s4, cls=TCLink , **s1s4)
    s4s2 = {'bw':20}
    net.addLink(s4, s2, cls=TCLink , **s4s2)
    s2s5 = {'bw':20}
    net.addLink(s2, s5, cls=TCLink , **s2s5)
    s5s4 = {'bw':20}
    net.addLink(s5, s4, cls=TCLink , **s5s4)
    s4s3 = {'bw':20}
    net.addLink(s4, s3, cls=TCLink , **s4s3)
    s1s2 = {'bw':20}
    net.addLink(s1, s2, cls=TCLink , **s1s2)
    s3h1 = {'bw':20}
    net.addLink(s3, h1, cls=TCLink , **s3h1)
    s3h2 = {'bw':20}
    net.addLink(s3, h2, cls=TCLink , **s3h2)
    s4h3 = {'bw':20}
    net.addLink(s4, h3, cls=TCLink , **s4h3)
    s4h4 = {'bw':20}
    net.addLink(s4, h4, cls=TCLink , **s4h4)
    s5h5 = {'bw':20}
    net.addLink(s5, h5, cls=TCLink , **s5h5)
    s5h6 = {'bw':20}
    net.addLink(s5, h6, cls=TCLink , **s5h6)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s3').start([c0])
    net.get('s4').start([c0])
    net.get('s2').start([c0])
    net.get('s1').start([c0])
    net.get('s5').start([c0])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
