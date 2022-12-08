from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo( Topo ):
    def __init__( self ):
        
        topology = ''
        Topo.__init__( self )

        leftHost = self.addHost( 'hLeft' )
        rightHost = self.addHost( 'hRight' )
        leftSwitch = self.addSwitch( 's1' )
        upSwitch = self.addSwitch( 's2' )
        downSwitch = self.addSwitch( 's3' )
        rightSwitch = self.addSwitch( 's4' )
        
        #hosts
        self.addLink( leftHost, leftSwitch, cls = TCLink, bw=1000,delay='0ms' )
        self.addLink( rightHost, rightSwitch , cls = TCLink, bw=1000,delay='0ms')
        
    

        #switches
        constant = dict(bw=8000,delay='100ms')
        linear =  dict(bw=80,delay='0ms')
        teleportation = dict(bw=8000, delay='0ms')

    

        
        self.addLink( leftSwitch, upSwitch ,cls = TCLink, bw=1,delay='1ms')
        self.addLink( leftSwitch, downSwitch,cls = TCLink, bw=1000,delay='500ms')
        self.addLink( upSwitch, downSwitch, cls = TCLink, bw=1000, delay='0ms')
        self.addLink( rightSwitch, upSwitch, cls = TCLink, bw=1000,delay='500ms')
        self.addLink( rightSwitch, downSwitch, cls = TCLink,bw=1,delay='1ms')

        
        self.addLink(leftSwitch, rightSwitch,cls = TCLink, bw=1000,delay='0ms')

topos = { 'mytopo': (lambda: MyTopo() ) }
