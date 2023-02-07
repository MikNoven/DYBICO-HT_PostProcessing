#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 14:29:06 2023

@author: gdf724
"""

##############Import necessary libraries###################
import os
import pandas as pd 
import glob
import postproc_helper_HT as pph 
import matplotlib.pyplot as plt

##############Set paths and plot options###################
#Change to where you have your data.
path='/Users/gdf724/Data/ReScale/HomeTrainingTest/' 
#List all subjects to process.
list_of_subjs=['P001', 'P002', 'P003']
report_dir='/Users/gdf724/Data/ReScale/HomeTrainingTest/Reports'


for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    HT_days = pph.get_HTfolders(path,subj)
    
    training_day=[]
    session=[]
    block=[]
    condgroup=[]
    durations=[]
    succ_times_both_150=[]
    succ_times_L_150=[]
    succ_times_R_150=[]
    succ_times_both_200=[]
    succ_times_L_200=[]
    succ_times_R_200=[]    
    succ_times_both_250=[]
    succ_times_L_250=[]
    succ_times_R_250=[]
    succ_times_both_300=[]
    succ_times_L_300=[]
    succ_times_R_300=[]
    for day in range(len(HT_days)):
        sess = HT_days[day]
        #Fix the data to the proper structure and in a PostProcessing-folder
        pph.make_PP_folder(sess)
        maxforce = pph.get_maxforce(sess)
        #if len(os.listdir(os.path.join(sess,'PostProcessing'))) < 2:
        for blockfile in glob.glob(os.path.join(sess,'hometraining_output_*.pkl')):
            pph.reshape_data(blockfile)
                
        DATAfiles = pph.get_DATAfiles(sess)
        #Loop over sessions.
        for k in range(len(DATAfiles)):
            datafile = DATAfiles[k]  
            
            
            filepath = os.path.join(path,subj,sess,'PostProcessing',datafile) #Modify this and later depending on save structure.
            
            # Read and sort the data
            file=pd.read_pickle(filepath)
            data = pph.drop_non_trials(file)
            
            ##############Postprocessing trials#################################  
            #Save information about block          
            S_block = 1
            A_block = 1

            for itr in range(len(data)):
                if data['targetTrial'][itr] != 'Baseline':
                    training_day.append(day+1)
                    session.append(k+1)
                    durations.append(data['duration'][itr])
                    tmp_t = [(data['time'][itr][j]-data['time'][itr][0]) for j in range(len(data['time'][itr]))]
                    tmp_target_L = [data['targets'][itr][k][0] for k in range(len(tmp_t))]
                    tmp_target_R = [data['targets'][itr][k][1] for k in range(len(tmp_t))]
                    (tmp_trial_succtimes, tmp_trial_success_time_L, tmp_trial_success_time_R, tmp_trial_success_time_both) = pph.check_success_times(data['force_L'][itr],data['force_R'][itr],tmp_target_L,tmp_target_R,tmp_t)
                    succ_times_both_150.append(tmp_trial_success_time_both[0])
                    succ_times_L_150.append(tmp_trial_success_time_L[0])
                    succ_times_R_150.append(tmp_trial_success_time_R[0])
                    succ_times_both_200.append(tmp_trial_success_time_both[1])
                    succ_times_L_200.append(tmp_trial_success_time_L[1])
                    succ_times_R_200.append(tmp_trial_success_time_R[1])
                    succ_times_both_250.append(tmp_trial_success_time_both[2])
                    succ_times_L_250.append(tmp_trial_success_time_L[2])
                    succ_times_R_250.append(tmp_trial_success_time_R[2])
                    succ_times_both_300.append(tmp_trial_success_time_both[3])
                    succ_times_L_300.append(tmp_trial_success_time_L[3])
                    succ_times_R_300.append(tmp_trial_success_time_R[3])
                    #0 if never true. Handle in coming steps. 
                    if data['targetTrial'][itr][0] == 'S':
                        block.append(S_block)
                        condgroup.append('S')
                    elif data['targetTrial'][itr][0] == 'A':
                        block.append(A_block)
                        condgroup.append('A')
                    
                    
                else:
                    if itr>0:
                        if data['targetTrial'][itr-1][0] == 'S':
                            S_block = S_block+1
                        elif data['targetTrial'][itr-1][0] == 'A':
                            A_block = A_block+1
            
            #Save session data + make session plots + calculate saved times
            
        #Save day data + Make day plots + calculate saved times
        
    #Make total plots + calculate saved times
    tot_save_pkl = pd.DataFrame(data = {'TrainingDay': training_day,
                                        'Session': session,
                                        'block': block,
                                        'Condition': condgroup,
                                        'Duration': durations,
                                        'SuccessTimes_R&L_150': succ_times_both_150,
                                        'SuccessTimes_L_150': succ_times_L_150,
                                        'SuccessTimes_R_150': succ_times_R_150,
                                        'SuccessTimes_R&L_200': succ_times_both_200,
                                        'SuccessTimes_L_200': succ_times_L_200,
                                        'SuccessTimes_R_200': succ_times_R_200,
                                        'SuccessTimes_R&L_250': succ_times_both_250,
                                        'SuccessTimes_L_250': succ_times_L_250,
                                        'SuccessTimes_R_250': succ_times_R_250,
                                        'SuccessTimes_R&L_300': succ_times_both_300,
                                        'SuccessTimes_L_300': succ_times_L_300,
                                        'SuccessTimes_R_300': succ_times_R_300})
    tot_save_pkl.to_csv(os.path.join(report_dir,subj+'_TrialSuccessTest.csv'))
            
