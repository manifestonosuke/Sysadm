#!/usr/bin/python
import re 
import sys
import time

# This program can be called without are and will use 
# this default file name to read as input
logfile="/admin/central/tmp/WWONAIRP.slowquery.log"
#logfile="test.log"

# log query time
# Queries less than logtime will be ignored
longtime=10.0
querytime=0.0

# initalise query as string
query=''

# Set the flags for regex 
p_querytime=re.compile("# Query_time:")
p_timestamp=re.compile("SET timestamp=")

# 
lineread=0
linematch=0
sorted=0

# When match limit is reached program will end 
# to avoid using too much memory 
matchlimit=100000

# Results dict for sorted output 
rez={}


# Basic argv processing 
# -s will go to sorted output based on the rez{} dictionnary
# last arg will be treated as input file
if len(sys.argv) > 1 :
	for i in sys.argv[1:]:
		if i == '-s' : 
			sorted=1
			sys.argv.remove(i)
			print "Sorted output chosen if can take time"
			time.sleep(1)
		else:
			if len(sys.argv) == 2:
				print "using {0} as input file".format(sys.argv[1])
				logfile=sys.argv[1]
				
			else:
				print "argument error : {0} is not valid".format(i)
				exit(0)

# Open input file and exit if error
try:
	f=open(logfile,"r")
except IOError:
	print "Cant read file "+str(logfile)	
	exit(9)

# End program with closing file and
# display rez dict if sorted is set to 1
def closeandout():
	if sorted == 1:
		outrez(rez)
	print "{0} total lines read".format(lineread)
	f.close()
	exit(0)

# Read the dict struct and show a summary for each query 
def outrez(dict):
	for i in dict:
		print i
		#print dict[i]
		nb=0.0
		total=0.0
		for j in dict[i]:
			total+=float(j)
			nb+=1.0
		avg=total/nb
		print "SQL called {0} times, min time is {1}, max {2}, average {3}\n".format(nb,min(dict[i]),max(dict[i]),avg)
		#q=raw_input() 

def read_one_line():
	global lineread
	global line
	line=f.readline().rstrip()
	if line == "": closeandout()
	lineread+=1
		
# This loop end when EOF is reached means readline return ""
lineread=0
while 1:
	query=""
	read_one_line()
	# Read until find a query time tag
	if p_querytime.match(line):
		querytime=line.split(" ")[2]
		# if query time above longtime setting process it
		if float(querytime) > longtime:
			read_one_line()

			#exclude all line until timestamp
			while not p_timestamp.match(line):
				read_one_line()
			# Convert timestamp EPOCH format to human readable
			timestamp=re.split(p_timestamp,line)[1]
			timestamp=timestamp[:len(timestamp)-1]
			timestamp=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(timestamp)))
			read_one_line()
			# then read all lines until # for the query 
			while not line[0] == '#':
				query+=line.rstrip()
				read_one_line()
			query=re.sub(" +"," ",query)
			# If sorted is 0 then display 
			if sorted == 0 :
				print querytime+" : "+timestamp+" : "+query
				print
			# il sorted not 0 then build the rez dict.
			else:
				if query in rez:
					#print "\n EXIST "+querytime+query
					rez[query].append(querytime)
					#q=raw_input() 
				else:
					#print "\n NEW "+querytime+query
					rez.update({query:[querytime]})
		else:
			pass
	# If sorted mode show a count of entries read	
	if sorted == 1:	
		print lineread,"\rlines read ",
	

	if linematch > matchlimit:
		print "Stopping now as too much (limit set to {2}) lines match, {0} entry match for {1} lines read".format(linematch,lineread,matchlimit)
		closeandout()
closeandout()
