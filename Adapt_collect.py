#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 22:13:14 2023
Collect adaptation data.
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
path='/Users/gdf724/Data/ReScale/ReScale2_Adapt'
#Change to where you want your statistics table.
#List all subjects to process.
sub_dir_list = sorted(glob.glob(os.path.join(path,'*/')))
list_of_subjs = [x[-5:-1] for x in sub_dir_list]

logtransform = True

ToT, Error, log_scale, condition, subject, agegroup, hande, trial_nbr, trial_block, adaptday  = [], [], [], [], [], [], [], [], [], []

for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    adapt_days = pph.get_HTfolders(path,subj)
    
    for day in range(len(adapt_days)):
            sess = adapt_days[day]
            #Fix the data to the proper structure and in a PostProcessing-folder
            pph.make_PP_folder(sess)
            maxforce = pph.get_maxforce(sess)
            #if len(os.listdir(os.path.join(sess,'PostProcessing'))) < 2:
            for blockfile in sorted(glob.glob(os.path.join(sess,'output_file_*.pkl'))):
                pph.reshape_data(blockfile)
                                
            block_files = sorted(glob.glob(os.path.join(sess,'PostProcessing','DATA_file_*.pkl')))
            #Loop over sessions.
            for k in range(len(block_files)):
                datafile = block_files[k]  
                
                
                filepath = os.path.join(path,subj,sess,'PostProcessing',datafile) #Modify this and later depending on save structure.
                
                # Read and sort the data
                file=pd.read_pickle(filepath)
                data = pph.drop_non_trials(file)
                
                ##############Postprocessing trials#################################  
                #Save information about block 
                trial_condition = []
                condgroup = []
                block = []
                
                S_block = 1
                A_block = 1
                
                trial_React_L, trial_React_R, trial_ACCtw_L, trial_ACCtw_R, trial_ACCimpact_L, \
                 trial_ACCimpact_R, trial_impacttime_L, trial_impacttime_R, trial_impact_L, trial_impact_R, \
                 trial_time_on_target_L, trial_time_on_target_R, \
                 trial_forcediff, trial_success_time_L, trial_success_time_R, trial_success_time_both = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
                
                trial_timebins, trial_overshoot_L, trial_overshoot_R, trial_undershoot_L, trial_undershoot_R, trial_handsep, trial_volatility_L, trial_volatility_R = [],[],[],[],[],[],[],[]
                trial_forceshift_L, trial_forceshift_R, trial_condshift = [],[],[]
                
                last_target_L = 0
                last_target_R = 0
                
                for itr in range(len(data)):
                    if data['targetTrial'][itr] != 'Baseline':
                        trial_condition.append(data['targetTrial'][itr])
                        condgroup.append(data['targetTrial'][itr][0])
                        
                        if data['targetTrial'][itr][0] == 'S':
                            block.append(S_block)
                        elif data['targetTrial'][itr][0] == 'A':
                            block.append(A_block)
                        tmp_t = [(data['time'][itr][j]-data['time'][itr][0]) for j in range(len(data['time'][itr]))]
                        if len(tmp_t)<2:
                            tmp_t = [(data['t'][j]-data['t'][0]) for j in range(len(data['t']))]
                        tmp_target_L = [data['targets'][itr][k][0] for k in range(len(tmp_t))]
                        tmp_target_R = [data['targets'][itr][k][1] for k in range(len(tmp_t))]
                        
                        tmp_dur = data['duration']
                        
                        (tmp_trial_React_L, tmp_trial_React_R, tmp_trial_ACCtw_L, tmp_trial_ACCtw_R, tmp_trial_ACCimpact_L, \
                         tmp_trial_ACCimpact_R, tmp_trial_impacttime_L, tmp_trial_impacttime_R, tmp_trial_impact_L, tmp_trial_impact_R, \
                         tmp_trial_time_on_target_L, tmp_trial_time_on_target_R, \
                         tmp_trial_forcediff, tmp_trial_success_time_L, tmp_trial_success_time_R, tmp_trial_success_time_both, \
                         tmp_trial_timebins, tmp_trial_overshoot_L, tmp_trial_overshoot_R, tmp_trial_undershoot_L, tmp_trial_undershoot_R, tmp_trial_handsep, tmp_trial_volatility_L, tmp_trial_volatility_R) = pph.get_trial_behaviour_HT(data['force_L'][itr],data['force_R'][itr],tmp_target_L,tmp_target_R,tmp_t,logtransform)#pph.get_trial_behaviour_HT(data['force_L'][itr],data['force_R'][itr],tmp_target_L,tmp_target_R,tmp_t)
                        
                        trial_React_L.append(tmp_trial_React_L)
                        trial_React_R.append(tmp_trial_React_R)
                        trial_ACCtw_L.append(tmp_trial_ACCtw_L) 
                        trial_ACCtw_R.append(tmp_trial_ACCtw_R) 
                        trial_ACCimpact_L.append(tmp_trial_ACCimpact_L)
                        trial_ACCimpact_R.append(tmp_trial_ACCimpact_R)
                        trial_impacttime_L.append(tmp_trial_impacttime_L)
                        trial_impacttime_R.append(tmp_trial_impacttime_R)
                        trial_impact_L.append(tmp_trial_impact_L)
                        trial_impact_R.append(tmp_trial_impact_R)
                        trial_time_on_target_L.append(tmp_trial_time_on_target_L)
                        trial_time_on_target_R.append(tmp_trial_time_on_target_R)
                        trial_forcediff.append(tmp_trial_forcediff)
                        trial_success_time_L.append(tmp_trial_success_time_L)
                        trial_success_time_R.append(tmp_trial_success_time_R)
                        trial_success_time_both.append(tmp_trial_success_time_both)
                        trial_timebins.append(tmp_trial_timebins) 
                        trial_overshoot_L.append(tmp_trial_overshoot_L) 
                        trial_overshoot_R.append(tmp_trial_overshoot_R) 
                        trial_undershoot_L.append(tmp_trial_undershoot_L) 
                        trial_undershoot_R.append(tmp_trial_undershoot_R) 
                        trial_handsep.append(tmp_trial_handsep) 
                        trial_volatility_L.append(tmp_trial_volatility_L) 
                        trial_volatility_R.append(tmp_trial_volatility_R)
                        if itr == 0:
                            trial_forceshift_L.append(tmp_target_L[0]-0.5)
                            trial_forceshift_R.append(tmp_target_R[0]-0.5) 
                            trial_condshift.append('start_to_'+data['targetTrial'][itr]) 
                        else:
                            trial_forceshift_L.append(tmp_target_L[0]-last_target_L)
                            trial_forceshift_R.append(tmp_target_R[0]-last_target_R) 
                            trial_condshift.append(data['targetTrial'][itr-1]+'_to_'+data['targetTrial'][itr]) 
                            
                        last_target_L = tmp_target_L[0]
                        last_target_R = tmp_target_R[0]
                    else:
                        if itr>0:
                            if data['targetTrial'][itr-1][0] == 'S':
                                S_block = S_block+1
                            elif data['targetTrial'][itr-1][0] == 'A':
                                A_block = A_block+1
                                

                    subject.append(subj)
                    agegroup.append(subj[0])
                    adaptday.append(day+1)
                    trial_block.append(k+1)
                    trial_nbr.append(itr)
                    hande.append('L')
                    condition.append(data['targetTrial'][itr][0])
                    if trial_block==1:
                        log_scale.append(0)
                    else:
                        log_scale.append(1)
                    ToT.append(tmp_trial_time_on_target_L)
                    Error.append(tmp_trial_ACCtw_L)
                    
                    subject.append(subj)
                    agegroup.append(subj[0])
                    adaptday.append(day+1)
                    trial_block.append(k+1)
                    trial_nbr.append(itr)
                    hande.append('R')
                    condition.append(data['targetTrial'][itr][0])
                    if trial_block==1:
                        log_scale.append(0)
                    else:
                        log_scale.append(1)
                    ToT.append(tmp_trial_time_on_target_R)
                    Error.append(tmp_trial_ACCtw_R)
                        
                #Save everything
                trial_behaviour = pd.DataFrame()
                trial_behaviour['condition'] = trial_condition
                trial_behaviour['symmetry'] = condgroup
                trial_behaviour['block'] = block
                trial_behaviour['ReactTime_L'] = trial_React_L
                trial_behaviour['ReactTime_R'] = trial_React_R
                trial_behaviour['ACCtw_L'] = trial_ACCtw_L
                trial_behaviour['ACCtw_R'] = trial_ACCtw_R
                trial_behaviour['ACCimpact_L'] = trial_ACCimpact_L
                trial_behaviour['ACCimpact_R'] = trial_ACCimpact_R
                trial_behaviour['impacttime_L'] = trial_impacttime_L
                trial_behaviour['impacttime_R'] = trial_impacttime_R
                trial_behaviour['impact_L'] = trial_impact_L
                trial_behaviour['impact_R'] = trial_impact_R
                trial_behaviour['TimeOnTarget_L'] = trial_time_on_target_L
                trial_behaviour['TimeOnTarget_R'] = trial_time_on_target_R
                trial_behaviour['forcediff'] = trial_forcediff
                trial_behaviour['trial_success_time_L'] = trial_success_time_L
                trial_behaviour['trial_success_time_R'] = trial_success_time_R
                trial_behaviour['trial_success_time_both'] = trial_success_time_both
                trial_behaviour['timebins'] = trial_timebins 
                trial_behaviour['overshoot_L'] = trial_overshoot_L 
                trial_behaviour['overshoot_R'] = trial_overshoot_R 
                trial_behaviour['undershoot_L'] = trial_undershoot_L 
                trial_behaviour['undershoot_R'] = trial_undershoot_R 
                trial_behaviour['handsep'] = trial_handsep 
                trial_behaviour['volatility_L'] = trial_volatility_L 
                trial_behaviour['volatility_R'] = trial_volatility_R
                trial_behaviour['forceshift_L'] = trial_forceshift_L
                trial_behaviour['forceshift_R'] = trial_forceshift_R
                trial_behaviour['condshift'] = trial_condshift
                trial_behaviour.to_pickle(os.path.join(path,subj,sess,'PostProcessing','Trial_Behaviour_Sess_'+str(k+1)+'.pkl'))
                
                
                ##############Averages and plots################################# 
                #Make save structure. One per run and subject.
                behaviour = pd.DataFrame()
                
                con_matrix = pph.sort_data_by_condition(data) 
                #Loop over conditions.
                for c in range(len(con_matrix)):
                    con_data = con_matrix[c]
                    con_data.index = range(len(con_data))     
                    
                    cond = con_data['targetTrial'][0]
                    
                    ##############Postprocessing average################################    
                    (force_L, force_R, avg_target_L, avg_target_R, time) = pph.extract_as_arrays_rebase(con_data)
                    # calculate averages for plotting and statistics
                    avg_L = force_L.mean(axis=0)
                    avg_R = force_R.mean(axis=0)
                    (tmp_React_L, tmp_React_R, \
                     tmp_ACCtw_L, tmp_ACCtw_R, tmp_ACCimpact_L, tmp_ACCimpact_R, \
                     tmp_impacttime_L, tmp_impacttime_R, tmp_impact_L, tmp_impact_R, \
                     tmp_time_on_target_L, tmp_time_on_target_R, \
                     tmp_force_diff, tmp_timebins, tmp_overshoot_L, tmp_overshoot_R, tmp_undershoot_L, tmp_undershoot_R, tmp_handsep, tmp_volatility_L, tmp_volatility_R) = pph.get_avg_behaviour_HT(avg_L, avg_R, avg_target_L, avg_target_R, time,logtransform)
                    
                    #We don't know the correct direction here so just do averages. 
                        
                    #Save behavioural data
                    #Average
                    save_pkl = pd.DataFrame()
                    save_pkl['Condition'] = [cond] #Possibly minus 1
                    save_pkl['React_L'] = tmp_React_L
                    save_pkl['React_R'] = tmp_React_R            
                    save_pkl['ACCtw_L'] = tmp_ACCtw_L
                    save_pkl['ACCtw_R'] = tmp_ACCtw_R
                    save_pkl['ACCimpact_L'] = tmp_ACCimpact_L
                    save_pkl['ACCimpact_R'] = tmp_ACCimpact_R
                    save_pkl['impacttime_L'] = tmp_impacttime_L
                    save_pkl['impacttime_R'] = tmp_impacttime_R
                    save_pkl['impact_L'] = tmp_impact_L
                    save_pkl['impact_R'] = tmp_impact_R     
                    save_pkl['time_on_target_L'] = tmp_time_on_target_L
                    save_pkl['time_on_target_R'] = tmp_time_on_target_R   
                    save_pkl['forcediff'] = tmp_force_diff 
                    save_pkl['timebins'] = [tmp_timebins] 
                    save_pkl['overshoot_L'] = [tmp_overshoot_L] 
                    save_pkl['overshoot_R'] = [tmp_overshoot_R] 
                    save_pkl['undershoot_L'] = [tmp_undershoot_L] 
                    save_pkl['undershoot_R'] = [tmp_undershoot_R] 
                    save_pkl['handsep'] = [tmp_handsep] 
                    save_pkl['volatility_L'] = [tmp_volatility_L] 
                    save_pkl['volatility_R'] = [tmp_volatility_R]
        
                    #Append to behaviour dataframe
                    behaviour = behaviour.append(save_pkl, ignore_index=True)                    
                    
                behaviour.to_pickle(os.path.join(path,subj,sess,'PostProcessing','Avg_Behaviour_Sess_'+str(k+1)+'.pkl'))


save_pkl = pd.DataFrame()
save_pkl['subject'] = subject #Possibly minus 1
save_pkl['group'] = agegroup
save_pkl['adaptation_day'] = adaptday            
save_pkl['block'] = trial_block
save_pkl['trial_number'] = trial_nbr
save_pkl['log_scale'] = log_scale
save_pkl['condition'] = condition
save_pkl['hand'] = hande
save_pkl['ToT'] = ToT
save_pkl['Error500ms'] = Error
save_pkl.to_csv(os.path.join(path,'Adaptation_Behavior.csv'),index=False)