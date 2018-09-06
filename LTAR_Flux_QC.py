# -*- coding: utf-8 -*-
"""
Created on Tue Aug 21 15:53:46 2018

@author: Eric S. Russell
Laboratory for Atmospheric Research
Dept. of Civil and Environmental Engineering
Washington State University
eric.s.russell@wsu.edu

Not all of these functions are used in the column rename script; these are potentially to be used with this processing 
depending on other's thoughts. This is a trial run of dealing with code across sites.
"""

import numpy as np
import pandas as pd

"""        
QA/QC processing for flux data:
    Inputs:
        data:  Full input data
        grade: Maximum QA/QC grade as assigned by the flux calculation code
        LE_B:  Two number array with the highest (LE_B[1]) and lowest (LE_B[0]) hard limit LE value
        H_B:   Same as LE_B but for H
        F_B:   Same as LE-B but for Fc
        cls:
        gg:
    Outputs:
        data:  Dataframe with the filtered data; does not track reason for removing data.
        
    Conditional for door_is_open_Hst since not all sites will/do have enclosure door sensors installed
"""    
# This function not implemented into the script; still thinking about how I want to format this and integrate so user doesn't have to do a lot to make work

def Grade_cs(data,info_file):
    grade, LE_B,H_B,F_B,gg,cls = ReadIn_Initial(info_file)
    pd.options.mode.chained_assignment = None  
    if (grade >9) | (grade<0):
        print('Grade number must be between 0-9.')
        return  # 'exit' function and return error 
    Good = None
    df = data
    if cls[1] in df.columns:
        HL = (df[cls[1]].astype(float) < LE_B[0]) | (df[cls[1]].astype(float)>LE_B[1]) | df[cls[1]].astype(float).isnull()
        Grade = (df[gg[1]].astype(float) <= grade) & (~HL)
        data[cls[1]][~Grade] = np.NaN
    if cls[0] in df.columns:
        HL = (df[cls[0]].astype(float) < H_B[0]) | (df[cls[0]].astype(float)> H_B[1]) | df[cls[0]].astype(float).isnull()
        Grade = (df[gg[0]].astype(float) <= grade) & (~HL)
        data[cls[0]][~Grade] = np.NaN
    if cls[2] in df.columns:
        HL = (df[cls[2]].astype(float) < F_B[0])|(df[cls[2]].astype(float) > F_B[1]) | df[cls[2]].astype(float).isnull()
        Grade = (df[gg[2]].astype(float) <= grade) & (~HL)
        data[cls[2]][~Grade] = np.NaN
        # Rain Mask
    if 'Precipitation_Tot' in df.columns:
        Precip = df['Precipitation_Tot'].astype(float) < 0.001
        precip = True
    else: precip = False     
    if 'CO2_samples_Tot' in df.columns:
        Samp_Good_IRGA = df['CO2_samples_Tot'].astype(float)>14400
        irga = True
    else: irga=False
    if 'sonic_samples_Tot' in df.columns:
        Samp_Good_Sonic = df['sonic_samples_Tot'].astype(float) > 14400
        sonic = True
    else: sonic=False
    if 'used_records' in df.columns: 
        Samp_Good_Sonic = df['used_records'].astype(float)>14400
        sonic = True
    else: sonic=False
    if 'door_is_open_Hst' in df.columns:
        Door_Closed = df['door_is_open_Hst'].astype(float) == 0
        pc = True
    else:
        pc = False
    if precip&irga&sonic&pc:
        Good = Door_Closed &Samp_Good_Sonic&Samp_Good_IRGA&Precip
    elif precip&irga&sonic&~pc:
        Good = Samp_Good_Sonic&Samp_Good_IRGA&Precip
    elif precip&~irga&~sonic&~pc:
        Good = Precip
    elif precip&~irga&sonic&~pc:
        Good = Samp_Good_Sonic&Precip
    elif ~precip&~irga&sonic&~pc:
        Good = Samp_Good_Sonic
    elif ~precip&irga&sonic&pc:
        Good = Samp_Good_Sonic&Samp_Good_IRGA
    if Good is not None:
        data[cls[2]][~Good] = np.NaN
        data[cls[1]][~Good] = np.NaN
        data[cls[0]][~Good] = np.NaN
    return data             


#Fills in the blanks spaces with NaN's so the time index is continuous
def indx_fill(df, time):   
    df.index = pd.to_datetime(df.index)
        # Sort index in case it came in out of order, a possibility depending on filenames and naming scheme
    df = df.sort_index()
        # Remove any duplicate times, can occur if files from mixed sources and have overlapping endpoints
    df = df[~df.index.duplicated(keep='first')]
        # Fill in missing times due to tower being down and pad dataframe to midnight of the first and last day
    idx = pd.date_range(df.index[0].floor('D'),df.index[len(df.index)-1].ceil('D'),freq = time)
    df = df.reindex(idx, fill_value=np.NaN)
    return df

# Used to format EddyPro data by combining the date and time into a common index and dropping the filename column
def format_ep(df):
    df.index = df['date']+' '+df['time']
    df = df.drop(['filename'],1)
    df.index = pd.to_datetime(df.index)
    return df

# This function not used in main script; potential to be used with QC function
def ReadIn_Initial(info):
    # Values pulled in from a separate *.csv file because easier and flexible
    grade = int(info['Val_L']['grade'])
    LE_B = [float(info['Val_L']['LE_B']),float(info['Val_U']['LE_B'])]
    H_B = [float(info['Val_L']['H_B']),float(info['Val_U']['H_B'])]
    F_B = [float(info['Val_L']['F_B']),float(info['Val_U']['F_B'])]
    gg = [(info['Val_L']['gg']),(info['Val_U']['gg']),(info['Val_3']['gg'])]
    cls = [(info['Val_L']['cls']),(info['Val_U']['cls']),(info['Val_3']['cls']), (info['Val_4']['cls'])]
    return grade, LE_B,H_B,F_B,gg,cls

# Reads in a directory of files based on the format for either EddyPro or EasyFlux
def Fast_Read(filenames, time, form):
    if len(filenames) == 0:
        print('No Files in directory, check the path name.')
        return  # 'exit' function and return error
    else:
        #Initialize dataframe used within function
        Final = [];Final = pd.DataFrame(Final)
        if form == 'EF':
            for k in range (0,len(filenames)):
                df = pd.read_csv(filenames[k],index_col = 'TIMESTAMP',header= 1,skiprows=[2,3],low_memory=False)
                Final = pd.concat([Final,df])
        elif form == 'EP':
            for k in range (0,len(filenames)):
                df = pd.read_csv(filenames[k],header= 1,skiprows=[2],sep=',',low_memory=False)
                Final = pd.concat([Final,df])
            Final.index = Final['date']+' '+Final['time'] # Eddypro outputs both time and date as separate columns
            Final =Final.drop(['filename'],1) # not needed string-based column; gets in the way of converting to floating point
        else: 
            print('Format must be either EF or EP')
            return
        # Convert time index
        Final = Final.sort_index()
        Out = indx_fill(Final, time)
    return Out # Return dataframe to main function.    
