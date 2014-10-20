#!/usr/bin/python2

'''
    TODO 
        1   setup the sample metric like second minute hour day ...
        2   select date to display (like -D 23/Oct/2014)
        3   review the ugly print statement
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
        -x      Use csv format
        '''

def parseargs(argv):
        try:
                opts, args = getopt.getopt(argv, "Ac:dhf:u:x", ["help", "url="])
        except getopt.GetoptError:
                usage()
                sys.exit(2)
        #print "Parsing opt",opts,"arg",args
        global option
        global DEBUG
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
                elif opt in "-f":
                        option['file']=arg
                        #print "using File "+file,
                elif opt in "-u":
                        option['unit']=arg 
                elif opt in "-x":
                        option['csv']=1

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

        def getlevel(cls):
                if len(Message.level) == 0:
                        return('unset')
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
        try:
            self.fd=open(logfile)
        except:
            print "ERROR : could not open file "+logfile

    def readone(self):
        l=self.fd.readline()
        if not l:
            return(0)
        #print l
        self.line=l
        return(1)

    def printline(self):
        print self.line

    def prepare(self):
        if self.kind=="apache":
            self.fulldate=self.line.split("[")[1].split("]")[0]
            self.payload=self.line.split('"')[1]
            self.day,self.hour,self.minute,self.second=self.fulldate.split()[0].split(':')
            self.hms=self.hour+":"+self.minute+":"+self.second
            self.ms=None
            self.all={'fulldate':fulldate}
        else:
            raise valueError


    def unit(self,value):
        print value
        return self.value




def displaylinestat(this,option):
    print '{0}{1}{2}{3}'.format(displaydate,csvchar,prevhms,csvchar),
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

count=0 
option={}

file="dovecot_error_log"
option['file']=file
option['count']=-1
kind="apache"
#refday="30/Sep/2014"
refday=""

if refday != "":
    print "Lookin for log for "+refday+" on file "+file
previous=-1

this={}
prevhms=-1
PATTERN=('PUT','GET','DELETE','HEAD')


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

Log=Logfile(option['file'],kind)


for i in PATTERN: 
    this[i]=0

if __name__ != '__main__':
    exit()

while True:
    l=Log.readone()  
    if not l: 
        if 'debug' in option:
           print "DEBUG : EOF for file "+file
        this=displaylinestat(this,option)
        break
    
    count+=1
    Log.prepare()
    if refday != "":
        displaydate=refday
        if day != refday: 
            print 'cont'+refday+":::"
        continue
    else:
       displaydate=Log.day
    Q=Log.payload.split()[0]
    if 'debug' in option: 
        print Q
    if Q in this.keys():
        this[Q]=this[Q]+1
    else:
        this[Q]=1 
    if previous == -1:
        previous=Log.second
        prevhms=Log.hms
    else:
        if previous != Log.second:
            #print '{0}{1}{2}{3}'.format(displaydate,csvchar,prevhms,csvchar),
            this=displaylinestat(this,option)
            print
            previous=Log.second
            prevhms=Log.hms
    if count == int(option['count']):
        print "Reaching limit lines parsed  "+option['count']+" lines"
        break

exit(2)

