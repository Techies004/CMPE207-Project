

from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.addresses as addresses
import pox.lib.packet as pocket
from pox.lib.packet.arp import arp
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
log = core.getLogger()


class Tutorial (object):


    def __init__(self, connection):
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # Taction = of.ofp_action_output(port = out_port)his binds our PacketIn event listener
        connection.addListeners(self)

        # Use this table to keep track of which ethernet address is on
        # which switch port (keys are MACs, values are ports).
        self.mac_to_port = {}
        self.arp_cache = {}
        self.store = None
        self.routerip = ["10.0.1.1", "10.0.2.1", "10.0.3.1"]
        self.routing_table = {'10.0.1.0/24': ['10.0.1.100', 's1-eth1', '10.0.1.1', 1], '10.0.2.0/24': [
            '10.0.2.100', 's1-eth2', '10.0.2.1', 2], '10.0.3.0/24': ['10.0.3.100', 's1-eth3', '10.0.3.1', 3]}

    def resend_packet(self, packet_in, out_port):
        """
        Instructs the switch to resend a packet that it had sent to us.
        "packet_in" is the ofp_packet_in object the switch had sent to the
        controller due to a table-miss.
        """
        msg = of.ofp_packet_out()
        msg.data = packet_in

        # Add an action to send to the specified port
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)

        # Send message to switch
        self.connection.send(msg)

    def act_like_hub(self, packet, packet_in):
        """
        Implement hub-like behavior -- send all packets to all ports besides
        the input port.
        """

        # We want to output to all ports -- we do that using the special
        # OFPP_ALL port as the output port.  (We could have also used
        # OFPP_FLOOD.)
        self.resend_packet(packet_in, of.OFPP_ALL)

        # Note that if we didn't get a valid buffer_id, a slightly better
        # implementation would check that we got the full data before
        # sending it (len(packet_in.data) should be == packet_in.total_len)).

    def act_like_switch(self, packet, packet_in):
        """
        Implement switch-like behavior.
        """
        # Here's some psuedocode to start you off implementing a learning
        # switch.  You'll need to rewrite it as real Python code.

        # Learn the port for the source MAC
        self.mac_to_port[packet.src] = packet_in.in_port
        if packet.dst in self.mac_to_port:
            # Send packet out the associated port
            #self.resend_packet(packet_in, self.mac_to_port[packet.dst])

            # Once you have the above working, try pushing a flow entry
            # instead of resending the packet (comment out the above and
            # uncomment and complete the below.)

            log.debug("port %d mapped to MAC %s" %
                      (self.mac_to_port[packet.dst], packet.dst))
            # Maybe the log statement should have source/destination/port?
            msg = of.ofp_flow_mod()
            # Set fields to match received packet

            msg.match = of.ofp_match.from_packet(packet)
            msg.data = packet_in
            #
            # < Set other fields of flow_mod (timeouts? buffer_id?) >
            #
            # < Add an output action, and send -- similar to resend_packet() >
            action = of.ofp_action_output(port=self.mac_to_port[packet.dst])
            msg.actions.append(action)
            self.connection.send(msg)

        else:
            # Flood the packet out everything but the input port
            # This part looks familiar, right?
            self.resend_packet(packet_in, of.OFPP_ALL)

    """
  def act_like_router(self,frame,packet_in):
  	if frame.type == 0x0806:
		packet = frame.payload
		network = 0
		if packet.opcode == 1 and packet.protodst in self.routerip: #arp request and ip dst in routing table 
			arp_data = arp(hwtype = packet.hwtype, prototype = packet.prototype, hwlen = packet.hwlen, protolen = packet.protolen, opcode = 2, hwdst = packet.hwsrc, protodst = packet.protosrc, protosrc = packet.protodst, hwsrc = addresses.EthAddr('FA:DE:DD:ED:AF:AA'))
			e_frame = ethernet(type = 0x0806, src=addresses.EthAddr('FA:DE:DD:ED:AF:AA'), dst=packet.hwsrc)
			e_frame.payload = arp_data
			out_packet = of.ofp_packet_out()
			out_packet.data = e_frame.pack()
			action = of.ofp_action_output(port = packet_in.in_port)
			out_packet.actions.append(action)
			self.connection.send(out_packet)
		
		elif (packet.opcode == 2):
			self.arp_cache[packet.protosrc] = packet.hwsrc
			to_send = self.store.payload
			
			for nw in self.routing_table:
				nw1 = self.routing_table[nw]
				if str(to_send.dstip) in nw1:
					network = nw
					break
			
			message = of.ofp_packet_out()

			action = of.ofp_action_output(port = self.routing_table[network][3])

			self.store.src = addresses.EthAddr('FA:DE:DD:ED:AF:AA')
			self.store.dst = self.arp_cache[to_send.dstip]
			message.data = self.store.pack()
			message.actions.append(action)
			self.connection.send(message)
			log.debug("ICMP: sent from router to host" )

			message = of.ofp_flow_mod()
			message.match.nw_dst = to_send.dstip
			message.match.dl_type = 0x0800
					
			message.actions.append(of.ofp_action_dl_addr.set_src(self.store.src))
			message.actions.append(of.ofp_action_dl_addr.set_dst(self.store.dst))
			message.actions.append(of.ofp_action_output(port = self.routing_table[network][3]))
			log.debug("Flow Mode install  Successfully")
			self.connection.send(message)				
			self.store = None
	elif frame.type == 0x0800:
		network = 0
                for nw in self.routing_table.keys():
                         nw1 = self.routing_table[nw]
                	 if str( frame.payload.dstip) in nw1:
                         	 network = nw
                                 break
                packet = frame.payload

		if network == 0:
			unreachable_type = pocket.unreach()
			unreachable_type.payload = frame.payload	
			icmp_type = pocket.icmp()
			icmp_type.type = 3
			icmp_type.payload = unreachable_type
			ip_type = pocket.ipv4(srcip = frame.payload.dstip, dstip = frame.payload.srcip, protocol = 1, payload = icmp_type)
	 		ethernet_type = pocket.ethernet(type = 0x0800, src = frame.dst, dst=frame.src, payload = ip_type)
	 		message = of.ofp_packet_out()
	 		message.data = ethernet_type.pack()
	 		message.actions.append(of.ofp_action_output(port = packet_in.in_port))
	 		self.connection.send(message)
	
		elif packet.protocol == 1:
			data_icmp = packet.payload
			if data_icmp.type == 8 and packet.dstip in self.routerip:
				echo_type = pocket.echo(seq = data_icmp.payload.seq + 1, id = data_icmp.payload.id)
				icmp_type = pocket.icmp(type = 0, payload = echo_type)
				ip_type = pocket.ipv4(srcip = packet.dstip, dstip = packet.srcip, protocol = 1, payload = icmp_type)
	                        ethernet_type = pocket.ethernet(type = 0x0800, src = frame.dst, dst=frame.src, payload = ip_type)
	                        message = of.ofp_packet_out()
        	                message.data = ethernet_type.pack()
                	        message.actions.append(of.ofp_action_output(port = packet_in.in_port))
                        	self.connection.send(message)
			elif packet.dstip not in self.arp_cache:
				self.store = frame
				arp_type = arp(hwlen = 6, hwdst = ETHER_BROADCAST, protodst = packet.dstip, hwsrc = addresses.EthAddr('FA:DE:DD:ED:AF:AA'), protosrc = packet.srcip)
				arp_type.opcode = 1
				ethernet_type = ethernet(type=0x0806, src=addresses.EthAddr('FA:DE:DD:ED:AF:AA'),dst=ETHER_BROADCAST)
				ethernet_type.set_payload(arp_type)
				message = of.ofp_packet_out()
				message.data = ethernet_type.pack()
				message.actions.append(of.ofp_action_output(port = self.routing_table[network][3]))
				message.in_port = packet_in.in_port
				self.connection.send(message)
			elif packet.dstip in self.arp_cache:
				message = of.ofp_packet_out()

				action = of.ofp_action_output(port = self.routing_table[network][3])

				frame.src = addresses.EthAddr('FA:DE:DD:ED:AF:AA')
				frame.dst = self.arp_cache[packet.dstip]
				message.data = frame.pack()
				message.actions.append(action)
				self.connection.send(message)

				message = of.ofp_flow_mod()
				message.match.nw_dst = packet.dstip
				message.match.dl_type = 0x0800
				
				message.actions.append(of.ofp_action_dl_addr.set_src(frame.src))
				message.actions.append(of.ofp_action_dl_addr.set_dst(frame.dst))
				message.actions.append(of.ofp_action_output(port = self.routing_table[network][3]))
				self.connection.send(message)
			
    """

    def _handle_PacketIn(self, event):
        """
        Handles packet in messages from the switch.
        """

        packet = event.parsed  # This is the parsed packet data.

        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return
        elif packet.find('tcp'):
            if packet.find('tcp').srcport == 5001 or packet.find('tcp').dstport == 5001:
                event.halt == True
                log.debug(" blocked iperf")
            else:
                packet_in = event.ofp
                self.act_like_switch(packet, packet_in)
        else:
            packet_in = event.ofp  # The actual ofp_packet_in message.

        # Comment out the following line and uncomment the one after
        # when starting the exercise.
        #self.act_like_hub(packet, packet_in)
            self.act_like_switch(packet, packet_in)
        #self.act_like_router(packet, packet_in)


def launch():
    """
    Starts the component
    """
    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Tutorial(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
