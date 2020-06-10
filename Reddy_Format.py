# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 11:15:25 2018

@author: Eric Russell
Laboratory for Atmospheric Research
Dept. Civil and Environmental Engineering
Washington State University
eric.s.russell@wsu.edu
"""

# CE = AF_Out_QC 
# FileName = Driver['Val_L']['REDDY_File']
# col_str= 'Start_AF'

import pandas as pd
import numpy as np
from datetime import datetime
def REddy_Format(CE, FileName, col_str):
    cols = pd.read_csv('C:\\Users\\Eric\\Desktop\\PySCripts\\Flux_Processing_Code\\Reddy_Cols.csv',header=0)
    z = pd.DataFrame(CE.index)
    z = z[0].astype(str)
    adate,Y,H,M = [],[],[],[]
    for k in range(0,len(z)):
        adate.append(datetime.strptime(z[k],"%Y-%m-%d %H:%M:%S").timetuple().tm_yday)
        dt = datetime.strptime(z[k], "%Y-%m-%d %H:%M:%S")
        Y.append(dt.year)
        H.append(dt.hour)
        M.append(dt.minute)
    M = pd.DataFrame(M);
    H = pd.DataFrame(H);
    Y = pd.DataFrame(Y);
    adate = pd.DataFrame(adate)
    qn = M==30
    H[qn] = H[qn]+0.5
    Outa = []; Outa = pd.DataFrame(Outa)
    Outa['Year'] = Y[0]
    Outa['DoY'] = adate[0]
    Outa['Hour'] = H[0]
    Outa.index = CE.index
    cls = CE.columns
    s = cls.isin(cols[col_str][3:])
    AF_Out = CE.drop(CE[cls[~s]],axis = 1)
    cls = AF_Out.columns
    Outa = Outa.join(AF_Out).astype(float)
    for k in range (3,len(cols)):
        Outa = Outa.rename(columns={cols[col_str][k]:cols['ReddyProc'][k]})
        qq = np.isnan(Outa[cols['ReddyProc'][k]].astype(float))
        del qq
    Outa.to_csv(FileName, sep = '\t', index=False, na_rep = -9999)