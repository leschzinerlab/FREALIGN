#!/bin/csh -f
#
#   Control script to submit multiple jobs on a workingstatio
#. Each job processes N particles. N is
#   specified in the 'mparameters' file as 'increment'.
#


cp mparameters mparameters_run

set start = `grep start_process mparameters_run | awk '{print $2}'`
set end   = `grep end_process mparameters_run | awk '{print $2}'`
set first = `grep first_particle mparameters_run | awk '{print $2}'`
set last  = `grep last_particle mparameters_run | awk '{print $2}'`
set incr  = `grep increment mparameters_run | awk '{print $2}'`
set data_input = `grep data_input mparameters_run | awk '{print $2}'`
set nclass  = `grep nclasses mparameters_run | awk '{print $2}'`
set mode = `grep MODE mparameters_run | awk '{print $2}'`
set working_directory = `pwd`
set SCRATCH = ../scratch

mainloop:

cp mparameters mparameters_run

set nc = 1
while ( $nc <= $nclass )
  \rm ${data_input}_${start}_r${nc}.par >& /dev/null
  @ nc = $nc + 1
end

# submission loop

@ prev = $start - 1

set firstn = $first
@ lastn = $first + $incr - 1

if ($mode == 0) goto reconstruct

while ( $lastn <= $last )
  echo "Submitted particles from" $firstn to $lastn on `date`
  
  set nc = 1 
  while ( $nc <= $nclass )
    ${working_directory}/mrefine_multiRef_n.csh $firstn $lastn $start $nc &
     @ nc = $nc + 1 
  end

  if ( $lastn == $last ) then
    goto alignment_done
  endif
  @ firstn = $firstn + $incr
  @ lastn = $lastn + $incr
  if ( $firstn >= $last ) set firstn = $last
  if ( $lastn >= $last ) set lastn = $last
end

alignment_done:

set nc = 1
while ( $nc <= $nclass )
  set firstn = $first
  @ lastn = $first + $incr - 1

checkdone:

    sleep 5
    while ( $firstn <= $last )
	
      grep --binary-files=text "overall score" $SCRATCH/${data_input}_${start}_r${nc}.par_${firstn}_$lastn >& /dev/null
      if ($status) goto checkdone

      echo "Particles $firstn to $lastn, finished....  "`date`
      if ($firstn == $first ) head -60 $SCRATCH/${data_input}_${start}_r${nc}.par_${firstn}_${lastn} | grep --binary-files=text C >> ${working_directory}/${data_input}_${start}_r${nc}.par

      grep -v C --binary-files=text $SCRATCH/${data_input}_${start}_r${nc}.par_${firstn}_${lastn} >> ${working_directory}/${data_input}_${start}_r${nc}.par
      \rm $SCRATCH/${data_input}_${start}_r${nc}.par_${firstn}_${lastn} >& /dev/null

      @ firstn = $firstn + $incr
      @ lastn = $lastn + $incr
      if ( $lastn >= $last ) set lastn = $last
    end

collect_done:
  @ nc = $nc + 1
end

time /opt/qb3/frealign-9.02-bs/bin/calc_occ.exe << eof >& calc_occ.log
$nclass
${data_input}_${start}_r1.par
${data_input}_${start}_r2.par
${data_input}_${start}_r1.par
${data_input}_${start}_r2.par
eof


reconstruct:
echo "Calculating 3D structure...."

set nc = 1
while ( $nc <= $nclass )

  \rm $SCRATCH/${data_input}_mult_reconstruct_r${nc}.log
  \rm $SCRATCH/${data_input}_r${nc}.shft_* 
  \rm $SCRATCH/${data_input}_mrefine_n.log_*
  ${working_directory}/mult_reconstruct_multiRef.csh  $first $last $start $nc &
  
  @ nc = $nc + 1

end

set nc = 1 
while ( $nc <= $nclass )

checkdoner:

  sleep 2

  grep --binary-files=text "mreconstruct.com finished" $SCRATCH/${data_input}_mult_reconstruct_r${nc}.log >& /dev/null
  if ($status) goto checkdoner

  ls ${working_directory}/${data_input}_${start}_r${nc}.spi >& /dev/null
  if ($status) goto checkdoner

  sleep 1

  cat $SCRATCH/${data_input}_${start}_r${nc}.res >> ${working_directory}/${data_input}_${start}_r${nc}.par
  \rm $SCRATCH/${data_input}_${start}_r${nc}.res
  \rm $SCRATCH/${data_input}_${start}_r${nc}.par

  @ nc = $nc + 1

end

sleep 10

echo "Cycle ${start} finished.... "`date`


if ($start < $end ) then
  @ start = $start + 1
  goto mainloop
endif
date
