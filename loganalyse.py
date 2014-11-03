#!/usr/bin/python2

'''
    TODO 
        DONE   setup the sample metric like second minute hour day ...
        DONE   select date to display (like -D 23/Oct/2014)
        3   review the ugly print statement
        4   replace old debug style with Message class 
        5   Improve message class to set hierachie in debug level
'''


import os 
import sys
import getopt

PRGNAME=os.path.basename(sys.argv[0])


def usage():
        global PRGNAME
        print PRGNAME,"usage"
        print "debug sys args",sys.argv
        #for arg in sys.argv:
        #       print arg
        print '''
        loganalyze -f FILE 
        -A      Analyze all the file
        -c      Analyze only this count of files
        -d      Debug
        -f      Use file 
        -u      Unit to sort data (hour/minute ...)
        -x      Use csv format

        -D      Specify a day to display (format as original log file ie apache 01/Jan/2011)
        -H      Specif an hour like 12 for 12h, 12:00 for 12h 00 mn 
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
                        option['csv']=1
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

msg=Message()
msg.setlevel('debug')

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
#    exit()

if 'unit' in option:
    zzzz=option['unit']
else:
    zzzz='minute'

#Message.setlevel('info')
#Message.getlevel(1)

PATTERN=('PUT','GET','DELETE','HEAD')
displaydate=""
prevhms=-7
def main(option):
    Message.debug(PRGNAME,":"+option['operation']+":")
    Log=Logfile(option['file'],kind)
    prevhms=-9
    previous=-1
    this={}
    total={}
    for i in PATTERN: 
        this[i]=0
        total[i]=0
    counted=0 
    count=0 
    while True:
	    l=Log.readone() 
	    if not l: 
	        Message.debug(PRGNAME,"no more lines")
                if option['operation'] == 'elapsed' :
	            Message.debug(PRGNAME,"calculate_elasped")
                    calculate_elasped(this,total,displaydate,prevhms)
                    break
	        if 'debug' in option:
	           print "DEBUG : EOF for file "+file
	        if counted != 0:
	            this=displaylinestat(this,option,displaydate,prevhms)
                    print
	        else:
	            Message.info(PRGNAME,"no line selected")
	        break
	    Log.prepare()
	    displaydate=Log.day
	    if 'day' in option:
	        if Log.day != option['day']:
	            continue
	    else:
	        counted+=1
	    count+=1
	    Q=Log.payload.split()[0]
            Message.debug(PRGNAME,"Payload is : "+Q)
	    if 'debug' in option: 
	        print Q
            if option['operation'] == 'rest':
                Message.debug(PRGNAME,"New op REST")
	        if Q in this.keys():
	            this[Q]=this[Q]+1
	        else:
	            this[Q]=1 
            if option['operation'] == 'elapsed':
	        this[Q]=this[Q]+1
                total[Q]=total[Q]+int(Log.elapsed)
	    if previous == -1:
	        previous=Log.unit(zzzz)
	        prevhms=Log.hms
	    else:
	        if previous != Log.unit(zzzz):
	            #print '::::{0}{1}{2}{3}:::'.format(displaydate,csvchar,prevhms,csvchar),
                    if option['operation'] == 'elapsed':
	                Message.debug(PRGNAME,"calculate_elasped")
                        calculate_elasped(this,total,displaydate,prevhms)
                        for i in PATTERN: 
                            this[i]=0
                            total[i]=0
                    if option['operation'] == 'rest':
	                Message.debug(PRGNAME,"displaylinestat")
	                this=displaylinestat(this,option,displaydate,prevhms)
	                print
	            previous=Log.unit(zzzz)
	            prevhms=Log.hms
	    if count == int(option['count']):
	        print "Reaching limit lines parsed  "+option['count']+" lines"
	        break
    Message.debug(PRGNAME,"\ntotal lines, counted lines "+str(count)+":" +str(counted))
    exit(0)

if __name__ == '__main__':
    main(option)
