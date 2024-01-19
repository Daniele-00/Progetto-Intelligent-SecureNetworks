from mininet.topo import Topo
from mininet.net import Mininet
from mininet.nodelib import NAT
from mininet.node import Node
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.link import Intf

class Router(Node):
   def config(self, **params):
      super(Router, self).config(**params)
      self.cmd("sysctl net.ipv4.ip_forward=1")
   
   def terminate(self):
      self.cmd("sysctl net.ipv4.ip_forward=0")
      super(Router, self).terminate()


class MyTopologia(Topo):
   def build(self, **_kwargs):
      r0 = self.addNode("r0", cls=Router)
      switch1 = self.addSwitch("s1")
      h1 = self.addHost("h1", ip="192.0.0.10/24", defaultRoute="via 192.0.0.1")
      h2 = self.addHost("h2", ip="192.0.0.20/24", defaultRoute="via 192.0.0.1")
      self.addLink(h1, switch1)
      self.addLink(h2, switch1)

      switch2 = self.addSwitch("s2")
      h3 = self.addHost("h3", ip="202.0.0.30/24", defaultRoute="via 202.0.0.1")
      h4 = self.addHost("h4", ip="202.0.0.40/24", defaultRoute="via 202.0.0.1")
      self.addLink(h3, switch2)
      self.addLink(h4, switch2)

      self.addLink(r0, switch1, intfName1="r0-eth1", params1={"ip": "192.0.0.1/24"})
      self.addLink(r0, switch2, intfName1="r0-eth2", params1={"ip": "202.0.0.1/24"})
   
def run():
   topo = MyTopologia()
   net = Mininet(topo=topo, waitConnected=True)
   net.start()
   router = net.getNodeByName("r0")
   _intf0 = Intf("enp0s3", node=router)
   router.cmd('dhclient enp0s3')
   router.cmd("ip r0-eth1 10.0.0.1 netmask 255.255.255.0")
   router.cmd("ip r0-eth2 20.0.0.1 netmask 255.255.255.0")
   router.cmd("iptables -t nat -A POSTROUTING -o enp0s3 -j MASQUERADE")
   CLI(net)
   net.stop()


if __name__ == "__main__":
   setLogLevel("info")
   run()
