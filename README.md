# NASTRAN Composite Processing Tool
Strength Ratio and Element Ply Stress data extractor and processor for NASTRAN F06 

This is a script tool that was developed to postprocess results obtained 
from NASTRAN calculation for composite elements. When doing structural analysis with composite materiales, PCOMP card in NASTRAN, it is possible to specify an output for Ply Strength Ratio (with PARAM SRCOMPS YES) and individual ply stress on each element according to the material orientation (PARAM NOCOMPS 1). The output file .f06 must contain Strength Ratio and Ply Element Stresses for this tool to work. 




