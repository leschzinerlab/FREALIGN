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
	parser.set_usage("%prog -p <parameter file> --apix=<float>")
	parser.add_option("-p",dest="param",type="string",metavar="FILE",
		help="FREALIGN parameter file after FREALIGN refinement")
	parser.add_option("--apix",dest="apix",type="float", metavar="FLOAT",
		help="Angstroms per pixel")
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

def main(params):

	param = params['param']
	apix = params['apix']
	debug = params['debug']
	o1 = '%s_old.par' %(param[:-4])
	out = open(o1,'w')
	f = open(param,'r')

	for line in f:

		l = line.split()

		if l[0] == 'C':
			print 'skipping line %s' %(l)
			continue
	
		if debug is True:

			print line

		count2 = float(l[0])
		psi = float(l[1])
		theta = float(l[2])
		phi = float(l[3])
		sx = float(l[4])/apix
		sy = float(l[5])/apix
		mag = float(l[6])
		micro = float(l[7])
                df1 = float(l[8])
                df2 = float(l[9])
                astig = float(l[10])
		occ = float(l[11])
		log = float(l[12])
		score = float(l[13])
		change = float(l[14])

		#print "%7d%8.3f%8.3f%8.3f%8.3f%8.3f%8.0f%6d%9.1f%9.1f%8.2f %7.2f %6.2f %6.2f %6.2f\n"%(count2,psi,theta,phi,sx,sy,mag,micro,df1,df2,astig,occ,log,score,change)
		out.write("%7d%8.3f%8.3f%8.3f%8.3f%8.3f%8.0f%6d%9.1f%9.1f%8.2f %7.2f %6.2f %6.2f %6.2f\n"%(count2,psi,theta,phi,sx,sy,mag,micro,df1,df2,astig,occ,log,score,change))

		#out.write("%7d%8.3f%8.3f%8.3f%8.3f%8.3f%9.0f%6d%9.1f%9.1f%8.2f%7.2f %6.2f %6.2f %6.2f\n" %(count2,psi,theta,phi,sx,sy,mag,micro,df1,df2,astig,occ,log,score,change))	


if __name__ == "__main__":
     params=setupParserOptions()
     main(params)

