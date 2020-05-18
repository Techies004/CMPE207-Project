
from mininet.topo import Topo


class advTopo(Topo):
    "Advanced Topology"

    def __init__(self):
        "Create custom topo."

        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches

        h3 = self.addHost('h3', ip="10.0.1.2/24", defaultRoute="via 10.0.1.1")
        h4 = self.addHost('h4', ip="10.0.1.3/24", defaultRoute="via 10.0.1.1")
        h5 = self.addHost('h5', ip="10.0.2.2/24", defaultRoute="via 10.0.2.1")

        S1 = self.addSwitch('s1')
        S2 = self.addSwitch('s2')

        # Add links
        self.addLink(h3, S1)
        self.addLink(h4, S1)
        self.addLink(h5, S2)
        self.addLink(S1, S2)


topos = {'topology3': (lambda: advTopo())}
