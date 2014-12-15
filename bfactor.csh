#!/bin/csh

/programs/x/bfactor/1.04/bin/bfactor.exe << EOF
M
run4_local_refine_ct_ct24_data_3D.mrc
run4_local_refine_ct_ct24_data_3D_60_filt6.mrc
1.77		!Pixel size
15.0,8.0	!Resolution range to fut B-factor (low, high)
-60.0		!B-factor to be applied
2		!Low-pass filter option (1=Gaussian, 2=Cosine edge)
6		!Filter radius
3		!Width of cosine edge (if cosine edge used)
EOF
