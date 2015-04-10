#!/usr/bin/env python

import optparse
from sys import *
import os,sys,re
from optparse import OptionParser
import glob
import subprocess
from os import system
import linecache
import time
from datetime import datetime
import calendar

#=========================
def setupParserOptions():
        parser = optparse.OptionParser()
        parser.set_usage("%prog -i <spot history file>")
        parser.add_option("-i",dest="inputfile",type="string",metavar="STRING",
                help="Spot history file")
	parser.add_option("-d", action="store_true",dest="debug",default=False,
                help="debug")
        options,args = parser.parse_args()

        if len(args) > 0:
                parser.error("Unknown commandline options: " +str(args))

        if len(sys.argv) < 2:
                parser.print_help()
                sys.exit()
        params={}
        for i in parser.option_list:
                if isinstance(i.dest,str):
                        params[i.dest] = getattr(options,i.dest)
        return params

#=============================
def calc_elapsed_time(params):
	f=params['inputfile']	
	o = '%s_elapsedTime.txt' %(params['inputfile'][:-4])
	o1 = open(o,'w')

	tot=len(open(f,'r').readlines())

	count=1

	while count <=tot-1:

		line = linecache.getline(f,count)
		linenext=linecache.getline(f,count+1)

		if params['debug'] is True:
			print line[:-2]
			print linenext[:-2]

		region1=line.split()[5]
		region2=linenext.split()[5]

		if region1 != region2:
			if params['debug'] is True:
				print '<--------------------------------->Next region..'
			count = count + 1
			continue
	
		t1=datetime.strptime(line.split()[2],'%Y-%m-%dT%H:%M:%S-0500')
		t2=datetime.strptime(linenext.split()[2],'%Y-%m-%dT%H:%M:%S-0500')
		price=line.split()[1]
		if params['debug'] is True:
			print (t1-t2).seconds
		o1.write('%s\t%s\t%f\n' %(region1,price,(t1-t2).seconds))

		count = count + 1

#==============================
def checkConflicts(params):
	if os.path.exists('%s_elapsedTime.txt' %(params['inputfile'][:-4])):
		print 'File %s_elapsedTime.txt already exists. Exiting.' %(params['inputfile'][:-4])
		sys.exit()
	
#==============================
def getTimeBelowThresh(f1,thresh,debug):

	if debug is True:
		print 'Working on price=%s' %(thresh)
	f = open(f1,'r')
	totalTime=0
	timeBelowThresh=0
	
	for line in f:
		price=line.split()[1]
		if debug is True:
			print 'Current price=%s' %(price)
		if float(price) < float(thresh):
			if debug is True:
				print '%s < %s' %(price,thresh)
			timeBelowThresh=timeBelowThresh+float(line.split()[2])
		totalTime=float(line.split()[2])+totalTime

	if debug is True:
		print 'Time below $%0.2f/hr: %0.3f seconds, %0.3f minutes, %0.3f hours, %0.3f days' %(float(thresh),timeBelowThresh,timeBelowThresh/60,timeBelowThresh/3600,timeBelowThresh/86400)
	print 'Fraction time below $%0.2f/hr:  %0.4f' %(float(thresh),timeBelowThresh/totalTime)

#==============================
if __name__ == "__main__":

	thresholds='0.35,0.45,0.55,0.65'.split(',')

	params=setupParserOptions()
	checkConflicts(params)
	
	print 'Working on %s' %(params['inputfile'])

	calc_elapsed_time(params)

	for thresh in thresholds:
		getTimeBelowThresh('%s_elapsedTime.txt' %(params['inputfile'][:-4]),thresh,params['debug'])

