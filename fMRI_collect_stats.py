#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 08:00:39 2023

Script for collecting the statistics for fMRI. 

@author: gdf724
"""
############ IMPORTS ############
import os
import pandas as pd
import glob

############ HELP FUNCTIONS######
def check_subject(subject,ReS1):
    subj_str = ''
    if ReS1:
        if len(subject)==15:
            subj_str = subject[-6:]
    else:
        if len(subject)==4:
            subj_str = subject
    return subj_str

############ MAIN ###############
def fMRI_collect_stats(datapath,background,RS1):
    #Get background
    if RS1:
        bg = pd.read_csv(background,';')
    else:
        bg = pd.read_excel(background)
    
    subj_col = []
    age_col = []
    sex_col = []
    group_col = []
    sess_col = []
    block_col = []
    biman_context_col = []
    cond_col = []
    forceshift_col = []
    hand_col = []
    ToT_col = []
    err_col = []
    imp_col = []
    impt_col= []
    forcediff_col = []
    vol_1_col = []
    vol_2_col = []
    vol_3_col = []
    us_1_col = []
    us_2_col = []
    us_3_col = []
    os_1_col = []
    os_2_col = []
    os_3_col = []
    vol_500_col = []
    
    #loop over subjects
    for sub in sorted(glob.glob(os.path.join(datapath,'*/'))):
        subj_pth = os.path.normpath(sub)
        subj = check_subject(os.path.split(subj_pth)[1],RS1)
        if len(subj)>0 and len(bg.loc[bg['subject'] == subj])>0:
            #Take relevant background.
            print(subj)
            subj_bg = bg.loc[bg['subject'] == subj]
            age = [int(x) for x in subj_bg['age']][0]
            sex = [str(x) for x in subj_bg['sex']][0]
            group = [str(x) for x in subj_bg['group']][0]
            #Load pickles
            if RS1:
                sessions = [subj_pth]
            else:
                sessions = sorted(glob.glob(os.path.join(subj_pth,'*/')))
            for sess_itr in range(len(sessions)):
                datafiles = sorted(glob.glob(os.path.join(sessions[sess_itr],'PostProcessing','Trial_*')))
                for block_itr in range(len(datafiles)):
                    data = pd.read_pickle(datafiles[block_itr])
                    #Build grand statistics file
                    for trial_itr in range(len(data)):
                        trial_data = data.iloc[trial_itr]
                        for hand in ['L', 'R']:
                            subj_col.append(subj)
                            age_col.append(age)
                            sex_col.append(sex)
                            group_col.append(group)
                            if not RS1:
                                sess_col.append(sess_itr+1)
                            block_col.append(block_itr+1)
                            biman_context_col.append(trial_data['condition'][0])
                            cond_col.append(trial_data['condition'])
                            forceshift_col.append(trial_data['forceshift_'+hand])
                            hand_col.append(hand)
                            ToT_col.append(trial_data['TimeOnTarget_'+hand])
                            err_col.append(trial_data['ACCtw_'+hand])
                            imp_col.append(trial_data['impact_'+hand])
                            impt_col.append(trial_data['impacttime_'+hand])
                            forcediff_col.append(trial_data['forcediff'])
                            vol_1_col.append(trial_data['volatility_'+hand][0])
                            vol_2_col.append(trial_data['volatility_'+hand][1])
                            vol_3_col.append(trial_data['volatility_'+hand][2])
                            us_1_col.append(trial_data['undershoot_'+hand][0])
                            us_2_col.append(trial_data['undershoot_'+hand][1])
                            us_3_col.append(trial_data['undershoot_'+hand][2])
                            os_1_col.append(trial_data['overshoot_'+hand][0])
                            os_2_col.append(trial_data['overshoot_'+hand][1])
                            os_3_col.append(trial_data['overshoot_'+hand][2])
                            vol_500_col.append(trial_data['volatility_500_'+hand])
            
    #Save to csv.
    if RS1:
        save_pkl= pd.DataFrame({'Subject': subj_col,
                                'Age': age_col,
                                'Sex': sex_col,
                                'Group': group_col,
                                'Block': block_col,
                                'Hand': hand_col,
                                'Coordination_context': biman_context_col,
                                'Condition': cond_col,
                                'HandSep': forcediff_col,
                                'ToT': ToT_col,
                                'Error500ms': err_col,
                                'Impact': imp_col,
                                'ImpactTime': impt_col,
                                'Volatility_tb1': vol_1_col,
                                'Volatility_tb2': vol_2_col,
                                'Volatility_tb3': vol_3_col,
                                'Overshoot_tb1': os_1_col,
                                'Overshoot_tb2': os_2_col,
                                'Overshoot_tb3': os_3_col,
                                'Undershoot_tb1': us_1_col,
                                'Undershoot_tb2': us_2_col,
                                'Undershoot_tb3': us_3_col,
                                'Volatility_500': vol_500_col})
    else:
        save_pkl= pd.DataFrame({'Subject': subj_col,
                                'Age': age_col,
                                'Sex': sex_col,
                                'Group': group_col,
                                'Day': sess_col,
                                'Block': block_col,
                                'Hand': hand_col,
                                'Coordination_context': biman_context_col,
                                'Condition': cond_col,
                                'HandSep': forcediff_col,
                                'ToT': ToT_col,
                                'Error500ms': err_col,
                                'Impact': imp_col,
                                'ImpactTime': impt_col,
                                'Volatility_tb1': vol_1_col,
                                'Volatility_tb2': vol_2_col,
                                'Volatility_tb3': vol_3_col,
                                'Overshoot_tb1': os_1_col,
                                'Overshoot_tb2': os_2_col,
                                'Overshoot_tb3': os_3_col,
                                'Undershoot_tb1': us_1_col,
                                'Undershoot_tb2': us_2_col,
                                'Undershoot_tb3': us_3_col,
                                'Volatility_500': vol_500_col})
    
    save_pkl.to_csv(os.path.join(datapath,'fMRI_behavior.csv'), index=False)
    
    
    
    
    
    
    
    