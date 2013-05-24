#!/usr/bin/python
# -*- coding: utf8 -*-

"""
	Virtualbox command line utility
"""

import sys
import os
import getopt
import signal

PRGNAME=os.path.basename(sys.argv[0])
if "DEBUG" in os.environ:
	DEBUG=os.environ["DEBUG"]
else: 
	DEBUG=0 

def sighandler(signum):
	if signum in [1,2,3,15]:
        	print("Caught signal %s, exiting." %(str(signum)))
	        sys.exit()
	else:
		print("Caught signal %s, ignoring." %(str(signum)))
	

def trap():
	""" This function is to trap sigevent by default use same proc for all """
	for i in [x for x in dir(signal) if x.startswith("SIG")]:
		try:
			signum = getattr(signal,i)
			signal.signal(signum,sighandler)
		except RuntimeError:
			print("Skipping %s" % i)

def usage():
	global PRGNAME
	ARGS=""
	message="""Handle command line for vbox easily
Run without arg will list vbox on the machine 
"""
	print(message)
	message="usage : "+PRGNAME+"\n"
	add="""
	-d : run in debug mode
        -l : List VM with power status (State) and general info about virtualbox configuration
        -p : pause the vbox 
        -r : resume the vbox
        -R : Reset the vbox     
        -s : start the vbox
        -S : Give summary status of a named vm 
        -O : Power OFF the vbox
        -v : full verbose mode (will list all vbox command runned)
	"""
	message=message+add
	print(message)	
	
	


class __print():
	"""
	print standard format with level : programme : message
	extra is optionnal arg to deal with extra behaviour 
	like verbose debug ...
	"""
	global DEBUG
	def __init__(self,prg,message,extra="standard"): 
		self.p=prg
		self.m=message
		self.e=extra
	
	def info(p,m):
		print("%-10s : %-10s : %-30s" % ("INFO",p,m))

	def debug(p,m):
		if DEBUG != 0 :
			print("%-10s : %-10s : %-30s" % ("DEBUG",p,m))

def parseargs(argv):
	#print "Parsing args",argv,"loop"
	try:
		opts, args = getopt.getopt(argv, "dG:hO:lp:r:R:s:S:v0:", ["help"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	#print "Parsing opt",opts,"arg",args
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt == '-d':
			global DEBUG
			DEBUG = 1
		elif opt == '-G':
			_vb.setvrde()
		elif opt == 'O' :
			_vb.guest_acpidown(arg)
		elif opt == 'l' :
			_vb.list()
		elif opt == 'p' :
			_vb.guest_pause(arg)
		elif opt == 'r' :
			_vb.guest_resume(arg)
		elif opt == 'R' : 
			_vb.guest_reset(arg)
		elif opt == 's' :
			_vb.guest_start(arg)
		elif opt == 'S' :
			_vb.guest_status(arg)
		elif opt == 'v' :
			global VERBOSE
			VERBOSE=1
		elif opt == 0 :
			_vb.guest_poweroff(arg)
		else: 
			message="Argument "+opt+"not valid"
			__print.normal(PRGNAME,message)
			usage()

class _vb:
	def setvrde():
		pass
	def guest_acpidown(arg):
		pass
	def list():
		pass
	def guest_pause(arg):
		pass
	def guest_resume(arg):
		pass
	def guest_reset(arg):
		pass
	def guest_start(arg):
		pass
	def guest_status(arg):
		pass
	def guest_poweroff(arg):
		pass

if (len(sys.argv) == 1) :
	__print.debug(PRGNAME,"argument parsing, only 1 arg")
	_vb.list()
else:
        parseargs(sys.argv[1:])



if __name__ == '__main__':
	message="Starting "+PRGNAME
	__print.debug(PRGNAME,message)

#usage()

