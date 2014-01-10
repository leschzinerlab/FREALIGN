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
	parser.set_usage("%prog -c <ctf> --mag=<float>")
	parser.add_option("-c",dest="ctf",type="string",metavar="FILE",
		help="per-particle CTF information file from APPION")
	parser.add_option("--mag",dest="mag",type="float", metavar="FLOAT",
		help="actual magnification of images")
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


def Eman2Freali(az,alt,phi):

    t1 = Transform({"type":"eman","az":az,"alt":alt,"phi":phi,"mirror":False})

    #t_conv = Transform({"type":"eman","alt":31.717474411458415,"az":90,"phi":-90,"mirror":False})

    #t2 = t1*t_conv.inverse()

    d = t1.get_params("eman")

    psi = d["phi"]+90

    if psi >360:

        psi = psi-360

    theta= d["alt"]

    phi = d["az"]-90

    return psi,theta,phi

def main(params):
		ctf = params['ctf']			
		mag = params['mag']
		debug = params['debug']

		f=open(ctf,'r')
		out = open("%s_frealign"%(ctf[:-4]),'w')
		count=1
		count2=1
			
		print "\n"
		print "Calculating euler angle conversion..."
		print "\n"

		mag = str(mag)
		mag = mag[:-1]				
		for line in f:
					
			l = line.split()
	 	
			parmPSI = 0
			parmTHETA = 0
			parmPHI = 0
			sx = 0
			sy = 0
			model = 0
			psi,theta,phi = (parmPSI,parmTHETA,parmPHI)	
			
			if debug is True:

				print line

			c = line.split()

			micro = 1
			df1 = float(c[0])
			df2 = float(c[1])
			astig = float(c[2])					

			out.write("%7d%8.3f%8.3f%8.3f%8.3f%8.3f  %s%6d%9.1f%9.1f%8.2f%7.2f%6.2f\n" %(count2,psi,theta,phi,sx,sy,mag,micro,df1,df2,astig,0,0))
			count2 = count2 + 1

		count = count + 1

		f.close()
		out.close()
		


if __name__ == "__main__":
     params=setupParserOptions()
     main(params)
   
