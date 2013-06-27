#!/usr/bin/python3
# -*- coding: utf8 -*-
"""
	fsarchiver based FS backup
"""

import sys
import os
import getopt
import subprocess
import re
from datetime import datetime 
from stat import *
from time import sleep
from datetime import datetime


#main

PRGNAME=os.path.basename(sys.argv[0])
NEEDED=['fsarchiver','blkid']



def end(code=0):
	sys.exit(code)

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
			print("%-10s : %-10s : %-30s" % ("INFO",p,m))
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

def usage():
	message="usage : "+PRGNAME
	add="""
	[-o] [-q] [ -F <FSTYPE> ] [ -t target dump dir ]  [ /dev/devicename OR LABEL ] || [-A] 
	Backup file sytem using fsarchiver
	default is to backup all partition of ext4 which are not mounted 
	-A      Do all parition but mounted one backup
	-d      debug mode
	-D      Default target disk to backup 
	-F      Filesytem type for the source device (by default just work for ext2/3/4)
	-h      This page 
	-L	List device/label for select fstype (default ext2/3/4)
	-o      Force overwrite when file exist
	-P      Save the MBR and partition table
	-q      Silent mode (to be done)
	-t      Target dir to write output file (if not specified $(pwd))
	-z      Compression level (as for fsarchiver)
	"""
	add+="\nDefault device to dump is "+option['DEVICE']
	add+="\nDefault target directory to store archives is "+option['TARGET']
		
	print(message+add)

def parseargs(argv,option):
	Message.debug(PRGNAME,"going debug, remaining args "+str(argv))
	if len(argv)==0:
		return option
	try:
		opts, args = getopt.getopt(argv, "AdF:hLoPs:t:qvz:", ["help"])
	except getopt.GetoptError:
		Message.fatal(PRGNAME,"Argument error",10)
	#if Message.getlevel()=='debug':
	Message.debug(PRGNAME,"Params "+str(opts)+" "+str(args))
	for i,el in enumerate(opts):
		if '-d' in el:
			"remove -d arg from opts string and go debug"
			opts.pop(i)
			Message.setlevel('debug')
			Message.debug(PRGNAME,"going debug, remaining args "+str(opts)+" "+str(args))
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			end(0)
		elif opt == '-A':
			option['ALL']=1
		elif opt == '-D':
			option['DEVICE']=arg
		elif opt == '-F':
			option['TYPE']=arg
		elif opt == '-L':
			option['ACTION']='list'
		elif opt == '-o':
			option['OVERWRITE']=1
		elif opt == 'q':
			Message.setlevel='silent'
		elif opt == '-P':
			option['ACTION']='part'
		elif opt == '-s':
			option['SOURCE'].append(arg)
		elif opt == '-t':
			option['TARGET']=arg
		elif opt == '-v':
			Message.setlevel='verbose'
		elif opt == '-z':
			option['ZIP']=arg
		else:
			Message.error(PRGNAME,"Option "+opt+" not valid")
			usage()
			end(1)
	""" Remaining args are devices to dump"""
	if len(args) > 0: 
		for i in args:
			option['SOURCE'].append(i)
	return option

def cmd_exists(cmd):
	return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def execute(cmd,option={}):
	if len(option) == 0:
		pass	 		

	 	

