#!/usr/bin/python2

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
                elif opt in "-x":
                        option['csv']=1

count=0 
option={}

file="dovecot_error_log"
option['file']=file
option['count']=-1
#refday="30/Sep/2014"
refday=""

if refday != "":
    print "Lookin for log for "+refday+" on file "+file
prevsec=-1

this={}
nb=0
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
    print '{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}'.format('date',csvchar,'hour',csvchar,'PUT',csvchar,'GET',csvchar,'DELETE',csvchar,'HEAD')

try: 
    fd=open(option['file'])
except:
    print "ERROR : could not open file "+file
    exit(9)


while True:
    nb+=1
    l=fd.readline()
    if not l: 
        if 'debug' in option:
           print "DEBUG : EOF for file "+file
        print '{0}{1}{2}{3}'.format(displaydate,csvchar,prevhms,csvchar),
        for i in PATTERN:
            if i in this.keys():
                if 'csv' in option:
                    print '{0}{1}'.format(str(this[i]),str(csvchar)),
                else:
                    print '{0}:{1} '.format(i,str(this[i])),
            else:
                if 'csv' in option:
                    print '{0}{1}'.format(0,str(csvchar)),
                else:
                    print '{0}:{1} '.format(i,'0'),
        break

    
    payload=l.split('"')[1]
    fulldate=l.split("[")[1].split("]")[0]
    #day=fulldate.split(':')[0].split(':')[0]
    day,h,m,s=fulldate.split()[0].split(':')
    hms=h+":"+m+":"+s
    count+=1
    if refday != "":
        displaydate=refday
        if day != refday: 
            print 'cont'+refday+":::"
        continue
    else:
       displaydate=day
    Q=payload.split()[0]
    if 'debug' in option: 
        print Q
    if Q in this.keys():
        this[Q]=this[Q]+1
    else:
        this[Q]=1 
    if prevsec == -1:
        prevsec=s
        prevhms=hms
    else:
        if prevsec != s:
            print '{0}{1}{2}{3}'.format(displaydate,csvchar,prevhms,csvchar),
            for i in PATTERN:
                if i in this.keys():
                    if 'csv' in option:
                        print '{0}{1}'.format(str(this[i]),str(csvchar)),
                    else:
                        print '{0}:{1} '.format(i,str(this[i])),
                else:
                    if 'csv' in option:
                        print '{0}{1}'.format(0,str(csvchar)),
                    else:
                        print '{0}:{1} '.format(i,'0'),
                this[i]=0
            print
            prevsec=s
            prevhms=hms
        #else:
        #    print h,m,s 
    if count == int(option['count']):
        print "Reaching limit lines parsed  "+option['count']+" lines"
        break
    #else:

exit(2)
