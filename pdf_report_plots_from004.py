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
from matplotlib.font_manager import FontProperties
import numpy as np


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

def sess_plot(print_data, plot_cond, plot_yaxis, save_destination):
    #In the future, try to make color in bar chart depend on trial condition.
    #E.g. are all low ToT in A_L5R2?
    plt.ioff() # To not show all the plots all the time.
    col_names = ['Blocks']
    for block_itr in range(len(print_data)):
        print_data[block_itr].insert(0, 'Block '+str(block_itr+1))

    
    for trial_itr in range(len(print_data[0])-1):
        col_names.append('Trial_'+str(trial_itr+1))
        
    print_df = pd.DataFrame(print_data, columns=col_names)
    
    ax = print_df.plot(x='Blocks', kind='bar', stacked=False, grid=True, legend=False, fontsize=14, color='k')
    ax.set_xlabel('Block',fontsize=16, fontweight='bold')
    ax.set_ylabel(plot_yaxis,fontsize=16, fontweight='bold')
    ax.grid(axis='x')
    ax.set_title(plot_cond, fontsize=16, fontweight='bold')
    ax.figure.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.

def sess_trialsuccess_plot(print_data_both, print_data_L, print_data_R, plot_yaxis, plot_cond, save_destination):
    plt.ioff() # To not show all the plots all the time
    
    print_data = [[] for x in range(len(print_data_both))]
    col_names = ['Blocks', 'L', 'R', 'L&R']
    for block_itr in range(len(print_data_both)):
        print_data[block_itr] = ['Block '+str(block_itr+1), 100*sum(print_data_L[block_itr])/len(print_data_L[block_itr]), \
                                 100*sum(print_data_R[block_itr])/len(print_data_R[block_itr]), 100*sum(print_data_both[block_itr])/len(print_data_both[block_itr])]

    print_df = pd.DataFrame(print_data, columns=col_names)
    
    ax = print_df.plot(x='Blocks', kind='bar', stacked=False, grid=False, legend=True, fontsize=14, colormap='tab20') #Good for colorblind
    ax.set_xlabel('Block',fontsize=16, fontweight='bold')
    ax.set_ylabel(plot_yaxis,fontsize=16, fontweight='bold')
    ax.grid(axis='y')
    ax.set_title(plot_cond, fontsize=16, fontweight='bold')
    ax.figure.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.
    
def tot_succ_plot(print_data_both, print_data_both_std, print_data_L, print_data_L_std, print_data_R, print_data_R_std, plot_yaxis, plot_title, save_destination, game_levels):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(print_data_both))
    width=0.15
    fig, ax = plt.subplots()
    ax.bar(x_pos-width*1.5, print_data_L, width=width, yerr=print_data_L_std, label='Left', color='navy')    
    ax.bar(x_pos, print_data_R, width=width, yerr=print_data_R_std, label='Right', color='goldenrod')
    ax.bar(x_pos+width*1.5, print_data_both, width=width, yerr=print_data_both_std, label='Both', color='seagreen')
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    ax.set_xticks(x_pos)
    xlab = []
    for trday_itr in range(len(print_data_both)):
        xlab.append('Training Day '+str(trday_itr+1))
    ax.set_xticklabels(xlab, fontsize=16, fontweight='bold', rotation=45, ha='right')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    if len(game_levels) > 1:
        ax2 = ax.twiny()
        ax2.set_xticks(x_pos)
        xlab_2 = []
        for level_itr in range(len(game_levels)):
            xlab_2.append('GL '+str(game_levels[level_itr]))
        ax2.set_xticklabels(xlab_2, rotation=45, ha='right')
    
    ax.yaxis.grid(True)
    ax.legend()
    
    fig.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.

def day_trialsuccess_plot(print_data_both, print_data_both_std, print_data_L, print_data_L_std, print_data_R, print_data_R_std, plot_yaxis, plot_title, save_destination):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(print_data_both))
    width=0.15
    fig, ax = plt.subplots()
    ax.bar(x_pos-width*1.5, print_data_L, width=width, yerr=print_data_L_std, label='Left', color='navy')    
    ax.bar(x_pos, print_data_R, width=width, yerr=print_data_R_std, label='Right', color='goldenrod')
    ax.bar(x_pos+width*1.5, print_data_both, width=width, yerr=print_data_both_std, label='Both', color='seagreen')
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Session 1', 'Session 2', 'Session 3'], fontsize=16, fontweight='bold')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    ax.yaxis.grid(True)
    ax.legend()
    
    fig.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.


def day_handsep_plot(print_data_means, print_data_std, plot_yaxis, plot_title, save_destination):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(print_data_means))
    fig, ax = plt.subplots()
    ax.bar(x_pos, print_data_means, yerr=print_data_std, color='darkgrey')
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Session 1', 'Session 2', 'Session 3'], fontsize=16, fontweight='bold')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    ax.yaxis.grid(True)
    
    fig.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.

def tot_handsep_plot(print_data_means, print_data_std, plot_yaxis, plot_title, save_destination, game_levels):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(print_data_means))
    fig, ax = plt.subplots()
    ax.bar(x_pos, print_data_means, yerr=print_data_std, color='darkgrey')
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    ax.set_xticks(x_pos)
    xlab = []
    for trday_itr in range(len(print_data_means)):
        xlab.append('Training Day '+str(trday_itr+1))
    ax.set_xticklabels(xlab, fontsize=16, fontweight='bold', rotation=45, ha='right')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    if len(game_levels) > 1:
        ax2 = ax.twiny()
        ax2.set_xticks(x_pos)
        xlab_2 = []
        for level_itr in range(len(game_levels)):
            xlab_2.append('GL '+str(game_levels[level_itr]))
        ax2.set_xticklabels(xlab_2, rotation=45, ha='right')
    
    ax.yaxis.grid(True)
    
    fig.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.

def day_plot(print_data_means_L, print_data_std_L, print_data_means_R, print_data_std_R, plot_yaxis, plot_title, save_destination):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(print_data_means_L))
    width=0.15
    fig, ax = plt.subplots()
    ax.bar(x_pos-width, print_data_means_L, width=width, yerr=print_data_std_L, label='Left', color='navy')
    ax.bar(x_pos+width, print_data_means_R, width=width, yerr=print_data_std_R, label='Right', color='goldenrod')
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Session 1', 'Session 2', 'Session 3'], fontsize=16, fontweight='bold')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    ax.yaxis.grid(True)
    ax.legend()
    
    fig.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.