def do_part_backup(option):
	""" we got the needed params in the list
	we build the dest file with device name and command name
	"""
	ret=0
	if not S_ISBLK(os.stat(option['DEVICE']).st_mode): 
		Message.fatal(PRGNAME,"device "+option['DEVICE']+ "is not block device")
	else:
		for i in option['DEVICE']:
			if len(i) > 0:
				shortfile=i
				
	d=str(datetime.now().year)+"."+str(datetime.now().month)+"."+str(datetime.now().day)
	if cmd_exists('dd') == False:
		Message.warning(PRGNAME,"dd not found cant part backup")
	else:
		Message.info(PRGNAME,"Running dd backup")
		output=option['TARGET']+"/part-dd."+d+".backup"
		if os.path.exists(output):
			if option['OVERWRITE'] == 1:
				Message.info(PRGNAME,"Overwriting "+output)
			else:
				Message.fatal(PRGNAME,"Cant overwrite "+output)
		command="dd if="+option['DEVICE']+" of="+output+" bs=512 count=1 2>&1"
		Message.debug(PRGNAME,"Attempting to run"+command)
		ps=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout,stderr=ps.communicate()
		if ps.returncode == 0:
			print(stdout.decode("utf-8"))
		else:
			Message.error(PRGNAME,"dd return an error"+stdout)
			ret+=ps.returncode
	
	if cmd_exists('sfdisk') == False:
		Message.warning(PRGNAME,"sfdisk not found cant part backup")
	else:
		Message.info(PRGNAME,"Running sfdisk backup")
		output=option['TARGET']+"/sfdisk."+d+".backup"
		if os.path.exists(output):
			if option['OVERWRITE'] == 1:
				Message.info(PRGNAME,"Overwriting "+output)
			else:
				Message.fatal(PRGNAME,"Cant overwrite "+output)
		command="sfdisk -d "+option['DEVICE']+" > "+output
		Message.debug(PRGNAME,"Attempting to run"+command)
		ps=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout,stderr=ps.communicate()
		if ps.returncode == 0:
			print(stderr.decode("utf-8"))
		else:
			Message.error(PRGNAME,"dd return an error"+stderr)
			ret+=ps.returncode
	
	if cmd_exists('blkid') == False:
		Message.warning(PRGNAME,"blkid not found cant part backup")
	else:
		Message.info(PRGNAME,"Running blkid backup")
		output=option['TARGET']+"/blkid."+d+".backup"
		if os.path.exists(output):
			if option['OVERWRITE'] == 1:
				Message.info(PRGNAME,"Overwriting "+output)
			else:
				Message.fatal(PRGNAME,"Cant overwrite "+output)
		command="blkid > "+output
		Message.debug(PRGNAME,"Attempting to run"+command)
		ps=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout,stderr=ps.communicate()
		if ps.returncode == 0:
			print(stderr.decode("utf-8"))
		else:
			Message.error(PRGNAME,"dd return an error"+stderr)
			ret+=ps.returncode
		
	return(ret)

def build_device_label_dict():
	cmd="/sbin/blkid -o device"
	ps=subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
