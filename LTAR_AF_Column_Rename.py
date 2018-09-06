# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 11:08:41 2018

@author: Eric
"""

# -*- coding: utf-8 -*-
"""
@author: Eric S. Russell
Laboratory for Atmospheric Research
Dept. of Civil and Environmental Engineering
Washington State University
eric.s.russell@wsu.edu
"""

import pandas as pd
import glob
import os
import numpy as np
# Change this path to the directory where the LTAR_Flux_QC.py file is located
os.chdir('C:\\*\\*\\*\\PyScripts')       
import LTAR_Flux_QC as LLT

files = glob.glob('C:\\*\\eddypro_LTAR_CookEast_CY2017.csv') #Directory or file name with file names here
AF = pd.read_csv('C:\\*\\AF_EP_EF_Column_Renames.csv',header = 0) # File path for where the column names sit
EP = True     # True if data being used is from EddyPro; must be false if EF is true
EF = False    # True if data being used is from EasyFlux; must be false if EP is true
Join = False  # True if there are other columns to be readin from a separate file; false if not
Format = '*' # Which format the column headers are in; 'Epro' or 'Eflux' are only accepted; must be in single quotes
#***************************                                                   
data= []; data= pd.DataFrame(data) # initialize a blank dataframe
if EP == True:
    for k in range (0,len(files)):
#Read in data and concat to one dataframe; no processing until data all read in - data formatted from EddyPro FullOutput
        df = pd.read_csv(files[k],header= 1,skiprows=[2],sep=',',low_memory=False)
        data= pd.concat([data,df])
    data.index = data['date']+' '+data['time'] # Eddypro outputs both time and date as separate columns
    data =data.drop(['filename'],1) # not needed string-based column; gets in the way of converting to floating point
elif EF == True:
    for k in range (0,len(files)):
    #Read in data and concat to one dataframe; no processing until data all read in; formatted for EasyFlux header style
        df = pd.read_csv(files[k],index_col = 'TIMESTAMP',header= 1,skiprows=[2,3],low_memory=False)
        data = pd.concat([data,df])
else: print('EF or EP needs to be true; script will Error')

if EP or EF:
    data.index=pd.to_datetime(data.index) # Convert to a time-based index
    if Join:
        filenames = glob.glob('C:\\*\\*.dat') #Directory or file name with file names that need to added to the main list put here
        Final = LLT.Fast_Read(filenames,'30min', '*') # Read-in data that contains extra columns not in the EddyPro output; specify 'EF' or 'EP' for EasyFlux or EddyPro
        Join_Cols = AF['Extra_Cols'].dropna() # Drop blank columns since this list is shorter than the other lists and good housekeeping
        for k in range (0,len(Join_Cols)): 
            data=data.join(Final[Join_Cols[k]]) # Loop to join the extra columns as defined above
    if EP:
#EddyPro outputs the variance which is the square of the standard deviation so need to convert back to standard deviation
        data['u_var'] = data['u_var'].astype(float)**0.5
        data['v_var'] = data['v_var'].astype(float)**0.5
        data['w_var'] = data['w_var'].astype(float)**0.5
        data['ts_var'] = data['ts_var'].astype(float)**0.5
    AM = data; cls = AM.columns # Keeping data as an unchanged variable from this point forward in case want to do more with it; can be changed

# Using data that came from EddyPro so selected the Epro column to check column names against.
    s = cls.isin(AF[Format])

# Drop columns not in the AmeriFlux data list
    AF_Out = AM.drop(AM[cls[~s]],axis = 1)
    cls = AF_Out.columns  #Grab column headers from AF_Out after dropping unneeded columns
    
# Change column header names and keep only columns that match
    for k in range (2,len(AF)):
        if AF[Format][k] in cls:
            qn = AF[Format][k] == cls
            AF_Out = AF_Out.rename(columns={cls[qn][0]:AF['AmeriFlux'][k]})
            print('Converting ',AF[Format][k],' to ',AF['AmeriFlux'][k])

#Shift time to match AmeriFlux format; can change this depending on how averaging time is assigned
    AF_Out['END'] = AF_Out.index.shift(1, '30T')
    AF_Out['START'] = AF_Out.index.shift(0, '30T')

# Format columns into a same order as in the input *.csv file because housekeeping is always good
    acl = AF['AmeriFlux']
    tt = acl[acl.isin(AF_Out.columns)]
    AF_Out=AF_Out[tt]

# Grab units for columns that are in the output final
    units = AF['Units'][acl.isin(AF_Out.columns)]

# Ameriflux uses -9999 to represent missing data so convert NaN to -9999
    AF_Out = AF_Out.fillna(-9999)

# Adjust header to have both units and column names; more housekeeping
    arrays = [np.array(tt),np.array(units)]                                 
    AF_Out.columns = arrays
#%%
# Change output directory to whatever it needs to be
    AF_Out.to_csv('*', index = False)
else: print('Select either EF or EP as true')