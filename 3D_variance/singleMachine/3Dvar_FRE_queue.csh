#!/bin/csh -f

#This is the control script for submitting individual frealign reconstructions
#to a cluster.

set realVol = iid_iia_scp_3.spi			#Volume 'placeholder for frealign
set base = input
set name = input_5_r 		#Basename for parameter file & volume file output

foreach file (*.par)
	
  set vol=`echo $file | sed -e 's/.par//'`	#Remove .par extension of parameter file
  set newVol = ${vol}.spi			#Add .spi extension to create filename (e.g. iid_iia_scp_5_r1.spi)

  set num=`echo $file | sed 's/'${name}'//' | sed -e 's/.par//'`	#Extract model number from parameter filename (e.g. 5)

  cp $realVol $newVol							#Copy placeholding volume into new volume file name

  mult_reconstruct.com 1 22992 5 $num					#Submit to cluster

  goto checkdoner

checkdoner:

  grep --binary-files=text "mreconstruct.com finished" scratch/${base}_mult_reconstruct_r${num}.log >& /dev/null
  if ($status) goto checkdoner

  cat scratch/${base}_${num}.res >> scratch/$file 

rm scratch/${base}_mult_reconstruct_r${num}.log

echo "Volume ${newVol} finished.... "`date`


end

