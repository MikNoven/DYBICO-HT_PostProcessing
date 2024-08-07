#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 16:19:17 2022

@author: Mikael Novén noven@nexs.ku.dk

A postproc script for gathering hometraining data.

"""

##############Import necessary libraries###################
import os
import pandas as pd 
import glob
import postproc_helper_HT as pph 
import matplotlib.pyplot as plt
import numpy as np
import HT_pdf_report_plots as reportbuilder

##############Helper functions###################

def calc_gamelevel(duration):
    if duration > 1.9 and duration < 2.1:
        gLvl = 1
    elif duration > 1.7 and duration < 1.9:
        gLvl = 2
    elif duration > 1.5 and duration < 1.7:
        gLvl = 3
    elif duration > 1.3 and duration < 1.5:
        gLvl = 4
    elif duration > 1.1 and duration < 1.3:
        gLvl = 5
        
    return gLvl


##############Set paths and plot options###################
#Change to where you have your data.
path='/Users/gdf724/Data/ReScale/ReScale2_HomeTraining'
report_dir='/Users/gdf724/Data/ReScale/ReScale2_reports/HomeTraining/'
#List all subjects to process.
#list_of_subjs=['y020']
list_of_subjs=['o016', 'y023']
sub_dir_list = sorted(glob.glob(os.path.join(path,'*/')))
#list_of_subjs = [x[-5:-1] for x in sub_dir_list]
#latest_training = [0]*len(list_of_subjs)
#Do you want to make trial GIFs for each run and condition? 
createGIFS = False 
#Do you want to make average trajectory plots for each run and condition?
doRunPlots = False
overwrite = False
makepdf = True
logtransform = True #Whether to logtransform data

##############Postprocessing################################
#Loop over subjects.
for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    HT_days = pph.get_HTfolders(path,subj)
    
    for day in range(len(HT_days)):
            sess = HT_days[day]
            if os.path.exists(os.path.join(sess,'SurveyAnswers.txt')):
                if not os.path.exists(os.path.join(path,subj,sess,'PostProcessing','Avg_Behaviour_Sess_1.pkl')) or overwrite:
        
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
                        trial_condition = []
                        condgroup = []
                        block = []
                        gameLvls = []
                        
                        S_block = 1
                        A_block = 1
                        
                        trial_React_L, trial_React_R, trial_ACCtw_L, trial_ACCtw_R, trial_ACCimpact_L, \
                         trial_ACCimpact_R, trial_impacttime_L, trial_impacttime_R, trial_impact_L, trial_impact_R, \
                         trial_time_on_target_L, trial_time_on_target_R, \
                         trial_forcediff, trial_success_time_L, trial_success_time_R, trial_success_time_both = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
                        
                        trial_timebins, trial_overshoot_L, trial_overshoot_R, trial_undershoot_L, trial_undershoot_R, trial_handsep, trial_volatility_L, trial_volatility_R = [],[],[],[],[],[],[],[]
                        trial_forceshift_L, trial_forceshift_R, trial_condshift = [],[],[]
                        
                        trial_volatility_500_L, trial_volatility_500_R = [],[]
                        
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
                                gameLvls.append(calc_gamelevel(tmp_dur[0]))
                                
                                (tmp_trial_React_L, tmp_trial_React_R, tmp_trial_ACCtw_L, tmp_trial_ACCtw_R, tmp_trial_ACCimpact_L, \
                                 tmp_trial_ACCimpact_R, tmp_trial_impacttime_L, tmp_trial_impacttime_R, tmp_trial_impact_L, tmp_trial_impact_R, \
                                 tmp_trial_time_on_target_L, tmp_trial_time_on_target_R, \
                                 tmp_trial_forcediff, tmp_trial_success_time_L, tmp_trial_success_time_R, tmp_trial_success_time_both, \
                                 tmp_trial_timebins, tmp_trial_overshoot_L, tmp_trial_overshoot_R, tmp_trial_undershoot_L, tmp_trial_undershoot_R, tmp_trial_handsep, tmp_trial_volatility_L, tmp_trial_volatility_R, tmp_trial_volatility_500_L, tmp_trial_volatility_500_R) = pph.get_trial_behaviour_HT(data['force_L'][itr],data['force_R'][itr],tmp_target_L,tmp_target_R,tmp_t,logtransform)#pph.get_trial_behaviour_HT(data['force_L'][itr],data['force_R'][itr],tmp_target_L,tmp_target_R,tmp_t)
                                
                                    
                                    
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
                        
                        #Save everything
                        trial_behaviour = pd.DataFrame()
                        trial_behaviour['condition'] = trial_condition
                        trial_behaviour['symmetry'] = condgroup
                        trial_behaviour['block'] = block
                        trial_behaviour['gamelevel'] = gameLvls
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
                        
                        #Create GIFs, the forth condition is whether or not to overwrite.
                        if createGIFS:
                            pph.makeConditionGIFs(os.path.join(path,subj,sess,'PostProcessing'), k, con_matrix, False) 
                
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
                             tmp_force_diff, tmp_timebins, tmp_overshoot_L, tmp_overshoot_R, tmp_undershoot_L, tmp_undershoot_R, tmp_handsep, tmp_volatility_L, tmp_volatility_R, tmp_volatility_500_L, tmp_volatility_500_R) = pph.get_avg_behaviour_HT(avg_L, avg_R, avg_target_L, avg_target_R, time,logtransform)
                            
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
        
    if makepdf:
        #if os.path.getmtime(os.path.join(report_dir,subj,subj+'_training.pdf'))
        reportbuilder.pdf_report_plots(path, report_dir, subj)
        
        
        
        
        
        
        