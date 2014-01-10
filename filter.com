#!/bin/csh -fx
#

/opt/qb3/frealign-9.02/bin/bfactor.exe << eof
S
../REF1/iid_iia_scp_8.spi
-4000		!B-factor
2		!Low-pass filter option (1=Gaussian, 2=Cosine edge)
32		!Filter radius
5.0		!Width of cosine edge (if cosine edge used)
6		!Pixel size
fil32A_B4000_iid_iia_scp_8.spi
eof
#
