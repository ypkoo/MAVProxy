import sys

if len(sys.argv) != 2:
	sys.exit(0)

filename = sys.argv[1]
# index = sys.argv[2]

f = open(filename, 'r')

for line in f.readlines():
	if len(line.split()) == 2:
		print line.split(':')[1].strip()

