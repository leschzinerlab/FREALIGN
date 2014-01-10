#!/bin/csh  

#unlimit

limit coredumpsize 0
set working_directory = `pwd`
#
set start = $3
@ prev = $start - 1
set data_input  = `grep data_input mparameters_run | awk '{print $2}'`
set raw_images	= `grep raw_images1 mparameters_run | awk '{print $2}'`
set radius      = `grep radius mparameters_run | awk '{print $2}'`
set thresh	= `grep thresh_reconst mparameters_run | awk '{print $2}'`
set target      = `grep thresh_refine mparameters_run | awk '{print $2}'`
set pbc         = `grep PBC mparameters_run | awk '{print $2}'`
set boff        = `grep BOFF mparameters_run | awk '{print $2}'`
set dang        = `grep DANG mparameters_run | awk '{print $2}'`
set itmax       = `grep ITMAX mparameters_run | awk '{print $2}'`
set mode        = `grep MODE mparameters_run | awk '{print $2}'`
set rrec        = `grep res_reconstruction mparameters_run | awk '{print $2}'`
set rref        = `grep res_refinement mparameters_run | awk '{print $2}'`
set rbf		= `grep RBFACT mparameters_run | awk '{print $2}'`
set pix		= `grep pixel_size mparameters_run | awk '{print $2}'`
set kV		= `grep kV1 mparameters_run | awk '{print $2}'`
set cs          = `grep CS mparameters_run | awk '{print $2}'`
set AmpC        = `grep WGH mparameters_run | awk '{print $2}'`
set mask	= `grep XSTD mparameters_run | awk '{print $2}'`
set dstep	= `grep dstep mparameters_run | awk '{print $2}'`
#
set SCRATCH = ${working_directory}/../scratch

cp ${data_input}_${prev}_r${4}.spi $SCRATCH/${data_input}_${start}_r${4}.spi

if ($mode == 0) then
   
  set parm = ${data_input}_${prev}_r${4}.par

else

  set parm = ${data_input}_${start}_r${4}.par

endif
#
cd $SCRATCH
#
\rm ${data_input}_${start}_r${4}.res
#
time /opt/qb3/frealign-9.02-bs/bin/frealign_v9_mp.exe << eot >& ${data_input}_mult_reconstruct_r${4}.log
S,0,F,F,F,F,0,F,F,F,0,F,4				!CFORM,IFLAG,FMAG,FDEF,FASTIG,FPART,IEWALD,FBEAUT,FCREF,FMATCH,IFSC,FSTAT,IBLOW
${radius},0.0,${pix},${AmpC},${mask},${pbc},0.0,10.,1,10	!RO,RI,PSIZE,WGH,XSTD,PBC,BOFF,DANG,ITMAX,IPMAX
0 0 0 0 0						!MASK
${1},${2}						!IFIRST,ILAST 
0							!ASYM symmetry card (I=icosahedral)
1.,${dstep},${target},${thresh},${cs},${kV},0.0,0.0		!RELMAG,DSTEP,TARGET,THRESH,CS,AKV,TX,TY
${rrec}, 200.0, ${rref}, 100.0, ${rbf}			!RREC,RMAX1,RMAX2,DFSTD,RBFACT
${working_directory}/../${raw_images}.spi
/dev/null
${working_directory}/$parm
${data_input}_${start}_r${4}.res
${data_input}_${start}_dummy_r${4}.shft
0., 0., 0., 0., 0., 0., 0., 0.				! terminator with RELMAG=0.0
${data_input}_${start}_r${4}.spi
${data_input}_${start}_weights_r${4}
${data_input}_${start}_map1_r${4}.spi
${data_input}_${start}_map2_r${4}.spi
${data_input}_${start}_r${4}_phasediffs
${data_input}_${start}_r${4}_pointspread
eot
#
mv ${data_input}_${start}_r${4}.spi ${working_directory}/.
\rm ${data_input}_${start}_r${4}_weights
\rm ${data_input}_${start}_dummy_r${4}.shft
\rm ${data_input}_${start}_map1_r${4}.spi
\rm ${data_input}_${start}_map2_r${4}.spi
\rm ${data_input}_${start}_r${4}_phasediffs
\rm ${data_input}_${start}_r${4}_pointspread
#
echo 'mreconstruct.com finished' >> ${data_input}_mult_reconstruct_r${4}.log
date
#