def tot_plot(print_data_means_L, print_data_std_L, print_data_means_R, print_data_std_R, plot_yaxis, plot_title, save_destination, game_levels):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(print_data_means_L))
    width=0.15
    fig, ax = plt.subplots()
    ax.bar(x_pos-width, print_data_means_L, width=width, yerr=print_data_std_L, label='Left', color='navy')
    ax.bar(x_pos+width, print_data_means_R, width=width, yerr=print_data_std_R, label='Right', color='goldenrod')
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    ax.set_xticks(x_pos)
    xlab = []
    for trday_itr in range(len(print_data_means_L)):
        xlab.append('Training Day '+str(trday_itr+1))
    ax.set_xticklabels(xlab, fontsize=16, fontweight='bold', rotation=45, ha='right')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    
    if len(game_levels) > 1:
        ax2 = ax.twiny()
        ax2.set_xticks(x_pos)
        xlab_2 = []
        for level_itr in range(len(game_levels)):
            xlab_2.append('GL '+str(game_levels[level_itr]))
        ax2.set_xticklabels(xlab_2, rotation=45, ha='right')
    
    ax.yaxis.grid(True)
    ax.legend()
    
    fig.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.
    
##############Set paths and plot options###################
#Change to where you have your data.
path='/Users/gdf724/Data/ReScale/HomeTrainingTest/' 
#List all subjects to process.
list_of_subjs=['P004']
report_dir='/Users/gdf724/Data/ReScale/HomeTrainingTest/Reports'

overwrite = True

