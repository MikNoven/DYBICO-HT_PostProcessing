#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  9 11:38:19 2024
Script for getting fMRI timing files in SPM format, not BIDS. 
@author: gdf724
"""

##############Import necessary libraries###################
import os
import pandas as pd 
import glob
import postproc_helper_HT as pph 

##############Set paths and plot options###################
RS1=False #ReScale1 structure slightly different due to not longitudinal.
if RS1:
    path='/Users/gdf724/Data/ReScale/ReScale1_fMRI_behavior'
    timing_dir='/Users/gdf724/Data/ReScale/ReScale1_fMRI_timing'
    background_path = '/Users/gdf724/Data/ReScale/ReScale1_background/RS1_background.csv'
    sub_dir_list = sorted(glob.glob(os.path.join(path,'*/')))
    list_of_subjs = ['D00056', 'Y00047', 'Y00014']
else:
    path='/Users/gdf724/Data/ReScale/ReScale2_fMRI_behavior'
    timing_dir='/Users/gdf724/Data/ReScale/ReScale2_fMRI_timing/'
    background_path = '/Users/gdf724/Data/ReScale/ReScale2_Pretests/ReScale2_background.xlsx'
    #list_of_subjs = ['o004', 'y011']
    sub_dir_list = sorted(glob.glob(os.path.join(path,'*/')))
    list_of_subjs = [x[-5:-1] for x in sub_dir_list]


for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    if RS1:
        fMRI_days =[sub_dir_list[i]]
    else:
        fMRI_days = pph.get_HTfolders(path,subj)
        
    if not os.path.exists(os.path.join(timing_dir,'sub-'+subj)):
        os.makedirs(os.path.join(timing_dir,'sub-'+subj))
    for day in range(len(fMRI_days)):
        if not os.path.exists(os.path.join(timing_dir,'sub-'+subj,'ses-'+str(day+1))):
            os.makedirs(os.path.join(timing_dir,'sub-'+subj,'ses-'+str(day+1)))
        sess = fMRI_days[day]
        
        DATAfiles = pph.get_DATAfiles(sess)
        
        #Loop over runs.
        for k in range(len(DATAfiles)):
            datafile = DATAfiles[k]  
            sym_onsets = []
            sym_durations = []
            asym_onsets = []
            asym_durations = []
            # Read and sort the data
            data=pd.read_pickle(datafile)
            
            current=data['targetTrial'][0][0]
            for itr in range(len(data['targetTrial'])):
                tmp=data['targetTrial'][itr]
                if tmp[0]!=current:
                    if tmp[0]=='A':
                        asym_onsets.append(data['onsets'][itr])
                    elif tmp[0]=='S':
                        sym_onsets.append(data['onsets'][itr])
                    elif tmp[0]=='P' and itr>7:
                        if current=='S':
                            sym_durations.append(data['t'][itr]-sym_onsets[len(sym_onsets)-1])
                        elif current=='A':
                            asym_durations.append(data['t'][itr]-asym_onsets[len(asym_onsets)-1])
                    current=tmp[0]
            #Check the names of the columns.
            sym_save_df = pd.DataFrame(''        
            #Make one tsv-file separated by actual tabs for asym and sym for each run. 
            #asym_run-01.tsv