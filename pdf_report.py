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
import numpy as np
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
    
def day_plot(print_data_means, print_data_std, plot_yaxis, plot_title, save_destination):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(print_data_means))
    fig, ax = plt.subplots()
    ax.bar(x_pos, print_data_means, yerr=print_data_std, align='center', alpha=0.5, ecolor='black', capsize=10, fontsize=14)
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Session 1', 'Session 2', 'Session 3'], fontsize=16, fontweight='bold')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    ax.yaxis.grid(True)
    
    fig.savefig(save_destination)
    
    plt.close(ax.figure)# To not show all the plots all the time.

def tot_plot(print_data_means, print_data_std, plot_yaxis, plot_title, save_destination):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(print_data_means))
    fig, ax = plt.subplots()
    ax.bar(x_pos, print_data_means, yerr=print_data_std, align='center', alpha=0.5, ecolor='black', capsize=10, fontsize=14)
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    ax.set_xticks(x_pos)
    xlab = []
    for trday_itr in range(len(print_data_means)):
        xlab.append('Training Day '+str(trday_itr+1))
    ax.set_xticklabels(xlab, fontsize=16, fontweight='bold')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    ax.yaxis.grid(True)
    
    fig.savefig(save_destination)
    
    plt.close(ax.figure)# To not show all the plots all the time.
