#!/usr/bin/python2

'''
	TODO 
		DONE   setup the sample metric like second minute hour day ...
		DONE   select date to display (like -D 23/Oct/2014)
		3   review the ugly print statement
		DONE   replace old debug style with Message class 
		5   Improve message class to set hierachie in debug level
		6	Add a picle option (need struct passed as json) to save/load data
                7   finalize classification of the Log related code
'''

from datetime import datetime
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
		-o option  Use specific option (see below) 
		-k	  specify log format (see below)
		-u	  Unit to sort data (hour/minute ...)
		-x	  Use csv format
                -T        TAG to search by default PUT/GET/DELETE/HEAD (still on dev)

		-D	  Specify a day to display (format as original log file ie apache 01/Jan/2011)
		-H	  Specif an hour like 12 for 12h, 12:00 for 12h 00 mn 

		supported option :
		elapsed : to display elapsed time with the default count

		supported log format :
		apache
		sproxyd
		'''

def parseargs(argv):
		try:
				opts, args = getopt.getopt(argv, "Ac:dD:hH:f:k:o:T:u:x", ["help", "url="])
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
						option['hour']=arg 
				elif opt in "-k":
						option['kind']=arg 
				elif opt in "-u":
						option['unit']=arg 
				elif opt in "-x":
						option['format']='csv'
				elif opt in "-o":
						option['operation']=arg
                                elif opt in "-p":
                                                if 'pickelin' not in option:
                                                    option['picklein']=[]
                                                option['picklein'].append(arg)
				elif opt in "-T":
						option['tag']=arg

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
				#print("%-10s : %-10s : %-30s" % ("ERROR",p,m))
				msg=format("%-10s : %-10s : %-30s" % ("ERROR",p,m))
				sys.stderr.write(msg)
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
                self.result={}
                self.tag=('PUT','GET','DELETE','HEAD')
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

        def settag(self,arg):
            self.tag=arg
            return

        # prepare data to be analyzed
	# fulldate format as apache : 03/Dec/2014:13:46:38
	def prepare(self):
		if self.kind=="apache" or self.kind=="dovecot" :
			self.fulldate=self.line.split("[")[1].split("]")[0]
			self.payload=self.line.split('"')[1]
			self.day,self.hour,self.minute,self.second=self.fulldate.split()[0].split(':')
			self.hms=self.hour+":"+self.minute+":"+self.second
			self.ms=None
                        if self.kind == "dovecot":
			    self.elapsed=self.line.split('*')[1]
                        else:
                            self.elapsed=self.line.split()[10]
			self.operation=self.payload.split()[0]
                        self.http_code=self.line.split()[8].strip('"')
			#self.all={'fulldate':fulldate}
			return True
		elif self.kind=="sproxyd":
			dict={}
			Message.debug(PRGNAME,self.line)
                        #if self.line.split()[7].split('"')[1] != 'end' :
			try:
				status=self.line.split()[7].split('"')[1]
			except IndexError:
				return 'LINEERROR'
			if status != 'end':
                            return None
			self.year=str(datetime.now().year)
			self.month=self.line.split()[0]
			self.day=str(self.line.split()[1])+'/'+self.month+'/'+self.year
			self.hms=self.line.split()[2]
			self.fulldate=str(self.day)+'/'+self.month+'/'+str(self.year)+':'+self.hms
			self.payload=self.line.split()[8:]
			self.hour,self.minute,self.second=self.hms.split(':')
			self.hms=self.hour+":"+self.minute+":"+self.second
			self.ms=None
			for k in self.payload:
				dict[k.split('=')[0]]=k.split('"')[1:]		
			self.elapsed=dict['elapsed'][0][:-2]
			self.operation=dict['method'][0]
			self.http_code=dict['http_code'][0]
			return True
			#print self.elapsed,self.hms,self.fulldate
                        #raw_input()
			#self.all={'fulldate':fulldate}
		else:
			raise valueError


	def unit(self,value):
		if value in ['second','minute','hour','day']: 
                        self.unit = value 
			#return self.second
			return 
		else:
			raise Exception("Unit not valid")

        #def aggragate_result(self,data,time,operation,elapsed):
        def aggragate_result(self,operation):
            #result,date,time,operation,elapsed
            #result,Log.day,Log.hms,Q,int(Log.elapsed))
            pass
	    substruct={}
	    if not self.day in self.result.keys():
		substruct[self.hms]={}
		substruct[self.hms][operation]=[self.elapsed,1]
		self.result[self.day]=substruct
		return()

	    substruct=self.result[self.day]	
	    if not self.hms in substruct:
		#print date+":"+time+":"+operation
		self.result[self.day][self.hms]={}
		self.result[self.day][self.hms][operation]=[self.elapsed,1]
		return()

	    if operation in substruct[self.hms]:
		total=0 
		count=0
		total=int(substruct[self.hms][operation][0])
		#count=substruct[time][operation][1]
		self.result[self.day][self.hms][operation][0]=total+int(self.elapsed)
		self.result[self.day][self.hms][operation][1]+=1
	    else:
		self.result[self.day][self.hms][operation]=[self.elapsed,1]
	    #return(result)		
    
        def display_results(self,option={}):
	    prevday=day=None
	    prevhour=hour=None
	    prevmin=minute=None
            prevsec=second=None
            # total['GET'][0]=total ... GET[1]=count
            total={}
            output={}
            #i=date, j=hms, k=get/put/del... 0=# 1=count
            if option['format']=='csv'and option['operation'] != 'elapsed' :
                print "#{0:12s}{1:9s}{2:8s}{3:8s}{4:8s}{5:8s}".format('day','time','GET','PUT','DELETE','HEAD')
            if option['format']=='csv'and option['operation'] == 'elapsed' :
                print "#{0:12s}{1:9s}{2:10s}{3:11s}{4:10s}{5:11s}{6:10s}{7:11s}{8:10s}{9:10s}".format('day','time','GET cnt','GET avg','PUT cnt','PUT avg','DEL cnt','DEL avg','HEAD cnt','HEAD avg')
            for i in sorted(self.result.keys()):
                if prevday==None: 
                    prevday=i
                    day=i
                for j in sorted(self.result[i].keys()):
                    h,m,s=j.split(':')
                    if prevhour==None: prevhour=h
                    if prevmin==None: prevmin=m
                    #if prevsec==None: prevsec=-1
                    if prevsec==None: prevsec=s
                    #print self.unit,h,m,s,prevhour,prevmin,prevsec
                    Message.debug(PRGNAME+":display_results",str(h)+","+str(m)+","+str(s)+","+str(prevsec))
                    if self.unit == 'second' and prevsec != s:
                        #time=h+":"+m+":"+str(s) 
                        time=prevhour+":"+prevmin+":"+str(prevsec)
                        total=display_results_print(total,i,time,option)
                        prevsec=s
                    if self.unit == 'minute' and prevmin != m:
                        time=prevhour+":"+prevmin+":00" 
                        #time=h+":"+prevmin+":"+s
                        total=display_results_print(total,i,time,option)
                        prevmin=m
                    if self.unit == 'hour' and prevhour != h:
                        time=prevhour+":"+m+":00" 
                        total=display_results_print(total,i,time,option)
                        prevhour=h
                    if self.unit == 'day' and prevday != day:
                        total=display_results_print(total,prevday,time,option)
                        prevday=d

                    Message.debug(PRGNAME+":display_results",self.result[i][j])
                    self.tag=sorted(self.result[i][j].keys())
                    for k in self.tag:
                        if k not in total.keys():
                            #print total
                            #print k,total,self.result[i][j][k][0]
                            total[k]=[self.result[i][j][k][0],0]
                            total[k][1]=self.result[i][j][k][1]
                        else:
                            #print self.result
                            #print total
                            total[k][0]=self.result[i][j][k][0]+int(total[k][0])
                            total[k][1]=self.result[i][j][k][1]+total[k][1]
                            #print k+"|"+str(count)+"|"+str(avg)+"|", 
		    #print k+"|"+str(count),
	    if self.unit != 'second':
	        display_results_print(total,i,j,option)


def display_results_print(list,date,time,option):
	""" get a list and display it while calculing stats"""
	print date+" "+time+" ",
	# total['GET'][0]=total ... GET[1]=count
	# csv need to have 0 value when entry is not found
	if option['format']=='dcsv':
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
				avg=int(list[k][0])/list[k][1]
			else:
				avg=0
		if option['format']=='csv'and option['operation'] == 'elapsed':
			print "{0:10s}{1:10s}".format(count,str(avg)),
		elif option['format']=='csv':
			print "{0:8s}".format(count),
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


#default option count rest command
option={'operation':'rest'}

file=""
option['file']=file
option['count']=-1
option['format']="list"



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
if 'kind' in option:
    kind=option['kind'] 
else:
    kind="apache"


#Message.setlevel('info')
Message.getlevel()

#tag=('PUT','GET','DELETE','HEAD')
displaydate=""
prevhms=-7
def main(option):
	Message.debug(PRGNAME,":"+option['operation']+":")
	Log=Logfile(option['file'],kind)
	result={}
	counted=0 
	count=0 
        if 'unit' in option:
            Log.unit(option['unit'])
        else:
	    Log.unit('minute')
        if 'tag' in option:
            Log.settag(option['tag'])
	while True:
		l=Log.readone() 
		count+=1
		if not l:
			""" no more lines in the file """ 
			Message.debug(PRGNAME,"EOF for file "+file)
			if counted != 0:
				print
				#display_results(Log.result,option)
				Log.display_results(option)
			else:
				Message.info(PRGNAME,"no line selected")
			break
		#Log.prepare()
		linestatus=Log.prepare()
                if linestatus == None :
                    continue
		elif linestatus == 'LINEERROR':
		    Log.printline() 
		    Message.error(PRGNAME,"Ignoring error reading line "+str(count)) 	
		    continue
		#	Ignore line not in option['day']
		if 'day' in option:
			if Log.day != option['day']:
				continue
		if 'hour' in option:
			if Log.hour != option['hour']:
				continue
			Message.debug(PRGNAME,'counted '+str(counted))
		counted+=1
		if count%100 == 0: 
			msg='\rLine browsed '+str(count) 
			sys.stderr.write(msg)
		Q=Log.operation
		if Q == 'DELETE': 
		    Q='DEL'
		Message.debug(PRGNAME,"Op is : "+Q+str(Log.elapsed))
		#result=process_elapsed_bydate(result,Log.day,Log.hms,Q,int(Log.elapsed))
		Log.aggragate_result(Q)
	# to treat where no data
	#display_results(result,option)
	exit(0)

if __name__ == '__main__':
	main(option)
