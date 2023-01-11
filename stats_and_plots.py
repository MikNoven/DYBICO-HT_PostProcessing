#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 21:28:39 2022
Script to get stats from pkl-files.
@author: gdf724
"""

##############Import necessary libraries###################
import os
import pandas as pd 
from numpy import nan
import postproc_helper_HT as pph

##############Set paths and initialize parameters###########
#Change to where you have your data.
#path='/Users/gdf724/Data/ReScale/HomeTrainingTest' 
path='/Volumes/io.erda.dk/NEXS/Sections/MN/VIP_Projects/ReScale/ReScale2/04_Data/01_DataFiles/00_Raw_Data'
#Change to where you want your statistics table.
#savepath='/Users/gdf724/Code/Rprojects/ReScale_HT'
savepath='/Volumes/io.erda.dk/NEXS/Sections/MN/VIP_Projects/ReScale/ReScale2/04_Data/01_DataFiles/01_Data_Process_and_Analysis_Steps/HomeTraining/'
#List all subjects to process.
list_of_subjs=['P001','P002']

ReactTime, ACCimpact, ACCtw, condition, subject, agegroup, hand, block, session = [], [], [], [], [], [], [], [], []

##############Load the data###############
for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    
    HT_sessions = pph.get_HTfolders(path, subj)
    for sess in range(len(HT_sessions)):
        sessionpath = HT_sessions[sess]
        for itr in range(3):
            tmp_data = pd.read_pickle(os.path.join(sessionpath,'PostProcessing','Der_Behaviour_Run_'+str(itr+1)+'.pkl'))
            for iitr in range(len(tmp_data)):
                cond_data = tmp_data.iloc[iitr]
                if cond_data['Condition'] != 'Baseline_force':  
                    if cond_data['React_L'] < 0.15 or cond_data['React_L'] > 2:
                        ReactTime.append(nan)
                    else:
                        ReactTime.append(cond_data['React_L'])
                    
                    ACCimpact.append(cond_data['ACCimpact_L'])
                    ACCtw.append(cond_data['ACCtw_L'])
                    condition.append(cond_data['Condition'])
                    subject.append(subj)
                    agegroup.append(subj[0])
                    hand.append('L')
                    block.append(str(itr+1))
                    session.append(str(sess+1))
                    
                    if cond_data['React_R'] < 0.15 or cond_data['React_R'] > 2:
                        ReactTime.append(nan)
                    else:
                        ReactTime.append(cond_data['React_R'])
                        
                    ACCimpact.append(cond_data['ACCimpact_R'])
                    ACCtw.append(cond_data['ACCtw_R'])              
                    condition.append(cond_data['Condition'])
                    subject.append(subj)
                    agegroup.append(subj[0])
                    hand.append('R')
                    block.append(str(itr+1))
                    session.append(str(sess+1))
            



##############Save data table############
#Between factors: agegroup (2 levels)
#Within factors: hand, condition, block
#One .csv-files with columns: RTstart, RTend, ACCimpact, subject, agegroup, hand, condition, block, impa
data = pd.DataFrame()
data['ReactTime'] = ReactTime
data['ACCimpact'] = ACCimpact
data['ACCtw'] = ACCtw
data['condition'] = condition
data['subject'] = subject
data['agegroup'] = agegroup
data['hand'] = hand
data['block'] = block
data['session'] = session

data.to_csv(os.path.join(savepath,'ReScale_HT_behaviour_der.csv'))
