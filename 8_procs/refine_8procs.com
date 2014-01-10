#!/bin/csh -f
#
#   Control script to submit multiple jobs on a cluster using
#   the Sun Grid Engine. Each job processes N particles. N is
#   specified in the 'mparameters' file as 'increment'.
#

cp mparameters mparameters_run

set start = `grep start_process mparameters_run | awk '{print $2}'`
set end   = `grep end_process mparameters_run | awk '{print $2}'`
set first = `grep first_particle mparameters_run | awk '{print $2}'`
set last  = `grep last_particle mparameters_run | awk '{print $2}'`
set incr  = `grep increment mparameters_run | awk '{print $2}'`
set data_input = `grep data_input mparameters_run | awk '{print $2}'`
set mode = `grep MODE mparameters_run | awk '{print $2}'`
set working_directory = `pwd`
set SCRATCH = ../scratch

mainloop:

cp mparameters mparameters_run
\rm ${data_input}_$start.par >& /dev/null

@ prev = $start - 1

set firstn = $first
@ lastn = $first + $incr - 1

if ($mode == 0) goto reconstruct

while ( $lastn <= $last )

  ${working_directory}/mrefine_n_v9.com $firstn $lastn $start &

  if ( $lastn == $last ) then
    goto alignment_done
  endif
  @ firstn = $firstn + $incr
  @ lastn = $lastn + $incr
  if ( $firstn >= $last ) set firstn = $last
  if ( $lastn >= $last ) set lastn = $last
end

alignment_done:

  set firstn = $first
  @ lastn = $first + $incr - 1

checkdone:

    sleep 5
    while ( $firstn <= $last )
	
      grep --binary-files=text "overall score" $SCRATCH/${data_input}_${start}.par_${firstn}_$lastn >& /dev/null
      if ($status) goto checkdone

      echo "Particles $firstn to $lastn, finished....  "`date`
      if ($firstn == $first ) head -60 $SCRATCH/${data_input}_${start}.par_${firstn}_${lastn} | grep --binary-files=text C >> ${working_directory}/${data_input}_${start}.par

      grep -v C --binary-files=text $SCRATCH/${data_input}_${start}.par_${firstn}_${lastn} >> ${working_directory}/${data_input}_${start}.par
      \rm $SCRATCH/${data_input}_${start}.par_${firstn}_${lastn} >& /dev/null

      @ firstn = $firstn + $incr
      @ lastn = $lastn + $incr
      if ( $lastn >= $last ) set lastn = $last
    end

reconstruct:
echo "Calculating 3D structure...."

  \rm $SCRATCH/${data_input}_mult_reconstruct.log
  \rm $SCRATCH/${data_input}.shft_* 
  \rm $SCRATCH/${data_input}_mrefine_n.log_*
  ${working_directory}/mult_reconstruct_v9.com $first $last $start

checkdoner:

  sleep 2

  grep --binary-files=text "mreconstruct.com finished" $SCRATCH/${data_input}_mult_reconstruct.log >& /dev/null
  if ($status) goto checkdoner

  ls ${working_directory}/${data_input}_${start}.spi >& /dev/null
  if ($status) goto checkdoner

  sleep 1

  cat $SCRATCH/${data_input}_${start}.res >> ${working_directory}/${data_input}_${start}.par
  \rm $SCRATCH/${data_input}_${start}.res
  \rm $SCRATCH/${data_input}_${start}.par


sleep 10

echo "Cycle ${start} finished.... "`date`

if ($start < $end ) then
  @ start = $start + 1
  goto mainloop
endif
date
