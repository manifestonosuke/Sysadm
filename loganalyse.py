#!/usr/bin/python2

'''
	TODO 
		DONE   setup the sample metric like second minute hour day ...
		DONE   select date to display (like -D 23/Oct/2014)
		3   review the ugly print statement
		DONE   replace old debug style with Message class 
		5   Improve message class to set hierachie in debug level
		6	Add a picle option (need struct passed as json) to save/load data
'''


import os 
import sys
import getopt

PRGNAME=os.path.basename(sys.argv[0])


def usage():
		global PRGNAME
		print PRGNAME,"usage"
		print '''
		loganalyze -f FILE 
		-A	  Analyze all the file
		-c	  Analyze only this count of files
		-d	  Debug
		-f	  Use file 
		-u	  Unit to sort data (hour/minute ...)
		-x	  Use csv format

		-D	  Specify a day to display (format as original log file ie apache 01/Jan/2011)
		-H	  Specif an hour like 12 for 12h, 12:00 for 12h 00 mn 
		'''

def parseargs(argv):
		try:
				opts, args = getopt.getopt(argv, "Ac:dD:hH:f:o:u:x", ["help", "url="])
		except getopt.GetoptError:
				usage()
				sys.exit(2)
		#print "Parsing opt",opts,"arg",args
		global option
		global DEBUG
		for i,el in enumerate(opts):
				if '-d' in el:
						"remove -d arg from opts string and go debug"
						opts.pop(i)
						Message.setlevel('debug')
						Message.debug(PRGNAME,"going debug, remaining args "+str(opts)+" "+str(args))
				else:
						Message.setlevel('info')
		for opt, arg in opts:
				if opt in ("-h", "--help"):
						usage()
						sys.exit()
				elif opt == '-A':
						option['ALL'] = 1
				elif opt == '-c':
						option['count'] = arg
				elif opt == '-d':
						DEBUG = 1
				elif opt == "-D":
						option['day']=arg 
				elif opt in "-f":
						option['file']=arg
						#print "using File "+file,
				elif opt in "-H":
						option['day']=arg 
				elif opt in "-u":
						option['unit']=arg 
				elif opt in "-x":
						option['format']='csv'
				elif opt in "-o":
						option['operation']=arg

class Message:
		"""
		print message according method and attribute
		if attribute level is set to certain value one can display more messages
		sample : if level is set to debug call to method debug will display message
				otherwise it will be silent
		"""
		level=""
		level_value=[ 'info','debug','verbose','run','error','fatal','silent','warning']
		def __init__(self):
				Message.level=""

		def setlevel(cls,level):
				if not level in Message.level_value:
						print("FATAL\t:\tlevel {} not defined".format(Message.level))
						raise ValueError("undefined value for Message class")
				Message.level=level
		setlevel=classmethod(setlevel)

		def getlevel(cls,display=0):
				if len(Message.level) == 0:
						return('unset')
				if display == 1:
					print "Message level : "+str(Message.level) 
				return(Message.level)
		getlevel=classmethod(getlevel)

		def info(cls,p,m):
				print("%-10s : %-10s : %-30s" % ("INFO",p,m))
		info=classmethod(info)

		def warning(cls,p,m):
				print("%-10s : %-10s : %-30s" % ("WARNING",p,m))
		warning=classmethod(warning)

		def debug(cls,p,m):
				if Message.level == 'debug':
						print("%-10s : %-10s : %-30s" % ("DEBUG",p,m))
		debug=classmethod(debug)

		def verbose(cls,p,m):
				if Message.level == 'verbose':
						print("%-10s : %-10s : %-30s" % ("VERBOSE",p,m))
		verbose=classmethod(verbose)

		def run(cls,p,m):
				if Message.level == 'run':
						print("%-10s : %-10s : %-30s" % ("INFO",p,m))
		run=classmethod(run)

		def error(cls,p,m):
				print("%-10s : %-10s : %-30s" % ("ERROR",p,m))
		error=classmethod(error)

		def fatal(cls,p,m,extra=99):
				print("%-10s : %-10s : %-30s" % ("FATAL",p,m))
				end(extra)
		fatal=classmethod(fatal)

		def test(cls):
				print("level",Message.level)
				print("level_value",Message.level_value)
		test=classmethod(test)

#msg=Message()
#msg.setlevel('debug')

