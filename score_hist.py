#!/usr/bin/env python

import os,sys,re
import subprocess
import optparse
import math
import numpy

def setupParserOptions():
	parser = optparse.OptionParser()
	parser.set_description("Takes a FREALIGN parameter file, and makes a file of binned phase residuals for plotting a histogram. Also outputs some useful statistics.")	
	parser.set_usage("%prog -p <parfile> --binsize <binsize>")
	parser.add_option("-p",dest="parfile",type="string",metavar="FILE",
		help="FREALIGN parameter file")
	parser.add_option("--binsize",dest="binsize",type="float",metavar="FLOAT",default="0.25",
		help="size of bins, default is 0.25")	
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
#==========================================================================
def checkConflicts(params):
	outputf = os.path.splitext(params['parfile'])[0]+"_binned.par"
	if os.path.exists(outputf):
		print "Error: %s already exists, remove it to continue\n"%outputf
		sys.exit()

#===========================================================================
def binParams(params):

	outputf = os.path.splitext(params['parfile'])[0]+"_binned.par"
	cmd="grep -v C %s > tempParFile"%params['parfile']
	subprocess.Popen(cmd,shell=True).wait()

	inputf = "tempParFile"
			
	phasereslist = []

	f=open(inputf,'r')

	for line in f:
			
		l = line.split()

		phaseres = float(l[11])		
		phasereslist.append(phaseres)

	f.close()

	binsize = params['binsize']	

	minbin = int((min(phasereslist))-(2*binsize))
	maxbin = int(round(max(phasereslist))+(2*binsize))

	numbins = int((float(maxbin-minbin)/binsize)+4)

	bins = []
	counts = []	
	bincounter = 0
	
	for i in range(0,numbins):
		bincounter=bincounter+binsize
		currentbin=float(minbin)+bincounter-binsize
		bins.append(currentbin)
		counts.append(0)

	for p in range (0,len(phasereslist)):
		phaseres = phasereslist[p]		
		for b in range (0,len(bins)):
			addme=0
			currentbin=bins[b]
			if currentbin <= phaseres < (currentbin + binsize):
				addme = addme + 1
			counts[b]=counts[b] + addme

	outputf = os.path.splitext(params['parfile'])[0]+"_binned.par"
 	out=open(outputf,'w')

	for bin in range (0,len(bins)):
		thisline="%10.2f%10i\n"%(bins[bin],counts[bin])
		out.write(thisline)
	out.close()

	print"Stats:" 
	print"Mean = %5.2f, Median = %5.2f, Stdev = %4.2f, Min = %5.2f, Max = %5.2f"%(numpy.mean(phasereslist),numpy.median(phasereslist),numpy.std(phasereslist),float(min(phasereslist)),float(max(phasereslist)))

	rmcmd = "rm -f tempParFile"
	subprocess.Popen(rmcmd,shell=True).wait()	
#================================================
if __name__ == "__main__":
	params=setupParserOptions()
	binParams(params)





