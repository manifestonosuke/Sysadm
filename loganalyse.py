#! /usr/bin/python2

import os 


count=0 
limit=-1 

file="dovecot_error_log"
fd=open(file)
#refday="28/Sep/2014"
refday=""

if refday != "":
    print "Lookin for log for "+refday+" on file "+file
prevsec=-1

this={}
nb=0
prevhms=-1

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
            sorted={}
            sorted=this
            for k in sorted.keys():
                #string=k+'='+str(sorted[k])+' '+string
                fstring=string+" "+fstring
            this={}
            #print '{0:20s} {1:10s} {2:7s}{3}'.format(refday,hms,Q,str(prevsec),string)
            #print '{0} {1} {2}'.format(displaydate,hms,string)
            print '{0} {1} '.format(displaydate,prevhms),
            for k in sorted.keys():
                print '{0:10s} {1:10s}'.format(k,str(sorted[k])),
            print
            prevsec=s
            prevhms=hms
        #else:
        #    print h,m,s 
    if count == limit:
        break

exit(0)