class Logfile:
	def __init__(self,logfile,kind="apache"):
		self.logfile=logfile
		self.kind=kind
		if logfile == "":
			print "ERROR : no file provided"
			exit(2)
		try:
			self.fd=open(logfile)
		except:
			print "ERROR : could not open file "+logfile
			raise IOError

	def readone(self):
		l=self.fd.readline()
		#Message.debug('readone',l)
		if not l:
			return(0)
		self.line=l
		return(1)

	def printline(self):
		print self.line,
		return(self.line)


	def prepare(self):
		if self.kind=="apache":
			self.fulldate=self.line.split("[")[1].split("]")[0]
			self.payload=self.line.split('"')[1]
			self.day,self.hour,self.minute,self.second=self.fulldate.split()[0].split(':')
			self.hms=self.hour+":"+self.minute+":"+self.second
			self.ms=None
			self.elapsed=self.line.split('*')[1]
			#self.all={'fulldate':fulldate}
		else:
			raise valueError


	def unit(self,value):
		if value in 'second':
			return self.second
		elif value in 'minute':
			return self.minute
		elif value in 'hour':
			return self.hour 
		elif value in 'day':
			return self.day
		elif value in 'month':
			return self.month
		else:
			raise Exception("Unit not valid")

def displaylinestat(this,option,date,hour):
	print '{0}{1}{2}{3}'.format(date,csvchar,hour,csvchar),
	for i in PATTERN:
		if i in this.keys():
			if 'csv' in option:
				value=this[i]+0
				print str(this[i])+csvchar,
			else:
				print '{0}:{1} '.format(i,str(this[i])),
		else:
			if 'csv' in option:
				print '{0}{1}'.format(0,str(csvchar)),
			else:
				print '{0}:{1} '.format(i,'0'),
		#if 'debug' in option: print this   
		this[i]=0
	return(this)

#process_elapsed_bydate(result,Log.day,Log.hms,Q,Log.elapsed)a
# { result { substruct { 
#{ 'date ' : { 'hour' : { 'GET' : [ 1 , 2 ] }, 'PUT' : [ total , count] }} 
# results struct content the data /sec 
def process_elapsed_bydate(result,date,time,operation,elapsed):
	substruct={}
	if not date in result.keys():
		substruct[time]={}
		substruct[time][operation]=[elapsed,1]
		result[date]=substruct
		return(result)

	substruct=result[date]	
	if not time in substruct:
		#print date+":"+time+":"+operation
		result[date][time]={}
		result[date][time][operation]=[elapsed,1]
		return(result)

	if operation in substruct[time]:
		total=0 
		count=0
		total=substruct[time][operation][0]
		#count=substruct[time][operation][1]
		result[date][time][operation][0]=total+elapsed
		result[date][time][operation][1]+=1
	else:
		#substruct[time]=result[date][time]
		#substruct[time][operation]=[elapsed,1]
		result[date][time][operation]=[elapsed,1]
	return(result)		

# Get a list of data sorted /sec and display according time value /day /sec /minute ..  
def display_results(result,option={}):
	prevday=day=None
	prevhour=hour=None
	prevmin=minute=None
	prevsec=second=None
	# total['GET'][0]=total ... GET[1]=count
	total={}
	output={}
	#for i in result.keys():
	#    for j in result[i].keys():
	#	print i,j,result[i][j]
	#return()
	if 'unit' in option:
	    unit=option['unit']
	else:
	    unit='second'
	#i=date, j=hms, k=get/put/del... 0=# 1=count
	if option['format']=='csv'and option['operation'] != 'elapsed' :
		print "#{0:12s}{1:8s}{2:7s}{3:7s}{4:7s}{5:7s}".format('day','time','GET','PUT','DELETE','HEAD')
	if option['format']=='csv'and option['operation'] == 'elapsed' :
		print "#{0:12s}{1:9s}{2:10s}{3:11s}{4:10s}{5:11s}{6:10s}{7:11s}{8:10s}{9:10s}".format('day','time','GET cnt','GET avg','PUT cnt','PUT avg','DEL cnt','DEL avg','HEAD cnt','HEAD avg')
	for i in sorted(result.keys()):
		if prevday==None: 
			prevday=i
			day=i
		for j in sorted(result[i].keys()):
			h,m,s=j.split(':')
			if prevhour==None: prevhour=h
			if prevmin==None: prevmin=m
			if prevsec==None: prevsec=-1
			
                        Message.debug(PRGNAME+":display_results",str(h)+","+str(m)+","+str(s)+","+str(prevsec))
			if unit == 'second' and prevsec != s:
			    time=h+":"+m+":"+str(s) 
			    total=display_results_print(total,i,time,option)
			    prevsec=s
			if unit == 'minute' and prevmin != m:
			    time=h+":"+m+":00" 
			    total=display_results_print(total,i,time,option)
			    prevmin=m
			if unit == 'hour' and prevhour != h:
			    time=prevhour+":"+m+":00" 
			    total=display_results_print(total,i,time,option)
			    prevhour=h
			if unit == 'day' and prevday != day:
			    total=display_results_print(total,prevday,time,option)
			    prevday=d

			Message.debug(PRGNAME+":display_results",result[i][j])
			PATTERN=sorted(result[i][j].keys())
			for k in PATTERN:
			    if k not in total.keys():
				#print k,total,result[i][j][k][0]
				total[k]=[result[i][j][k][0],0]
				total[k][1]=result[i][j][k][1]
			    else:
				total[k][0]=result[i][j][k][0]+total[k][0]
				total[k][1]=result[i][j][k][1]+total[k][1]
			    #print k+"|"+str(count)+"|"+str(avg)+"|", 
			    #print k+"|"+str(count),
	if unit != 'second':
	    display_results_print(total,i,j,option)


