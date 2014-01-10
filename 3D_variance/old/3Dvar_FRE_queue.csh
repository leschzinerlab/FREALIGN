#!/bin/csh -f

set realVol = vol.spi
set name = iid_iia_scp_5_r

foreach file (*.par)

set vol=`echo $file | sed -e 's/.par//'`
set newVol = ${vol}.spi

set num=`echo $file | sed 's/'${name}'//' | sed -e 's/.par//'`

echo $num
echo $file
echo $newVol

cp $realVol $newVol

qsub submit_FRE.csh $num


end