##############Set paths and plot options###################
#Change to where you have your data.
path='/Users/gdf724/Data/ReScale/HomeTrainingTest/' 
#List all subjects to process.
list_of_subjs=['P001', 'P002', 'P003']
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
    handsep_asym = [] 
    handsep_sym = []
    ToT_asym_L_std = [] #One value per day
    ToT_asym_R_std = []
    ToT_sym_L_std = []
    ToT_sym_R_std = []
    err_asym_L_std = []
    err_asym_R_std = []
    err_sym_L_std = []
    err_sym_R_std = []
    trialSuccess_asym_L_std = []
    trialSuccess_asym_R_std = []
    trialSuccess_sym_L_std = []
    trialSuccess_sym_R_std = []
    trialSuccess_asym_both_std = []
    trialSuccess_sym_both_std = []
    handsep_asym_std = [] 
    handsep_sym_std = []
    
    RT_asym_L = [] #Save RT for later, or make the plots but don't put in report
    RT_asym_R = []
    RT_sym_L = []
    RT_sym_R = []
    
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
            # #Make one then make a function for it.
            # sess_plot([element*100 for element in block_ToT_asym_L], 'Time on Target for Asymmetric conditions\nLeft Hand', \
            #           'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_A_L.png'))
            # sess_plot([element*100 for element in block_ToT_asym_R], 'Time on Target for Asymmetric conditions\nRight Hand', \
            #           'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_A_R.png'))
            # sess_plot([element*100 for element in block_ToT_sym_L], 'Time on Target for Symmetric conditions\nLeft Hand', \
            #           'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_S_L.png'))
            # sess_plot([element*100 for element in block_ToT_sym_R], 'Time on Target for Symmetric conditions\nRight Hand', \
            #           'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_S_R.png'))
                    
            # ##Error last 500 ms
            # sess_plot([x[:] for x in block_err_asym_L], 'Error last 500 ms for Asymmetric conditions\nLeft Hand', \
            #           'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_A_L.png'))
            # sess_plot([x[:] for x in block_err_asym_R], 'Error last 500 ms for Asymmetric conditions\nRight Hand', \
            #           'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_A_R.png'))
            # sess_plot([x[:] for x in block_err_sym_L], 'Error last 500 ms for Symmetric conditions\nLeft Hand', \
            #           'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_S_L.png'))
            # sess_plot([x[:] for x in block_err_sym_R], 'Error last 500 ms for Symmetric conditions\nRight Hand', \
            #           'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_S_R.png'))
            
            # ##Stable for 200 ms success
            # sess_trialsuccess_plot(block_trialSuccess_sym_both, block_trialSuccess_sym_L, block_trialSuccess_sym_R, \
            #                        'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Symmetric conditions', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Succ_S.png'))
            # sess_trialsuccess_plot(block_trialSuccess_asym_both, block_trialSuccess_asym_L, block_trialSuccess_asym_R, \
            #                        'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Asymmetric conditions', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Succ_A.png'))
            
            # ##Hand separation
            # sess_plot([x[:] for x in block_handsep_asym], 'Absolute force difference between hands\nAsymmetric conditions', \
            #           'Force difference', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_HandSep_A.png'))
            # sess_plot([x[:] for x in block_handsep_sym], 'Absolute force difference between hands\nSymmetric condition', \
            #           'Force difference', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_HandSep_S_L.png'))
            
            
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
        #Make the day-specific plots and report and use the session values.
        ##ToT
        day_plot([100*x for x in sess_ToT_asym_L], [100*x for x in sess_std_ToT_asym_L], 'Time on target /\n% of trial time', 'Time on Target for Asymmetric conditions\nLeft Hand', os.path.join(day_save_folder,'Day_ToT_A_L.png'))
        day_plot([100*x for x in sess_ToT_asym_R], [100*x for x in sess_std_ToT_asym_R], 'Time on target /\n% of trial time', 'Time on Target for Asymmetric conditions\nRight Hand', os.path.join(day_save_folder,'Day_ToT_A_R.png'))
        day_plot([100*x for x in sess_ToT_sym_L], [100*x for x in sess_std_ToT_sym_L], 'Time on target /\n% of trial time', 'Time on Target for Symmetric conditions\nLeft Hand', os.path.join(day_save_folder,'Day_ToT_S_L.png'))
        day_plot([100*x for x in sess_ToT_sym_R], [100*x for x in sess_std_ToT_sym_R], 'Time on target /\n% of trial time', 'Time on Target for Symmetric conditions\nRight Hand', os.path.join(day_save_folder,'Day_ToT_S_R.png'))
        
        ##Err
        day_plot([x for x in sess_err_asym_L], [x for x in sess_std_err_asym_L], 'Error', 'Error last 500 ms for Asymmetric conditions\nLeft Hand', os.path.join(day_save_folder,'Day_Err_A_L.png'))
        day_plot([x for x in sess_err_asym_R], [x for x in sess_std_err_asym_R], 'Error', 'Error last 500 ms for Asymmetric conditions\nRight Hand', os.path.join(day_save_folder,'Day_Err_A_R.png'))
        day_plot([x for x in sess_err_sym_L], [x for x in sess_std_err_sym_L], 'Error', 'Error last 500 ms for Symmetric conditions\nLeft Hand', os.path.join(day_save_folder,'Day_Err_S_L.png'))
        day_plot([x for x in sess_err_sym_R], [x for x in sess_std_err_sym_R], 'Error', 'Error last 500 ms for Symmetric conditions\nRight Hand', os.path.join(day_save_folder,'Day_Err_S_R.png'))
        
        ##Trial Successes, maybe only both relevant
        day_plot([x for x in sess_trialSuccess_asym_L], [x for x in sess_std_trialSuccess_asym_L], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Asymmetric conditions Left hand', os.path.join(day_save_folder,'Day_Succ_A_L.png'))
        day_plot([x for x in sess_trialSuccess_asym_R], [x for x in sess_std_trialSuccess_asym_R], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Asymmetric conditions Right hand', os.path.join(day_save_folder,'Day_Succ_A_R.png'))
        day_plot([x for x in sess_trialSuccess_sym_L], [x for x in sess_std_trialSuccess_sym_L], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Symmetric conditions Left hand', os.path.join(day_save_folder,'Day_Succ_S_L.png'))
        day_plot([x for x in sess_trialSuccess_sym_R], [x for x in sess_std_trialSuccess_sym_R], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Symmetric conditions Right hand', os.path.join(day_save_folder,'Day_Succ_S_R.png'))
        
        ##handsep
        day_plot([x for x in sess_handsep_asym], [x for x in sess_std_handsep_asym], 'Force difference', 'Absolute force difference between hands\nAsymmetric condition', os.path.join(day_save_folder,'Day_HandSep_A.png'))
        day_plot([x for x in sess_handsep_sym], [x for x in sess_std_handsep_sym], 'Force difference', 'Absolute force difference between hands\nSymmetric condition', os.path.join(day_save_folder,'Day_HandSep_S.png'))

        #Save daily measurement + std
        #Standard deviation between blocks. If interested in standard deviation within blocks, one needs to look at the daily plots. 
        ToT_asym_L[day_itr] = np.mean(np.asarray(sess_ToT_asym_L)) #One value per day
        ToT_asym_R[day_itr] = np.mean(np.asarray(sess_ToT_asym_R))
        ToT_sym_L[day_itr] = np.mean(np.asarray(sess_ToT_sym_L))
        ToT_sym_R[day_itr] = np.mean(np.asarray(sess_ToT_sym_R))
        err_asym_L[day_itr] = np.mean(np.asarray(sess_err_asym_L))
        err_asym_R[day_itr] = np.mean(np.asarray(sess_err_asym_R))
        err_sym_L[day_itr] = np.mean(np.asarray(sess_err_sym_L))
        err_sym_R[day_itr] = np.mean(np.asarray(sess_err_sym_R))
        trialSuccess_asym_L[day_itr] = np.mean(np.asarray(sess_trialSuccess_asym_L))
        trialSuccess_asym_R[day_itr] = np.mean(np.asarray(sess_trialSuccess_asym_R))
        trialSuccess_sym_L[day_itr] = np.mean(np.asarray(sess_trialSuccess_sym_L))
        trialSuccess_sym_R[day_itr] = np.mean(np.asarray(sess_trialSuccess_sym_R))
        trialSuccess_asym_both[day_itr] = np.mean(np.asarray(sess_trialSuccess_asym_both))
        trialSuccess_sym_both[day_itr] = np.mean(np.asarray(sess_trialSuccess_sym_both))
        handsep_asym[day_itr] = np.mean(np.asarray(sess_handsep_asym))
        handsep_sym[day_itr] = np.mean(np.asarray(sess_handsep_sym))
        ToT_asym_L_std[day_itr] = np.std(np.asarray(sess_ToT_asym_L)) #One value per day
        ToT_asym_R_std[day_itr] = np.std(np.asarray(sess_ToT_asym_R))
        ToT_sym_L_std[day_itr] = np.std(np.asarray(sess_ToT_sym_L))
        ToT_sym_R_std[day_itr] = np.std(np.asarray(sess_ToT_sym_R))
        err_asym_L_std[day_itr] = np.std(np.asarray(sess_err_asym_L))
        err_asym_R_std[day_itr] = np.std(np.asarray(sess_err_asym_R))
        err_sym_L_std[day_itr] = np.std(np.asarray(sess_err_sym_L))
        err_sym_R_std[day_itr] = np.std(np.asarray(sess_err_sym_R))
        trialSuccess_asym_L_std[day_itr] = np.std(np.asarray(sess_trialSuccess_asym_L))
        trialSuccess_asym_R_std[day_itr] = np.std(np.asarray(sess_trialSuccess_asym_R))
        trialSuccess_sym_L_std[day_itr] = np.std(np.asarray(sess_trialSuccess_sym_L))
        trialSuccess_sym_R_std[day_itr] = np.std(np.asarray(sess_trialSuccess_sym_R))
        trialSuccess_asym_both_std[day_itr] = np.std(np.asarray(sess_trialSuccess_asym_both))
        trialSuccess_sym_both_std[day_itr] = np.std(np.asarray(sess_trialSuccess_sym_both))
        handsep_asym_std[day_itr] = np.std(np.asarray(sess_handsep_asym))
        handsep_sym_std[day_itr] = np.std(np.asarray(sess_handsep_sym))
    
    
    ##############Make weekly plots###################
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
    ##ToT
    tot_plot([100*x for x in ToT_asym_L], [100*x for x in ToT_asym_L_std], 'Time on target /\n% of trial time', 'Time on Target for Asymmetric conditions\nLeft Hand', os.path.join(report_dir,subj,'Tot_ToT_A_L.png'))
    tot_plot([100*x for x in ToT_asym_R], [100*x for x in ToT_asym_R_std], 'Time on target /\n% of trial time', 'Time on Target for Asymmetric conditions\nRight Hand', os.path.join(day_save_folder,'Day_ToT_A_R.png'))
    tot_plot([100*x for x in ToT_sym_L], [100*x for x in ToT_sym_L_std], 'Time on target /\n% of trial time', 'Time on Target for Symmetric conditions\nLeft Hand', os.path.join(day_save_folder,'Day_ToT_S_L.png'))
    tot_plot([100*x for x in ToT_sym_R], [100*x for x in ToT_sym_R_std], 'Time on target /\n% of trial time', 'Time on Target for Symmetric conditions\nRight Hand', os.path.join(day_save_folder,'Day_ToT_S_R.png'))
    
    ##Err
    tot_plot([x for x in err_asym_L], [x for x in err_asym_L_std], 'Error', 'Error last 500 ms for Asymmetric conditions\nLeft Hand', os.path.join(day_save_folder,'Tot_Err_A_L.png'))
    tot_plot([x for x in err_asym_R], [x for x in err_asym_R_std], 'Error', 'Error last 500 ms for Asymmetric conditions\nRight Hand', os.path.join(day_save_folder,'Tot_Err_A_R.png'))
    tot_plot([x for x in err_sym_L], [x for x in err_sym_L_std], 'Error', 'Error last 500 ms for Symmetric conditions\nLeft Hand', os.path.join(day_save_folder,'Tot_Err_S_L.png'))
    tot_plot([x for x in err_sym_R], [x for x in err_sym_R_std], 'Error', 'Error last 500 ms for Symmetric conditions\nRight Hand', os.path.join(day_save_folder,'Tot_Err_S_R.png'))
    
    ##Trial Successes, maybe only both relevant
    tot_plot([x for x in trialSuccess_asym_L], [x for x in trialSuccess_asym_L_std], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Asymmetric conditions Left hand', os.path.join(day_save_folder,'Tot_Succ_A_L.png'))
    tot_plot([x for x in trialSuccess_asym_R], [x for x in trialSuccess_asym_R_std], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Asymmetric conditions Right hand', os.path.join(day_save_folder,'Tot_Succ_A_R.png'))
    tot_plot([x for x in trialSuccess_sym_L], [x for x in trialSuccess_sym_L_std], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Symmetric conditions Left hand', os.path.join(day_save_folder,'Tot_Succ_S_L.png'))
    tot_plot([x for x in trialSuccess_sym_R], [x for x in trialSuccess_sym_R_std], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 200 ms)\nin Symmetric conditions Right hand', os.path.join(day_save_folder,'Tot_Succ_S_R.png'))
    
    ##handsep
    tot_plot([x for x in handsep_asym], [x for x in handsep_asym_std], 'Force difference', 'Absolute force difference between hands\nAsymmetric condition', os.path.join(day_save_folder,'Tot_HandSep_A.png'))
    tot_plot([x for x in handsep_sym], [x for x in handsep_sym_std], 'Force difference', 'Absolute force difference between hands\nSymmetric condition', os.path.join(day_save_folder,'Tot_HandSep_S.png'))
   
    #Make sleep plot
    
    #Make PA table
    
    