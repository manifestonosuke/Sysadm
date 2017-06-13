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
import pickle
import gzip


PRGNAME=os.path.basename(sys.argv[0])


#default option count rest command
option={'operation':'rest'}
option['valid_kind']=['apache','dovecot','chunkapi','restapi','sproxyd','chordbucket']
option['file']=""
option['format']="list"
option['tag']='REST'

def usage():
		global PRGNAME
                print "\n\tSyntax : {0} -f FILE [option]".format(PRGNAME)
		print '''
                -c <number> Analyze only this count of files
		-d	    Debug
		-D <day>    Specify a day to display (format as original log file ie apache 01/Jan/2011)
		-f <file>   Source data log file
		-i <file>   Load data from a pickle file (previously saved with -p)
                -h          This help
		-H <hour>   Specif an hour like 12 for 12h, 12:00 for 12h 00 mn 
		-k <type>   specify log type (see below)
		-o <option> Use specific option (see below) 
		-p <file>   Save data in pickle format (-i to load) 
                -T <tag>    TAG to search by default REST 
		-u <unit>   Unit to sort data : hour, minute or second
                -v          Verbose mode (Additionnal messages less verbose that debug)
		-x	    Use csv format to display output

		supported option :
		elapsed : to display elapsed time with the default count
                bizioname : Only with chunkapi format, display nb iops per disk

                Note : REST tag is used as  PUT/GET/DELETE/HEAD request 
		'''
                print "\t"*2+"Accepted log type :"
                for i in option['valid_kind']:
                    print "\t"*3+i
                    

