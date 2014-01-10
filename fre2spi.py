#!/usr/bin/env python

#To run:

#./fre2spi.py [frealign parameter file] [pixel size]
import optparse
from sys import *
import os,sys,re
from optparse import OptionParser
import glob
import subprocess
import sys

def setupParserOptions():
	parser = optparse.OptionParser()
	parser.set_usage("%prog -f <parameter>")
	parser.add_option("-f",dest="param",type="string",metavar="FILE",
		help="FREALIGN parameter file")
	parser.add_option("--apix",dest="apix",type="float", metavar="FLOAT",
		help="pixel size")
	options,args = parser.parse_args()

	if len(args) > 2:
		parser.error("Unknown commandline options: " +str(args))

	if len(sys.argv) < 3:
		parser.print_help()
		sys.exit()
		
	params={}
	for i in parser.option_list:
		if isinstance(i.dest,str):
			params[i.dest] = getattr(options,i.dest)
	return params

def main(params):
	parm=params['param']
	apix=float(params['apix'])

	new=parm.strip('.par')

	w=open('%s_param.spi' %(new),'w')

	shift=open('%s_shifts.spi' %(new),'w')

	angle=open('%s_angular.spi' %(new),'w')

	f=open(parm,'r')

	for line in f:

		l=line.split()

		if l[0] is 'C':

			continue

		sx=float(l[4])
		shx=sx/apix
		sy=float(l[5])
		shy=sy/apix

		w.write('%s	14	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s\n' %(l[0],l[1],l[2],l[3],shx,shy,l[6],l[7],l[8],l[9],l[10],l[11],l[12],l[13],l[14]))

		shift.write('%s		2	%s	%s\n' %(l[0],shx,shy))
		angle.write('%s		3	%s	%s	%s\n' %(l[0],l[1],l[2],l[3]))
	
	f.close()
	w.close()
	shift.close()
	angle.close()

if __name__ == "__main__":
     params=setupParserOptions()
     main(params)
