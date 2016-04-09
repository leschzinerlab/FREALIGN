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


#=========================
def setupParserOptions():
        parser = optparse.OptionParser()
        parser.set_usage("%prog --input=<micros> --apix=<pixelSize> --cs=<cs>")
        parser.add_option("--input",dest="micros",type="string",metavar="FILE",
                help="Wild card containing absolute path to .mrc micrographs ('/path/micro/*.mrc')")
        parser.add_option("--apix",dest="apix",type="float", metavar="FLOAT",
                help="Pixel size of micrographs")
	parser.add_option("--cs",dest="cs",type="float", metavar="float",
                help="Cs of microscope (mm)")
        parser.add_option("--kev",dest="kev",type="int", metavar="INT",
                help="Accelerating voltage (keV)")
	parser.add_option("--ampContrast",dest="contrast",type="float", metavar="FLOAT",
                help="Amplitude contrast (0.07 - cryo; 0.15 - neg. stain)")
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
def checkConflicts(params):
        if not params['apix']:
                print "\nWarning: no pixel size specified\n"
		sys.exit()

	if os.path.exists('ctf_param.txt'):
		print "\nOutput file ctf_param.txt already exists. Continuing unfinished run...\n"

	currentPath = sys.argv[0][:-24]
	ctffind = '%s/ctffind4.exe'%(currentPath)
	if os.path.exists(ctffind):
		return ctffind
	if os.path.exists('/data/software/repo/ctffind4/4.0.16/ctffind.exe'):
		return '/data/software/repo/ctffind4/4.0.16/ctffind.exe'
	if os.path.exists('%s/ctffind4.exe'%(currentPath)):
		return '%s/ctffind4.exe'%(currentPath)
	print "\nError: ctffind4.exe was not found in /usr/bin or %s\n" %(ctffind)	

#==============================
def estimateCTF(params,ctffindPath):

	#Read in all micros

	microList = sorted(glob.glob('%s'%(params['micros'])))

	if not os.path.exists('ctf_param.txt'):
		outMicroList = open('ctf_param.txt','w')
		outMicroList.write('%s,%s,%s,%s,#cs,ht,apix,ampcontrast' %(str(params['cs']),str(params['kev']),str(params['apix']),str(params['contrast'])))
		outMicroList.write('#Micro\tDF1\tDF2\tAstig\tResLimit\n')

	if os.path.exists('ctf_param.txt'):
		outMicroList=open('ctf_param.txt','a')

	for micro in microList:

		checkflag=0
		if os.path.exists('ctf_param.txt'):
			readopen=open('ctf_param.txt','r')
			for line in readopen:
				if line.split()[0] == micro:
					print 'Micro %s already estimated, continuing...' %(micro)
					checkflag=1
			readopen.close()
	
		if checkflag == 0:

			df1,df2,astig,cc,reslim = ctffind(micro,params['apix'],params['cs'],params['kev'],params['contrast'],ctffindPath)	
		
			outMicroList.write('%s\t%s\t%s\t%s\t%s\t%s\n' %(micro,df1,df2,astig,cc,reslim))

			os.remove('%s_pow.mrc' %(micro[:-4]))
			os.remove('%s_pow.txt' %(micro[:-4]))
			os.remove('ctffindLog.log')
			os.remove('%s_pow_avrot.txt' %(micro[:-4]))
			os.remove('ctffindrun.com')
	outMicroList.close()

#==============================
def ctffind(micro,apix,cs,kev,contrast,ctffindPath):

	shell=subprocess.Popen("echo $SHELL", shell=True, stdout=subprocess.PIPE).stdout.read()
	shell=shell.split('/')[-1][:-1]

	ctf='#!/bin/%s -x\n' %(shell)
	ctf+='%s << eof\n' %(ctffindPath)
	ctf+='%s\n' %(micro)
	ctf+='%s_pow.mrc\n' %(micro[:-4])
	ctf+='%f\n' %(apix)
	ctf+='%f\n' %(float(kev))
	ctf+='%f\n' %(float(cs))
	ctf+='%f\n' %(float(contrast))
	ctf+='512\n'
	ctf+='50\n'	
	ctf+='5\n'
	ctf+='5000\n'
	ctf+='80000\n'
	ctf+='500\n'
	ctf+='100\n'
	ctf+='no\n'
	ctf+='eof\n'

	if os.path.exists('ctffindrun.com'):
		os.remove('ctffindrun.com')

	if os.path.exists('ctffindLog.log'):
		os.remove('ctffindLog.log')

	ctfFile = open('ctffindrun.com','w')
 	ctfFile.write(ctf)
	ctfFile.close()

	cmd = 'chmod +x ctffindrun.com'	
	subprocess.Popen(cmd,shell=True).wait()	

	cmd = './ctffindrun.com > ctffindLog.log'
	subprocess.Popen(cmd,shell=True).wait()  

	ctfline=linecache.getline('%s_pow.txt' %(micro[:-4]),6).split()
	return ctfline[1],ctfline[2],ctfline[3],ctfline[5],ctfline[6]

#==============================
if __name__ == "__main__":

        params=setupParserOptions()
        ctffindPath = checkConflicts(params)
	estimateCTF(params,ctffindPath)

