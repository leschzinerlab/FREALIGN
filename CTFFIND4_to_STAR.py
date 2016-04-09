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
        parser.set_usage("%prog -i <ctf from appion> --path=<path to micros> --appion=<appion base name to remove> --cs=<cs> --kev=<kev> ")
        parser.add_option("-i",dest="ctf",type="string",metavar="FILE",
                help="CTFFIND4 output file 'ctf_param.txt'")
	parser.add_option("--path",dest="folder",type="string",metavar="STRING",
                help="Relative path to micrographs that Relion will use (e.g. 'Micrographs')")
	parser.add_option("--mag",dest="mag",type="int",metavar="INT",
                help="Nominal magnification of microscope")
	parser.add_option("--detectorpix",dest="detector",type="float",metavar="float",
                help="Physical detector pixel size. Note: Detector pix / mag = apix")
	parser.add_option("--reslim",dest="reslim",type="float",metavar="float",
                help="Resolution fit limit for micrograph")
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
def checkConflicts(params):
        if not os.path.exists(params['ctf']):
                print "\nError: CTF file '%s' does not exist\n" % params['CTF']
                sys.exit()

        if os.path.exists('all_micrographs_ctf.star'):
                print "\nError: all_micrograhps_ctf.star already exists, exiting.\n"
                sys.exit()

#===============================
def convertToRelionCTF(params):

	relionOut = writeRelionHeader()

	out = open('all_micrographs_ctf.star','w')

	ctf = open(params['ctf'],'r')

	for line in ctf:
		l = line.split()
		
		if l[-1] == 'ResLimit':
			'''2.7,200,1.35,0.07,#cs,ht,apix,ampcontrast#Micro	DF1	DF2	Astig	ResLimit'''
			ampcontrast=float(line.split(',')[3])
			cs=float(line.split(',')[0])
			kev=float(line.split(',')[1])
			continue
		if float(l[-1]) > params['reslim']:
			if params['debug'] is True:
				print 'skipping micrograph %s bc res limit is %f' %(l[0],float(l[-1]))
			continue
		micro=l[0]	
		#Prepare micrograph name
		microname = '%s/' %(params['folder'])+micro

		if params['debug'] is True:
			print microname
	
		#Get defocus information
		df1 = float(l[1])
		df2 = float(l[2])
		astig = float(l[3])
		crosscorr = float(l[4])
		
		relionOut+='%s  %.6f  %.6f  %.6f  %.6f  %.6f  %.6f  %.6g  %.6f  %.6f\n' %(microname,df1,df2,astig,kev,cs,ampcontrast,params['mag'],params['detector'],crosscorr)

		ctflog = '%s/' %(params['folder'])+micro[:-4]+'_ctffind3.log'

		#Check if new ctf log file exists
                if os.path.exists(ctflog):
                        print '%s already exists. Exiting.' %(ctflog)
                        sys.exit()

                #Open new ctf log file
                ctf='\n'
                ctf+=' CTF DETERMINATION, V3.5 (9-Mar-2013)\n'
                ctf+=' Distributed under the GNU General Public License (GPL)\n'
                ctf+='\n'
                ctf+=' Parallel processing: NCPUS =         4\n'
                ctf+='\n'
                ctf+=' Input image file name\n'
                ctf+='%s\n' %(microname)
                ctf+='\n'
                ctf+='\n'
                ctf+=' Output diagnostic file name\n'
                ctf+='%s.ctf\n'%(microname[:-4])
                ctf+='\n'
                ctf+='\n'
                ctf+=' CS[mm], HT[kV], AmpCnst, XMAG, DStep[um]\n'
                ctf+='  %.1f    %.1f    %.2f   %.1f    %.3f\n' %(cs,kev,ampcontrast,params['mag'],params['detector'])
                ctf+='\n'
                ctf+='\n'
                ctf+='      DFMID1      DFMID2      ANGAST          CC\n'
                ctf+='\n'
                ctf+='    %.2f\t%.2f\t%.2f\t%.5f\tFinal Values\n' %(df1,df2,astig,crosscorr)

                outctf = open(ctflog,'w')
                outctf.write(ctf)
                outctf.close()

 
	out.write(relionOut)

#================================
def writeRelionHeader():

	relion='\n'
	relion+='data_\n'
	relion+='\n'
	relion+='loop_\n'
	relion+='_rlnMicrographName #1\n'
	relion+='_rlnDefocusU #2\n'
	relion+='_rlnDefocusV #3\n'
	relion+='_rlnDefocusAngle #4\n'
	relion+='_rlnVoltage #5\n'
	relion+='_rlnSphericalAberration #6\n' 
	relion+='_rlnAmplitudeContrast #7\n'
	relion+='_rlnMagnification #8\n'
	relion+='_rlnDetectorPixelSize #9\n'
	relion+='_rlnCtfFigureOfMerit #10\n' 

	return relion

#==============================
if __name__ == "__main__":

        params=setupParserOptions()
        checkConflicts(params)
	convertToRelionCTF(params)
