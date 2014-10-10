#!/usr/bin/python2

import os 
import sys
import getopt

PRGNAME=os.path.basename(sys.argv[0])

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

def usage():
        global PRGNAME
        print PRGNAME,"usage"
        print "debug sys args",sys.argv
        #for arg in sys.argv:
        #       print arg

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
                        option['cvs']=1

if (len(sys.argv) != 1) :
    parseargs(sys.argv[1:])


if 'ALL' in option:
    refday=""
if 'cvs' in option:
    print '{0:10s} {1:10s} {2:7s}{3:7s}{4:7s}{5:7s}'.format('date','hour','PUT','GET','DELETE','HEAD')

fd=open(option['file'])
while True:
    nb+=1
    l=fd.readline()
    lq=l.split('"')[1]
    ld=l.split("[")[1].split("]")[0]
    ldd=ld.split(':')[0].split(':')[0]
    h,m,s=ld.split()[0].split(':')[1:]
    hms=h+":"+m+":"+s
    count+=1
    if refday != "":
        displaydate=refday
        if ldd != refday: 
            print 'cont'+refday+":::"
        continue
    else:
       displaydate=ldd
    Q=lq.split()[0]
    # this will contain the PUT/GET/DELETE ... 
    if Q in this.keys():
        this[Q]=this[Q]+1
        #print this
    else:
        this[Q]=1 
    if prevsec == -1:
        prevsec=s
        prevhms=hms
    else:
        if prevsec != s:
            string=""
            fstring=""
            print '{0} {1} '.format(displaydate,prevhms),
            for i in PATTERN:
                if i in this.keys():
                    if 'cvs' in option:
                        print '{0} '.format(str(this[i])),
                    else:
                        print '{0}:{1} '.format(i,str(this[i])),
                else:
                    if 'cvs' in option:
                        print '{0} '.format(0),
                    else:
                        print '{0}:{1} '.format(i,'0'),
                this[i]=0
            print
            #print '{0:20s} {1:10s} {2:7s}{3}'.format(refday,hms,Q,str(prevsec),string)
            #print '{0} {1} {2}'.format(displaydate,hms,string)
            #print '{0} {1} '.format(displaydate,prevhms),
            prevsec=s
            prevhms=hms
        #else:
        #    print h,m,s 
    if count == int(option['count']):
        print "Reaching limit lines parsed  "+option['count']+" lines"
        break
    #else:

exit(2)
