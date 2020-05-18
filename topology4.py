
from mininet.topo import Topo


class advTopo(Topo):
    "Advanced Topology"

    def __init__(self):
        "Create custom topo."

        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches

        h4 = self.addHost('h4', ip="10.0.1.2/24", defaultRoute="via 10.0.1.1")
        h5 = self.addHost('h5', ip="10.0.1.3/24", defaultRoute="via 10.0.1.1")
        h6 = self.addHost('h6', ip="10.0.1.4/24", defaultRoute="via 10.0.1.1")
        h7 = self.addHost('h7', ip="10.0.2.2/24", defaultRoute="via 10.0.2.1")
        h8 = self.addHost('h8', ip="10.0.2.3/24", defaultRoute="via 10.0.2.1")
        h9 = self.addHost('h9', ip="10.0.2.4/24", defaultRoute="via 10.0.2.1")
        h10 = self.addHost('h10', ip="10.0.3.2/24",
                           defaultRoute="via 10.0.3.1")
        h11 = self.addHost('h11', ip="10.0.3.3/24",
                           defaultRoute="via 10.0.3.1")
        h12 = self.addHost('h12', ip="10.0.3.4/24",
                           defaultRoute="via 10.0.3.1")

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # Add links
        self.addLink(h4, s1)
        self.addLink(h5, s1)
        self.addLink(h6, s1)
        self.addLink(h7, s2)
        self.addLink(h8, s2)
        self.addLink(h9, s2)
        self.addLink(h10, s3)
        self.addLink(h11, s3)
        self.addLink(h12, s3)
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s3)


topos = {'topology4': (lambda: advTopo())}
