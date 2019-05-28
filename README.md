# NASTRAN Composite Processing Tool
Strength Ratio and Element Ply Stress data extractor and processor for NASTRAN F06 

This is a script tool that was developed to postprocess results obtained 
from NASTRAN calculation for composite elements. When doing structural analysis with composite materiales, PCOMP card in NASTRAN, it is possible to specify an output for Ply Strength Ratio (with PARAM SRCOMPS YES) and individual ply stress on each element according to the material orientation (PARAM NOCOMPS 1). The output file .f06 must contain Strength Ratio and Ply Element Stresses for this tool to work. 

When the program starts, it will read the .f06 file and output 2 .csv results file for all Strength Ratio and Ply Element Stresses that it has found in the input file. After that it can also postprocess the .csv files using the pandas module to obtain results. The user can specify certain elements that he wants results for, also calculate margins of saftey for ply strength ratio or ply shear stress. 

Things to update globally:
- ~Create function to read elements from Patran format to list in python~
- ~Create GUI~ 
- Accept text from user with elements structured on groups
- Calculate MoS for Strength Ratio and Element Stress in program
- Output values in excel and minimum MOS global in GUI window
- Output values in word tables 

In Work:
- Add elements and groups in table view and also save them in variables for future uses
	- ~group and elements~
	- ~material facing~
	- ~material core~
	- resize column width to view the whole table
- Update check boxes for processing True/False
- ~Add headers to the view tables ~
- Add SQLITE database for better performance and to store all data


