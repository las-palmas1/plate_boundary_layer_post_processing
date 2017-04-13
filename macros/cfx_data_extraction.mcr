#!MC 1410
$!VarSet |MFBD| = 'C:\Program Files\Tecplot\Tecplot 360 EX 2016 R2'
$!READDATASET  'data_files\cfx\very_high_density_k_eps_i1_outlet.plt'
$!EXTRACTFROMPOLYLINE
EXTRACTLINEPOINTSONLY = NO
EXTRACTTHROUGHVOLUME = YES
EXTRACTTOFILE = YES
FNAME = 'extracted_data\cfx\very_high_density_k_eps_i1_outlet_line_0.dat'
NUMPTS = 1500
RAWDATA
2
7.9 0.15 0
7.9 0.15 0.35
$!EXTRACTFROMPOLYLINE
EXTRACTLINEPOINTSONLY = NO
EXTRACTTHROUGHVOLUME = YES
EXTRACTTOFILE = YES
FNAME = 'extracted_data\cfx\very_high_density_k_eps_i1_outlet_line_1.dat'
NUMPTS = 3000
RAWDATA
2
7.9 0.15 0
7.9 0.15 0.003
$!EXTRACTFROMPOLYLINE
EXTRACTLINEPOINTSONLY = NO
EXTRACTTHROUGHVOLUME = YES
EXTRACTTOFILE = YES
FNAME = 'extracted_data\cfx\very_high_density_k_eps_i1_outlet_line_2.dat'
NUMPTS = 2000
RAWDATA
2
0 0.15 0
8 0.15 0
$!RemoveVar |MFBD|
$!Quit