##############Make daily reports and build averages###################
for subj in list_of_subjs:
    HT_days = pph.get_HTfolders(path, subj)
    max_forces_L=[] 
    max_forces_R=[]
    time_of_day=[]
    sleep_times=[]
    sleep_qualities=[]
    game_levels=[]
    physical_activity_matrix=[]
    pa_rows = ['Training day %d' % x for x in range(1,len(HT_days)+1)]
    pa_columns = ('Brisk walk', 'Cardio', 'Swimming', 'Weight training', 'Other')
    
    ToT_asym_L_12 = [None]*len(HT_days) #One value per day
    ToT_asym_R_12 = [None]*len(HT_days)
    ToT_sym_L_12 = [None]*len(HT_days)
    ToT_sym_R_12 = [None]*len(HT_days)
    err_asym_L_12 = [None]*len(HT_days)
    err_asym_R_12 = [None]*len(HT_days)
    err_sym_L_12 = [None]*len(HT_days)
    err_sym_R_12 = [None]*len(HT_days)
    trialSuccess_asym_L_12 = [None]*len(HT_days)
    trialSuccess_asym_R_12 = [None]*len(HT_days)
    trialSuccess_sym_L_12 = [None]*len(HT_days)
    trialSuccess_sym_R_12 = [None]*len(HT_days)
    trialSuccess_asym_both_12 = [None]*len(HT_days)
    trialSuccess_sym_both_12 = [None]*len(HT_days)
    handsep_asym_12 = [None]*len(HT_days) 
    handsep_sym_12 = [None]*len(HT_days)
    ToT_asym_L_12_std = [None]*len(HT_days) #One value per day
    ToT_asym_R_12_std = [None]*len(HT_days)
    ToT_sym_L_12_std = [None]*len(HT_days)
    ToT_sym_R_12_std = [None]*len(HT_days)
    err_asym_L_12_std = [None]*len(HT_days)
    err_asym_R_12_std = [None]*len(HT_days)
    err_sym_L_12_std = [None]*len(HT_days)
    err_sym_R_12_std = [None]*len(HT_days)
    trialSuccess_asym_L_12_std = [None]*len(HT_days)
    trialSuccess_asym_R_12_std = [None]*len(HT_days)
    trialSuccess_sym_L_12_std = [None]*len(HT_days)
    trialSuccess_sym_R_12_std = [None]*len(HT_days)
    trialSuccess_asym_both_12_std = [None]*len(HT_days)
    trialSuccess_sym_both_12_std = [None]*len(HT_days)
    handsep_asym_12_std = [None]*len(HT_days)
    handsep_sym_12_std = [None]*len(HT_days)
    
    ToT_asym_L_3 = [None]*len(HT_days) #One value per day
    ToT_asym_R_3 = [None]*len(HT_days)
    ToT_sym_L_3 = [None]*len(HT_days)
    ToT_sym_R_3 = [None]*len(HT_days)
    err_asym_L_3 = [None]*len(HT_days)
    err_asym_R_3 = [None]*len(HT_days)
    err_sym_L_3 = [None]*len(HT_days)
    err_sym_R_3 = [None]*len(HT_days)
    trialSuccess_asym_L_3 = [None]*len(HT_days)
    trialSuccess_asym_R_3 = [None]*len(HT_days)
    trialSuccess_sym_L_3 = [None]*len(HT_days)
    trialSuccess_sym_R_3 = [None]*len(HT_days)
    trialSuccess_asym_both_3 = [None]*len(HT_days)
    trialSuccess_sym_both_3 = [None]*len(HT_days)
    handsep_asym_3 = [None]*len(HT_days) 
    handsep_sym_3 = [None]*len(HT_days)
    ToT_asym_L_3_std = [None]*len(HT_days) #One value per day
    ToT_asym_R_3_std = [None]*len(HT_days)
    ToT_sym_L_3_std = [None]*len(HT_days)
    ToT_sym_R_3_std = [None]*len(HT_days)
    err_asym_L_3_std = [None]*len(HT_days)
    err_asym_R_3_std = [None]*len(HT_days)
    err_sym_L_3_std = [None]*len(HT_days)
    err_sym_R_3_std = [None]*len(HT_days)
    trialSuccess_asym_L_3_std = [None]*len(HT_days)
    trialSuccess_asym_R_3_std = [None]*len(HT_days)
    trialSuccess_sym_L_3_std = [None]*len(HT_days)
    trialSuccess_sym_R_3_std = [None]*len(HT_days)
    trialSuccess_asym_both_3_std = [None]*len(HT_days)
    trialSuccess_sym_both_3_std = [None]*len(HT_days)
    handsep_asym_3_std = [None]*len(HT_days)
    handsep_sym_3_std = [None]*len(HT_days)
    
    
    #Make subject dir
    if not os.path.exists(os.path.join(report_dir,subj)):
        os.makedirs(os.path.join(report_dir,subj))
    
    for day_itr in range(len(HT_days)): #Check if it's not already done and if overwrite is false
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
        physical_activity_matrix.append([str(day_itr+1), bwalk, cardio, swim, wtrain, ot])
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
        sess_handsep_asym = [[] for x in range(3)] 
        sess_handsep_sym = [[] for x in range(3)]
        sess_std_ToT_asym_L = [[] for x in range(3)] #List of every value for the entire day. One per session.
        sess_std_ToT_asym_R = [[] for x in range(3)]
        sess_std_ToT_sym_L = [[] for x in range(3)]
        sess_std_ToT_sym_R = [[] for x in range(3)]
        sess_std_err_asym_L = [[] for x in range(3)]
        sess_std_err_asym_R = [[] for x in range(3)]
        sess_std_err_sym_L = [[] for x in range(3)]
        sess_std_err_sym_R = [[] for x in range(3)]
        sess_std_trialSuccess_asym_L = [[] for x in range(3)]
        sess_std_trialSuccess_asym_R = [[] for x in range(3)]
        sess_std_trialSuccess_sym_L = [[] for x in range(3)]
        sess_std_trialSuccess_sym_R = [[] for x in range(3)]
        sess_std_trialSuccess_asym_both = [[] for x in range(3)]
        sess_std_trialSuccess_sym_both = [[] for x in range(3)]
        sess_std_handsep_asym = [[] for x in range(3)] 
        sess_std_handsep_sym = [[] for x in range(3)]
        for sess_itr in range(3):
            sess_trial_data = pd.read_pickle(os.path.join(day_path,'PostProcessing','Trial_Behaviour_Sess_'+str(sess_itr+1)+'.pkl'))
            if sess_itr == 0:
                tmp_gmlvl = sess_trial_data['gamelevel']
                game_levels.append(tmp_gmlvl[0])
            
            (A_blocks, S_blocks) = get_block_data(sess_trial_data)
            
            #Make the session-specific plots and save them in reports folder.
            block_ToT_asym_L = [[] for x in range(len(A_blocks))] 
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
            block_handsep_asym = [[] for x in range(len(A_blocks))] 
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
                block_trialSuccess_asym_L[block_itr] = list(map(int,block_trialSuccess_asym_L[block_itr]))
                block_trialSuccess_asym_R[block_itr] = list(map(int,block_trialSuccess_asym_R[block_itr]))
                block_trialSuccess_asym_both[block_itr] = list(map(int,block_trialSuccess_asym_both[block_itr]))
            #Build symmetry dataset
            for block_itr in range(len(S_blocks)): #This assumes equal number of blocks. 
                for trial_itr in range(len(S_blocks[block_itr])):
                    tmp_data = S_blocks[block_itr][trial_itr]
                    block_condition_sym[block_itr].append(tmp_data['condition'])
                    block_ToT_sym_L[block_itr].append(tmp_data['TimeOnTarget_L'])
                    block_ToT_sym_R[block_itr].append(tmp_data['TimeOnTarget_R'])
                    block_err_sym_L[block_itr].append(tmp_data['ACCtw_L'])
                    block_err_sym_R[block_itr].append(tmp_data['ACCtw_R'])
                    block_trialSuccess_sym_L[block_itr].append(tmp_data['trial_success_time_L']>0) #Only interested in the success or not. But better as int. 
                    block_trialSuccess_sym_R[block_itr].append(tmp_data['trial_success_time_R']>0)
                    block_trialSuccess_sym_both[block_itr].append(tmp_data['trial_success_time_both']>0)
                    block_handsep_sym[block_itr].append(tmp_data['forcediff'])
                block_trialSuccess_sym_L[block_itr] = list(map(int,block_trialSuccess_sym_L[block_itr]))
                block_trialSuccess_sym_R[block_itr] = list(map(int,block_trialSuccess_sym_R[block_itr]))
                block_trialSuccess_sym_both[block_itr] = list(map(int,block_trialSuccess_sym_both[block_itr]))
            #Make session-specific plots
            ##ToT
            if not os.path.exists(os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_A_L.png')) or overwrite:
                #Make one then make a function for it.
                sess_plot([element*100 for element in block_ToT_asym_L], 'Time on Target for Asymmetric conditions\nLeft Hand Level'+str(game_levels[-1]), \
                          'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_A_L.png'))
                sess_plot([element*100 for element in block_ToT_asym_R], 'Time on Target for Asymmetric conditions\nRight Hand Level'+str(game_levels[-1]), \
                          'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_A_R.png'))
                sess_plot([element*100 for element in block_ToT_sym_L], 'Time on Target for Symmetric conditions\nLeft Hand Level'+str(game_levels[-1]), \
                          'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_S_L.png'))
                sess_plot([element*100 for element in block_ToT_sym_R], 'Time on Target for Symmetric conditions\nRight Hand Level'+str(game_levels[-1]), \
                          'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_S_R.png'))
                        
                ##Error last 500 ms
                sess_plot([x[:] for x in block_err_asym_L], 'Error last 500 ms for Asymmetric conditions\nLeft Hand Level'+str(game_levels[-1]), \
                          'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_A_L.png'))
                sess_plot([x[:] for x in block_err_asym_R], 'Error last 500 ms for Asymmetric conditions\nRight Hand Level'+str(game_levels[-1]), \
                          'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_A_R.png'))
                sess_plot([x[:] for x in block_err_sym_L], 'Error last 500 ms for Symmetric conditions\nLeft Hand Level'+str(game_levels[-1]), \
                          'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_S_L.png'))
                sess_plot([x[:] for x in block_err_sym_R], 'Error last 500 ms for Symmetric conditions\nRight Hand Level'+str(game_levels[-1]), \
                          'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_S_R.png'))
                
                ##Stable for 200 ms success
                sess_trialsuccess_plot(block_trialSuccess_sym_both, block_trialSuccess_sym_L, block_trialSuccess_sym_R, \
                                        'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Symmetric conditions Level'+str(game_levels[-1]), os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Succ_S.png'))
                sess_trialsuccess_plot(block_trialSuccess_asym_both, block_trialSuccess_asym_L, block_trialSuccess_asym_R, \
                                        'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Asymmetric conditions Level'+str(game_levels[-1]), os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Succ_A.png'))
                
                ##Hand separation
                sess_plot([x[:] for x in block_handsep_asym], 'Absolute force difference between hands\nAsymmetric conditions Level'+str(game_levels[-1]), \
                          'Force difference', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_HandSep_A.png'))
                sess_plot([x[:] for x in block_handsep_sym], 'Absolute force difference between hands\nSymmetric condition Level'+str(game_levels[-1]), \
                          'Force difference', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_HandSep_S.png'))
                
            
            #Save session data in row of sess_ variables + sd to make error bars. Average between blocks.
            sess_ToT_asym_L[sess_itr] = np.mean(np.asarray(block_ToT_asym_L))
            sess_std_ToT_asym_L[sess_itr] = np.std(np.asarray(block_ToT_asym_L))
            sess_ToT_asym_R[sess_itr] = np.mean(np.asarray(block_ToT_asym_R))
            sess_std_ToT_asym_R[sess_itr] = np.std(np.asarray(block_ToT_asym_R))
            sess_ToT_sym_L[sess_itr] = np.mean(np.asarray(block_ToT_sym_L))
            sess_std_ToT_sym_L[sess_itr] = np.std(np.asarray(block_ToT_sym_L))
            sess_ToT_sym_R[sess_itr] = np.mean(np.asarray(block_ToT_sym_R))
            sess_std_ToT_sym_R[sess_itr] = np.std(np.asarray(block_ToT_sym_R))
            sess_err_asym_L[sess_itr] = np.mean(np.asarray(block_err_asym_L))
            sess_std_err_asym_L[sess_itr] = np.std(np.asarray(block_err_asym_L))
            sess_err_asym_R[sess_itr] = np.mean(np.asarray(block_err_asym_R))
            sess_std_err_asym_R[sess_itr] = np.std(np.asarray(block_err_asym_R))
            sess_err_sym_L[sess_itr] = np.mean(np.asarray(block_err_sym_L))
            sess_std_err_sym_L[sess_itr] = np.std(np.asarray(block_err_sym_L))
            sess_err_sym_R[sess_itr] = np.mean(np.asarray(block_err_sym_R))
            sess_std_err_sym_R[sess_itr] = np.std(np.asarray(block_err_sym_R))
            sess_trialSuccess_asym_L[sess_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_asym_L[0])/len(block_trialSuccess_asym_L[0]), 100*sum(block_trialSuccess_asym_L[1])/len(block_trialSuccess_asym_L[1]), 100*sum(block_trialSuccess_asym_L[2])/len(block_trialSuccess_asym_L[2])]))
            sess_std_trialSuccess_asym_L[sess_itr] = np.std(np.asarray([100*sum(block_trialSuccess_asym_L[0])/len(block_trialSuccess_asym_L[0]), 100*sum(block_trialSuccess_asym_L[1])/len(block_trialSuccess_asym_L[1]), 100*sum(block_trialSuccess_asym_L[2])/len(block_trialSuccess_asym_L[2])]))
            sess_trialSuccess_asym_R[sess_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_asym_R[0])/len(block_trialSuccess_asym_R[0]), 100*sum(block_trialSuccess_asym_R[1])/len(block_trialSuccess_asym_R[1]), 100*sum(block_trialSuccess_asym_R[2])/len(block_trialSuccess_asym_R[2])]))
            sess_std_trialSuccess_asym_R[sess_itr] = np.std(np.asarray([100*sum(block_trialSuccess_asym_R[0])/len(block_trialSuccess_asym_R[0]), 100*sum(block_trialSuccess_asym_R[1])/len(block_trialSuccess_asym_R[1]), 100*sum(block_trialSuccess_asym_R[2])/len(block_trialSuccess_asym_R[2])]))
            sess_trialSuccess_sym_L[sess_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_sym_L[0])/len(block_trialSuccess_sym_L[0]), 100*sum(block_trialSuccess_sym_L[1])/len(block_trialSuccess_sym_L[1]), 100*sum(block_trialSuccess_sym_L[2])/len(block_trialSuccess_sym_L[2])]))
            sess_std_trialSuccess_sym_L[sess_itr] = np.std(np.asarray([100*sum(block_trialSuccess_sym_L[0])/len(block_trialSuccess_sym_L[0]), 100*sum(block_trialSuccess_sym_L[1])/len(block_trialSuccess_sym_L[1]), 100*sum(block_trialSuccess_sym_L[2])/len(block_trialSuccess_sym_L[2])]))
            sess_trialSuccess_sym_R[sess_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_sym_R[0])/len(block_trialSuccess_sym_R[0]), 100*sum(block_trialSuccess_sym_R[1])/len(block_trialSuccess_sym_R[1]), 100*sum(block_trialSuccess_sym_R[2])/len(block_trialSuccess_sym_R[2])]))
            sess_std_trialSuccess_sym_R[sess_itr] = np.std(np.asarray([100*sum(block_trialSuccess_sym_R[0])/len(block_trialSuccess_sym_R[0]), 100*sum(block_trialSuccess_sym_R[1])/len(block_trialSuccess_sym_R[1]), 100*sum(block_trialSuccess_sym_R[2])/len(block_trialSuccess_sym_R[2])]))
            sess_trialSuccess_asym_both[sess_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_asym_both[0])/len(block_trialSuccess_asym_both[0]), 100*sum(block_trialSuccess_asym_both[1])/len(block_trialSuccess_asym_both[1]), 100*sum(block_trialSuccess_asym_both[2])/len(block_trialSuccess_asym_both[2])]))
            sess_std_trialSuccess_asym_both[sess_itr] = np.std(np.asarray([100*sum(block_trialSuccess_asym_both[0])/len(block_trialSuccess_asym_both[0]), 100*sum(block_trialSuccess_asym_both[1])/len(block_trialSuccess_asym_both[1]), 100*sum(block_trialSuccess_asym_both[2])/len(block_trialSuccess_asym_both[2])]))
            sess_trialSuccess_sym_both[sess_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_sym_both[0])/len(block_trialSuccess_sym_both[0]), 100*sum(block_trialSuccess_sym_both[1])/len(block_trialSuccess_sym_both[1]), 100*sum(block_trialSuccess_sym_both[2])/len(block_trialSuccess_sym_both[2])]))
            sess_std_trialSuccess_sym_both[sess_itr] = np.std(np.asarray([100*sum(block_trialSuccess_sym_both[0])/len(block_trialSuccess_sym_both[0]), 100*sum(block_trialSuccess_sym_both[1])/len(block_trialSuccess_sym_both[1]), 100*sum(block_trialSuccess_sym_both[2])/len(block_trialSuccess_sym_both[2])]))
            sess_handsep_asym[sess_itr] = np.mean(np.asarray(block_handsep_asym))
            sess_std_handsep_asym[sess_itr] = np.std(np.asarray(block_handsep_asym))
            sess_handsep_sym[sess_itr] = np.mean(np.asarray(block_handsep_sym))
            sess_std_handsep_sym[sess_itr] = np.std(np.asarray(block_handsep_sym))
            if sess_itr==2:
                ToT_asym_L_3[day_itr] = np.mean(np.asarray(block_ToT_asym_L)) #One value per day
                ToT_asym_R_3[day_itr] = np.mean(np.asarray(block_ToT_asym_R))
                ToT_sym_L_3[day_itr] = np.mean(np.asarray(block_ToT_sym_L))
                ToT_sym_R_3[day_itr] = np.mean(np.asarray(block_ToT_sym_R))
                err_asym_L_3[day_itr] = np.mean(np.asarray(block_err_asym_L))
                err_asym_R_3[day_itr] = np.mean(np.asarray(block_err_asym_R))
                err_sym_L_3[day_itr] = np.mean(np.asarray(block_err_sym_L))
                err_sym_R_3[day_itr] = np.mean(np.asarray(block_err_sym_R))
                trialSuccess_asym_L_3[day_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_asym_L[0])/len(block_trialSuccess_asym_L[0]), 100*sum(block_trialSuccess_asym_L[1])/len(block_trialSuccess_asym_L[1]), 100*sum(block_trialSuccess_asym_L[2])/len(block_trialSuccess_asym_L[2])]))
                trialSuccess_asym_R_3[day_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_asym_R[0])/len(block_trialSuccess_asym_R[0]), 100*sum(block_trialSuccess_asym_R[1])/len(block_trialSuccess_asym_R[1]), 100*sum(block_trialSuccess_asym_R[2])/len(block_trialSuccess_asym_R[2])]))
                trialSuccess_sym_L_3[day_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_sym_L[0])/len(block_trialSuccess_sym_L[0]), 100*sum(block_trialSuccess_sym_L[1])/len(block_trialSuccess_sym_L[1]), 100*sum(block_trialSuccess_sym_L[2])/len(block_trialSuccess_sym_L[2])]))
                trialSuccess_sym_R_3[day_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_sym_R[0])/len(block_trialSuccess_sym_R[0]), 100*sum(block_trialSuccess_sym_R[1])/len(block_trialSuccess_sym_R[1]), 100*sum(block_trialSuccess_sym_R[2])/len(block_trialSuccess_sym_R[2])]))
                trialSuccess_asym_both_3[day_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_asym_both[0])/len(block_trialSuccess_asym_both[0]), 100*sum(block_trialSuccess_asym_both[1])/len(block_trialSuccess_asym_both[1]), 100*sum(block_trialSuccess_asym_both[2])/len(block_trialSuccess_asym_both[2])]))
                trialSuccess_sym_both_3[day_itr] = np.mean(np.asarray([100*sum(block_trialSuccess_sym_both[0])/len(block_trialSuccess_sym_both[0]), 100*sum(block_trialSuccess_sym_both[1])/len(block_trialSuccess_sym_both[1]), 100*sum(block_trialSuccess_sym_both[2])/len(block_trialSuccess_sym_both[2])]))
                handsep_asym_3[day_itr] = np.mean(np.asarray(block_handsep_asym))
                handsep_sym_3[day_itr] = np.mean(np.asarray(block_handsep_sym))
                ToT_asym_L_3_std[day_itr] = np.std(np.asarray(block_ToT_asym_L)) #One value per day
                ToT_asym_R_3_std[day_itr] = np.std(np.asarray(block_ToT_asym_R))
                ToT_sym_L_3_std[day_itr] = np.std(np.asarray(block_ToT_sym_L))
                ToT_sym_R_3_std[day_itr] = np.std(np.asarray(block_ToT_sym_R))
                err_asym_L_3_std[day_itr] = np.std(np.asarray(block_err_asym_L))
                err_asym_R_3_std[day_itr] = np.std(np.asarray(block_err_asym_R))
                err_sym_L_3_std[day_itr] = np.std(np.asarray(block_err_sym_L))
                err_sym_R_3_std[day_itr] = np.std(np.asarray(block_err_sym_R))
                trialSuccess_asym_L_3_std[day_itr] = np.std(np.asarray([100*sum(block_trialSuccess_asym_L[0])/len(block_trialSuccess_asym_L[0]), 100*sum(block_trialSuccess_asym_L[1])/len(block_trialSuccess_asym_L[1]), 100*sum(block_trialSuccess_asym_L[2])/len(block_trialSuccess_asym_L[2])]))
                trialSuccess_asym_R_3_std[day_itr] = np.std(np.asarray([100*sum(block_trialSuccess_asym_R[0])/len(block_trialSuccess_asym_R[0]), 100*sum(block_trialSuccess_asym_R[1])/len(block_trialSuccess_asym_R[1]), 100*sum(block_trialSuccess_asym_R[2])/len(block_trialSuccess_asym_R[2])]))
                trialSuccess_sym_L_3_std[day_itr] = np.std(np.asarray([100*sum(block_trialSuccess_sym_L[0])/len(block_trialSuccess_sym_L[0]), 100*sum(block_trialSuccess_sym_L[1])/len(block_trialSuccess_sym_L[1]), 100*sum(block_trialSuccess_sym_L[2])/len(block_trialSuccess_sym_L[2])]))
                trialSuccess_sym_R_3_std[day_itr] = np.std(np.asarray([100*sum(block_trialSuccess_sym_R[0])/len(block_trialSuccess_sym_R[0]), 100*sum(block_trialSuccess_sym_R[1])/len(block_trialSuccess_sym_R[1]), 100*sum(block_trialSuccess_sym_R[2])/len(block_trialSuccess_sym_R[2])]))
                trialSuccess_asym_both_3_std[day_itr] = np.std(np.asarray([100*sum(block_trialSuccess_asym_both[0])/len(block_trialSuccess_asym_both[0]), 100*sum(block_trialSuccess_asym_both[1])/len(block_trialSuccess_asym_both[1]), 100*sum(block_trialSuccess_asym_both[2])/len(block_trialSuccess_asym_both[2])]))
                trialSuccess_sym_both_3_std[day_itr] = np.std(np.asarray([100*sum(block_trialSuccess_sym_both[0])/len(block_trialSuccess_sym_both[0]), 100*sum(block_trialSuccess_sym_both[1])/len(block_trialSuccess_sym_both[1]), 100*sum(block_trialSuccess_sym_both[2])/len(block_trialSuccess_sym_both[2])]))
                handsep_asym_3_std[day_itr] = np.std(np.asarray(block_handsep_asym))
                handsep_sym_3_std[day_itr] = np.std(np.asarray(block_handsep_sym))
            #Make the day-specific plots and report and use the session values.
            ##ToT
        if not os.path.exists(os.path.join(day_save_folder,'Day_Succ_A.png')) or overwrite:
            day_plot([100*x for x in sess_ToT_asym_L], [100*x for x in sess_std_ToT_asym_L], [100*x for x in sess_ToT_asym_R], [100*x for x in sess_std_ToT_asym_R], 'Time on target /\n% of trial time', 'Time on Target for Asymmetric conditions\nLevel '+str(game_levels[-1]), os.path.join(day_save_folder,'Day_ToT_A.png'))
            day_plot([100*x for x in sess_ToT_sym_L], [100*x for x in sess_std_ToT_sym_L], [100*x for x in sess_ToT_sym_R], [100*x for x in sess_std_ToT_sym_R], 'Time on target /\n% of trial time', 'Time on Target for Symmetric conditions\nLevel '+str(game_levels[-1]), os.path.join(day_save_folder,'Day_ToT_S.png'))
            
            ##Err
            day_plot([x for x in sess_err_asym_L], [x for x in sess_std_err_asym_L], [x for x in sess_err_asym_R], [x for x in sess_std_err_asym_R], 'Error', 'Error last 500 ms for Asymmetric conditions\nLevel '+str(game_levels[-1]), os.path.join(day_save_folder,'Day_Err_A.png'))
            day_plot([x for x in sess_err_sym_L], [x for x in sess_std_err_sym_L], [x for x in sess_err_sym_R], [x for x in sess_std_err_sym_R], 'Error', 'Error last 500 ms for Symmetric conditions\nLevel '+str(game_levels[-1]), os.path.join(day_save_folder,'Day_Err_S.png'))
            
            ##Trial Successes, maybe only both relevant
            day_trialsuccess_plot([x for x in sess_trialSuccess_asym_both], [x for x in sess_std_trialSuccess_asym_both], [x for x in sess_trialSuccess_asym_L], [x for x in sess_std_trialSuccess_asym_L], [x for x in sess_trialSuccess_asym_R], [x for x in sess_std_trialSuccess_asym_R], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 300 ms)\nin Asymmetric conditions Level '+str(game_levels[-1]), os.path.join(day_save_folder,'Day_Succ_A.png'))
            day_trialsuccess_plot([x for x in sess_trialSuccess_sym_both], [x for x in sess_std_trialSuccess_sym_both], [x for x in sess_trialSuccess_sym_L], [x for x in sess_std_trialSuccess_sym_L], [x for x in sess_trialSuccess_sym_R], [x for x in sess_std_trialSuccess_sym_R], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 300 ms)\nin Symmetric conditions Level '+str(game_levels[-1]), os.path.join(day_save_folder,'Day_Succ_S.png'))
            
            ##handsep
            day_handsep_plot([x for x in sess_handsep_asym], [x for x in sess_std_handsep_asym], 'Force difference', 'Absolute force difference between hands\nAsymmetric condition Level '+str(game_levels[-1]), os.path.join(day_save_folder,'Day_HandSep_A.png'))
            day_handsep_plot([x for x in sess_handsep_sym], [x for x in sess_std_handsep_sym], 'Force difference', 'Absolute force difference between hands\nSymmetric condition Level '+str(game_levels[-1]), os.path.join(day_save_folder,'Day_HandSep_S.png'))
            
        #Save daily measurement + std
        #Standard deviation between blocks. If interested in standard deviation within blocks, one needs to look at the daily plots. 
         
        ToT_asym_L_12[day_itr] = np.mean(np.asarray(sess_ToT_asym_L[0:2])) #One value per day
        ToT_asym_R_12[day_itr] = np.mean(np.asarray(sess_ToT_asym_R[0:2]))
        ToT_sym_L_12[day_itr] = np.mean(np.asarray(sess_ToT_sym_L[0:2]))
        ToT_sym_R_12[day_itr] = np.mean(np.asarray(sess_ToT_sym_R[0:2]))
        err_asym_L_12[day_itr] = np.mean(np.asarray(sess_err_asym_L[0:2]))
        err_asym_R_12[day_itr] = np.mean(np.asarray(sess_err_asym_R[0:2]))
        err_sym_L_12[day_itr] = np.mean(np.asarray(sess_err_sym_L[0:2]))
        err_sym_R_12[day_itr] = np.mean(np.asarray(sess_err_sym_R[0:2]))
        trialSuccess_asym_L_12[day_itr] = np.mean(np.asarray(sess_trialSuccess_asym_L[0:2]))
        trialSuccess_asym_R_12[day_itr] = np.mean(np.asarray(sess_trialSuccess_asym_R[0:2]))
        trialSuccess_sym_L_12[day_itr] = np.mean(np.asarray(sess_trialSuccess_sym_L[0:2]))
        trialSuccess_sym_R_12[day_itr] = np.mean(np.asarray(sess_trialSuccess_sym_R[0:2]))
        trialSuccess_asym_both_12[day_itr] = np.mean(np.asarray(sess_trialSuccess_asym_both[0:2]))
        trialSuccess_sym_both_12[day_itr] = np.mean(np.asarray(sess_trialSuccess_sym_both[0:2]))
        handsep_asym_12[day_itr] = np.mean(np.asarray(sess_handsep_asym[0:2]))
        handsep_sym_12[day_itr] = np.mean(np.asarray(sess_handsep_sym[0:2]))
        ToT_asym_L_12_std[day_itr] = np.std(np.asarray(sess_ToT_asym_L[0:2])) #One value per day
        ToT_asym_R_12_std[day_itr] = np.std(np.asarray(sess_ToT_asym_R[0:2]))
        ToT_sym_L_12_std[day_itr] = np.std(np.asarray(sess_ToT_sym_L[0:2]))
        ToT_sym_R_12_std[day_itr] = np.std(np.asarray(sess_ToT_sym_R[0:2]))
        err_asym_L_12_std[day_itr] = np.std(np.asarray(sess_err_asym_L[0:2]))
        err_asym_R_12_std[day_itr] = np.std(np.asarray(sess_err_asym_R[0:2]))
        err_sym_L_12_std[day_itr] = np.std(np.asarray(sess_err_sym_L[0:2]))
        err_sym_R_12_std[day_itr] = np.std(np.asarray(sess_err_sym_R[0:2]))
        trialSuccess_asym_L_12_std[day_itr] = np.std(np.asarray(sess_trialSuccess_asym_L[0:2]))
        trialSuccess_asym_R_12_std[day_itr] = np.std(np.asarray(sess_trialSuccess_asym_R[0:2]))
        trialSuccess_sym_L_12_std[day_itr] = np.std(np.asarray(sess_trialSuccess_sym_L[0:2]))
        trialSuccess_sym_R_12_std[day_itr] = np.std(np.asarray(sess_trialSuccess_sym_R[0:2]))
        trialSuccess_asym_both_12_std[day_itr] = np.std(np.asarray(sess_trialSuccess_asym_both[0:2]))
        trialSuccess_sym_both_12_std[day_itr] = np.std(np.asarray(sess_trialSuccess_sym_both[0:2]))
        handsep_asym_12_std[day_itr] = np.std(np.asarray(sess_handsep_asym[0:2]))
        handsep_sym_12_std[day_itr] = np.std(np.asarray(sess_handsep_sym[0:2]))

        
    ##############Make weekly plots###################
    #if the number of training days is more than 1
    #From P004 and onward, split into sessions1+2 and session 3. 
    #ToT vs day plots (AsymL+R, SymL+R)
    #Error 500 ms vs day (AsymL+R, SymL+R)
    #Trial Successes vs day (AsymL+R+both, SymL+R+both)
    #Hand separation vs day (Asym, Sym)
    #ReactTime vs day plots (AsymL+R, SymL+R)
    #MaxForce vs day (L+R)
    #Time of day 
    #Sleep + sleep quality
    #PA table
    #Sessions 1 and 2
    ##Tot
    tot_plot([100*x for x in ToT_asym_L_12], [100*x for x in ToT_asym_L_12_std], [100*x for x in ToT_asym_R_12], [100*x for x in ToT_asym_R_12_std], 'Time on target /\n% of trial time', 'Time on Target for Asymmetric conditions', os.path.join(report_dir,subj,'Tot_12_ToT_A.png'), game_levels)
    tot_plot([100*x for x in ToT_sym_L_12], [100*x for x in ToT_sym_L_12_std], [100*x for x in ToT_sym_R_12], [100*x for x in ToT_sym_R_12_std], 'Time on target /\n% of trial time', 'Time on Target for Symmetric conditions', os.path.join(report_dir,subj,'Tot_12_ToT_S.png'), game_levels)
    
    ##Err
    tot_plot([x for x in err_asym_L_12], [x for x in err_asym_L_12_std], [x for x in err_asym_R_12], [x for x in err_asym_R_12_std], 'Error', 'Error last 500 ms for Asymmetric conditions', os.path.join(report_dir,subj,'Tot_12_Err_A.png'), game_levels)
    tot_plot([x for x in err_sym_L_12], [x for x in err_sym_L_12_std], [x for x in err_sym_R_12], [x for x in err_sym_R_12_std], 'Error', 'Error last 500 ms for Symmetric conditions', os.path.join(report_dir,subj,'Tot_12_Err_S.png'), game_levels)
    
    ##Trial Successes, maybe only both relevant
    tot_succ_plot([x for x in trialSuccess_asym_both_12], [x for x in trialSuccess_asym_both_12_std], [x for x in trialSuccess_asym_L_12], [x for x in trialSuccess_asym_L_12_std], [x for x in trialSuccess_asym_R_12], [x for x in trialSuccess_asym_R_12_std], 'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Asymmetric conditions', os.path.join(report_dir,subj,'Tot_12_Succ_A.png'), game_levels)
    tot_succ_plot([x for x in trialSuccess_sym_both_12], [x for x in trialSuccess_sym_both_12_std], [x for x in trialSuccess_sym_L_12], [x for x in trialSuccess_sym_L_12_std], [x for x in trialSuccess_sym_R_12], [x for x in trialSuccess_sym_R_12_std], 'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Symmetric conditions', os.path.join(report_dir,subj,'Tot_12_Succ_S.png'), game_levels)
    
    ##handsep
    tot_handsep_plot([x for x in handsep_asym_12], [x for x in handsep_asym_12_std], 'Force difference', 'Absolute force difference between hands\nAsymmetric condition', os.path.join(report_dir,subj,'Tot_12_HandSep_A.png'), game_levels)
    tot_handsep_plot([x for x in handsep_sym_12], [x for x in handsep_sym_12_std], 'Force difference', 'Absolute force difference between hands\nSymmetric condition', os.path.join(report_dir,subj,'Tot_12_HandSep_S.png'), game_levels)
    
    #Session 3
    ##Tot
    tot_plot([100*x for x in ToT_asym_L_3], [100*x for x in ToT_asym_L_3_std], [100*x for x in ToT_asym_R_3], [100*x for x in ToT_asym_R_3_std], 'Time on target /\n% of trial time', 'Time on Target for Asymmetric conditions', os.path.join(report_dir,subj,'Tot_3_ToT_A.png'), [1])
    tot_plot([100*x for x in ToT_sym_L_3], [100*x for x in ToT_sym_L_3_std], [100*x for x in ToT_sym_R_3], [100*x for x in ToT_sym_R_3_std], 'Time on target /\n% of trial time', 'Time on Target for Symmetric conditions', os.path.join(report_dir,subj,'Tot_3_ToT_S.png'), [1])
    
    ##Err
    tot_plot([x for x in err_asym_L_3], [x for x in err_asym_L_3_std], [x for x in err_asym_R_3], [x for x in err_asym_R_3_std], 'Error', 'Error last 500 ms for Asymmetric conditions', os.path.join(report_dir,subj,'Tot_3_Err_A.png'), [1])
    tot_plot([x for x in err_sym_L_3], [x for x in err_sym_L_3_std], [x for x in err_sym_R_3], [x for x in err_sym_R_3_std], 'Error', 'Error last 500 ms for Symmetric conditions', os.path.join(report_dir,subj,'Tot_3_Err_S.png'), [1])
    
    ##Trial Successes, maybe only both relevant
    tot_succ_plot([x for x in trialSuccess_asym_both_3], [x for x in trialSuccess_asym_both_3_std], [x for x in trialSuccess_asym_L_3], [x for x in trialSuccess_asym_L_3_std], [x for x in trialSuccess_asym_R_3], [x for x in trialSuccess_asym_R_3_std], 'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Asymmetric conditions', os.path.join(report_dir,subj,'Tot_3_Succ_A.png'), [1])
    tot_succ_plot([x for x in trialSuccess_sym_both_3], [x for x in trialSuccess_sym_both_3_std], [x for x in trialSuccess_sym_L_3], [x for x in trialSuccess_sym_L_3_std], [x for x in trialSuccess_sym_R_3], [x for x in trialSuccess_sym_R_3_std], 'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Symmetric conditions', os.path.join(report_dir,subj,'Tot_3_Succ_S.png'), [1])
    
    ##handsep
    tot_handsep_plot([x for x in handsep_asym_3], [x for x in handsep_asym_3_std], 'Force difference', 'Absolute force difference between hands\nAsymmetric condition', os.path.join(report_dir,subj,'Tot_3_HandSep_A.png'), [1])
    tot_handsep_plot([x for x in handsep_sym_3], [x for x in handsep_sym_3_std], 'Force difference', 'Absolute force difference between hands\nSymmetric condition', os.path.join(report_dir,subj,'Tot_3_HandSep_S.png'), [1])
    
    
    #Max force plots
    #Both hands in same plot
    plt.ioff()
    handplot_df = pd.DataFrame(data=[[x for x in range(1,len(HT_days)+1)], [x for x in max_forces_L], [x for x in max_forces_R]])
    handplot_df = handplot_df.T
    handplot_df.set_axis(['TrainingDay', 'MaxForce_L', 'MaxForce_R'], axis=1, inplace=True)
    ax = handplot_df.plot(x='TrainingDay', kind='bar', stacked=False, grid=True, legend=True, fontsize=14, colormap='tab10')
    ax.set_xlabel('TrainingDay',fontsize=16, fontweight='bold')
    ax.set_ylabel('Max Force / g',fontsize=16, fontweight='bold')
    ax.grid(axis='x')
    ax.set_title('Max Force for each Training Day', fontsize=16, fontweight='bold')
    ax.figure.savefig(os.path.join(report_dir,subj,'MaxForces.png'), bbox_inches="tight")
    plt.close(ax.figure)
    #Make time of day plot
    plt.ioff()
    ToD_df = pd.DataFrame(data=[[x for x in range(1,len(HT_days)+1)], [x for x in time_of_day]])
    ToD_df = ToD_df.T
    ToD_df.set_axis(['TrainingDay', 'Time of Day'], axis=1, inplace=True)
    ax = ToD_df.plot(x='TrainingDay', kind='bar', stacked=False, grid=True, legend=True, fontsize=14, color='k')
    ax.set_xlabel('TrainingDay',fontsize=16, fontweight='bold')
    ax.set_ylabel('Time of Day / hours',fontsize=16, fontweight='bold')
    ax.grid(axis='x')
    ax.set_title('Time of Day for each Training Day', fontsize=16, fontweight='bold')
    ax.figure.savefig(os.path.join(report_dir,subj,'TimeOfDay.png'), bbox_inches="tight")
    plt.close(ax.figure)
    #Make sleep plot
    #NbrOfHours as line, quality as bar. Can share y-axis.
    plt.ioff()
    sleep_df = pd.DataFrame({'TrainingDay' : [x for x in range(1,len(HT_days)+1)], 'Hours' : [float(x) for x in sleep_times],'Quality' : [float(x) for x in sleep_qualities]})
    sleep_df['Hours'].plot()
    sleep_df['Quality'].plot(kind='bar',fontsize=14, color='k')
    ax=plt.gca()
    ax.set_xlabel('TrainingDay',fontsize=16, fontweight='bold')
    ax.set_ylabel('Hours of Sleep or \nReported quality',fontsize=16, fontweight='bold')
    ax.grid(axis='y')
    ax.set_title('Sleep time (line) and quality (bar) \nfor each Training Day', fontsize=16, fontweight='bold')
    ax.figure.savefig(os.path.join(report_dir,subj,'Sleep.png'), bbox_inches="tight")
    plt.close(ax.figure)
    #Make PA table
    plt.ioff()
    PA_df = pd.DataFrame(data=physical_activity_matrix, columns=['TrainingDay', 'Walk/min', 'Cardio/min', 'Swimming/min', 'Weight Training/min', 'Other/min'])
    fig, ax = plt.subplots()
    ax.axis('off')
    ax.axis('tight')
    table = ax.table(cellText=PA_df.values, colLabels=PA_df.columns, loc='center')
    for (row,col), cell in table.get_celld().items():
        if row==0:
            cell.set_text_props(fontproperties=FontProperties(weight='bold'))
    fig.tight_layout()
    fig.savefig(os.path.join(report_dir,subj,'PA_table.png'), dpi=300, bbox_inches="tight")
    plt.close(ax.figure)



