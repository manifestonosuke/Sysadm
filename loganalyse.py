#!/usr/bin/python2

'''
	TODO 
		DONE    setup the sample metric like second minute hour day ...
		DONE    select date to display (like -D 23/Oct/2014)
		3       review the ugly print statement
		DONE    replace old debug style with Message class 
		5       Improve message class to set hierachie in debug level
		DONE    Add a picle option (need struct passed as json) to save/load data
                DONE    finalize classification of the Log related code
                x       describe file format with 3 param (grep pattern, elapsed format, pattern to read)  and be able to parse various log files 
'''

from datetime import datetime
import gzip
import os 
import sys
import getopt
import pickle

PRGNAME=os.path.basename(sys.argv[0])

def usage():
		global PRGNAME
		print PRGNAME,"usage"
		print '''
		loganalyze -f FILE 
		-c          Analyze only this count of files
		-d          Debug
		-f file     Use file filname, with following extention will do :
                            .gz  : will read it as gzipped file (without extracting)
                            .pickle : will read the file as a python pickle (see option -p)
		-o option   Use specific option (see below) 
                -p          Save the stat in pickle format for later use. output pickle is original filename.pickle
		-k format   specify log format (see below)
		-u unit     Unit to sort data (hour/minute ...)
		-x	    Use csv format
                -T          TAG to search by default REST 
		-D	    Specify a day to display (format as original log file ie apache 01/Jan/2011)
		-H	    Specif an hour like 12 for 12h, 12:00 for 12h 00 mn 
		supported option for -o :
		elapsed : to display elapsed time with the default count
		supported log format :
		apache
                dovecot (similar to apache with elapsed between "*" )
		sproxyd
                
                TAG is used for entries to check in the log file 
                    REST tag is used as  PUT/GET/DELETE/HEAD request 
                    http_code is used to search http_code in apache like files 
                pickle option will create a file 
		'''

