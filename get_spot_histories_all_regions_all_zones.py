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
import datetime
import calendar

#=========================
def setupParserOptions():
        parser = optparse.OptionParser()
        parser.set_usage("%prog -i <instance type> --days=<days>")
        parser.add_option("-i",dest="instance",type="string",metavar="STRING",
                help="Amazon instance type (e.g. r3.8xlarge, t2.micro, etc.)")
        parser.add_option("--days",dest="days",type="int",metavar="INT",
                help="Timeframe over which to retrieve spot instance price history. Maximum is 90 days.")
	parser.add_option("-d", action="store_true",dest="debug",default=False,
                help="debug")
        options,args = parser.parse_args()

        if len(args) > 0:
                parser.error("Unknown commandline options: " +str(args))

        if len(sys.argv) < 3:
                parser.print_help()
                sys.exit()
        params={}
        for i in parser.option_list:
                if isinstance(i.dest,str):
                        params[i.dest] = getattr(options,i.dest)
        return params

#=============================
def getSpotHistory(params,outdir,timeFrame,currentTime):	

	#Inputs
	instance=params['instance']

	#Regions returned from command: $ ec2-describe-regions
	if os.path.exists('%s/regions.txt'%(outdir)): 
		os.remove('%s/regions.txt' %(outdir))
 
	cmd = 'ec2-describe-regions > %s/regions.txt' %(outdir)
	subprocess.Popen(cmd,shell=True).wait()

	r1 = open('%s/regions.txt' %(outdir),'r')

	#Loop over all regions
	for regionline in r1:
		
		region=regionline.split()[2]

		os.environ["EC2_URL"] = "%s" %(region)

		#Get region name
		region=region.split('.')[1]

		print '\n Working on region %s' %(region)

		if os.path.exists('%s/%s.txt' %(outdir,region)):
			os.remove('%s/%s.txt' %(outdir,region))

		#Get list of availability zones
		cmd = 'ec2-describe-availability-zones --region %s > %s/%s.txt' %(region,outdir,region)
		if params['debug'] is True:
                                print cmd
		subprocess.Popen(cmd,shell=True).wait()

		f1=open('%s/%s.txt' %(outdir,region),'r')

		for line in f1: 
			zone=line.split()[1]
		
			if os.path.exists('%s/%s_%s_%s_to_%s_spotHistory.txt' %(outdir,zone,instance,timeFrame,currentTime)):
				os.remove('%s/%s_%s_%s_to_%s_spotHistory.txt' %(outdir,zone,instance,timeFrame,currentTime))	

			cmd = 'ec2-describe-spot-price-history -t %s -d Linux/UNIX -a %s -s %sT14:10:34-0500 > %s/%s_%s_%s_to_%s_spotHistory.txt' %(instance,zone,timeFrame,outdir,zone,instance,timeFrame,currentTime)
			if params['debug'] is True:
				print cmd
			subprocess.Popen(cmd,shell=True).wait()
			

		f1.close()

		os.remove('%s/%s.txt' %(outdir,region))

	r1.close()
	os.remove('%s/regions.txt' %(outdir))


#==============================
def checkConflicts(params):

	instanceList='m3.large, i2.8xlarge, c3.2xlarge, hs1.8xlarge, c1.xlarge, r3.4xlarge, g2.2xlarge, m1.small, c1.medium, m3.2xlarge, c3.8xlarge, m2.xlarge, r3.2xlarge, t1.micro, cr1.8xlarge, r3.8xlarge, cc1.4xlarge, m1.medium, r3.large, c3.xlarge, i2.xlarge, m3.medium, cc2.8xlarge, m1.large, cg1.4xlarge, i2.2xlarge, c3.large, i2.4xlarge, c3.4xlarge, r3.xlarge, m1.xlarge, hi1.4xlarge, m2.4xlarge, m2.2xlarge, m3.xlarge'.split(', ')

	if not params['instance'] in instanceList:
		print '\nError: Instance %s is not a valid Amazon instance type. Exiting.\n' %(params['instance'])
		sys.exit()

	if params['days'] >90:
		print '\nA larger time frame than 90 days has been specified (%i days). Using 90 day limit instead.\n' %(params['days'])
		params['days']=90

	if os.path.exists('SpotHistory_%s_%s_last%02ddays' %(params['instance'],datetime.datetime.now().strftime('%Y-%m-%d'),params['days'])):
		print '\nError: Directory SpotHistory_%s_%s_last%02ddays already exists. Exiting.\n' %(params['instance'],datetime.datetime.now().strftime('%Y-%m-%d'),params['days'])
		sys.exit()

	return params

#==============================
def getDates(prevDay):

	today = datetime.datetime.now()
	dtdelta=datetime.timedelta(days=-prevDay)
	prevDate=today+dtdelta

	return '%s' %(prevDate.strftime('%Y-%m-%d'))

#=============================
def checkAWSPath():

	ec2 = subprocess.Popen("env | grep EC2_HOME", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
	
	if not ec2:
                print '\n Error: No AWS CLI tools environment set for $EC2_HOME. Exiting.\n' 

	key=subprocess.Popen("env | grep AWS_ACCESS_KEY", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
	secret=subprocess.Popen("env | grep AWS_SECRET_KEY", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
	awsid=	subprocess.Popen("env | grep AWS_USER_ID", shell=True, stdout=subprocess.PIPE).stdout.read().strip()

	if not key: 
		print '\n Error: No AWS_ACCESS_KEY specified in the environment as $AWS_ACCESS_KEY. Exiting.\n' 
		sys.exit()

	if not secret: 
                print '\n Error: No AWS_SECRET_KEY specified in the environment as $AWS_SECRET_KEY. Exiting.\n' 
		sys.exit()

	if not awsid: 
                print '\n Error: No AWS_USER_ID specified in the environment as $AWS_USER_ID. Exiting.\n' 
		sys.exit()
#==============================
if __name__ == "__main__":

	params=setupParserOptions()
	
	checkAWSPath()
	params=checkConflicts(params)
	prevDate=getDates(params['days'])

	outdir='SpotHistory_%s_%s_last%02ddays' %(params['instance'],datetime.datetime.now().strftime('%Y-%m-%d'),params['days'])
	os.makedirs(outdir)
	getSpotHistory(params,outdir,prevDate,datetime.datetime.now().strftime('%Y-%m-%d'))
		
