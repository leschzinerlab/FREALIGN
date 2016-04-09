#!/usr/bin/env python

from pylab import *
from matplotlib.colors import LogNorm
import numpy as np
import matplotlib.pyplot as plt
import optparse
from sys import *
import os,sys,re
import linecache

#=========================
def setupParserOptions():
        parser = optparse.OptionParser()
        parser.set_usage("%prog --starfile=<relion_star_file>")
        parser.add_option("--input",dest="input",type="string",metavar="FILE",
                help="Output ctf file from estimateCTF_CTFFIND4.py ('ctf_param.txt')")
        parser.add_option("--binsize",dest="bin",type="int",metavar="INT",default=5,
                help="Optional: bin size for histogram of euler angles (Default=1 Angstrom)")
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

#==============================
def checkConflicts(params):

        if not os.path.exists(params['input']):
            print 'Error: File %s does not exist' %(params['input'])
            sys.exit()

#===============================
def getRelionColumnIndex(star,rlnvariable):

    counter=50
    i=1

    while i<=50:

        line=linecache.getline(star,i)

        if len(line)>0:
            if len(line.split())>1:
                if line.split()[0] == rlnvariable:
                    return line.split()[1][1:]

        i=i+1

#===============================
def plot_single(star,colnum,debug,binsize):

    #open star file
    f1=open(star,'r')

    #remove temporary file
    tmp='tmp_relion_star.star'
    if os.path.exists(tmp):
        os.remove(tmp)

    #open for writing into new tmp file without header
    o1=open(tmp,'w')

    for line in f1:
        if l.split()[-1] == 'ResLimit':
            continue
        o1.write(line)

    o1.close()
    f1.close()

    usecolumn=int(colnum-1)

    eulers=np.loadtxt(tmp,usecols=[usecolumn])

    #Get number of particles
    tot=len(open(tmp,'r').readlines())

    #Create bins:
    bins=np.arange(3,30,params['bin'])

    #Plot histogram
    plt.hist(eulers,bins=bins)
    plt.title("Micrograph resolution histogram")
    plt.xlabel("Resolution of CTFFIND4 confidence limit (Angstroms)")
    plt.ylabel("Number of micrographs")
    plt.show()

#==============================
if __name__ == "__main__":

        params=setupParserOptions()

        #Check that file exists & relion euler designation is real
        checkConflicts(params)

        #Get column number for euler designation
        plot_single(params['input'],6,params['debug'],params['bin'])

