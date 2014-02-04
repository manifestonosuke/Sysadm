#!/usr/bin/python3
# -*- coding: utf8 -*-

"""
	Virtualbox command line utility
"""

"""
	DONE
	* Improve date display with -l option (...6T14:14:43.847000000)
	* Change option S that easy mistake with -s 
	TODO 
	* Show all ips when -L 
	* Improve ssh connection to fork and exit instead of os.system
	* Improve VRDE settings 
	* Add IP in -l (interesting ?)
	* Improve extention pack (install and display info) => Check other OS  
	* Show disk info on -L (VBoxManage showvminfo openwave_ows3_1380702533  --machinereadable  |grep -i "SATA Controller" puis vboxmanage hdinfo)

"""

import sys
import os
import getopt
import signal
import subprocess
import re
from time import sleep


PORT="3389-3399"
PRGNAME=os.path.basename(sys.argv[0])
if "DEBUG" in os.environ:
	DEBUG=os.environ["DEBUG"]
	#logit.debug(PRGNAME,'DEBUG mode set from shell ')
	#print('osdebug '+DEBUG)
else: 
	DEBUG=0 
VBLOG=0


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
	#global PRGNAME
	ARGS=""
	message="""Handle command line for vbox easily
Run without arg will list vbox on the machine 
"""
	print(message)
	message="usage : "+PRGNAME+"\n"
	add="""
	-d : run in debug mode
        -l : List VM with power status (State) and general info about virtualbox configuration
        -L : Give summary status of a named vm 
        -p : pause the vbox 
        -r : resume the vbox
        -R : Reset the vbox     
        -s : start the vbox
        -S : ssh to the boxes name 
        -0 : Power OFF the vbox
        -v : full verbose mode (will list all vbox command runned)
	-V : set vrde on on port range 3389-3399
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
	#global DEBUG
	#print('logit debug '+str(DEBUG))
	def __init__(self,prg,message,extra="standard"): 
		self.p=prg
		self.m=message
		self.e=extra
	
	def info(p,m):
		print("%-10s : %-10s : %-30s" % ("INFO",p,m))
	
	def error(p,m):
		print("%-10s : %-10s : %-30s" % ("ERROR",p,m))	
		end(9)

	def debug(p,m):
		#print('debug.debug : ',DEBUG)
		if DEBUG == 1:
			#print('debug.debug : ',DEBUG)
			print("%-10s : %-10s : %-30s" % ("DEBUG",p,m))
	def exec(p,m):
		if VBLOG == 1:
			print("%-10s : %-10s : %-30s" % ("VBLOG",p,m))

def parseargs(argv):
	global DEBUG
	#print('debug '+str(DEBUG))
	if '-d' in sys.argv :
		print('debug',sys.argv)
		DEBUG=1
		while "-d" in sys.argv : sys.argv.pop(sys.argv.index("-d"))	
		print('debug',sys.argv)
	logit.debug(PRGNAME+"...parseargs","Parsing args")
	if len(sys.argv) == 1:
		logit.debug(PRGNAME,"argument parsing, only 0 arg")
		vmlist=vbctl.list()
		logit.info(PRGNAME,vmlist)
		end()
	if len(sys.argv) == 2 and sys.argv[1][0] != "-" :
		logit.debug(PRGNAME,"argument parsing, only 1 arg")
		if vbctl.exist(sys.argv[1],silent=1) == 0 :
                        logit.info(PRGNAME,"Machine "+sys.argv[1]+" do not exist")
                        sys.exit(0)
		else:
			#vmlist=vbctl.list()
			#print(sys.argv[1])
			AA=vbctl.guest_status(sys.argv[1],'VMState')
			print(AA)
			end()
	try:
		opts, args = getopt.getopt(argv, "dG:hO:lL:p:r:R:s:S:vV:0:", ["help"])
	except getopt.GetoptError:
		logit.info(PRGNAME+"...parseargs","Bad argument")
		usage()
		sys.exit(2)
	# print(opts,args)
	# Debug option need to be setup first
	#for i in opts:
	#	if i[0] == '-d':
	#		DEBUG=1
	logit.debug(PRGNAME," APARSE : "+str(opts)+" : "+str(args))
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt == '-d':
			##global DEBUG
			DEBUG = 1
		elif opt == '-G':
			vbctl.setvrde()
		elif opt == '-0' :
			vbctl.guest_off(arg)
			end(0)
		elif opt == '-l' :
			for i in vbctl.list().split():
				logit.debug(PRGNAME,"guest_status")
				vmstruct=vbctl.guest_status(i,'none')
				status=vbctl.guest_status(i,'VMState',vmstruct)
				logit.debug(PRGNAME,"guest_status")
				status=status+" since "+vbctl.guest_status(i,'VMStateChangeTime',vmstruct)
				status=status.split()[0]+" ("+status.split()[2][0:10]+")"
				logit.info(PRGNAME,i+" "+status)
			cmd="VBoxManage list extpacks"
			output=execute(cmd).decode('utf-8')
			pack=0
			packlist=[]
			vrde=""
			for i in output.split('\n'):
				if re.match('Pack no.',i):
					pack=1
					packlist.append(i)
				if re.match('VRDE Module',i):
					vrde=i	
			if vrde != "":
				logit.info(PRGNAME,"Extension found")
				print(vrde)
			if pack == 1 : 
				for i in packlist:
					print(i)
			else:
				cmd="VBoxManage --version"
				output=execute(cmd).decode('utf-8')
				output=output.split('_')[0]
				print(PRGNAME,"Download ext pack here : ")
				print('http://download.virtualbox.org/virtualbox/'+output+'/Oracle_VM_VirtualBox_Extension_Pack-'+output+'.vbox-extpack')
			end(0)
		elif opt == '-L' :
			status=vbctl.guest_details(arg)
			end(0)	
		elif opt == '-p' :
			vbctl.guest_pause(arg)
			end(0)
		elif opt == '-r' :
			vbctl.guest_resume(arg)
			end(0)
		elif opt == '-R' : 
			vbctl.guest_reset(arg)
			end(0)
		elif opt == '-s' :
			logit.info(PRGNAME,"Starting machine "+arg)
			rez=vbctl.guest_start(arg)
			end(0)
		elif opt == '-S' :
			arg=vbctl.exist(arg,1)
			if arg == "none" :
				logit.info(PRGNAME,"Machine "+arg+" do not exist")
				sys.exit(0)
			print(arg)
			status=vbctl.guest_ssh(arg)
			end(0)	
		elif opt == '-v' :
			global VERBOSE
			VERBOSE=1
		elif opt == '-V' :
			status=vbctl.guest_details(arg,param="vrde")
			if status == "on":
				logit.info(PRGNAME,"VRDE is already on")
			else:
				logit.info(PRGNAME,"Setting VRDE port range "+PORT)
				cmd="VBoxManage modifyvm "+arg+" --vrde on"
				output=execute(cmd).decode('utf-8')
				cmd="VBoxManage modifyvm "+arg+" --vrdeport "+PORT
				output=execute(cmd).decode('utf-8')
			end(0)
		elif opt == 0 :
			vbctl.guest_poweroff(arg)
			end(0)
		else: 
			message="Argument "+opt+" not valid"
			logit.info(PRGNAME,message)
			end(0)

def execute(command, **option):
	global PRGNAME
	#global DEBUG
	THISFUNC=PRGNAME+".execute"
	logit.debug(THISFUNC,"Executing : "+command)
	if len(option) != 0:
		for i in option:
			if i == "background":
				timewait=option[i]
		logit.debug(THISFUNC,"Subprocess with timer "+str(timewait))
		command=command+" &"
		logit.exec(PRGNAME,cmd)
		ps=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		sleep(timewait)
		logit.debug(THISFUNC,"launched"+command)
		output=ps.stdout.read()
		print(output)	
		end(0)
	
	logit.exec(PRGNAME,command)
	ps=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#retcode = ps.returncode
	stdout,stderr=ps.communicate()
	retcode = ps.returncode
	if (retcode != 0):
		logit.debug(THISFUNC,"Error executing  %s " % command)
		logit.debug(THISFUNC,"return message is : "+str(stderr.decode("utf-8")))
		message="Error executing "+command+"\n"+stderr.decode("utf-8")
		#raise Exception(message)	
		logit.error(THISFUNC,message)
	else:
		#logit.debug(THISFUNC,"Command return errorlog "+str(stderr))
		#logit.debug(THISFUNC,"Command output standard"+str(stdout))
		return(stdout)

class vbctl():
	global PRGNAME
	global DEBUG
	#print('vbctl.debug : '+DEBUG)
	def __init__(self,a,b="none"):
		arg=a
		value=b
	def setvrde():
		pass
	def exist(arg,fuzzy=0,silent=0):
		THISFUNC=PRGNAME+".exist"
		logit.debug(THISFUNC,"checking if "+arg+" exist")
		list=vbctl.list().split()
		logit.debug(THISFUNC,"vbox list "+str(list))
		found=0
		if fuzzy == 0:
			if arg in list: 
				return 1
			else:
				return 0
				
		for vm in list:
			if str(re.search(arg,vm)) != 'None':
				target=vm
				found+=1
		logit.debug(PRGNAME,"fuzzy search "+str(found)+" "+arg+" "+str(list))
		if found == 0 :
			if silent != 1 : 
				logit.debug(PRGNAME,"vm not found "+arg)
			return "none"
		if found > 1 :
			logit.error(PRGNAME,"vm name matching return more than 1 host for "+arg)
			exit(2)
		else:
			if silent != 1 :
				logit.debug(PRGNAME,"vm name matching return "+target)
			found=1
			return target
 
	def guest_off(arg):
		THISFUNC=PRGNAME+".guest_off"
		logit.debug(THISFUNC,"Pausing")
		if vbctl.exist(arg) == 0 :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			sys.exit(0)
		cmd="VBoxManage controlvm "+arg+" poweroff"
		output=execute(cmd)
		#print(output)
		logit.debug(THISFUNC,"Pausing proc exit")
		sys.exit(0)
	def list():
		cmd="VBoxManage list vms"
		output=execute(cmd).decode("utf-8")
		#print(output)
		if len(output)==0:
			logit.info(PRGNAME,"No machine found")
			return("")
		list=output.split("\n")[::]
		message=""
		for el in list:
			if len(el) != 0:	
				message=el.split('"')[1]+" "+message
		return(message)
	def guest_details(arg,param="default"):
		THISFUNC=PRGNAME+".guestdetails"
		arg=vbctl.exist(arg,1)
		if arg == "none" :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			end(0)
		dict=vbctl.guest_status(arg,'none')
		if param != "default":
			return(dict[param][0].strip('"'))
		param=['ostype','VMState','memory','cpus']
		print("Name\t: {} ".format(arg))
		### not needed  ?###  dict=vbctl.guest_status(arg)
		if vbctl.guest_status(arg,'vrde',dict) == "on":
			param.append('vrdeports')
		else:
			param.append('vrde')
		for i in param:
			if i in dict.keys():
				print(i+"\t: {} ".format(dict[i][0].strip('"')))
			else:
				print(i+"\t: not set")
		# ip forward check until forward(0) dont exist 
		for N in range(0,6):
			label='Forwarding('+str(N)+')'
			#label1='Forwarding(0)'
			#print(label)
			#print(label1)
			#logit.info(PRGNAME,label)
			#dict.keys()
			if label in dict.keys():
				print(label+"\t: {} ".format(dict[label][0].strip('"')))
				#dict[label]
		# Nic info
		for N in range(1,8):
			label='nic'+str(N)
			logit.debug(PRGNAME,"Checking nic conf for "+label)
			if label in dict.keys():
				#print(dict[label][0])
				if dict[label][0].strip('"') == 'none':
					break
				else:
					if dict[label][0].strip('"') == "hostonly" :
						label1='hostonlyadapter'+str(N)
						print(label+"\t: hostonly ({})".format(dict[label1][0].strip('"')))
					else:
						print(label+"\t: {} ".format(dict[label][0].strip('"')))
				dummy="/VirtualBox/GuestInfo/Net/"+str(N-1)+"/V4/IP"	
				ip=vbctl.guest_property(arg,dummy)
				print("ip"+str(N)+" \t: "+ip)
		#end(0)
	def guest_pause(arg):
		THISFUNC=PRGNAME+".guest_pause"
		logit.debug(THISFUNC,"Pausing")
		if vbctl.exist(arg) == 0 :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			sys.exit(0)
		cmd="VBoxManage controlvm "+arg+" pause"
		output=execute(cmd)
		logit.debug(THISFUNC,"Pausing proc exit")
		sys.exit(0)
	def guest_resume(arg):
		THISFUNC=PRGNAME+".guest_resume"
		logit.debug(THISFUNC,"Pausing")
		if vbctl.exist(arg) == 0 :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			sys.exit(0)
		cmd="VBoxManage controlvm "+arg+" resume"
		output=execute(cmd)
		logit.debug(THISFUNC,"Pausing proc exit")
		end(0)
	def guest_reset(arg):
		THISFUNC=PRGNAME+".guest_reset"
		logit.debug(THISFUNC,"Reset")
		if vbctl.exist(arg) == 0 :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			sys.exit(0)
		cmd="VBoxManage controlvm "+arg+" reset"
		output=execute(cmd)
		logit.debug(THISFUNC,"Pausing proc exit")
		end(0)
	def guest_start(arg):
		THISFUNC=PRGNAME+".guest_start"
		logit.debug(THISFUNC,"Starting "+arg)
		if vbctl.exist(arg) == 0 :
			logit.info(PRGNAME,"Machine "+arg+" do not exist")
			sys.exit(1)
		#cmd=("VBoxHeadless --startvm "+arg+" -vrde on &")
		#cmd=("VBoxHeadless --startvm "+arg+" -vrde on")
		cmd=("VBoxManage startvm "+arg+" --type headless")
		output=execute(cmd).decode("utf-8")
		print(output)
		logit.debug(THISFUNC,"Starting proc exit")
		end(0)
	def guest_status(arg,ask,dict={}):
		""" return showvminfo struct if ask == none 
		or dict that contain the VBoxManage showvminfo result """
		
		THISFUNC=PRGNAME+".guest_status"
		logit.debug(THISFUNC,"args => "+arg+" "+ask)
		if dict == {}:
			showvminfo={}
			cmd="VBoxManage showvminfo --machinereadable "+arg
			output=execute(cmd).decode("utf-8")
			for el in output.split("\n"):
				el2=el.split('=')
				key,value=el2[0],el2[1:]
				showvminfo[key]=value
		else:
			showvminfo=dict
		if ask=="display":
			print(showvminfo)
			return(showvminfo)
		elif ask=="none":
			return(showvminfo)
		else:
			# vboxmanage return list with "" chars
			# get the 1st el and remove the " with split (return list)
			# and get the el #1
			status=str(showvminfo[ask][0]).split('"')[1]
			logit.debug(THISFUNC,"Status : "+status)
			return(status)

	# Now only returning IP (0)	
	def guest_property(arg,query="/VirtualBox/GuestInfo/Net/0/V4/IP",field="value:"):
		THISFUNC=PRGNAME+".guest_status"
		logit.debug(THISFUNC,"args => "+arg+" "+query)	
		showvminfo={}
		cmd="VBoxManage guestproperty enumerate "+arg
		output=execute(cmd).decode("utf-8")
		for el in output.split("\n"):
			if query in el:
				this=re.split(' ',el)
				pos=this.index(field)
				#print(this,pos)
				ret=this[pos+1]
				if ret != "," and ret != "" :
					ret=ret.rstrip(",")
					return(ret)
				else:
					#print("unknow")
					return("unknow") 
		return("none")
	
	def guest_poweroff(arg):
		pass
	
	def guest_ssh(arg):
		THISFUNC=PRGNAME+".guest_ssh"
		ip=vbctl.guest_property(arg)
		#print('ip'+ip+"unknow")
		if ip == "unknow" :
			logit.debug(THISFUNC,"Cant ssh ip request returned "+ip)
			message="Host IP for "+arg+" is not know, ssh impossible"
			logit.info(PRGNAME,message)
		else:
			logit.debug(THISFUNC,"Trying to ssh to ip "+str(ip))
			command="ssh root@"+str(ip)
			print(command)
			os.system(command)
			#pro=subprocess.Popen(command)
			#pro.communicate()
			

def main():
	#global DEBUG
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