class Blkid():
	def __init__2(self):
		self.blkstruct={}
		cmd="blkid -o export"
		ps=subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout,stderr=ps.communicate()
		blk=stdout.decode("utf-8")
		blk=blk.split('\n')
		for i in blk:
			#print("begin "+i)
			if len(i) == 0:
				continue
			k,v=i.split("=")
			Message.debug(PRGNAME,"k v : "+k+" "+v)
			if k == "DEVNAME":
				device=v
				#device=str(os.path.split(v)[1])
				Message.debug(PRGNAME,"This is new dev "+v)
				self.blkstruct[device]={}
			else:
				Message.debug(PRGNAME,"This is new value "+k+" "+v)
				#print("device='{}'".format(device))
				self.blkstruct[device].update({str(k):str(v)})
				Message.debug(PRGNAME,self.blkstruct)

	def __init__(self):
		self.blkstruct={}
		cmd="blkid"
		ps=subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)	
		stdout,stderr=ps.communicate()
		blk=stdout.decode("utf-8")
		blk=blk.split('\n')
		blk.remove('')
		for line in blk:
			device=line.split(':')[0]
			args=line.split(':')[1]
			#print(device,args)
			self.blkstruct[device]={}
			args=args.split(' ')
			for tuple in args:
				if len(tuple) == 0:
					continue
				k,v=tuple.split("=")
				v=v.replace('"','')
				#print(tuple.split("=")[0],tuple.split("=")[1])
				#self.blkstruct[device].update({tuple.split("=")[0]:tuple.split("=")[1]})
				self.blkstruct[device].update({k:v})
		#print(self.blkstruct)
			
			

	def get(self):
		return self.blkstruct

	def get_device_label(self,option):
		for device in self.blkstruct:
			if self.blkstruct[device]['TYPE'] not in option['TYPE']:
				continue
			if 'LABEL' in self.blkstruct[device]:
				print(device+" : "+self.blkstruct[device]['LABEL'])
			else:
				print(device)
	
	def __getitem__(self):
		return self.blkstruct

	def get_valid_device(self,option):
		list=[]
		for i in self.blkstruct:
			if self.blkstruct[i]['TYPE'] in option['TYPE']:
				list.append(i)
		list.sort()
		return list

	def dev_to_x(self,dev='ALL',type='LABEL'):
		""" blkstruct is a Blkid object 
		match device name with blkid type with type var 
		return the list of type object mathing the device
		if dev arg is ALL return a list for all devices 
		"""
		list=[]
		ret=[]
		if dev == 'ALL':
			for i in self.blkstruct:
				list.append(i)
		else:
			list=[dev]
		for device in list:
			Message.debug(PRGNAME,"device : "+device+" struct keys"+str(self.blkstruct.keys()))
			if device not in self.blkstruct:
				Message.error(PRGNAME,"Device "+device+" not in blk sutruct")
				continue
			print('type',device,self.blkstruct[device])
			if type in self.blkstruct[device]:
				Message.debug(PRGNAME,"Label found "+self.blkstruct[device][type])
				ret.append(self.blkstruct[device][type])
		return ret
	
	def x_to_dev(self,value,x='LABEL'):
		"""return the device of the blkid flag x (default is LABEL)"""
		ret=[]
		for dev in self.blkstruct:
			if x in self.blkstruct[dev]:
				#print(self.blkstruct[dev][x],value)
				if self.blkstruct[dev][x] == value:
					#print(self.blkstruct[dev][x])
					ret.append(dev)
		return ret  

def is_dev(dev):
	if re.match('/dev/',dev):
		return True
	else:
		return False


def dump_fs(option,blk):
	""" dump the fs option is the struct with all params blk the blkid struct"""
	output=""
	cmd="fsarchiver savefs -v -j2"
	if not option['ZIP'] ==  0:
		cmd+="-z option['ZIP']"
	if not option['OVERWRITE'] ==  1:
		cmd+="-o "
	# i is the device to dump it can be dev like /dev/sdX or Label
	# blk.get() to retrieve blk data
	for i in option['SOURCE']:
		# get the sdxxxx part from /dev/...
		output=""
		run=""
		# We are on a device name using name has hostname + part number as filename
		if is_dev(i):
			part=i.split('/')[-1]
			this=blk.get()[i]
			if 'LABEL' in this:
				label=this['LABEL']
				Message.debug(PRGNAME,"found label "+label+"for device "+i)
				output=label+"."+part	
			else:
				output=os.uname()[1]+"."+part
		# We have a label and thus extract device 
		# Use label + partition (stripped from /dev.../) for filename	
		else:
			label=i
			Message.debug(PRGNAME,"Trying blk.x_to_dev for "+i)
			if blk.x_to_dev(i) == []:
				Message.warning(PRGNAME,"No dump for not found label "+i)
				continue
			#this=blk.get()[i]
			#if not 'LABEL' in this:
			#	Message.error(PRGNAME,"label "+label+"not found for device "+i)
			#	continue
			part=blk.x_to_dev(i)[0]
			shortpart=part.split('/')[-1]
			if len(part) == 0:
				Message.warning(PRGNAME,"Cant find label "+i+" skipping")
				continue
			output=label+"."+shortpart
		output=option['TARGET']+'/'+output+".fsa"
		run=cmd+" "+output+" "+part
		Message.debug(PRGNAME,"run command : "+run)
		run=run.split()
		ps=subprocess.Popen(run,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		Message.info(PRGNAME,"Attempting to dump "+part+" on file "+output)
		timestart=str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second)
		Message.info(PRGNAME,"Starting at "+timestart)
		
		# Prepare terminal settings
		term_size=int(os.popen('stty size', 'r').read().split()[1])
		delete=""

		
		while True:
			if ps.poll() != None:
				break
			try:
				# fsarchiver do write on stderr
				nextline = next(ps.stderr)
			except StopIteration:
				break
			
			line=nextline.decode('utf-8').rstrip('\n')
			# We will sort out lines starting with - for backup stream
			if not line[0] == '-':
				print(line)
				sys.stdout.flush()
			# Match bracket with word inside starting by 0 or more blank
			# and ending with 0 or more percenta
			# arg is the path of files dumped (starting from /)
			else:
				fields=re.findall("(\[ *\w*%?\])",line)
				percent=fields[1]
				arg=line[line.index('/'):]
				# Building output
				string=percent+" "+arg
				# limit output to term size
				string=string[:term_size-1]
				# Add time display 
				timecur="["+str(datetime.now().hour)+":"+str(datetime.now().minute)+"]"
				string=timecur+string
				print("\r"+string,sep='',end='')
				sleep(.001)
				line_size=len(string)
				sys.stdout.flush()
				delete=' '*line_size
				print("\r"+delete,end='')
		
		print()
		output = ps.communicate()[0].decode("utf-8")
		if len(output) > 0:
			print(output)
		ret = ps.returncode
		timeend=str(datetime.now().hour)+":"+str(datetime.now().minute)+":"+str(datetime.now().second)
		Message.info(PRGNAME,'End Job at '+timeend)

		#stdout,stderr=ps.communicate()
		#if ps.returncode == 0:
		#	print(stdout.decode("utf-8"))
		#else:
		#	Message.error(PRGNAME,"fsarchiver return an error")
		#	print(stderr)
		#	ps.returncode
		#print(stdout)	
		return ret	
	


