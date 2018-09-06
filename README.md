# CAF_EC_Column_Rename
This holds the code for a Python (V3) script that will rename column headers from either EddyPro or EasyFlux into the Ameriflux format as part of the Phenology Initiative for the Long-Term Agroecosystem Research network funded by the USDA ARS.

The script requires three files to make work:
1) LTAR_AF_Column_Rename.py: This is the main script for the column renaming. Anything signified with an asterik (*) needs to be updated or changed to match with the usage on your system; this is mainly file and directory paths. Anything without an asterik can be chagned if needed but may impact the usage of the script.

2) LTAR_Flux_QC.py: Library that contains functions called in the main script. Changes in this script should be minimally if non-existant. There are more functions in this libary than used in the main script.

3) AF_EP_EF_Column_Renames.csv: Contains the different column headers for AmeriFlux, EddyPro, and EasyFlux columns. Also contains an "Extras" columns if columns from outside the main dataset need to be joined into the script. The full list and description of AmeriFlux data are in the Excel file in the repository or at http://ameriflux.lbl.gov/data/aboutdata/data-variables/#base

Questions or comments, contact: 

      Eric Russell: eric.s.russell@wsu.edu
      Bryan Carlson: bryan.carlson@ars.usda.gov
