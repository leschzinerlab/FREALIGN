#!/bin/csh -fx

# Set parallel environment; set number of processors
#$ -pe orte 1  

# Max walltime for this job (2 hrs)
##$ -l h_rt=02:00:00

# Merge the standard out and standard error to one file
##$ -j y

# Run job through csh shell
#$ -S /bin/csh

# use current working directory
#$ -cwd

# The following is for reporting only. It is not really needed
# to run the job. It will show up in your output file.
#

echo "Job starting `date`"
echo "Current working directory: $cwd"
echo "Got $NSLOTS processors."

# The job

#unlimit

limit coredumpsize 0
set working_directory = `pwd`
set SCRATCH = ../scratch

set start = $3

set radius      = `grep radius mparameters_run | awk '{print $2}'`
set target      = `grep thresh_refine mparameters_run | awk '{print $2}'`
set thresh      = `grep thresh_reconst mparameters_run | awk '{print $2}'`
set pbc         = `grep PBC mparameters_run | awk '{print $2}'`
set boff        = `grep BOFF mparameters_run | awk '{print $2}'`
set dang        = `grep DANG mparameters_run | awk '{print $2}'`
set itmax       = `grep ITMAX mparameters_run | awk '{print $2}'`
set mode        = `grep MODE mparameters_run | awk '{print $2}'`
set flip        = `grep FLIP mparameters_run | awk '{print $2}'`
set rrec        = `grep res_reconstruction mparameters_run | awk '{print $2}'`
set rref        = `grep res_refinement mparameters_run | awk '{print $2}'`
set rlowref     = `grep res_low_refinement mparameters_run | awk '{print $2}'`
set data_input  = `grep data_input mparameters_run | awk '{print $2}'`
set raw_images1 = `grep raw_images1 mparameters_run | awk '{print $2}'`
set pixel_s     = `grep pixel_size mparameters_run | awk '{print $2}'`
set dstep       = `grep dstep mparameters_run | awk '{print $2}'`
set w_gh        = `grep WGH mparameters_run | awk '{print $2}'`
set kV1         = `grep kV1 mparameters_run | awk '{print $2}'`
set cs          = `grep CS mparameters_run | awk '{print $2}'`
set xstd        = `grep XSTD mparameters_run | awk '{print $2}'`
set fmag        = `grep FMAG mparameters_run | awk '{print $2}'`
set fdef        = `grep FDEF mparameters_run | awk '{print $2}'`
set fastig      = `grep FASTIG mparameters_run | awk '{print $2}'`
set rbfact      = `grep RBFACT mparameters_run | awk '{print $2}'`
set iewald      = `grep IEWALD mparameters_run | awk '{print $2}'`

@ prev = $start - 1
cd $SCRATCH

cp ${working_directory}/${data_input}_${prev}_r${4}.par ${data_input}_${prev}_r${4}.par_$1_$2
cp ${working_directory}/${data_input}_${prev}_r${4}.spi ${data_input}_${start}_r${4}.spi_$1_$2
\rm ${data_input}_${start}_r${4}.par_${1}_${2} >& /dev/null

time /opt/qb3/frealign-9.02-bs/bin/frealign_v9.exe << eot >& ${data_input}_mult_refine_n_r${4}.log_${1}_${2}
S,${mode},${fmag},${fdef},${fastig},${flip},${iewald},T,F,F,F,0		!CFORM,IFLAG,FMAG,FDEF,FASTIG,FFLIP,IEWALD,FMATCH,FHIST,FBEAUT,FCREF,IFSC,FSTAT,IBLOW
${radius},0.,${pixel_s},${w_gh},${xstd},${pbc},${boff},${dang},${itmax},10	!RO,RI,PSIZE,WGH,XSTD,PBC,BOFF,DANG,ITMAX,IPMAX
1 1 1 1 1								!MASK
${1},${2},								!IFIRST,ILAST 
0
1.0, ${dstep}, ${target}, ${thresh}, ${cs}, ${kV1}, 0., 0.		!RELMAG,DSTEP,TARGET,THRESH,CS,AKV,TX,TY
${rrec},${rlowref},${rref},${rbfact},					!RREC,RMAX1,RMAX2,RBFACT
${working_directory}/../${raw_images1}.spi
${data_input}_match_r${4}.spi_${1}_${2}
${data_input}_${prev}_r${4}.par_$1_$2
${data_input}_${start}_r${4}.par_${1}_${2}
${data_input}_r${4}.shft_${1}_${2}
-100., -100., -100., -100., -100., -100.,-100.,-100.						!terminator with RELMAG=0.0
${data_input}_${start}_r${4}.spi_${1}_${2}
${data_input}_weights_${start}_r${4}_${1}_${2}
${data_input}_map1_r${4}_${1}_${2}
${data_input}_map2_r${4}_${1}_${2}
${data_input}_phasediffs_r${4}_${1}_${2}
${data_input}_pointspread_r${4}_${1}_${2}
eot
#