if __name__ != '__main__':
	print('loaded')
else:
	for i in NEEDED:
		if cmd_exists(i) == False:
			Message.fatal(PRGNAME,"Command "+i+" is not found")
	option={
		'DEVICE' : '/dev/sda',	
		'SOURCE' : [],
		'TARGET' : './',
		'OVERWRITE' : 0,
		'ALL' : 0,
		'ACTION' : 'dump',
		'ZIP' : 0,
		'TYPE' : ['ext2','ext3','ext4']
	}

	option=parseargs(sys.argv[1:],option)
	if os.geteuid() != 0:
		Message.error(PRGNAME,"You have no root perms")	
	if "DEBUG" in os.environ:
        	Message.setlevel('debug')
	Message.debug(PRGNAME,"Main - running options are : \n"+str(option))
	try:
		if not S_ISDIR(os.stat(option['TARGET']).st_mode):
			Message.fatal(PRGNAME,"Directory "+option['TARGET']+" is not a directory")
	except OSError:
			Message.fatal(PRGNAME,"Directory "+option['TARGET']+" is not accessible")
	if option['ACTION'] == 'part':
		ret=do_part_backup(option)
		end(ret)
	
	devices=Blkid()
	if option['ACTION'] == 'list':
		ret=devices.get_device_label(option)
		end(0)

	if option['ALL'] == 0 and option['SOURCE'] == []:
		Message.error(PRGNAME,"no device to dump specified")
		usage()
		end(0)		
	
	if option['ALL'] == 1:
		# get_valid_device return list of device matching option['TYPE']
		valid_devices=devices.get_valid_device(option)
		for i in valid_devices:
			option['SOURCE'].append(i)
		if len(valid_devices) == 0:
			Message.warning(PRGNAME,"no devices selected with this arguments")
			end(0)
		Message.info(PRGNAME,"Starting to dump : "+" ".join(valid_devices)) 
	else:
		Message.info(PRGNAME,"starting to dump : "+" ".join(option['SOURCE']))
			
	dump_fs(option,devices)
	#disk.get()
	end(0)
