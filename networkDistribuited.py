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
      self.cmd("sysctl net.ipv4.ip_forward=1") #comando per abilitare ip forward
   
   def terminate(self):
      self.cmd("sysctl net.ipv4.ip_forward=0")  #comando per disabilitare ip forward
      super(Router, self).terminate()

#Creazione topologia di rete personalizzata
class MyTopologia(Topo):
   def build(self, **_kwargs):
      r0 = self.addNode("r0", cls=Router) #aggiunta nodo router
      switch1 = self.addSwitch("s1")
      #Aggiunta di 3 host e assegnazione ip nella prima subnet con indirizzo 10.0.0.0/24
      h1 = self.addHost("h1", ip="10.0.0.10/24", defaultRoute="via 10.0.0.1")
      h2 = self.addHost("h2", ip="10.0.0.11/24", defaultRoute="via 10.0.0.1")
      h3 = self.addHost("h3", ip="10.0.0.12/24", defaultRoute="via 10.0.0.1")
      #Creazione collegamento host-switch
      self.addLink(h1, switch1)
      self.addLink(h2, switch1)
      self.addLink(h3, switch1)
      
      #Aggiunta di 3 host e assegnazione ip nella seconda subnet con indirizzo 192.168.0.0/24
      switch2 = self.addSwitch("s2")
      h4 = self.addHost("h4", ip="192.168.0.13/24", defaultRoute="via 192.168.0.1")
      h5 = self.addHost("h5", ip="192.168.0.14/24", defaultRoute="via 192.168.0.1")
      h6 = self.addHost("h6", ip="192.168.0.15/24", defaultRoute="via 192.168.0.1")
      #Creazione collegamento host-switch
      self.addLink(h4, switch2)
      self.addLink(h5, switch2)
      self.addLink(h6, switch2)

      #Collegamento tra il router e i due switch attraverso interfaccia
      self.addLink(r0, switch1, intfName1="r0-eth1", params1={"ip": "10.0.0.1/24"})
      self.addLink(r0, switch2, intfName1="r0-eth2", params1={"ip": "192.168.0.1/24"})
   
def run():
   topo = MyTopologia() #istanziamento topologia di rete personalizzata
   net = Mininet(topo=topo, waitConnected=True) 
   net.start()
   router = net.getNodeByName("r0")
   _intf0 = Intf("enp0s3", node=router) #interfaccia enp0s3 configurata come router
   router.cmd('dhclient enp0s3') #assegna tramite dhclinet indirizzo (?)
   router.cmd("ifconfig r0-eth1 10.0.0.1 netmask 255.255.255.0")
   router.cmd("ifconfig 192.168.0.1 netmask 255.255.255.0")
   router.cmd("iptables -t nat -A POSTROUTING -o enp0s3 -j MASQUERADE") #regole di NAT per router
   
   CLI(net)
   net.stop()


if __name__ == "__main__":
   setLogLevel("info")
   run()