def parseargs(argv):
		try:
				opts, args = getopt.getopt(argv, "c:dD:hH:i:f:k:o:p:T:u:vx", ["help"])
		except getopt.GetoptError:
				usage()
				sys.exit(2)
		#print "Parsing opt",opts,"arg",args
		global option
		global DEBUG
		Message.setlevel('info')
		for i,el in enumerate(opts):
				if '-d' in el:
						"remove -d arg from opts string and go debug"
						opts.pop(i)
						Message.setlevel('debug')
						Message.debug(PRGNAME,"going debug, remaining args "+str(opts)+" "+str(args))
						#break
		for opt, arg in opts:
				if opt in ("-h", "--help"):
						usage()
						sys.exit()
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
                                                if ':' in option['hour']:
                                                    option['minute']=option['hour'].split(':')[1]
                                                    option['hour']=option['hour'].split(':')[0]
                                                    Message.debug(PRGNAME,"time selected {0} {1}".format(option['hour'],option['minute']))
                                elif opt in "-i":
                                                option['picklein']=arg
				elif opt in "-k":
						if arg in option['valid_kind']:
							option['kind']=arg 
						else:
							Message.error(PRGNAME,"type {0} not a valid type {1}\n".format(arg,str(option['valid_kind'])))
							sys.exit(9)
				elif opt in "-u":
						option['unit']=arg 
				elif opt in "-x":
						option['format']='csv'
				elif opt in "-o":
						option['operation']=arg
                                elif opt in "-p":
                                                option['pickleout']=arg
				elif opt in "-T":
						option['tag']=arg
				elif opt in "-v":
						Message.setlevel('verbose')
						option['verbose']=arg

                if 'operation' in option:
                        if option['operation'] == 'bizioname':
                            if option['kind'] != 'chunkapi':
                                Message.error(PRGNAME,"option bizioname must be on chunkapi files")
                                exit(9)
                            

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
				if Message.level == 'verbose' or Message.level == 'debug':
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
	def __init__(self,logfile,kind="apache",option={}):
		self.logfile=logfile
		self.kind=kind
                self.result={}
                self.settag('none')
                self.banner=[]
		if 'operation' in option:
			self.op=option['operation']
			if ',' in self.op:
				self.opfilter=self.op.split(',')[1]
				self.op=self.op.split(',')[0]
				Message.debug(PRGNAME,"operation and filter {0} {1}".format(self.op,self.opfilter))
			else:
				self.opfilter=None
				Message.debug(PRGNAME,"operation {0}".format(self.op))
		if logfile == "":
			print "ERROR : no file provided"
			return(2)
                ext=self.logfile.split('.')[-1:][0]
                if ext == "gz":
                    Message.debug(PRGNAME,"opening file {0} as gzip".format(self.logfile))
                    try:
                        self.fd=gzip.open(self.logfile,'r')
                    except:
                        print "ERROR : could not open file "+str(self.logfile)
                        raise IOError
                else:
                    Message.debug(PRGNAME,"opening file {0}".format(self.logfile))
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

	def load_pickle(self,file):
		try:
			self.result = pickle.load(open(file,"r"))
		except IOError as e:
			Message.error(PRGNAME,"Error opening {2} {0}: {1}".format(e.errno, e.strerror,option['picklein']))
		except ValueError:
			Message.error("Error loading data from {2} {0}: {1}".format(e.errno, e.strerror,option['picklein']))
		return

	def printline(self):
	    print self.line,
	    return(self.line)

        def settag(self,arg):
            self.tag=arg
            if self.tag == 'REST':
                self.realtag=('PUT','GET','DELETE','HEAD')
            else:
                self.realtag=self.tag
            return

        def getop(self):
            if self.tag == 'REST':
                Q=self.operation
                if Q == 'DELETE':
                    Q='DEL'
            if self.tag == 'http_code':
                Q=self.http_code
            return(Q)


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
		elif self.kind=="chunkapi":
                        dict={}
                        l=self.line.split()
                        if l[2] != self.kind:
                            Message.warning(PRGNAME,"suspect Line, ignoring : "+l[2])
                            return None
                        type=l[4].split('=')[1].split('"')[1]
                        if type != 'end':
                            return None
                        self.year=l[0][0:4]
                        self.month=l[0][4:6]
                        self.day=l[0][6:8]
                        self.hms=l[1]
                        self.ms=self.hms.split('.')[1]
                        self.hms=self.hms.split('.')[0]
                        self.hour,self.minute,self.second=self.hms.split(':')
                        self.payload=l[3:]
			for k in self.payload:
			    dict[k.split('=')[0]]=k.split('=')[1].strip('"')
                        try:
			    if dict['status'] != "CHUNKAPI_STATUS_OK":
				Message.verbose(PRGNAME,"key status is not OK ignored {0}".format(str(self.payload)))
				return None
			except KeyError:
			    Message.verbose(PRGNAME,"Error on this line, no status found {0}, ignoring : ".format(str(dict)))
			    return None
			if ('elasped' and 'bizioname' and 'cmd') not in dict.keys():
                            Message.verbose(PRGNAME,"Missing pattern in line {0}, ignoring : ".format(str(dict)))
                            return None
                        self.elapsed=dict['elapsed'][:-2]
                        self.returncode=dict['status']
                        # cmd is not present on error some error status
                        if self.op == 'bizioname':
			    if self.opfilter:
				if 'cmd' not in dict.keys():
					print str(self.payload)
			        if dict['cmd'] != self.opfilter:
				    Message.verbose(PRGNAME,"Operation filtered out {0}".format(dict['cmd']))
			            return None
                            try:
                            	self.operation=dict['bizioname']
                            except KeyError:
                                return 'BIZIO NAME ERROR'
			    return True
                        try:
                            self.operation=dict['cmd']
                        except KeyError:
                             return 'CHUNKERROR'
                        #Message.debug(PRGNAME,dict)
                        return True
		elif self.kind=="restapi":
                        dict={}
                        l=self.line.split()
                        if l[2] != self.kind:
                            Message.warning(PRGNAME,"suspect Line, ignoring : "+l[2])
                            return None
                        self.payload=l[3:]
			for k in self.payload:
			    dict[k.split('=')[0]]=k.split('=')[1].strip('"')
                        if 'elapsed' not in dict.keys():
                            return None
                        if dict['cmd'] != 'finished': 
                            return None
                        if dict['code'] == '403': 
                            return None
                        
                        self.year=l[0][0:4]
                        self.month=l[0][4:6]
                        self.day=l[0][6:8]
                        self.hms=l[1]
                        self.ms=self.hms.split('.')[1]
                        self.hms=self.hms.split('.')[0]
                        
                        self.elapsed=dict['elapsed'][:-2]
                        self.returncode=dict['code']
                        # cmd is not present on error some error status
                        try:
                            self.operation=dict['method']
                        except KeyError:
                             return 'Line Error : No method'
                        Message.debug(PRGNAME,dict)
                        return True
                elif self.kind=="chordbucket":
                        dict={}
                        l=self.line.split()
                        #Message.warning(PRGNAME,"processing : "+str(l))
                        if l[2] != self.kind:
                            Message.warning(PRGNAME,"suspect Line, ignoring : "+l[2])
                            return None
                        for i in l[3:]:
                            dict[i.split('=')[0]]=i.split('=')[1]
                        #type=l[4].split('=')[1].split('"')[1]
                        if "elapsed" not in dict:
                            return None
                        if dict["action"] not in ["DEL_OBJ","PUT_OBJ","GET_OBJ","GET_BUCKETACL"]:
                            return None
                        self.year=l[0][0:4]
                        self.month=l[0][4:6]
                        self.day=l[0][6:8]
                        self.hms=l[1]
                        self.ms=self.hms.split('.')[1]
                        self.hms=self.hms.split('.')[0]
                        self.payload=l[3:]
                        self.elapsed=dict['elapsed'][:-2]
                        self.returncode=dict['status']
                        # cmd is not present on error some error status
                        try:
                            self.operation=dict['action']
                        except KeyError:
                             return 'CHORDBUCKET ERROR'
                        #Message.debug(PRGNAME,dict)
                        return True

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
            if operation not in self.banner:
                self.banner.append(operation)
                Message.debug(PRGNAME,"banner "+str(self.banner))
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
 
        def display_results(self,option={}):
            if 'pickleout' in option:
            	outfile=option['pickleout']
		try:
			pickle.dump(self.result,open(outfile,"w"))
		except:
                        print "Unexpected error:", sys.exc_info()[0]
                        sys.exit(2)
		Message.info(PRGNAME,"file {0} dumped".format(outfile))
		sys.exit(0)
	    prevday=day=None
	    prevhour=hour=None
	    prevmin=minute=None
            prevsec=second=None
            # total['GET'][0]=total ... GET[1]=count
            total={}
            output={}
            #i=date, j=hms, k=get/put/del... 0=# 1=count
            formatstring=[]
            for el in self.banner:
                formatstring.append(el)
            if option['format']=='csv'and option['operation'] != 'elapsed' :
                formatstring=[]
                for el in sorted(self.banner):
                    formatstring.append(el)
                #print "#{0:12s}{1:9s}{2:8s}{3:8s}{4:8s}{5:8s}".format('day','time','GET','PUT','DELETE','HEAD')
                print "::{0:4s}{1:8s}".format('day','time'),
                for i in formatstring:
                    print i.ljust(10),
                print
            if option['format']=='csv'and option['operation'] == 'elapsed' :
                #print "#{0:12s}{1:9s}{2:10s}{3:11s}{4:10s}{5:11s}{6:10s}{7:11s}{8:10s}{9:10s}".format('day','time','GET cnt','GET avg','PUT cnt','PUT avg','DEL cnt','DEL avg','HEAD cnt','HEAD avg')
                formatstring=[]
                for el in self.banner:
                    formatstring.append(el)
                    formatstring.append("avg")
                print "::{0:4s}{1:8s}".format('day','time'),
                for i in sorted(formatstring):
                    print i.ljust(9),
                print
            if self.result.keys() == []:
                Message.warning(PRGNAME+" No results found",None)
                exit(0)
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
                        time=h+":"+m+":"+str(s) 
                        total=display_results_print(total,i,time,option,self.banner)
                        prevsec=s
                    if self.unit == 'minute' and prevmin != m:
                        #time=prevhour+":"+prevmin+":00" 
                        #time=h+":"+prevmin+":"+s
                        time=h+":"+m+":"+str(s) 
                        total=display_results_print(total,i,time,option,self.banner)
                        prevmin=m
                    if self.unit == 'hour' and prevhour != h:
                        time=prevhour+":"+m+":00" 
                        total=display_results_print(total,i,time,option,self.banner)
                        prevhour=h
                    if self.unit == 'day' and prevday != day:
                        total=display_results_print(total,prevday,time,option,self.banner)
                        prevday=d

                    Message.debug(PRGNAME+":display_results",self.result[i][j])
                    self.realtag=sorted(self.result[i][j].keys())
                    #print self.realtag
                    for k in self.realtag:
                        if k not in total.keys():
                            #print total
                            #print k,total,self.result[i][j][k][0]
                            total[k]=[self.result[i][j][k][0],0]
                            total[k][1]=self.result[i][j][k][1]
                        else:
                            #print self.result
                            #print total
                            total[k][0]=int(self.result[i][j][k][0])+int(total[k][0])
                            total[k][1]=self.result[i][j][k][1]+total[k][1]
                            #print k+"|"+str(count)+"|"+str(avg)+"|",
                        if k not in self.banner:
                            self.banner.append(k)
	    if self.unit != 'second':
	        display_results_print(total,i,j,option,self.banner)


