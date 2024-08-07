#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 09:43:08 2024
Script to get values from FreeSurfer Stats file.
@author: gdf724
"""

import pandas as pd
import numpy as np

list_of_subjects = ['sub-X03380',  'sub-X05985',  'sub-X07261',  'sub-X07583',  'sub-X08350',  'sub-X13042',  'sub-X15499',  'sub-X16415',  'sub-X17531',  'sub-X17889',  'sub-X19539',  'sub-X20073',  'sub-X21391',  'sub-X25542',  'sub-X27569',  'sub-X28113',  'sub-X28182',  'sub-X31844',  'sub-X32429',  'sub-X34710',  'sub-X35113',  'sub-X35432',  'sub-X41822',  'sub-X43185',  'sub-X44222',  'sub-X45611',  'sub-X47295',  'sub-X48358',  'sub-X51652',  'sub-X57496',  'sub-X66530',  'sub-X68270',  'sub-X68602',  'sub-X69148',  'sub-X70069',  'sub-X71136',  'sub-X73411',  'sub-X75536',  'sub-X75767',  'sub-X76468',  'sub-X82865',  'sub-X86029',  'sub-X86857',  'sub-X87751',  'sub-X98419',  'sub-X98895']
ROIs = ['L_6a_ROI-096', 'L_LO3_ROI-159', 'L_SCEF_ROI-043', 'L_M1hand', 'R_6a_ROI-096', 'R_LO3_ROI-159', 'R_SCEF_ROI-043', 'R_M1hand']

subjcol = []
ROIcol = []
#CT_array = np.zeros((len(list_of_subjects),len(ROIs)))
#Myelin_array = np.zeros((len(list_of_subjects),len(ROIs)))
CTcol = []

for ROIitr in range(len(ROIs)):
    ROI=ROIs[ROIitr]
    for subjitr in range(len(list_of_subjects)):
        subject=list_of_subjects[subjitr]
        with open('/Users/gdf724/Data/ReScale/ReScal1_cortical/Refined_subjectdata/'+subject+'_'+ROI+'.label_CT.stats') as f:
            for line in f:
                pass
            last_line=line
        CTcol.append(last_line.split()[2])
        ROIcol.append(ROI)
        subjcol.append(subject)
        
save_df = pd.DataFrame({'subject': subjcol,
                        'node': ROIcol,
                        'CT': CTcol})

save_df.to_csv('/Users/gdf724/Data/ReScale/ReScal1_cortical/ReScale1_CorticalData_GlasserROIs_refined.csv', index=False)
