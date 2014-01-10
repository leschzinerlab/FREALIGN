#!/usr/bin/env python

import optparse
from sys import *
import os,sys,re
from optparse import OptionParser
import glob
import subprocess
from os import system
import linecache

def setupParserOptions():
	parser = optparse.OptionParser()
	parser.set_usage("%prog --f1=<stack1> --f2=<stack2> --p1=<parameter1> --p2=<parameter2>")
	parser.add_option("--f1",dest="stack1",type="string",metavar="FILE",
		help="raw, IMAGIC particle stack for stack #1 (black particles)")
	parser.add_option("--f2",dest="stack2",type="string",metavar="FILE",
		help="raw, IMAGIC particle stack for stack #2 (black particles)")
	parser.add_option("--p1",dest="param1",type="string",metavar="FILE",
		help="Parameter file #1 from FREALIGN refinement for stack #1")
	parser.add_option("--p2",dest="param2",type="string",metavar="FILE",
		help="Parameter file #2 from FREALIGN refinement for stack #2")
	parser.add_option("--apix",dest="apix",type="float", metavar="FLOAT",
                help="pixel size")
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

def getIMAGICPath():
	### get the imagicroot directory
	impath = subprocess.Popen("env | grep IMAGIC_ROOT", shell=True, stdout=subprocess.PIPE).stdout.read().strip()
        imagicpath = impath.replace("IMAGIC_ROOT=","")
        if imagicpath != '/opt/qb3/imagic-070813':
			print "imagic/070813 was not found, make sure it is in your path"
        		sys.exit()


def getImagicVersion(imagicroot):
        ### get IMAGIC version from the "version_######S" file in
        ### the imagicroot directory, return as an int
        versionstr=glob.glob(os.path.join(imagicroot,"version_*"))
        if versionstr:
                v = re.search('\d\d\d\d\d\d',versionstr[0]).group(0)
                return int(v)
        else:
                print "Could not get version number from imagic root directory"
		sys.exit()

def main(params):

	stack1 = params['stack1']
	stack2 = params['stack2']
	param1 = params['param1']
	param2 = params['param2']	
	apix = float(params['apix'])
	debug = params['debug']
	p1 = open(param1,'r')
	p2 = open(param2,'r')

	p1_1 = param1.strip('.par')
	r1 = open("merge_r1.par",'w')

	p2_1 = param2.strip('.par')
	r2 = open("merge_r2.par",'w')

	#Create parameter files
	print "\n"
	print "Creating new parameter files..."
	print "\n"
	count = 1 
	for line in p1:

		l = line.split()

		if l[0] == 'C':
			continue
	
		r1.write("%7d%8.3f%8.3f%8.3f%8.3f%8.3f%8.1f%6d%9.1f%9.1f%8.2f%7.2f%7.2f%6.2f%6.2f\n" %(float(l[0]),float(l[1]),float(l[2]),float(l[3]),(float(l[4]))/apix,(float(l[5]))/apix,float(l[6]),float(l[7]),float(l[8]),float(l[9]),float(l[10]),float(l[11]),float(l[12]),float(l[13]),float(l[14])))
		
		r2.write("%7d%8.3f%8.3f%8.3f%8.3f%8.3f%8.1f%6d%9.1f%9.1f%8.2f%7.2f%7.2f%6.2f%6.2f\n" %(float(l[0]),float(l[1]),float(l[2]),float(l[3]),(float(l[4]))/apix,(float(l[5])/apix),float(l[6]),float(l[7]),float(l[8]),float(l[9]),float(l[10]),0,float(l[12]),float(l[13]),float(l[14])))
	
		count = 1 + count

	count = count - 1
	for line in p2:
		l2 = line.split()
		if l2[0] == 'C':
			continue
		
		r1.write("%7d%8.3f%8.3f%8.3f%8.3f%8.3f%8.1f%6d%9.1f%9.1f%8.2f%7.2f%7.2f%6.2f%6.2f\n" %(float(l2[0])+count,float(l2[1]),float(l2[2]),float(l2[3]),(float(l2[4]))/apix,(float(l2[5]))/apix,float(l2[6]),float(l2[7]),float(l2[8]),float(l2[9]),float(l2[10]),0,float(l2[12]),float(l2[13]),float(l2[14])))
		
		r2.write("%7d%8.3f%8.3f%8.3f%8.3f%8.3f%8.1f%6d%9.1f%9.1f%8.2f%7.2f%7.2f%6.2f%6.2f\n" %(float(l2[0])+count,float(l2[1]),float(l2[2]),float(l2[3]),(float(l2[4]))/apix,(float(l2[5]))/apix,float(l2[6]),float(l2[7]),float(l2[8]),float(l2[9]),float(l2[10]),float(l2[11]),float(l2[12]),float(l2[13]),float(l2[14])))
	
	r1.close()
	r2.close()	
	
	#Reverse order of each stack
	cmd="~michael/bin/reverseStack.b %s" %(stack1)
	subprocess.Popen(cmd,shell=True).wait()

	cmd="~michael/bin/reverseStack.b %s" %(stack2)
	subprocess.Popen(cmd,shell=True).wait()

	#Merge reversed stacks
	print "\n"
	print "Merging stacks..."
	print "\n"

	s1 = stack1[:-4]
	s2 = stack2[:-4]

	if debug is True:

		print "proc2d %s_rev.img merge.img" %(s1)

	cmd="proc2d %s_rev.img merge.img" %(s1)
	subprocess.Popen(cmd,shell=True).wait()	

	cmd="proc2d %s_rev.img merge.img" %(s2)
	subprocess.Popen(cmd,shell=True).wait()

	print "\n"
	print "Converting particle stack into FREALIGN format..."
	print "\n"

	cmd="~michael/bin/imagic_to_frealign_mult.b merge.img"
	subprocess.Popen(cmd,shell=True).wait()

if __name__ == "__main__":
     imagicroot = getIMAGICPath()
     params=setupParserOptions()
     main(params)
   
