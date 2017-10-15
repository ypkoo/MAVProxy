#!/usr/bin/env python
'''
Example Module
Peter barker, September 2016

This module simply serves as a starting point for your own MAVProxy module.

1. copy this module sidewise (e.g. "cp mavproxy_example.py mavproxy_coolfeature.py"
2. replace all instances of "example" with whatever your module should be called
(e.g. "coolfeature")

3. trim (or comment) out any functionality you do not need
'''

import os
import os.path
import sys
from pymavlink import mavutil
import errno
import time
from datetime import datetime
from threading import Timer

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import mp_settings

class MAVPacketLogger(object):
	def __init__(self, filename):
		self.f = open(filename, 'w')

	def log(self, m):
		self.f.write("[%s] %s\n" % (datetime.now().strftime('%H:%M:%S.%f'), m))

	def __del__(self):
		self.f.close()




class PacketMonitorModule(mp_module.MPModule):
	def __init__(self, mpstate):
		"""Initialise module"""
		super(PacketMonitorModule, self).__init__(mpstate, "monitor", "monitoring MAVLink packets")
		self.status_callcount = 0
		self.boredom_interval = 10 # seconds
		self.last_bored = time.time()
		self.jamming_on = False
		self.cur_seqnum = None
		self.cur_radio_seqnum = None
		self.cur_radio_status_seqnum = None

		#self.logfile = open('packet_log.txt', mode='w') # possible extension: receive filename as an argument
		pathname = os.path.abspath('log/')
		filename = datetime.now().strftime('%m%d_%H%M') + ".txt"

		full_filename = os.path.join(pathname, filename)

		self.logger = MAVPacketLogger(full_filename)


		self.packets_mytarget = 0
		self.packets_othertarget = 0
		self.verbose = False

		self.example_settings = mp_settings.MPSettings(
			[ ('verbose', bool, False),
		  ])
		self.add_command('jamming', self.cmd_jamming, "jamming")

	def usage(self):
		'''show help on command line options'''
		return "Usage: jamming <start [duration_in_minute]|stop>"

	def cmd_jamming(self, args):

		if len(args) == 0:
			print self.usage()
		elif args[0] == "start":
			if len(args) != 2:
				print self.usage()
			elif self.jamming_on == False:
				try:
					jamming_duration = int(args[1])
				except ValueError:
					print self.usage()
					return
				
				t = Timer(jamming_duration * 60, self.jamming_stop)
				t.start()
				self.logger.log("JAMMING_START")
				print 'Jamming start (%dmin)' % jamming_duration
				self.jamming_on = True
			else:
				print "Jamming signal is already on"
		elif args[0] == "stop":
			if self.jamming_on == True:
				self.logger.log("JAMMING_STOP")
				print 'Jamming stop'
				self.jamming_on = False
			else:
				print "Jamming signal is already off"



	def idle_task(self):
		'''called rapidly by mavproxy'''
		pass

	def jamming_stop(self):
		if self.jamming_on == True:
			self.logger.log("JAMMING_STOP")
			print 'Jamming stop'
			self.jamming_on = False

	def mavlink_packet(self, m):
		'''handle mavlink packets'''
		t = m.get_type()
		s = int(m.get_seq())

		if t == 'RADIO':
			if self.cur_radio_seqnum:
				next_seqnum = self.cur_radio_seqnum + 1
				gap = (s - next_seqnum) % 256

				if gap != 0:
					dropped = range(next_seqnum, next_seqnum + gap)
					dropped = [i % 256 for i in dropped]
					print '[RADIO]: %s got dropped' % str(dropped)

			self.cur_radio_seqnum = s
		elif t == 'RADIO_STATUS':
			if self.cur_radio_status_seqnum:
				next_seqnum = self.cur_radio_status_seqnum + 1
				gap = (s - next_seqnum) % 256

				if gap != 0:
					dropped = range(next_seqnum, next_seqnum + gap)
					dropped = [i % 256 for i in dropped]
					print '[RADIO_STATUS]: %s got dropped' % str(dropped)

			self.cur_radio_status_seqnum = s
		else:
			if self.cur_seqnum:
				next_seqnum = self.cur_seqnum + 1
				gap = (s - next_seqnum) % 256

				if gap != 0:
					dropped = range(next_seqnum, next_seqnum + gap)
					dropped = [i % 256 for i in dropped]
					print '[NON_RADIO]: %s got dropped' % str(dropped)

			self.cur_seqnum = s
			

		log_msg = "[%s] %s" % (s, t)
		self.logger.log(log_msg)


		

def init(mpstate):
	'''initialise module'''
	return PacketMonitorModule(mpstate)
