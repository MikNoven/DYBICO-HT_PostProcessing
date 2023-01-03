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

##############Set paths and plot options###################
#Change to where you have your data.
path='/Users/gdf724/Data/ReScale/HomeTrainingTest/' 
#List all subjects to process.
list_of_subjs=['P001']
#Do you want to make trial GIFs for each run and condition? 
createGIFS = False 
#Do you want to make average trajectory plots for each run and condition?
doRunPlots = True

##############Postprocessing################################
#Loop over subjects.
for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    HT_sessions = pph.get_HTfolders(path,subj)
    
    for sess in HT_sessions:
        #Fix the data to the proper structure and in a PostProcessing-folder
        pph.make_PP_folder(sess)
        maxforce = pph.get_maxforce(sess)
        if len(os.listdir(os.path.join(sess,'PostProcessing'))) < 2:
            for blockfile in glob.glob(os.path.join(sess,'hometraining_output_*.pkl')):
                pph.reshape_data(blockfile)
                
        DATAfiles = pph.get_DATAfiles(sess)
        
        #Loop over blocks.
        for k in range(len(DATAfiles)):
            datafile = DATAfiles[k]  
            
            
            filepath = os.path.join(path,subj,sess,'PostProcessing',datafile) #Modify this and later depending on save structure.
            
            # Read and sort the data
            file=pd.read_pickle(filepath)
            data = pph.drop_non_trials(file)
            
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
                
                (shortest_trial, force_L, force_R, target_L, target_R, time) = pph.extract_as_arrays(con_data)
                t = [(time[j]-time[j][0]) for j in range(len(time))][0]
                
                cond = con_data['targetTrial'][0]
                
                ##############Postprocessing average################################                
                # calculate averages for plotting and statistics
                avg_L = force_L.mean(axis=0)
                avg_R = force_R.mean(axis=0)
                avg_target_L = target_L.sum(axis=0)/len(target_L)
                avg_target_R = target_R.sum(axis=0)/len(target_R)
                (tmp_React_L, tmp_React_R, tmp_RTstart_L, tmp_RTstart_R, tmp_RTend_L, tmp_RTend_R, \
                 tmp_ACCtw_L, tmp_ACCtw_R, tmp_ACCimpact_L, tmp_ACCimpact_R, \
                 tmp_impacttime_L, tmp_impacttime_R, tmp_impact_L, tmp_impact_R, tmp_impacttime_bl_L, \
                 tmp_impacttime_bl_R, tmp_performance_score_L, tmp_performance_score_R, \
                 tmp_force_diff) = pph.get_trial_behaviour_HT(cond, avg_L, avg_R, avg_target_L, avg_target_R, t)
                
                #We don't know the correct direction here so just do averages. 
                    
                #Save behavioural data
                #Average
                save_pkl = pd.DataFrame()
                save_pkl['Condition'] = [cond] #Possibly minus 1
                save_pkl['React_L'] = tmp_React_L
                save_pkl['React_R'] = tmp_React_R            
                save_pkl['RTstart_L'] = tmp_RTstart_L
                save_pkl['RTstart_R'] = tmp_RTstart_R
                save_pkl['RTend_L'] = tmp_RTend_L
                save_pkl['RTend_R'] = tmp_RTend_R
                save_pkl['ACCtw_L'] = tmp_ACCtw_L
                save_pkl['ACCtw_R'] = tmp_ACCtw_R
                save_pkl['ACCimpact_L'] = tmp_ACCimpact_L
                save_pkl['ACCimpact_R'] = tmp_ACCimpact_R
                save_pkl['impacttime_L'] = tmp_impacttime_L
                save_pkl['impacttime_R'] = tmp_impacttime_R
                save_pkl['impact_L'] = tmp_impact_L
                save_pkl['impact_R'] = tmp_impact_R            
                save_pkl['impacttime_bl_L'] = tmp_impacttime_bl_L
                save_pkl['impacttime_bl_R'] = tmp_impacttime_bl_R
                save_pkl['performance_score_L'] = tmp_performance_score_L
                save_pkl['performance_score_R'] = tmp_performance_score_R
                save_pkl['forcediff'] = tmp_force_diff #Not interesting?
    
                #Append to behaviour dataframe
                behaviour = behaviour.append(save_pkl, ignore_index=True)                    
                
                if doRunPlots: #Add overwrite functionality
                    if not os.path.exists(os.path.join(path,subj,sess,'PostProcessing','Avg_Run_'+str(k+1)+'_'+con_data['targetTrial'][0]+'.png')):
                        plt.figure(c)
                        plt.xlim([0,2])
                        plt.ylim([0,1.5])
                        plt.plot(t,avg_R, 'r', label="Right force")
                        plt.plot(t,avg_target_R, 'r--', label="Right target")
                        plt.plot(t,avg_L, 'b', label="Left force")
                        plt.plot(t,avg_target_L, 'b--', label="Left target")
                        plt.title(con_data['targetTrial'][0])
                        plt.legend()
                        plt.xlabel('Seconds')
                        plt.ylabel('Maxforce')
                        plt.yticks([0.25, 0.5, 0.75, 1.0, 1.25], ['2.5%', '5%', '7.5%', '10%', '12.5%'])
                        #plt.show()
                        # save the figure 
                        plt.savefig(os.path.join(path,subj,sess,'PostProcessing','Avg_Run_'+str(k+1)+'_'+con_data['targetTrial'][0]+'.png'))
                        plt.clf()
    
            #Save behavior to file
            behaviour.to_pickle(os.path.join(path,subj,sess,'PostProcessing','Der_Behaviour_Run_'+str(k+1)+'.pkl'))
            