#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 17:03:21 2023
Code for generating a pdf report over learning.

This script will output a training report for the entire training period (thus far) containing:
- Plot of max force for each hand and day
- Plot of the time of day that training started
- Plot of sleep time and quality
- Table of physical activity for each day
as well as performance measures averaged for each day. 

It will also produce training reports for each training day with performance measures 
between sessions, within sessions, and within blocks.

@author: gdf724
"""
##############Import necessary libraries###################
import os
import pandas as pd 
import postproc_helper_HT as pph
import matplotlib.pyplot as plt
from fpdf import FPDF


def get_block_data(sess_t_data):
    #Returns a list of indices for the block, one block for each row.
    A_block = [[] for x in range(max(sess_t_data['block']))]
    S_block = [[] for x in range(max(sess_t_data['block']))]
    for itr in range(len(sess_t_data)):
        if sess_t_data['symmetry'][itr]=='S':
            S_block[sess_t_data['block'][itr]-1].append(sess_t_data.iloc[itr])
        elif sess_t_data['symmetry'][itr]=='A':
            A_block[sess_t_data['block'][itr]-1].append(sess_t_data.iloc[itr])
    
    return A_block, S_block

##############Set paths and plot options###################
#Change to where you have your data.
path='/Users/gdf724/Data/ReScale/HomeTrainingTest/' 
#List all subjects to process.
list_of_subjs=['P001', 'P002', 'P003']
report_dir='/Users/gdf724/Data/ReScale/HomeTrainingTest/Reports'

##############Make daily reports and build averages###################
for subj in list_of_subjs:
    HT_days = pph.get_HTfolders(path, subj)
    max_forces_L=[] 
    max_forces_R=[]
    time_of_day=[]
    sleep_times=[]
    sleep_qualities=[]
    physical_activity_matrix=[]
    pa_rows = ['Training day %d' % x for x in range(1,len(HT_days)+1)]
    pa_columns = ('Brisk walk', 'Cardio', 'Swimming', 'Weight training', 'Other')
    
    ToT_asym_L = [] #One value per day
    ToT_asym_R = []
    ToT_sym_L = []
    ToT_sym_R = []
    err_asym_L = []
    err_asym_R = []
    err_sym_L = []
    err_sym_R = []
    trialSuccess_asym_L = []
    trialSuccess_asym_R = []
    trialSuccess_sym_L = []
    trialSuccess_sym_R = []
    trialSuccess_asym_both = []
    trialSuccess_sym_both = []
    handsep_asym = [] #Right now it's the sum of Right-Left, not absolute. Modify when necessary.
    handsep_sym = []
    RT_asym_L = [] #Save RT for later, or make the plots but don't put in report
    RT_asym_R = []
    RT_sym_L = []
    RT_sym_R = []
    
    #Make subject dir
    if not os.path.exists(os.path.join(report_dir,subj)):
        os.makedirs(os.path.join(report_dir,subj))
    
    for day_itr in range(len(HT_days)):
        day_save_folder = os.path.join(report_dir,subj,'Day_'+str(day_itr+1))
        if not os.path.exists(day_save_folder):
            os.makedirs(day_save_folder)
        day_path = HT_days[day_itr]
        with open(os.path.join(day_path,'PostProcessing','maxforce.csv')) as mf:
            max_forces_L.append(float(mf.readline())) #Double check the order of the hands.
            max_forces_R.append(float(mf.readline()))
        tmp_timeofday = pph.get_DATAfiles(day_path)[0][-8:-4]
        time_of_day.append(float(tmp_timeofday[0:2])+float(tmp_timeofday[2:])/60) #Defined as hours.
        (sleep_time, sleep_quality, bwalk, cardio, swim, wtrain, ot, what_ot) = pph.get_survey_answers(day_path)
        sleep_times.append(sleep_time)
        sleep_qualities.append(sleep_quality)
        physical_activity_matrix.append([bwalk, cardio, swim, wtrain, ot])
        #Make averages of performance measures and start building daily reports.
        #Daily report:
        # Maybe header with time of day, max force, composite sleep, and physical activity. 
        # 1. Sess averages
        # 2. Block averages
        # 3. Trial information within blocks (plus save number of trial successes for A and S)
        sess_ToT_asym_L = [[] for x in range(3)] #List of every value for the entire day. One per session.
        sess_ToT_asym_R = [[] for x in range(3)]
        sess_ToT_sym_L = [[] for x in range(3)]
        sess_ToT_sym_R = [[] for x in range(3)]
        sess_err_asym_L = [[] for x in range(3)]
        sess_err_asym_R = [[] for x in range(3)]
        sess_err_sym_L = [[] for x in range(3)]
        sess_err_sym_R = [[] for x in range(3)]
        sess_trialSuccess_asym_L = [[] for x in range(3)]
        sess_trialSuccess_asym_R = [[] for x in range(3)]
        sess_trialSuccess_sym_L = [[] for x in range(3)]
        sess_trialSuccess_sym_R = [[] for x in range(3)]
        sess_trialSuccess_asym_both = [[] for x in range(3)]
        sess_trialSuccess_sym_both = [[] for x in range(3)]
        sess_handsep_asym = [[] for x in range(3)] #Right now it's the sum of Right-Left, not absolute. Modify when necessary.
        sess_handsep_sym = [[] for x in range(3)]
        for sess_itr in range(3):
            sess_trial_data = pd.read_pickle(os.path.join(day_path,'PostProcessing','Trial_Behaviour_Sess_'+str(sess_itr+1)+'.pkl'))
            (A_blocks, S_blocks) = get_block_data(sess_trial_data)
            #Make the session-specific plots and save them in reports folder.
            block_ToT_asym_L = [[] for x in range(len(A_blocks))] #List of every value for the session. One row for every block, one element per trial.
            block_ToT_asym_R = [[] for x in range(len(A_blocks))]
            block_ToT_sym_L = [[] for x in range(len(S_blocks))]
            block_ToT_sym_R = [[] for x in range(len(S_blocks))]
            block_err_asym_L = [[] for x in range(len(A_blocks))]
            block_err_asym_R = [[] for x in range(len(A_blocks))]
            block_err_sym_L = [[] for x in range(len(S_blocks))]
            block_err_sym_R = [[] for x in range(len(S_blocks))]
            block_trialSuccess_asym_L = [[] for x in range(len(A_blocks))]
            block_trialSuccess_asym_R = [[] for x in range(len(A_blocks))]
            block_trialSuccess_sym_L = [[] for x in range(len(S_blocks))]
            block_trialSuccess_sym_R = [[] for x in range(len(S_blocks))]
            block_trialSuccess_asym_both = [[] for x in range(len(A_blocks))]
            block_trialSuccess_sym_both = [[] for x in range(len(S_blocks))]
            block_handsep_asym = [[] for x in range(len(A_blocks))] #Right now it's the sum of Right-Left, not absolute. Modify when necessary.
            block_handsep_sym = [[] for x in range(len(S_blocks))]
            block_condition_asym = [[] for x in range(len(A_blocks))]
            block_condition_sym = [[] for x in range(len(S_blocks))]
            
            #Build asymmetry data set
            for block_itr in range(len(A_blocks)): #This assumes equal number of blocks. 
                for trial_itr in range(len(A_blocks[block_itr])):
                    tmp_data = A_blocks[block_itr][trial_itr]
                    block_condition_asym[block_itr].append(tmp_data['condition'])
                    block_ToT_asym_L[block_itr].append(tmp_data['TimeOnTarget_L'])
                    block_ToT_asym_R[block_itr].append(tmp_data['TimeOnTarget_R'])
                    block_err_asym_L[block_itr].append(tmp_data['ACCtw_L'])
                    block_err_asym_R[block_itr].append(tmp_data['ACCtw_R'])
                    block_trialSuccess_asym_L[block_itr].append(tmp_data['trial_success_time_L']>0) #Only interested in the success or not. 
                    block_trialSuccess_asym_R[block_itr].append(tmp_data['trial_success_time_R']>0)
                    block_trialSuccess_asym_both[block_itr].append(tmp_data['trial_success_time_both']>0)
                    block_handsep_asym[block_itr].append(tmp_data['forcediff'])
            #Build symmetry dataset
            for block_itr in range(len(S_blocks)): #This assumes equal number of blocks. 
                for trial_itr in range(len(S_blocks[block_itr])):
                    tmp_data = S_blocks[block_itr][trial_itr]
                    block_condition_sym[block_itr].append(tmp_data['condition'])
                    block_ToT_sym_L[block_itr].append(tmp_data['TimeOnTarget_L'])
                    block_ToT_sym_R[block_itr].append(tmp_data['TimeOnTarget_R'])
                    block_err_sym_L[block_itr].append(tmp_data['ACCtw_L'])
                    block_err_sym_R[block_itr].append(tmp_data['ACCtw_R'])
                    block_trialSuccess_sym_L[block_itr].append(tmp_data['trial_success_time_L']>0) #Only interested in the success or not. 
                    block_trialSuccess_sym_R[block_itr].append(tmp_data['trial_success_time_R']>0)
                    block_trialSuccess_sym_both[block_itr].append(tmp_data['trial_success_time_both']>0)
                    block_handsep_sym[block_itr].append(tmp_data['forcediff'])
            #Make session-specific plots
            
            
            #Save session data in row of sess_ variables

        #Make the day-specific plots and report
        
    
    
    ##############Make weekly reports###################
    #if the number of training days is more than 1
    #ToT vs day plots (AsymL+R, SymL+R)
    #Error 500 ms vs day (AsymL+R, SymL+R)
    #Trial Successes vs day (AsymL+R+both, SymL+R+both)
    #Hand separation vs day (Asym, Sym)
    #ReactTime vs day plots (AsymL+R, SymL+R)
    #MaxForce vs day (L+R)
    #Time of day 
    #Sleep + sleep quality
    #PA table
    
    