def parseargs(argv):
		try:
				opts, args = getopt.getopt(argv, "Ac:dD:hH:f:k:o:pT:u:x", ["help", "url="])
		except getopt.GetoptError:
				usage()
				sys.exit(2)
		Message.setlevel('info')
		global option
		global DEBUG
		for i,el in enumerate(opts):
                    #print 'enum : '+str(i),el
		    if '-d' in el:
		        "remove -d arg from opts string and go debug"
		        opts.pop(i)
		        Message.setlevel('debug')
		        Message.debug(PRGNAME,"going debug, remaining args "+str(opts)+" "+str(args))
		for opt, arg in opts:
		    if opt in ("-h", "--help"):
			usage()
			sys.exit()
	            elif opt == '-A':
		        option['ALL'] = 1
                    elif opt == '-c':
		        option['count'] = arg
		    elif opt == "-D":
		        option['day']=arg 
		    elif opt == "-f":
		        option['file']=arg 
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
                        option['pickle']='pickle'
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
		level_value=[ 'info','debug','verbose','run','error','fatal','silent','warning','all']
                level_value_d={'info':10,'debug':20,'verbose':30,'run':40,'error':50,'fatal':60,'silent':0,'warning':60,'all':100}
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

		def info(cls,p,m,option=None):
                    if option == "stderr":
                        string="%-10s : %-10s : %-30s" % ("INFO",p,m)
                        sys.stderr.write(string)
                    else:
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
                    print
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
	#def __init__(self,logfile,kind="apache"):
	def __init__(self,option):
                self.option={}
                self.result={}
                self.banner=[]
                self.setoption('unit','minute')
                for key in option.keys():
                    self.setoption(key,option[key])
		self.logfile=self.getoption('file')
		self.kind=self.getoption('kind','apache')
                self.settag('REST')
                self.unit=self.getoption('unit') 
                if self.logfile == "":
			print "ERROR : no file provided"
			exit(2)
                if self.logfile.split('.')[-1] == 'gz' :
		    try:
		        self.fd=gzip.open(self.logfile)
		    except:
			print "ERROR : could not open file "+logfile
			raise IOError
                else: 
                    try:
                        self.fd=open(self.logfile,'r')
		    except:
			print "ERROR : could not open file "+logfile
			raise IOError
                
                if self.logfile.split('.')[-1] == 'pickle' :
                    self.readpickle()
      

        def setoption(self,param,value=None):
            try:
                self.option[param]=value
            except:
                Message.error('Log.getoption',"cant set option :"+param)

        def name(self):
            if not self.logfile:
                return(False)
            else:
                return(self.logfile)

        def getoption(self,param='enum',default=None):
            if param == 'enum':
                for key in self.option:
                    print self.option[key]
                return(True)
            if param not in self.option:
                if default == None:
                    Message.error("Log.option","Invalid operation "+param)
                    raise TypeError
                else:
                    return(default)
            else:
                return(self.option[param])
                

        def readpickle(self):
            Message.info(PRGNAME,"Reading pickle file "+str(self.logfile),"stderr")
	    self.result=pickle.load(self.fd)
            self.banner=self.result.pop('banner')
            self.display_results()
            exit()

	def readone(self):
            l=self.fd.readline()
            if not l:
                    return(0)
            self.line=l
	    return(1)

        def pickfile(self,op="dump",file="out.pickle"):
            try:
                pickler=open(file,'w')
            except:
                Message.error(PRGNAME,"Can not open pickle file")
                return(1)
            if op == "dump":
                self.result['banner']=self.banner
                pickle.dump(self.result,pickler)   
                pickler.close()
                return(True)
            return(None)

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
            Q=None
            if self.tag == 'REST':
                Q=self.operation
                if Q == 'DELETE':
                    Q='DEL'
            if self.tag == 'http_code':
                Q=self.http_code
            if Q == None:
                Message.error(PRGNAME,"Tag no valid :"+str(self.tag))
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
		elif self.kind=="restapi":
			dict={}
			Message.debug(PRGNAME,self.line)
                        #if self.line.split()[7].split('"')[1] != 'end' :
			
			#step="REQ_END"
			try:
				status=self.line.split()[4].split('"')[1]
				if status != 'generic': 
					return None
				status=self.line.split()[7].split('"')[1]
					
			except IndexError:
				return 'LINEERROR'
			if status != 'REQ_END':
                            return None
			self.year=str(datetime.now().year)
			self.month=self.line.split()[0][4:6]
			self.day=self.line.split()[0][6:8]
			self.hms=self.line.split()[1].split('.')[0]
			self.fulldate=str(self.day)+'/'+self.month+'/'+str(self.year)+':'+self.hms
			self.payload=self.line.split()[4:]
			self.hour,self.minute,self.second=self.hms.split(':')
			self.hms=self.hour+":"+self.minute+":"+self.second
			self.ms=None
			#print self.payload
			for k in self.payload:
				dict[k.split('=')[0]]=k.split('"')[1:]	
			self.elapsed=dict['elapsed'][0][:-2]
			self.operation=dict['method'][0]
			if "code" not in dict.keys():
				print self.payload
				self.http_code="666"
			else:	
				self.http_code=dict['code'][0]
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
            option=self.option
	    prevday=day=None
	    prevhour=hour=None
	    prevmin=minute=None
            prevsec=second=None
            # total['GET'][0]=total ... GET[1]=count
            total={}
            output={}
            #i=date, j=hms, k=get/put/del... 0=# 1=count
            self.banner.sort()
            if option['format']=='csv'and option['operation'] == 'elapsed' :
                #print "#{0:12s}{1:9s}{2:10s}{3:11s}{4:10s}{5:11s}{6:10s}{7:11s}{8:10s}{9:10s}".format('day','time','GET cnt','GET avg','PUT cnt','PUT avg','DEL cnt','DEL avg','HEAD cnt','HEAD avg')
                formatstring=[]
                for el in self.banner:
                    formatstring.append(el)
                    formatstring.append("avg")
                print "#{0}:{1:20s}".format('day','time'),
                for i in formatstring:
                    print i.ljust(9),
                print
            else:
                formatstring=[]
                for el in self.banner:
                    formatstring.append(el)
                #print "#{0:12s}{1:9s}{2:8s}{3:8s}{4:8s}{5:8s}".format('day','time','GET','PUT','DELETE','HEAD')
                print "#{0}:{1:16s}".format('day','time'),
                for i in formatstring:
                    print i.ljust(10),
                print
                
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
                        total=display_results_print(total,i,time,option)
                        prevsec=s
                    if self.unit == 'minute' and prevmin != m:
                        #time=prevhour+":"+prevmin+":00" 
                        #time=h+":"+prevmin+":"+s
                        time=h+":"+m+":"+str(s) 
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
                    self.realtag=sorted(self.result[i][j].keys())
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
		    #print k+"|"+str(count),
	    #if self.unit != 'second':
	    #    display_results_print(total,i,j,option)


def display_results_print(list,date,time,option):
	""" get a list and display it while calculing stats"""
	print date+":"+time+" ",
	# total['GET'][0]=total ... GET[1]=count
	# csv need to have 0 value when entry is not found
	if option['tag']=='REST':
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


#default option count rest command
option={'operation':'rest'}

file=""
option['file']=file
option['count']=-1
option['format']="list"
option['tag']='REST'



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


Message.getlevel()

#tag=('PUT','GET','DELETE','HEAD')
displaydate=""
prevhms=-7





def main(option):
	Message.debug(PRGNAME,":"+option['operation']+":")
	#Log=Logfile(option['file'],option)
	Log=Logfile(option)
	result={}
	counted=0 
	count=0 
        #if 'unit' in option:
        #    Log.unit(option['unit'])
        #else:
	#    Log.unit('minute')
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
                                if 'pickle' in option:
                                    p=str(Log.logfile)+'.pickle'
                                    Log.pickfile("dump",p)
			            sys.stderr.write("\n")
                                    Message.info(PRGNAME,"pickle file "+p+" created","stderr")
			else:
				Message.info(PRGNAME,"no line selected")
			break
		#Log.prepare()
		linestatus=Log.prepare()
                if linestatus == None :
                    continue
		elif linestatus == 'LINEERROR':
		    #Log.printline() 
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
		#Q=Log.operation
		#if Q == 'DELETE': 
		#    Q='DEL'
                Q=Log.getop()
		Message.debug(PRGNAME,"Op is : "+Q+str(Log.elapsed))
		#result=process_elapsed_bydate(result,Log.day,Log.hms,Q,int(Log.elapsed))
		Log.aggragate_result(Q)
	# to treat where no data
	#display_results(result,option)
	exit(0)

if __name__ == '__main__':
	main(option)