def display_results_print(list,date,time,option,banner=None):
	""" get a list and display it while calculing stats"""
	#print date+" "+time+" ",
        print "{0:6s}{1:8s}".format(date,time),
	# total['GET'][0]=total ... GET[1]=count
	# csv need to have 0 value when entry is not found
	#if option['tag']=='REST':
	if option['tag']=='BLOB':
	#print "{0:12s}{1:9s}{2:6s}{3:6s}{4:6s}{5:6s}".format('day','time','GET','PUT','DELETE','HEAD')
		pattern=['GET','PUT','DEL','HEAD']
	else:
		#pattern=sorted(list.keys())
		##!## pattern=sorted(banner)
                pattern=sorted(list.keys())
	#if option['format']=='csv'and option['operation'] == 'elapsed':
	#	print "{0:10s}{1:10s}".format(count,str(avg)),
	#elif option['format']=='csv':
	#	print "{0:8s}".format(count),
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
			print "{0:10s}".format(count),
		else:
			if option['operation'] == 'elapsed':
				#display='{2}:{0}|{1}|\t'.format(avg,count,k)
				display='{2}:{0}|{1}|'.format(avg,count,k)
				##!## display='{0:30s}'.format(display)
			else:
				display='{0}|{1}\t'.format(count,k)
				##!## display='{1}|{0}'.format(count,k)
				##!## display='{0:25}'.format(display)
			print display,
		if k in list:
			del list[k]
	print
	return(list)





