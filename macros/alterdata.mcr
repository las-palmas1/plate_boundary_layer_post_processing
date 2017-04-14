#!MC 1410
$!VarSet |MFBD| = 'C:\Program Files\Tecplot\Tecplot 360 EX 2016 R2'
$!READDATASET  'C:\Users\User\Documents\tasks\boundary_layer_on_plate\tecplot_data_files\average_grid_density_sp_al.plt'
$!ALTERDATA
  EQUATION = '{X/h} = {X}'
  IGNOREDIVIDEBYZERO = NO
  DATATYPE = SINGLE
$!ALTERDATA
  EQUATION = '{Y/h} = {Y}'
  IGNOREDIVIDEBYZERO = NO
  DATATYPE = SINGLE
$!ALTERDATA
  EQUATION = '{Z/h} = {Z}'
  IGNOREDIVIDEBYZERO = NO
  DATATYPE = SINGLE
$!SAVELAYOUT  'C:\Users\User\Documents\tasks\boundary_layer_on_plate\tecplot_data_files\average_grid_density_sp_al.lay'
  INCLUDEDATA = YES
  INCLUDEPREVIEW = NO
$!RemoveVar |MFBD|
$!Quit