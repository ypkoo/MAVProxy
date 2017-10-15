import sys

import pandas as pd

if (len(sys.argv) != 2): 
	print "Usage: log_analyzer [logfile.txt]"
	sys.exit(0)

TARGET_LOG = sys.argv[1]
NON_RADIO_TYPES = ['ATTITUDE_TARGET', 'BATTERY_STATUS', 'EXTENDED_SYS_STATE', 'HEARTBEAT', 'SYSTEM_TIME', 'SYS_STATUS', 'VFR_HUD']

def time_diff_sec(start_, end_):
	""" remove brackets and split"""
	start = start_[1:-1].split(':')
	end = end_[1:-1].split(':')

	start = [float(i) for i in start]
	end = [float(i) for i in end]

	h_diff = (end[0] - start[0]) % 24
	m_diff = (end[1] - start[1])
	s_diff = (end[2] - start[2])

	return h_diff*3600 + m_diff*60 + s_diff


def main():
	df = pd.read_csv(TARGET_LOG, names=['time', 'seq', 'type'], delim_whitespace=True)
	start_index = df.index[df['seq'] == 'JAMMING_START'].tolist()
	stop_index = df.index[df['seq'] == 'JAMMING_STOP'].tolist()
	# df.drop(df.index[start_index], inplace=True)
	# df.drop(df.index[stop_index], inplace=True)
	if len(start_index) == 1 and len(stop_index) == 1:
		df = df[start_index[0] + 1: stop_index[0]]
		print df.shape[0]

	start_time = df.iloc[0]['time']
	end_time = df.iloc[-1]['time']

	non_radio_packets = df.loc[df['type'].isin(NON_RADIO_TYPES)]

	sent_num = 0
	dropped_num = 0
	cur_seqnum = int(non_radio_packets.iloc[0]['seq'][1:-1])

	non_radio_packets = non_radio_packets.iloc[1:]

	for index, row in non_radio_packets.iterrows():
		# print index, cur_seqnum
		s = int(row['seq'][1:-1])
		next_seqnum = cur_seqnum + 1
		gap = (s - next_seqnum) % 256

		sent_num += 1 + gap
		dropped_num += gap

		cur_seqnum = s

	received_num = sent_num - dropped_num

	time_diff = time_diff_sec(start_time, end_time)

	types = sorted(df.type.unique())

	""" remove nan """
	types = [t for t in types if str(t) != 'nan']

	print types

	for t in types:
		count = df[df['type'] == t].shape[0]
		print t+': ', count/time_diff

	print """
sent: %d
received: %d
dropped: %d
jamming rate: %f
	""" % (sent_num, received_num, dropped_num, float(dropped_num)/float(sent_num))

if __name__ == '__main__':
	main()