if (len(sys.argv) != 1) :
	parseargs(sys.argv[1:])


if 'csv' in option:
	csvchar=';'
else:
	csvchar=" "

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
	Log=Logfile(option['file'],kind,option)
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
                if 'picklein' in option:
			Log.load_pickle(option['picklein'])
			Log.display_results(option)
			exit(0)

		if not l:
			""" no more lines in the file """ 
			Message.debug(PRGNAME,"EOF for file "+option['file'])
			if counted != 0:
				print
				Log.display_results(option)
			else:
				Message.info(PRGNAME,"no line selected")
			break
                if "count" in option and count > int(option['count']):
			""" reach manual line count setting """
			Message.debug(PRGNAME,"Reach the max counter of lines"+option['file'])
			if counted != 0:
				print
				Log.display_results(option)
			else:
				Message.info(PRGNAME,"no line selected")
			break
		linestatus=Log.prepare()
                if linestatus == None :
                    continue
		elif linestatus == 'LINEERROR':
		    Log.printline() 
		    Message.error(PRGNAME,"Ignoring error reading line "+str(count)) 	
		    continue
		elif linestatus == 'CHUNKERROR':
		    if 'verbose' in option:
		        Log.printline()
		        Message.error(PRGNAME,"Ignoring error reading line "+str(count)) 	
                        continue
		#	Ignore line not in option['day']
		if count%100 == 0: 
			msg='\rLine browsed '+str(count)+":::::"+str(counted)
			sys.stderr.write(msg)
		if 'day' in option:
			if Log.day != option['day']:
				continue
		if 'hour' in option:
			if Log.hour != option['hour']:
				continue
			Message.debug(PRGNAME,'counted hour'+str(counted))
                        if 'minute' in option and Log.minute != option['minute']:
                                continue
			Message.debug(PRGNAME,'counted minute'+str(counted))
		counted+=1
		#Q=Log.operation
		#if Q == 'DELETE': 
		#    Q='DEL'
                Q=Log.getop()
		Message.debug(PRGNAME,"Op is : "+Q+':'+str(Log.elapsed))
		#result=process_elapsed_bydate(result,Log.day,Log.hms,Q,int(Log.elapsed))
		Log.aggragate_result(Q)
	# to treat where no data
	#display_results(result,option)
	exit(0)

if __name__ == '__main__':
	main(option)