def display_results_print(list,date,time,option):
	""" get a list and display it while calculing stats"""
	print date+" "+time+" ",
	# total['GET'][0]=total ... GET[1]=count
	# csv need to have 0 value when entry is not found
	if option['format']=='csv':
	#print "{0:12s}{1:9s}{2:6s}{3:6s}{4:6s}{5:6s}".format('day','time','GET','PUT','DELETE','HEAD')
		pattern=['GET','PUT','DEL','HEAD']
	else:
		pattern=sorted(list.keys())
	for k in pattern:
		if k not in list:
			count="0"
			avg="0"
		else:
			count=str(list[k][1])
			if not list[k][1] == 0:
				avg=list[k][0]/list[k][1]
			else:
				avg=0
		if option['format']=='csv'and option['operation'] == 'elapsed':
			print "{0:10s}{1:10s}".format(count,str(avg)),
		elif option['format']=='csv':
			print "{0:10s}".format(count),
		else:
			if option['operation'] == 'elapsed':
				display='{2}:{0}|{1}|\t'.format(avg,count,k)
			else:
				display='{0}|{1}\t'.format(count,k)
				#print k+"|"+display,
			print display,
		if k in list:
			del list[k]
	print
	return(list)


def calculate_elasped(this,total,date,hour):
	print date+" "+hour,
	for i in total.keys():
		if this[i] != 0:
			avg=total[i]/this[i]
		else:
			avg=0
		print i+"("+str(this[i])+")"+" : "+str(avg),
	print
	#print 'end elapsed'

#default option count rest command
option={'operation':'rest'}

file=""
option['file']=file
option['count']=-1
option['format']="list"
kind="apache"



if (len(sys.argv) != 1) :
	parseargs(sys.argv[1:])


if 'csv' in option:
	csvchar=';'
else:
	csvchar=" "

if 'ALL' in option:
	refday=""

if 'csv' in option:
	print 'date'+csvchar+'hour'+csvchar+'PUT'+csvchar+'GET'+csvchar+'DELETE'+csvchar+'HEAD'




#if __name__ != '__main__':
#	exit()

if 'unit' in option:
	zzzz=option['unit']
else:
	zzzz='minute'

#Message.setlevel('info')
Message.getlevel()

PATTERN=('PUT','GET','DELETE','HEAD')
displaydate=""
prevhms=-7
def main(option):
	Message.debug(PRGNAME,":"+option['operation']+":")
	Log=Logfile(option['file'],kind)
	result={}
	counted=0 
	count=0 
	while True:
		l=Log.readone() 
		if not l:
			""" no more lines in the file """ 
			Message.debug(PRGNAME,"EOF for file "+file)
			if counted != 0:
				print
				display_results(result,option)
				#this=displaylinestat(this,option,displaydate,prevhms)
			else:
				Message.info(PRGNAME,"no line selected")
			break
		Log.prepare()
		#	Ignore line not in option['day']
		if 'day' in option:
			if Log.day != option['day']:
				continue
		else:
			counted+=1
		count+=1
		if count%100 == 0: 
			#print '\r>> You have finished %d%%' % i,
			#print '\rLine browsed %d' %count,
			msg='\rLine browsed '+str(count) 
			sys.stderr.write(msg)
		Q=Log.payload.split()[0]
		if Q == 'DELETE': 
		    Q='DEL'
		Message.debug(PRGNAME,"Op is : "+Q)
		result=process_elapsed_bydate(result,Log.day,Log.hms,Q,int(Log.elapsed))
	# to treat where no data
	#display_results(result,option)
	exit(0)

if __name__ == '__main__':
	main(option)
