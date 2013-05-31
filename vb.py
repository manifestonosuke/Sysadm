#!/usr/bin/python
# -*- coding: utf8 -*-

"""
	Virtualbox command line utility
"""

import sys
import os
import getopt
import signal
import subprocess

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
	
	
def end(code=0):
	#print("exit code %i " % code)
	sys.exit(code)


class logit():
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
		if DEBUG == 1:
			print("%-10s : %-10s : %-30s" % ("DEBUG",p,m))

def parseargs(argv):
	logit.debug(PRGNAME+"...parseargs","Parsing args")
	if len(sys.argv) == 1:
		logit.debug(PRGNAME,"argument parsing, only 0 arg")
		vmlist=vbctl.list()
		logit.info(PRGNAME,vmlist)
		end()
	try:
		opts, args = getopt.getopt(argv, "dG:hO:lp:r:R:s:S:v0:", ["help"])
		logit.debug(PRGNAME," : "+str(opts)+" : "+str(args))
	except getopt.GetoptError:
		logit.info(PRGNAME+"...parseargs","Bad argument")
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt == '-d':
			global DEBUG
			DEBUG = 1
		elif opt == '-G':
			vbctl.setvrde()
		elif opt == '-O' :
			vbctl.guest_acpidown(arg)
		elif opt == '-l' :
			rez=vbctl.list()
			logit.info(PRGNAME,rez)
			sys.exit(0)
		elif opt == '-p' :
			vbctl.guest_pause(arg)
		elif opt == '-r' :
			vbctl.guest_resume(arg)
		elif opt == '-R' : 
			vbctl.guest_reset(arg)
		elif opt == '-s' :
			rez=vbctl.guest_start(arg)
		elif opt == '-S' :
			vbctl.guest_status(arg)
		elif opt == '-v' :
			global VERBOSE
			VERBOSE=1
		elif opt == 0 :
			vbctl.guest_poweroff(arg)
		else: 
			message="Argument "+opt+" not valid"
			logit.info(PRGNAME,message)
			#usage()
			#sys.exit(1)

def execute(command, option=False):
	global PRGNAME
	DEBUGNAME=PRGNAME+"..execute"
	logit.debug(DEBUGNAME,"Executing : "+command)

	if option == "DETACHED_PROCESS":
		logit.debug(DEBUGNAME,"Process detached")
		#option="creationflags=0x00000008"
		ps=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,creationflags=0x00000008)
	else: 
		ps=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout,stderr=ps.communicate()
	retcode = ps.returncode
	if (retcode != 0):
		logit.debug(PRGNAME,"Executing  %s " % command)
		logit.debug(DEBUGNAME,"return message is : "+str(stderr))
		message="Error executing "+command
		raise Exception(message)
	else:
		return stdout

class vbctl():
	global PRGNAME
	def __init__(self,a):
		arg=a
	def setvrde():
		passa
	def exist(argi,out=0):
		logit.debug(PRGNAME,"checking if "+arg+" exist")
		list=vbctl.list()
		logit.debug(PRGNAME,"vbox list "+list)
		found=0
		for i in list.split():
			if i == arg :
				found=1
				break
		if found == 0 and out == 1 :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			end(0)
		return found 
	def guest_acpidown(arg):
		pass
	def list():
		cmd="VBoxManage list vms"
		output=execute(cmd).decode("utf-8")
		list=output.split("\n")[::]
		message=""
		for el in list:
			if len(el) != 0:	
				message=el.split('"')[1]+" "+message
		#print(message)
		return(message)
	def guest_pause(arg):
		logit.debug(PRGNAME,"Pausing")
		if vbctl.exist(arg) == 0 :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			sys.exit(0)
		cmd="VBoxManage controlvm "+arg+" pause"
		output=execute(cmd)
		logit.debug(PRGNAME,"Pausing proc exit")
		sys.exit(0)
	def guest_resume(arg):
		logit.debug(PRGNAME,"Pausing")
		if vbctl.exist(arg) == 0 :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			sys.exit(0)
		cmd="VBoxManage controlvm "+arg+" resume"
		output=execute(cmd)
		logit.debug(PRGNAME,"Pausing proc exit")
		sys.exit(0)
		pass
	def guest_reset(arg):
		pass
	def guest_start(arg):
		logit.debug(PRGNAME,"Starting "+arg)
		if vbctl.exist(arg) == 0 :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			sys.exit(0)
		cmd=("VBoxHeadless --startvm "+arg+" -vrde on &")
		output=execute(cmd).decode("utf-8")
		logit.debug(PRGNAME,"Pausing proc exit")
		end(0)
	def guest_status(arg):
		end(0)
	def guest_poweroff(arg):
		pass

def main():
	parseargs(sys.argv[1:])
	message="Starting "+PRGNAME
	logit.debug(PRGNAME,message)
	vmlist=vbctl.list()
	logit.info(PRGNAME,vmlist)
	end()

if __name__ == '__main__': 
	main()
else: 
	print("LOADED")
