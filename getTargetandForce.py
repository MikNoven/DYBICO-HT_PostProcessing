#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 19:43:50 2023

@author: gdf724
"""

##############Import necessary libraries###################
import os
import pandas as pd 
import glob
import postproc_helper_HT as pph 
import numpy as np

##############Set paths###################
#Change to where you have your data.
#List all subjects to process.
RS1=True #ReScale1 structure slightly different due to not longitudinal.
if RS1:
    path='/Users/gdf724/Data/ReScale/ReScale1_fMRI_behavior'
    target_dir='/Users/gdf724/Data/ReScale/ReScale1_covariate_files/'
    background_path = '/Users/gdf724/Data/ReScale/ReScale1_background/RS1_background.csv'
    sub_dir_list = sorted(glob.glob(os.path.join(path,'*/')))
    list_of_subjs = [x[-7:-1] for x in sub_dir_list]
else:
    path='/Users/gdf724/Data/ReScale/ReScale2_fMRI_behavior'
    target_dir='/Users/gdf724/Data/ReScale/ReScale2_covariate_files/'
    background_path = '/Users/gdf724/Data/ReScale/ReScale2_Pretests/ReScale2_background.xlsx'
    #list_of_subjs = ['y005']
    sub_dir_list = sorted(glob.glob(os.path.join(path,'*/')))
    list_of_subjs = [x[-5:-1] for x in sub_dir_list]

for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    if RS1:
        fMRI_days =[sub_dir_list[i]]
    else:
        fMRI_days = pph.get_HTfolders(path,subj)
        
    if not os.path.exists(os.path.join(target_dir,subj)):
        os.makedirs(os.path.join(target_dir,subj))
        
    for day in range(len(fMRI_days)):
            sess = fMRI_days[day]
            datafiles = pph.get_Blockfiles(sess)
            
            #Loop over sessions.
            for k in range(len(datafiles)):
                datafile = datafiles[k]  
                data=pd.read_pickle(datafile)
                #Get the time, force and target 
                time = data['time'][0]
                force_L_asym = [0]*len(time)
                force_R_asym = [0]*len(time)
                target_L_asym = [0]*len(time)
                target_R_asym = [0]*len(time)
                force_L_sym = [0]*len(time)
                force_R_sym = [0]*len(time)
                target_L_sym = [0]*len(time)
                target_R_sym = [0]*len(time)
                for itr in range(len(time)):
                    if data['target_name'][0][itr][0] == 'A':
                        target_L_asym[itr] = data['target'][0][itr][0]
                        target_R_asym[itr] = data['target'][0][itr][1]
                        force_L_asym[itr] = data['left_force'][0][itr]
                        force_R_asym[itr] = data['right_force'][0][itr]
                    elif data['target_name'][0][itr][0] == 'S':
                        target_L_sym[itr] = data['target'][0][itr][0]
                        target_R_sym[itr] = data['target'][0][itr][1]
                        force_L_sym[itr] = data['left_force'][0][itr]
                        force_R_sym[itr] = data['right_force'][0][itr]
                        
                savedata = {'time': time,
                        'target_L_asym': target_L_asym,
                        'target_R_asym': target_R_asym,
                        'force_L_asym': force_L_asym,
                        'force_R_asym': force_R_asym,
                        'target_L_sym': target_L_sym,
                        'target_R_sym': target_R_sym,
                        'force_L_sym': force_L_sym,
                        'force_R_sym': force_R_sym}
                savedf = pd.DataFrame(savedata)
                savedf.to_csv(os.path.join(target_dir,subj,'DYBICO_data_run-0'+str(k+1)+'.csv'),header=True,index=False)                    
