#!/bin/csh
#
#   Control script to submit a single job on a single CPU.
#
cp mparameters mparameters_run

set start = `grep start_process mparameters_run | awk '{print $2}'`
set end   = `grep end_process mparameters_run | awk '{print $2}'`
set first = `grep first_particle mparameters_run | awk '{print $2}'`
set last  = `grep last_particle mparameters_run | awk '{print $2}'`
set incr  = `grep increment mparameters_run | awk '{print $2}'`
set data_input = `grep data_input mparameters_run | awk '{print $2}'`
set working_directory = `pwd`
set SCRATCH = ../scratch

mainloop:

cp mparameters mparameters_run
\rm ${data_input}_$start.par >& /dev/null

$working_directory/mrefine_n.com $first $last $start

checkdone:

  grep "overall score" $SCRATCH/${data_input}.par_${first}_$last >& /dev/null
  if ($status) then
	sleep 30
	goto checkdone
  endif

cp $SCRATCH/${data_input}.par_${first}_${last} ${working_directory}/${data_input}_${start}.par
cp $SCRATCH/${data_input}_${start}.spi_${first}_${last} ${working_directory}/${data_input}_${start}.spi
#
echo "Cycle ${start} finished....  "`date`

if ($start < $end ) then
  @ start = $start + 1
  goto mainloop
endif
date
