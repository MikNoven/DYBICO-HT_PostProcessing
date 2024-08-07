#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 21:19:23 2023
Collect stats file for HT data.
@author: gdf724
"""

##############Import necessary libraries###################
import os
import pandas as pd 
import numpy as np
import postproc_helper_HT as pph
import glob

##############Set paths and initialize parameters###########
#Change to where you have your data.
#path='/Users/gdf724/Data/ReScale/HomeTrainingTest' 
path='/Users/gdf724/Data/ReScale/ReScale2_HomeTraining'
#Change to where you want your statistics table.
#List all subjects to process.
sub_dir_list = sorted(glob.glob(os.path.join(path,'*/')))
list_of_subjs = [x[-5:-1] for x in sub_dir_list]

ToT, Error, short, showcase, condition, subject, agegroup, hande, blocke, trainingday = [], [], [], [], [], [], [], [], [], []
ToT_t, Error_t, short_t, showcase_t, condition_t, subject_t, agegroup_t, hand_t, tenthOfTraining = [], [], [], [], [], [], [], [], []

for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    HT_days = pph.get_HTfolders(path,subj)
    
    for day in range(len(HT_days)):
            sess = HT_days[day]
            block_files = pph.get_block_files(sess)
            for block in range(len(block_files)):
                blockdata = pd.read_pickle(block_files[block])
                for hand in ['L', 'R']:
                    for cond in ['A', 'S']:
                        subject.append(subj)
                        agegroup.append(subj[0])
                        trainingday.append(day+1)
                        blocke.append(block+1)
                        if len(blockdata) < 120:
                            short.append(1)
                            if len(blockdata) < 50:
                                showcase.append(1)
                            else:
                                showcase.append(0)
                        else:
                            short.append(0)
                            showcase.append(0)
                        ToT.append(np.mean(blockdata['TimeOnTarget_'+hand][blockdata['symmetry']==cond]))
                        Error.append(np.mean(blockdata['ACCtw_'+hand][blockdata['symmetry']==cond]))
                        hande.append(hand)
                        condition.append(cond)


save_pkl = pd.DataFrame()
save_pkl['subject'] = subject #Possibly minus 1
save_pkl['group'] = agegroup
save_pkl['training_day'] = trainingday            
save_pkl['block'] = blocke
save_pkl['condition'] = condition
save_pkl['hand'] = hande
save_pkl['ToT'] = ToT
save_pkl['Error500ms'] = Error
save_pkl['IsShort'] = short
save_pkl['IsShowcase'] = showcase
save_pkl.to_csv(os.path.join(path,'Hometraining_Behavior.csv'),index=False)
                
                
                