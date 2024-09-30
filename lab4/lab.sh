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
    controller=net.addController(name='controller',
                      controller=RemoteController,
                      ip='10.224.78.243',
                      protocol='tcp',
                      port=6653)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)

    info( '*** Add links\n')
    s2h1 = {'bw':10}
    net.addLink(s2, h1, cls=TCLink , **s2h1)
    s2h2 = {'bw':10}
    net.addLink(s2, h2, cls=TCLink , **s2h2)
    s3h3 = {'bw':10}
    net.addLink(s3, h3, cls=TCLink , **s3h3)
    s3h4 = {'bw':10}
    net.addLink(s3, h4, cls=TCLink , **s3h4)
    s2s1 = {'bw':10}
    net.addLink(s2, s1, cls=TCLink , **s2s1)
    s1s3 = {'bw':10}
    net.addLink(s1, s3, cls=TCLink , **s1s3)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([controller])
    net.get('s3').start([controller])
    net.get('s2').start([controller])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
myNetwork()
