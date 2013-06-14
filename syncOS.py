#!/usr/bin/python
# -*- coding: utf8 -*-
"""
	fsarchiver based FS backup
"""

import sys
import os
import getopt
import subprocess

#main

PRGNAME=os.path.basename(sys.argv[0])
NEEDED=['fsarchiver']

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
	level_value=[ 'info','debug','verbose','run','error','fatal','silent']		
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
	print('PRGNAME')

def parseargs(argv):
	option={}
	if len(argv)==0:
		return
	try:
		opts, args = getopt.getopt(argv, "AdF:hoPs:t:qvz:", ["help"])
	except getopt.GetoptError:
		Message.fatal(PRGNAME,"Argument error",10)
	if Message.getlevel()=='debug':
		Message.debug(PRGNAME,"Params "+str(opts)+" "+str(args))
	for i,el in enumerate(opts):
		if '-d' in el:
			"remove -d arg from opts string and go debug"
			opts.pop(i)
			Message.setlevel('debug')
			Message.debug(PRGNAME,"going debug, remaining args "+str(opts))
	
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			end(0)
		elif opt == '-A':
			option['ALL']=1
		elif opt == '-D':
			option['DEST']=arg
		elif opt == '-o':
			option['OVERWRITE']=1
		elif opt == 'q':
			Message.setlevel='silent'
		elif opt == '-P':
			option['PART']=1
		elif opt == '-t':
			option['TARGET']=arg
		elif opt == '-z':
			option['ZIP']=arg
		else:
			Message.error(PRGNAME,"Option "+opt+" not valid")
			usage()
			end(1)

def cmd_exists(cmd):
	return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

if __name__ != '__main__':
	print('loaded')
else:
	for i in NEEDED:
		if cmd_exists(i) == False:
			Message.fatal(PRGNAME,"Command "+i+" is not found")
	if os.geteuid() != 0:
		Message.error(PRGNAME,"You have no root perms")	
	option={}
	parseargs(sys.argv[1:])
	if "DEBUG" in os.environ:
        	Message.setlevel('debug')
	Message.debug(PRGNAME,'main')
