#!/bin/csh -f

#This is the control script for submitting individual frealign reconstructions
#to a cluster.

set realVol = vol.spi			#Volume 'placeholder for frealign

set name = iid_iia_scp_5_r 		#Basename for parameter file & volume file output

foreach file (*.par)
	
  set vol=`echo $file | sed -e 's/.par//'`	#Remove .par extension of parameter file
  set newVol = ${vol}.spi			#Add .spi extension to create filename (e.g. iid_iia_scp_5_r1.spi)

  set num=`echo $file | sed 's/'${name}'//' | sed -e 's/.par//'`	#Extract model number from parameter filename (e.g. 5)

  cp $realVol $newVol							#Copy placeholding volume into new volume file name

  qsub submit_FRE.csh $num						#Submit to cluster

  waiting:

   sleep 1
   qstat | grep michael | grep "  qw  " >& /dev/null			#Waiting feature to ensure that you don't totally ovewhelm queuing system
   if (! $status) goto waiting

end

