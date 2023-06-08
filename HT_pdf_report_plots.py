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
from fpdf import FPDF, HTMLMixin


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.WIDTH = 210
        self.HEIGHT = 297
        
    def page_body(self, images):
        # Determine how many plots there are per page and set positions
        # and margins accordingly
        if len(images) == 8:
            self.image(images[0], h=self.HEIGHT/5, w=self.WIDTH/2, x=0, y=self.HEIGHT/10)
            self.image(images[1], h=self.HEIGHT/5, w=self.WIDTH/2, x=self.WIDTH/2, y=self.HEIGHT/10)
            self.image(images[2], h=self.HEIGHT/5, w=self.WIDTH/2, x=0, y=self.HEIGHT/10+self.HEIGHT/5)
            self.image(images[3], h=self.HEIGHT/5, w=self.WIDTH/2, x=self.WIDTH/2, y=self.HEIGHT/10+self.HEIGHT/5)
            self.image(images[4], h=self.HEIGHT/5, w=self.WIDTH/2, x=0, y=self.HEIGHT/10+2*self.HEIGHT/5)
            self.image(images[5], h=self.HEIGHT/5, w=self.WIDTH/2, x=self.WIDTH/2, y=self.HEIGHT/10+2*self.HEIGHT/5)
            self.image(images[6], h=self.HEIGHT/5, w=self.WIDTH/2, x=0, y=self.HEIGHT/10+3*self.HEIGHT/5)
            self.image(images[7], h=self.HEIGHT/5, w=self.WIDTH/2, x=self.WIDTH/2, y=self.HEIGHT/10+3*self.HEIGHT/5)
        elif len(images) == 4:
            self.image(images[0], h=self.HEIGHT/5, w=self.WIDTH/2)
            self.image(images[1], h=self.HEIGHT/5, w=self.WIDTH/2)
            self.image(images[2], h=self.HEIGHT/5, w=self.WIDTH/2)
            self.image(images[3], h=self.HEIGHT/4, w=self.WIDTH*0.8)
        else:
            self.image(images[0], 15, 25, self.WIDTH - 30)
            
    def print_page(self, images):
        # Generates the report
        self.add_page()
        self.page_body(images)


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
    
def tot_succ_plot(print_data_both, print_data_both_std, print_data_L, print_data_L_std, print_data_R, print_data_R_std, plot_yaxis, plot_title, save_destination):
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

def day_impact_plot(impacttime_L, impacttime_std_L, impacttime_R, impacttime_std_R, impact_L, impact_std_L, impact_R, impact_std_R, plot_yaxis, plot_title, save_destination):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(impacttime_L))
    width=0.15
    fig, ax = plt.subplots()
    ax.bar(x_pos-width, impacttime_L, width=width, yerr=impacttime_std_L, label='Left', color='navy')
    ax.bar(x_pos+width, impacttime_R, width=width, yerr=impacttime_std_R, label='Right', color='goldenrod')
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Session 1', 'Session 2', 'Session 3'], fontsize=16, fontweight='bold')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    ax.yaxis.grid(True)
    textstr = 'Fractions that make impact.\n'
    for itr in range(len(impacttime_L)):
        textstr = textstr+'Session '+str(itr+1)+': Left: '+str(round(impact_L[itr],2))+' Right:'+str(round(impact_R[itr],2))+'\n'
    ax.text(0,-0.8, textstr, fontsize=14)
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

def tot_handsep_plot(print_data_means, print_data_std, plot_yaxis, plot_title, save_destination):
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
    ax.yaxis.grid(True)
    
    fig.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.

def tot_impact_plot(impacttime_L, impacttime_std_L, impacttime_R, impacttime_std_R, impact_L, impact_std_L, impact_R, impact_std_R, plot_yaxis, plot_title, save_destination):
    plt.ioff() # To not show all the plots all the time
    
    x_pos = np.arange(len(impacttime_L))
    width=0.15
    fig, ax = plt.subplots()
    ax.bar(x_pos-width, impacttime_L, width=width, yerr=impacttime_std_L, label='Left', color='navy')
    ax.bar(x_pos+width, impacttime_R, width=width, yerr=impacttime_std_R, label='Right', color='goldenrod')
    ax.set_ylabel(plot_yaxis, fontsize=16, fontweight='bold')
    #ax.set_ylim((0,100))
    ax.set_xticks(x_pos)
    xlab = []
    textstr = 'Fractions that make impact.\n'
    for trday_itr in range(len(impacttime_L)):
        xlab.append('Training Day '+str(trday_itr+1))
        textstr = textstr+'Session '+str(trday_itr+1)+': Left: '+str(round(impact_L[trday_itr],2))+' Right:'+str(round(impact_R[trday_itr],2))+'\n'
        ax.text(0,-0.2*(len(impacttime_L)-trday_itr), textstr, fontsize=14)
    ax.set_xticklabels(xlab, fontsize=16, fontweight='bold', rotation=45, ha='right')
    ax.set_title(plot_title, fontsize=16, fontweight='bold')
    
    
    ax.yaxis.grid(True)
    ax.legend()
    
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

def tot_plot(print_data_means_L, print_data_std_L, print_data_means_R, print_data_std_R, plot_yaxis, plot_title, save_destination):
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
    
    ax.yaxis.grid(True)
    ax.legend()
    
    fig.savefig(save_destination, bbox_inches="tight")
    
    plt.close(ax.figure)# To not show all the plots all the time.
    
##############Set paths and plot options###################
#Change to where you have your data.
path='/Users/gdf724/Data/ReScale/ReScale2_HomeTraining'
#List all subjects to process.
report_dir='/Users/gdf724/Data/ReScale/ReScale2_reports/HomeTraining/'
def pdf_report_plots(path,report_dir,subj):
    overwrite = False
    
    HT_days = pph.get_HTfolders(path, subj)
    max_forces_L=[] 
    max_forces_R=[]
    time_of_day=[]
    sleep_times=[]
    sleep_qualities=[]
    physical_activity_matrix=[]
    pa_rows = ['Training day %d' % x for x in range(1,len(HT_days)+1)]
    pa_columns = ('Brisk walk', 'Cardio', 'Swimming', 'Weight training', 'Other')
    
    ToT_asym_L = [None]*len(HT_days) #One value per day
    ToT_asym_R = [None]*len(HT_days)
    ToT_sym_L = [None]*len(HT_days)
    ToT_sym_R = [None]*len(HT_days)
    err_asym_L = [None]*len(HT_days)
    err_asym_R = [None]*len(HT_days)
    err_sym_L = [None]*len(HT_days)
    err_sym_R = [None]*len(HT_days)
    impacttime_asym_L = [None]*len(HT_days)
    impacttime_asym_R = [None]*len(HT_days)
    impacttime_sym_L = [None]*len(HT_days)
    impacttime_sym_R = [None]*len(HT_days)
    impact_asym_L = [None]*len(HT_days)
    impact_asym_R = [None]*len(HT_days)
    impact_sym_L = [None]*len(HT_days)
    impact_sym_R = [None]*len(HT_days)
    trialSuccess_asym_L = [None]*len(HT_days)
    trialSuccess_asym_R = [None]*len(HT_days)
    trialSuccess_sym_L = [None]*len(HT_days)
    trialSuccess_sym_R = [None]*len(HT_days)
    trialSuccess_asym_both = [None]*len(HT_days)
    trialSuccess_sym_both = [None]*len(HT_days)
    handsep_asym = [None]*len(HT_days) 
    handsep_sym = [None]*len(HT_days)
    overshoot_L_asym = [[0.0,0.0,0.0]]*len(HT_days) 
    overshoot_R_asym = [[0.0,0.0,0.0]]*len(HT_days) 
    overshoot_L_sym = [[0.0,0.0,0.0]]*len(HT_days) 
    overshoot_R_sym = [[0.0,0.0,0.0]]*len(HT_days) 
    undershoot_L_asym = [[0.0,0.0,0.0]]*len(HT_days) 
    undershoot_R_asym = [[0.0,0.0,0.0]]*len(HT_days) 
    undershoot_L_sym = [[0.0,0.0,0.0]]*len(HT_days) 
    undershoot_R_sym = [[0.0,0.0,0.0]]*len(HT_days) 
    tb_handsep_asym = [[0.0,0.0,0.0]]*len(HT_days) 
    tb_handsep_sym = [[0.0,0.0,0.0]]*len(HT_days) 
    volatility_L_asym = [[0.0,0.0,0.0]]*len(HT_days) 
    volatility_R_asym = [[0.0,0.0,0.0]]*len(HT_days)
    volatility_L_sym = [[0.0,0.0,0.0]]*len(HT_days) 
    volatility_R_sym = [[0.0,0.0,0.0]]*len(HT_days)
    ToT_asym_L_std = [None]*len(HT_days) #One value per day
    ToT_asym_R_std = [None]*len(HT_days)
    ToT_sym_L_std = [None]*len(HT_days)
    ToT_sym_R_std = [None]*len(HT_days)
    err_asym_L_std = [None]*len(HT_days)
    err_asym_R_std = [None]*len(HT_days)
    err_sym_L_std = [None]*len(HT_days)
    err_sym_R_std = [None]*len(HT_days)
    impacttime_asym_L_std = [None]*len(HT_days)
    impacttime_asym_R_std = [None]*len(HT_days)
    impacttime_sym_L_std = [None]*len(HT_days)
    impacttime_sym_R_std = [None]*len(HT_days)
    impact_asym_L_std = [None]*len(HT_days)
    impact_asym_R_std = [None]*len(HT_days)
    impact_sym_L_std = [None]*len(HT_days)
    impact_sym_R_std = [None]*len(HT_days)
    trialSuccess_asym_L_std = [None]*len(HT_days)
    trialSuccess_asym_R_std = [None]*len(HT_days)
    trialSuccess_sym_L_std = [None]*len(HT_days)
    trialSuccess_sym_R_std = [None]*len(HT_days)
    trialSuccess_asym_both_std = [None]*len(HT_days)
    trialSuccess_sym_both_std = [None]*len(HT_days)
    handsep_asym_std = [None]*len(HT_days)
    handsep_sym_std = [None]*len(HT_days)
    overshoot_L_asym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    overshoot_R_asym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    overshoot_L_sym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    overshoot_R_sym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    undershoot_L_asym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    undershoot_R_asym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    undershoot_L_sym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    undershoot_R_sym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    tb_handsep_asym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    tb_handsep_sym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    volatility_L_asym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    volatility_R_asym_std = [[0.0,0.0,0.0]]*len(HT_days)
    volatility_L_sym_std = [[0.0,0.0,0.0]]*len(HT_days) 
    volatility_R_sym_std = [[0.0,0.0,0.0]]*len(HT_days)
    
    
    #Make subject dir
    if not os.path.exists(os.path.join(report_dir,subj)):
        os.makedirs(os.path.join(report_dir,subj))
    
    for day_itr in range(len(HT_days)): #Check if it's not already done and if overwrite is false
        print('Subject: '+subj+' Day: '+str(day_itr+1))
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
        sess_impacttime_asym_L = [[] for x in range(3)]
        sess_impacttime_asym_R = [[] for x in range(3)]
        sess_impacttime_sym_L = [[] for x in range(3)]
        sess_impacttime_sym_R = [[] for x in range(3)]
        sess_impact_asym_L = [[] for x in range(3)]
        sess_impact_asym_R = [[] for x in range(3)]
        sess_impact_sym_L = [[] for x in range(3)]
        sess_impact_sym_R = [[] for x in range(3)]
        sess_trialSuccess_asym_L = [[] for x in range(3)]
        sess_trialSuccess_asym_R = [[] for x in range(3)]
        sess_trialSuccess_sym_L = [[] for x in range(3)]
        sess_trialSuccess_sym_R = [[] for x in range(3)]
        sess_trialSuccess_asym_both = [[] for x in range(3)]
        sess_trialSuccess_sym_both = [[] for x in range(3)]
        sess_handsep_asym = [[] for x in range(3)] 
        sess_handsep_sym = [[] for x in range(3)]
        sess_overshoot_L_asym = [[0,0,0] for x in range(3)] 
        sess_overshoot_R_asym = [[0,0,0] for x in range(3)]
        sess_overshoot_L_sym = [[0,0,0] for x in range(3)]
        sess_overshoot_R_sym = [[0,0,0] for x in range(3)]
        sess_undershoot_L_asym = [[0,0,0] for x in range(3)] 
        sess_undershoot_R_asym = [[0,0,0] for x in range(3)]
        sess_undershoot_L_sym = [[0,0,0] for x in range(3)]
        sess_undershoot_R_sym = [[0,0,0] for x in range(3)]
        sess_tb_handsep_asym = [[0,0,0] for x in range(3)]
        sess_tb_handsep_sym = [[0,0,0] for x in range(3)]
        sess_volatility_L_asym = [[0,0,0] for x in range(3)]
        sess_volatility_R_asym = [[0,0,0] for x in range(3)]
        sess_volatility_L_sym = [[0,0,0] for x in range(3)]
        sess_volatility_R_sym = [[0,0,0] for x in range(3)]
        sess_std_ToT_asym_L = [[] for x in range(3)] #List of every value for the entire day. One per session.
        sess_std_ToT_asym_R = [[] for x in range(3)]
        sess_std_ToT_sym_L = [[] for x in range(3)]
        sess_std_ToT_sym_R = [[] for x in range(3)]
        sess_std_err_asym_L = [[] for x in range(3)]
        sess_std_err_asym_R = [[] for x in range(3)]
        sess_std_err_sym_L = [[] for x in range(3)]
        sess_std_err_sym_R = [[] for x in range(3)]
        sess_std_impacttime_asym_L = [[] for x in range(3)]
        sess_std_impacttime_asym_R = [[] for x in range(3)]
        sess_std_impacttime_sym_L = [[] for x in range(3)]
        sess_std_impacttime_sym_R = [[] for x in range(3)]
        sess_std_impact_asym_L = [[] for x in range(3)]
        sess_std_impact_asym_R = [[] for x in range(3)]
        sess_std_impact_sym_L = [[] for x in range(3)]
        sess_std_impact_sym_R = [[] for x in range(3)]
        sess_std_trialSuccess_asym_L = [[] for x in range(3)]
        sess_std_trialSuccess_asym_R = [[] for x in range(3)]
        sess_std_trialSuccess_sym_L = [[] for x in range(3)]
        sess_std_trialSuccess_sym_R = [[] for x in range(3)]
        sess_std_trialSuccess_asym_both = [[] for x in range(3)]
        sess_std_trialSuccess_sym_both = [[] for x in range(3)]
        sess_std_handsep_asym = [[] for x in range(3)] 
        sess_std_handsep_sym = [[] for x in range(3)]
        sess_std_overshoot_L_asym = [[0,0,0] for x in range(3)] 
        sess_std_overshoot_R_asym = [[0,0,0] for x in range(3)]
        sess_std_overshoot_L_sym = [[0,0,0] for x in range(3)]
        sess_std_overshoot_R_sym = [[0,0,0] for x in range(3)]
        sess_std_undershoot_L_asym = [[0,0,0] for x in range(3)] 
        sess_std_undershoot_R_asym = [[0,0,0] for x in range(3)]
        sess_std_undershoot_L_sym = [[0,0,0] for x in range(3)]
        sess_std_undershoot_R_sym = [[0,0,0] for x in range(3)]
        sess_std_tb_handsep_asym = [[0,0,0] for x in range(3)]
        sess_std_tb_handsep_sym = [[0,0,0] for x in range(3)]
        sess_std_volatility_L_asym = [[0,0,0] for x in range(3)]
        sess_std_volatility_R_asym = [[0,0,0] for x in range(3)]
        sess_std_volatility_L_sym = [[0,0,0] for x in range(3)]
        sess_std_volatility_R_sym = [[0,0,0] for x in range(3)]
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
            block_impacttime_asym_L = [[] for x in range(len(A_blocks))]
            block_impacttime_asym_R = [[] for x in range(len(A_blocks))]
            block_impacttime_sym_L = [[] for x in range(len(S_blocks))]
            block_impacttime_sym_R = [[] for x in range(len(S_blocks))]
            block_impact_asym_L = [[] for x in range(len(A_blocks))]
            block_impact_asym_R = [[] for x in range(len(A_blocks))]
            block_impact_sym_L = [[] for x in range(len(S_blocks))]
            block_impact_sym_R = [[] for x in range(len(S_blocks))]
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
            block_overshoot_L_asym = [[] for x in range(len(A_blocks))]
            block_overshoot_R_asym = [[] for x in range(len(A_blocks))]
            block_overshoot_L_sym = [[] for x in range(len(S_blocks))]
            block_overshoot_R_sym = [[] for x in range(len(S_blocks))]
            block_undershoot_L_asym = [[] for x in range(len(A_blocks))]
            block_undershoot_R_asym = [[] for x in range(len(A_blocks))]
            block_undershoot_L_sym = [[] for x in range(len(S_blocks))]
            block_undershoot_R_sym = [[] for x in range(len(S_blocks))]
            block_tb_handsep_asym = [[] for x in range(len(A_blocks))]
            block_tb_handsep_sym = [[] for x in range(len(S_blocks))]
            block_volatility_L_asym = [[] for x in range(len(A_blocks))]
            block_volatility_R_asym = [[] for x in range(len(A_blocks))]
            block_volatility_L_sym = [[] for x in range(len(S_blocks))]
            block_volatility_R_sym = [[] for x in range(len(S_blocks))]
            
            #Build asymmetry data set
            for block_itr in range(len(A_blocks)): #This assumes equal number of blocks. 
                for trial_itr in range(len(A_blocks[block_itr])):
                    tmp_data = A_blocks[block_itr][trial_itr]
                    block_condition_asym[block_itr].append(tmp_data['condition'])
                    block_ToT_asym_L[block_itr].append(tmp_data['TimeOnTarget_L'])
                    block_ToT_asym_R[block_itr].append(tmp_data['TimeOnTarget_R'])
                    block_err_asym_L[block_itr].append(tmp_data['ACCtw_L'])
                    block_err_asym_R[block_itr].append(tmp_data['ACCtw_R'])
                    if tmp_data['impact_L'] == 1:
                        block_impacttime_asym_L[block_itr].append(tmp_data['impacttime_L'])
                    else:
                        block_impacttime_asym_L[block_itr].append(np.nan)
                    if tmp_data['impact_R'] == 1:
                        block_impacttime_asym_R[block_itr].append(tmp_data['impacttime_R'])
                    else:
                        block_impacttime_asym_R[block_itr].append(np.nan)
                    block_impact_asym_L[block_itr].append(tmp_data['impact_L'])
                    block_impact_asym_R[block_itr].append(tmp_data['impact_R'])
                    block_trialSuccess_asym_L[block_itr].append(tmp_data['trial_success_time_L']>0) #Only interested in the success or not. 
                    block_trialSuccess_asym_R[block_itr].append(tmp_data['trial_success_time_R']>0)
                    block_trialSuccess_asym_both[block_itr].append(tmp_data['trial_success_time_both']>0)
                    block_handsep_asym[block_itr].append(tmp_data['forcediff'])
                    block_overshoot_L_asym[block_itr].append(tmp_data['overshoot_L'])
                    block_overshoot_R_asym[block_itr].append(tmp_data['overshoot_R'])
                    block_undershoot_L_asym[block_itr].append(tmp_data['undershoot_L'])
                    block_undershoot_R_asym[block_itr].append(tmp_data['undershoot_R'])
                    block_tb_handsep_asym[block_itr].append(tmp_data['handsep'])
                    block_volatility_L_asym[block_itr].append(tmp_data['volatility_L'])
                    block_volatility_R_asym[block_itr].append(tmp_data['volatility_R'])
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
                    if tmp_data['impact_L'] == 1:
                        block_impacttime_sym_L[block_itr].append(tmp_data['impacttime_L'])
                    else:
                        block_impacttime_sym_L[block_itr].append(np.nan)
                    if tmp_data['impact_R'] == 1:
                        block_impacttime_sym_R[block_itr].append(tmp_data['impacttime_R'])
                    else:
                        block_impacttime_sym_R[block_itr].append(np.nan)
                    block_impact_sym_L[block_itr].append(tmp_data['impact_L'])
                    block_impact_sym_R[block_itr].append(tmp_data['impact_R'])
                    block_trialSuccess_sym_L[block_itr].append(tmp_data['trial_success_time_L']>0) #Only interested in the success or not. But better as int. 
                    block_trialSuccess_sym_R[block_itr].append(tmp_data['trial_success_time_R']>0)
                    block_trialSuccess_sym_both[block_itr].append(tmp_data['trial_success_time_both']>0)
                    block_handsep_sym[block_itr].append(tmp_data['forcediff'])
                    block_overshoot_L_sym[block_itr].append(tmp_data['overshoot_L'])
                    block_overshoot_R_sym[block_itr].append(tmp_data['overshoot_R'])
                    block_undershoot_L_sym[block_itr].append(tmp_data['undershoot_L'])
                    block_undershoot_R_sym[block_itr].append(tmp_data['undershoot_R'])
                    block_tb_handsep_sym[block_itr].append(tmp_data['handsep'])
                    block_volatility_L_sym[block_itr].append(tmp_data['volatility_L'])
                    block_volatility_R_sym[block_itr].append(tmp_data['volatility_R'])
                block_trialSuccess_sym_L[block_itr] = list(map(int,block_trialSuccess_sym_L[block_itr]))
                block_trialSuccess_sym_R[block_itr] = list(map(int,block_trialSuccess_sym_R[block_itr]))
                block_trialSuccess_sym_both[block_itr] = list(map(int,block_trialSuccess_sym_both[block_itr]))
            #Make session-specific plots
            ##ToT
            if False:
            #if not os.path.exists(os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_A_L.png')) or overwrite:
                #Make one then make a function for it.
                sess_plot([element*100 for element in block_ToT_asym_L], 'Time on Target for Asymmetric conditions\nLeft Hand', \
                          'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_A_L.png'))
                sess_plot([element*100 for element in block_ToT_asym_R], 'Time on Target for Asymmetric conditions\nRight Hand', \
                          'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_A_R.png'))
                sess_plot([element*100 for element in block_ToT_sym_L], 'Time on Target for Symmetric conditions\nLeft Hand', \
                          'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_S_L.png'))
                sess_plot([element*100 for element in block_ToT_sym_R], 'Time on Target for Symmetric conditions\nRight Hand', \
                          'Time on target /\n% of trial time', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_ToT_S_R.png'))
                        
                ##Error last 500 ms
                sess_plot([x[:] for x in block_err_asym_L], 'Error last 500 ms for Asymmetric conditions\nLeft Hand', \
                          'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_A_L.png'))
                sess_plot([x[:] for x in block_err_asym_R], 'Error last 500 ms for Asymmetric conditions\nRight Hand', \
                          'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_A_R.png'))
                sess_plot([x[:] for x in block_err_sym_L], 'Error last 500 ms for Symmetric conditions\nLeft Hand', \
                          'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_S_L.png'))
                sess_plot([x[:] for x in block_err_sym_R], 'Error last 500 ms for Symmetric conditions\nRight Hand', \
                          'Error', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Err_S_R.png'))
                
                ##Impact and impacttime
                sess_plot([x[:] for x in block_impacttime_asym_L], 'Time of impact (0.5%) for Asymmetric conditions\nLeft Hand', \
                          'Time of impact', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_imp_A_L.png'))
                sess_plot([x[:] for x in block_impacttime_asym_R], 'Time of impact (0.5%) for Asymmetric conditions\nRight Hand', \
                          'Time of impact', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_imp_A_R.png'))
                sess_plot([x[:] for x in block_impacttime_sym_L], 'Time of impact (0.5%) for Asymmetric conditions\nLeft Hand', \
                          'Time of impact', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_imp_S_L.png'))
                sess_plot([x[:] for x in block_impacttime_sym_R], 'Time of impact (0.5%) for Asymmetric conditions\nRight Hand', \
                          'Time of impact', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_imp_S_R.png'))
                ##Stable for 200 ms success
                sess_trialsuccess_plot(block_trialSuccess_sym_both, block_trialSuccess_sym_L, block_trialSuccess_sym_R, \
                                        'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Symmetric conditions', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Succ_S.png'))
                sess_trialsuccess_plot(block_trialSuccess_asym_both, block_trialSuccess_asym_L, block_trialSuccess_asym_R, \
                                        'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Asymmetric conditions', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_Succ_A.png'))
                
                ##Hand separation
                sess_plot([x[:] for x in block_handsep_asym], 'Absolute force difference between hands\nAsymmetric conditions', \
                          'Force difference', os.path.join(day_save_folder,'sess_'+str(sess_itr+1)+'_HandSep_A.png'))
                sess_plot([x[:] for x in block_handsep_sym], 'Absolute force difference between hands\nSymmetric condition', \
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
            sess_handsep_asym[sess_itr] = np.nanmean(np.asarray(block_handsep_asym))
            sess_std_handsep_asym[sess_itr] = np.nanstd(np.asarray(block_handsep_asym))
            sess_handsep_sym[sess_itr] = np.nanmean(np.asarray(block_handsep_sym))
            sess_std_handsep_sym[sess_itr] = np.nanstd(np.asarray(block_handsep_sym))
            sess_overshoot_L_asym[sess_itr] = np.mean(np.mean(np.asarray(block_overshoot_L_asym),axis=1),axis=0)
            sess_std_overshoot_L_asym[sess_itr] = np.std(np.std(np.asarray(block_overshoot_L_asym),axis=1),axis=0)
            sess_overshoot_R_asym[sess_itr] = np.mean(np.mean(np.asarray(block_overshoot_R_asym),axis=1),axis=0)
            sess_std_overshoot_R_asym[sess_itr] = np.std(np.std(np.asarray(block_overshoot_R_asym),axis=1),axis=0)
            sess_overshoot_L_sym[sess_itr] = np.mean(np.mean(np.asarray(block_overshoot_L_sym),axis=1),axis=0)
            sess_std_overshoot_L_sym[sess_itr] = np.std(np.std(np.asarray(block_overshoot_L_sym),axis=1),axis=0)
            sess_overshoot_R_sym[sess_itr] = np.mean(np.mean(np.asarray(block_overshoot_R_sym),axis=1),axis=0)
            sess_std_overshoot_R_sym[sess_itr] = np.std(np.std(np.asarray(block_overshoot_R_sym),axis=1),axis=0)
            sess_undershoot_L_asym[sess_itr] = np.mean(np.mean(np.asarray(block_undershoot_L_asym),axis=1),axis=0)
            sess_std_undershoot_L_asym[sess_itr] = np.std(np.std(np.asarray(block_undershoot_L_asym),axis=1),axis=0)
            sess_undershoot_R_asym[sess_itr] = np.mean(np.mean(np.asarray(block_undershoot_R_asym),axis=1),axis=0)
            sess_std_undershoot_R_asym[sess_itr] = np.std(np.std(np.asarray(block_undershoot_R_asym),axis=1),axis=0)
            sess_undershoot_L_sym[sess_itr] = np.mean(np.mean(np.asarray(block_undershoot_L_sym),axis=1),axis=0)
            sess_std_undershoot_L_sym[sess_itr] = np.std(np.std(np.asarray(block_undershoot_L_sym),axis=1),axis=0)
            sess_undershoot_R_sym[sess_itr] = np.mean(np.mean(np.asarray(block_undershoot_R_sym),axis=1),axis=0)
            sess_std_undershoot_R_sym[sess_itr] = np.std(np.std(np.asarray(block_undershoot_R_sym),axis=1),axis=0
                                                         
                                                         )
            sess_tb_handsep_asym[sess_itr] = np.mean(np.mean(np.asarray(block_tb_handsep_asym),axis=1),axis=0)
            sess_std_tb_handsep_asym[sess_itr] = np.std(np.std(np.asarray(block_tb_handsep_asym),axis=1),axis=0)
            sess_tb_handsep_sym[sess_itr] = np.mean(np.mean(np.asarray(block_tb_handsep_sym),axis=1),axis=0)
            sess_std_tb_handsep_sym[sess_itr] = np.std(np.std(np.asarray(block_tb_handsep_sym),axis=1),axis=0)
            sess_volatility_L_asym[sess_itr] = np.mean(np.mean(np.asarray(block_volatility_L_asym),axis=1),axis=0)
            sess_std_volatility_L_asym[sess_itr] = np.std(np.std(np.asarray(block_volatility_L_asym),axis=1),axis=0)
            sess_volatility_R_asym[sess_itr] = np.mean(np.mean(np.asarray(block_volatility_R_asym),axis=1),axis=0)
            sess_std_volatility_R_asym[sess_itr] = np.std(np.std(np.asarray(block_volatility_R_asym),axis=1),axis=0)
            sess_volatility_L_sym[sess_itr] = np.mean(np.mean(np.asarray(block_volatility_L_sym),axis=1),axis=0)
            sess_std_volatility_L_sym[sess_itr] = np.std(np.std(np.asarray(block_volatility_L_sym),axis=1),axis=0)
            sess_volatility_R_sym[sess_itr] = np.mean(np.mean(np.asarray(block_volatility_R_sym),axis=1),axis=0)
            sess_std_volatility_R_sym[sess_itr] = np.std(np.std(np.asarray(block_volatility_R_sym),axis=1),axis=0)
            
            sess_impacttime_asym_L[sess_itr] = np.mean(np.asarray(block_impacttime_asym_L)[~np.isnan(block_impacttime_asym_L)])
            sess_impacttime_asym_R[sess_itr] = np.mean(np.asarray(block_impacttime_asym_R)[~np.isnan(block_impacttime_asym_R)])
            sess_impacttime_sym_L[sess_itr] = np.mean(np.asarray(block_impacttime_sym_L)[~np.isnan(block_impacttime_sym_L)])
            sess_impacttime_sym_R[sess_itr] = np.mean(np.asarray(block_impacttime_sym_R)[~np.isnan(block_impacttime_sym_R)])
            sess_impact_asym_L[sess_itr] = np.mean(np.asarray(block_impact_asym_L))
            sess_impact_asym_R[sess_itr] = np.mean(np.asarray(block_impact_asym_R))
            sess_impact_sym_L[sess_itr] = np.mean(np.asarray(block_impact_sym_L))
            sess_impact_sym_R[sess_itr] = np.mean(np.asarray(block_impact_sym_R))
            sess_std_impacttime_asym_L[sess_itr] = np.std(np.asarray(block_impacttime_asym_L)[~np.isnan(block_impacttime_asym_L)])
            sess_std_impacttime_asym_R[sess_itr] = np.std(np.asarray(block_impacttime_asym_R)[~np.isnan(block_impacttime_asym_R)])
            sess_std_impacttime_sym_L[sess_itr] = np.std(np.asarray(block_impacttime_sym_L)[~np.isnan(block_impacttime_sym_L)])
            sess_std_impacttime_sym_R[sess_itr] = np.std(np.asarray(block_impacttime_sym_R)[~np.isnan(block_impacttime_sym_R)])
            sess_std_impact_asym_L[sess_itr] = np.std(np.asarray(block_impact_asym_L))
            sess_std_impact_asym_R[sess_itr] = np.std(np.asarray(block_impact_asym_R))
            sess_std_impact_sym_L[sess_itr] = np.std(np.asarray(block_impact_sym_L))
            sess_std_impact_sym_R[sess_itr] = np.std(np.asarray(block_impact_sym_R))
            
            #Make the day-specific plots and report and use the session values.
            ##ToT
        if not os.path.exists(os.path.join(day_save_folder,'Day_Succ_A.png')) or overwrite:
            day_plot([100*x for x in sess_ToT_asym_L], [100*x for x in sess_std_ToT_asym_L], [100*x for x in sess_ToT_asym_R], [100*x for x in sess_std_ToT_asym_R], 'Time on target /\n% of trial time', 'Time on Target for Asymmetric conditions', os.path.join(day_save_folder,'Day_ToT_A.png'))
            day_plot([100*x for x in sess_ToT_sym_L], [100*x for x in sess_std_ToT_sym_L], [100*x for x in sess_ToT_sym_R], [100*x for x in sess_std_ToT_sym_R], 'Time on target /\n% of trial time', 'Time on Target for Symmetric conditions', os.path.join(day_save_folder,'Day_ToT_S.png'))
            
            ##Err
            day_plot([x for x in sess_err_asym_L], [x for x in sess_std_err_asym_L], [x for x in sess_err_asym_R], [x for x in sess_std_err_asym_R], 'Error', 'Error last 500 ms for Asymmetric conditions', os.path.join(day_save_folder,'Day_Err_A.png'))
            day_plot([x for x in sess_err_sym_L], [x for x in sess_std_err_sym_L], [x for x in sess_err_sym_R], [x for x in sess_std_err_sym_R], 'Error', 'Error last 500 ms for Symmetric conditions', os.path.join(day_save_folder,'Day_Err_S.png'))
            
            ##Impact
            day_plot([x for x in sess_impact_asym_L], [x for x in sess_std_impact_asym_L], [x for x in sess_impact_asym_R], [x for x in sess_std_impact_asym_R], 'Impact rate', 'Rate of impact (0.5%) Asymmetric conditions', os.path.join(day_save_folder,'Day_imp_A.png'))
            day_plot([x for x in sess_impact_sym_L], [x for x in sess_std_impact_sym_L], [x for x in sess_impact_sym_R], [x for x in sess_std_impact_sym_R], 'Impact rate', 'Rate of impact (0.5%) Symmetric conditions', os.path.join(day_save_folder,'Day_imp_S.png'))
            
            ##Impacttime
            day_plot([x for x in sess_impacttime_asym_L], [x for x in sess_std_impacttime_asym_L], [x for x in sess_impacttime_asym_R], [x for x in sess_std_impacttime_asym_R], 'Impact time', 'Time of impact (0.5%) Asymmetric conditions', os.path.join(day_save_folder,'Day_impt_A.png'))
            day_plot([x for x in sess_impacttime_sym_L], [x for x in sess_std_impacttime_sym_L], [x for x in sess_impacttime_sym_R], [x for x in sess_std_impacttime_sym_R], 'Impact time', 'Time of impact (0.5%) Symmetric conditions', os.path.join(day_save_folder,'Day_impt_S.png'))
    
            ##Trial Successes, maybe only both relevant
            day_trialsuccess_plot([x for x in sess_trialSuccess_asym_both], [x for x in sess_std_trialSuccess_asym_both], [x for x in sess_trialSuccess_asym_L], [x for x in sess_std_trialSuccess_asym_L], [x for x in sess_trialSuccess_asym_R], [x for x in sess_std_trialSuccess_asym_R], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 300 ms)\nin Asymmetric conditions', os.path.join(day_save_folder,'Day_Succ_A.png'))
            day_trialsuccess_plot([x for x in sess_trialSuccess_sym_both], [x for x in sess_std_trialSuccess_sym_both], [x for x in sess_trialSuccess_sym_L], [x for x in sess_std_trialSuccess_sym_L], [x for x in sess_trialSuccess_sym_R], [x for x in sess_std_trialSuccess_sym_R], 'Successful trials / %', 'Successfully stable (<=0.5% max force for 300 ms)\nin Symmetric conditions', os.path.join(day_save_folder,'Day_Succ_S.png'))
            
            ##handsep
            day_handsep_plot([x for x in sess_handsep_asym], [x for x in sess_std_handsep_asym], 'Force difference', 'Absolute force difference between hands\nAsymmetric condition', os.path.join(day_save_folder,'Day_HandSep_A.png'))
            day_handsep_plot([x for x in sess_handsep_sym], [x for x in sess_std_handsep_sym], 'Force difference', 'Absolute force difference between hands\nSymmetric condition', os.path.join(day_save_folder,'Day_HandSep_S.png'))
            
            ##overshoot
            nbrOfTimeBins=len(block_overshoot_L_asym)
            for itr in range(nbrOfTimeBins):
                day_plot([x[itr] for x in sess_overshoot_L_asym], [x[itr] for x in sess_std_overshoot_L_asym], [x[itr] for x in sess_overshoot_R_asym], [x[itr] for x in sess_std_overshoot_R_asym], 'Overshoot', 'Overshoot timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nAsymmetric condition', os.path.join(day_save_folder,'Day_OS_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_A.png'))
                day_plot([x[itr] for x in sess_overshoot_L_sym], [x[itr] for x in sess_std_overshoot_L_sym], [x[itr] for x in sess_overshoot_R_sym], [x[itr] for x in sess_std_overshoot_R_sym], 'Overshoot', 'Overshoot timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nSymmetric condition', os.path.join(day_save_folder,'Day_OS_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_S.png'))
            ##undershoot 
            for itr in range(nbrOfTimeBins):
                day_plot([x[itr] for x in sess_undershoot_L_asym], [x[itr] for x in sess_std_undershoot_L_asym], [x[itr] for x in sess_undershoot_R_asym], [x[itr] for x in sess_std_undershoot_R_asym], 'Undershoot', 'Undershoot timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nAsymmetric condition', os.path.join(day_save_folder,'Day_US_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_A.png'))
                day_plot([x[itr] for x in sess_undershoot_L_sym], [x[itr] for x in sess_std_undershoot_L_sym], [x[itr] for x in sess_undershoot_R_sym], [x[itr] for x in sess_std_undershoot_R_sym], 'Undershoot', 'Undershoot timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nSymmetric condition', os.path.join(day_save_folder,'Day_US_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_S.png'))
            ##volatility
            for itr in range(nbrOfTimeBins):
                day_plot([x[itr] for x in sess_volatility_L_asym], [x[itr] for x in sess_std_volatility_L_asym], [x[itr] for x in sess_volatility_R_asym], [x[itr] for x in sess_std_volatility_R_asym], 'Volatility', 'Volatility timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nAsymmetric condition', os.path.join(day_save_folder,'Day_vol_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_A.png'))
                day_plot([x[itr] for x in sess_volatility_L_sym], [x[itr] for x in sess_std_volatility_L_sym], [x[itr] for x in sess_volatility_R_sym], [x[itr] for x in sess_std_volatility_R_sym], 'Volatility', 'Volatility timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nSymmetric condition', os.path.join(day_save_folder,'Day_vol_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_S.png'))
            
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
        impacttime_asym_L[day_itr] = np.mean(np.asarray(sess_impacttime_asym_L))
        impacttime_asym_R[day_itr] = np.mean(np.asarray(sess_impacttime_asym_R))
        impacttime_sym_L[day_itr] = np.mean(np.asarray(sess_impacttime_sym_L))
        impacttime_sym_R[day_itr] = np.mean(np.asarray(sess_impacttime_sym_R))
        impact_asym_L[day_itr] = np.mean(np.asarray(sess_impact_asym_L))
        impact_asym_R[day_itr] = np.mean(np.asarray(sess_impact_asym_R))
        impact_sym_L[day_itr] = np.mean(np.asarray(sess_impact_sym_L))
        impact_sym_R[day_itr] = np.mean(np.asarray(sess_impact_sym_R))
        trialSuccess_asym_L[day_itr] = np.mean(np.asarray(sess_trialSuccess_asym_L))
        trialSuccess_asym_R[day_itr] = np.mean(np.asarray(sess_trialSuccess_asym_R))
        trialSuccess_sym_L[day_itr] = np.mean(np.asarray(sess_trialSuccess_sym_L))
        trialSuccess_sym_R[day_itr] = np.mean(np.asarray(sess_trialSuccess_sym_R))
        trialSuccess_asym_both[day_itr] = np.mean(np.asarray(sess_trialSuccess_asym_both))
        trialSuccess_sym_both[day_itr] = np.mean(np.asarray(sess_trialSuccess_sym_both))
        handsep_asym[day_itr] = np.mean(np.asarray(sess_handsep_asym))
        handsep_sym[day_itr] = np.mean(np.asarray(sess_handsep_sym))
        overshoot_L_asym[day_itr] = np.mean(np.asarray(sess_overshoot_L_asym),axis=0)
        overshoot_R_asym[day_itr] = np.mean(np.asarray(sess_overshoot_R_asym),axis=0)
        overshoot_L_sym[day_itr] = np.mean(np.asarray(sess_overshoot_L_sym),axis=0)
        overshoot_R_sym[day_itr] = np.mean(np.asarray(sess_overshoot_R_sym),axis=0)
        undershoot_L_asym[day_itr] = np.mean(np.asarray(sess_undershoot_L_asym),axis=0)
        undershoot_R_asym[day_itr] = np.mean(np.asarray(sess_undershoot_R_asym),axis=0) 
        undershoot_L_sym[day_itr] = np.mean(np.asarray(sess_undershoot_L_sym),axis=0)
        undershoot_R_sym[day_itr] = np.mean(np.asarray(sess_undershoot_R_sym),axis=0)
        tb_handsep_asym[day_itr] = np.mean(np.asarray(sess_tb_handsep_asym),axis=0)
        tb_handsep_sym[day_itr] = np.mean(np.asarray(sess_tb_handsep_sym),axis=0)
        volatility_L_asym[day_itr] = np.mean(np.asarray(sess_volatility_L_asym),axis=0)
        volatility_R_asym[day_itr] = np.mean(np.asarray(sess_volatility_R_asym),axis=0)
        volatility_L_sym[day_itr] = np.mean(np.asarray(sess_volatility_L_sym),axis=0)
        volatility_R_sym[day_itr] = np.mean(np.asarray(sess_volatility_R_sym),axis=0)
        
        ToT_asym_L_std[day_itr] = np.std(np.asarray(sess_ToT_asym_L)) #One value per day
        ToT_asym_R_std[day_itr] = np.std(np.asarray(sess_ToT_asym_R))
        ToT_sym_L_std[day_itr] = np.std(np.asarray(sess_ToT_sym_L))
        ToT_sym_R_std[day_itr] = np.std(np.asarray(sess_ToT_sym_R))
        err_asym_L_std[day_itr] = np.std(np.asarray(sess_err_asym_L))
        err_asym_R_std[day_itr] = np.std(np.asarray(sess_err_asym_R))
        err_sym_L_std[day_itr] = np.std(np.asarray(sess_err_sym_L))
        err_sym_R_std[day_itr] = np.std(np.asarray(sess_err_sym_R))
        impacttime_asym_L_std[day_itr] = np.std(np.asarray(sess_impacttime_asym_L))
        impacttime_asym_R_std[day_itr] = np.std(np.asarray(sess_impacttime_asym_R))
        impacttime_sym_L_std[day_itr] = np.std(np.asarray(sess_impacttime_sym_L))
        impacttime_sym_R_std[day_itr] = np.std(np.asarray(sess_impacttime_sym_R))
        impact_asym_L_std[day_itr] = np.std(np.asarray(sess_impact_asym_L))
        impact_asym_R_std[day_itr] = np.std(np.asarray(sess_impact_asym_R))
        impact_sym_L_std[day_itr] = np.std(np.asarray(sess_impact_sym_L))
        impact_sym_R_std[day_itr] = np.std(np.asarray(sess_impact_sym_R))
        trialSuccess_asym_L_std[day_itr] = np.std(np.asarray(sess_trialSuccess_asym_L))
        trialSuccess_asym_R_std[day_itr] = np.std(np.asarray(sess_trialSuccess_asym_R))
        trialSuccess_sym_L_std[day_itr] = np.std(np.asarray(sess_trialSuccess_sym_L))
        trialSuccess_sym_R_std[day_itr] = np.std(np.asarray(sess_trialSuccess_sym_R))
        trialSuccess_asym_both_std[day_itr] = np.std(np.asarray(sess_trialSuccess_asym_both))
        trialSuccess_sym_both_std[day_itr] = np.std(np.asarray(sess_trialSuccess_sym_both))
        handsep_asym_std[day_itr] = np.std(np.asarray(sess_handsep_asym))
        handsep_sym_std[day_itr] = np.std(np.asarray(sess_handsep_sym))
        overshoot_L_asym_std[day_itr] = np.std(np.asarray(sess_overshoot_L_asym),axis=0)
        overshoot_R_asym_std[day_itr] = np.std(np.asarray(sess_overshoot_R_asym),axis=0)
        overshoot_L_sym_std[day_itr] = np.std(np.asarray(sess_overshoot_L_sym),axis=0)
        overshoot_R_sym_std[day_itr] = np.std(np.asarray(sess_overshoot_R_sym),axis=0)
        undershoot_L_asym_std[day_itr] = np.std(np.asarray(sess_undershoot_L_asym),axis=0)
        undershoot_R_asym_std[day_itr] = np.std(np.asarray(sess_undershoot_R_asym),axis=0) 
        undershoot_L_sym_std[day_itr] = np.std(np.asarray(sess_undershoot_L_sym),axis=0)
        undershoot_R_sym_std[day_itr] = np.std(np.asarray(sess_undershoot_R_sym),axis=0)
        tb_handsep_asym_std[day_itr] = np.std(np.asarray(sess_tb_handsep_asym),axis=0)
        tb_handsep_sym_std[day_itr] = np.std(np.asarray(sess_tb_handsep_sym),axis=0)
        volatility_L_asym_std[day_itr] = np.std(np.asarray(sess_volatility_L_asym),axis=0)
        volatility_R_asym_std[day_itr] = np.std(np.asarray(sess_volatility_R_asym),axis=0)
        volatility_L_sym_std[day_itr] = np.std(np.asarray(sess_volatility_L_sym),axis=0)
        volatility_R_sym_std[day_itr] = np.std(np.asarray(sess_volatility_R_sym),axis=0)
        
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
    ##Tot
    tot_plot([100*x for x in ToT_asym_L], [100*x for x in ToT_asym_L_std], [100*x for x in ToT_asym_R], [100*x for x in ToT_asym_R_std], 'Time on target /\n% of trial time', 'Time on Target for Asymmetric conditions', os.path.join(report_dir,subj,'Tot_ToT_A.png'))
    tot_plot([100*x for x in ToT_sym_L], [100*x for x in ToT_sym_L_std], [100*x for x in ToT_sym_R], [100*x for x in ToT_sym_R_std], 'Time on target /\n% of trial time', 'Time on Target for Symmetric conditions', os.path.join(report_dir,subj,'Tot_ToT_S.png'))
    
    ##Err
    tot_plot([x for x in err_asym_L], [x for x in err_asym_L_std], [x for x in err_asym_R], [x for x in err_asym_R_std], 'Error', 'Error last 500 ms for Asymmetric conditions', os.path.join(report_dir,subj,'Tot_Err_A.png'))
    tot_plot([x for x in err_sym_L], [x for x in err_sym_L_std], [x for x in err_sym_R], [x for x in err_sym_R_std], 'Error', 'Error last 500 ms for Symmetric conditions', os.path.join(report_dir,subj,'Tot_Err_S.png'))
    
    ##Impact
    tot_plot([x for x in impact_asym_L], [x for x in impact_asym_L_std], [x for x in impact_asym_R], [x for x in impact_asym_R_std], 'Impact rate', 'Rate of impact (0.5%) Asymmetric conditions', os.path.join(report_dir,subj,'Tot_imp_A.png'))
    tot_plot([x for x in impact_sym_L], [x for x in impact_sym_L_std], [x for x in impact_sym_R], [x for x in impact_sym_R_std], 'Impact rate', 'Rate of impact (0.5%) Symmetric conditions', os.path.join(report_dir,subj,'Tot_imp_S.png'))
    
    ##Impacttime
    tot_plot([x for x in impacttime_asym_L], [x for x in impacttime_asym_L_std], [x for x in impacttime_asym_R], [x for x in impacttime_asym_R_std], 'Impact time', 'Time of impact (0.5%) Asymmetric conditions', os.path.join(report_dir,subj,'Tot_impt_A.png'))
    tot_plot([x for x in impacttime_sym_L], [x for x in impacttime_sym_L_std], [x for x in impacttime_sym_R], [x for x in impacttime_sym_R_std], 'Impact time', 'Time of impact (0.5%) Symmetric conditions', os.path.join(report_dir,subj,'Tot_impt_S.png'))
    
    ##Trial Successes, maybe only both relevant
    tot_succ_plot([x for x in trialSuccess_asym_both], [x for x in trialSuccess_asym_both_std], [x for x in trialSuccess_asym_L], [x for x in trialSuccess_asym_L_std], [x for x in trialSuccess_asym_R], [x for x in trialSuccess_asym_R_std], 'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Asymmetric conditions', os.path.join(report_dir,subj,'Tot_Succ_A.png'))
    tot_succ_plot([x for x in trialSuccess_sym_both], [x for x in trialSuccess_sym_both_std], [x for x in trialSuccess_sym_L], [x for x in trialSuccess_sym_L_std], [x for x in trialSuccess_sym_R], [x for x in trialSuccess_sym_R_std], 'Successful trials / %', 'Successfully stable\n(<=0.5% max force for 300 ms)\nin Symmetric conditions', os.path.join(report_dir,subj,'Tot_Succ_S.png'))
    
    ##handsep
    tot_handsep_plot([x for x in handsep_asym], [x for x in handsep_asym_std], 'Force difference', 'Absolute force difference between hands\nAsymmetric condition', os.path.join(report_dir,subj,'Tot_HandSep_A.png'))
    tot_handsep_plot([x for x in handsep_sym], [x for x in handsep_sym_std], 'Force difference', 'Absolute force difference between hands\nSymmetric condition', os.path.join(report_dir,subj,'Tot_HandSep_S.png'))
    
    ##overshoot
    for itr in range(nbrOfTimeBins):
        tot_plot([x[itr] for x in overshoot_L_asym], [x[itr] for x in overshoot_L_asym_std], [x[itr] for x in overshoot_R_asym], [x[itr] for x in overshoot_R_asym_std], 'Overshoot', 'Overshoot timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nAsymmetric condition', os.path.join(report_dir,subj,'Tot_OS_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_A.png'))
        tot_plot([x[itr] for x in overshoot_L_sym], [x[itr] for x in overshoot_L_sym_std], [x[itr] for x in overshoot_R_sym], [x[itr] for x in overshoot_R_sym_std], 'Overshoot', 'Overshoot timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nSymmetric condition', os.path.join(report_dir,subj,'Tot_OS_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_S.png'))
    ##undershoot 
    for itr in range(nbrOfTimeBins):
        tot_plot([x[itr] for x in undershoot_L_asym], [x[itr] for x in undershoot_L_asym_std], [x[itr] for x in undershoot_R_asym], [x[itr] for x in undershoot_R_asym_std], 'Undershoot', 'Undershoot timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nAsymmetric condition', os.path.join(report_dir,subj,'Tot_US_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_A.png'))
        tot_plot([x[itr] for x in undershoot_L_sym], [x[itr] for x in undershoot_L_sym_std], [x[itr] for x in undershoot_R_sym], [x[itr] for x in undershoot_R_sym_std], 'Undershoot', 'Undershoot timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nSymmetric condition', os.path.join(report_dir,subj,'Tot_US_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_S.png'))
    ##volatility
    for itr in range(nbrOfTimeBins):
        tot_plot([x[itr] for x in volatility_L_asym], [x[itr] for x in volatility_L_asym_std], [x[itr] for x in volatility_R_asym], [x[itr] for x in volatility_R_asym_std], 'Volatility', 'Volatility timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nAsymmetric condition', os.path.join(report_dir,subj,'Tot_vol_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_A.png'))
        tot_plot([x[itr] for x in volatility_L_sym], [x[itr] for x in volatility_L_sym_std], [x[itr] for x in volatility_R_sym], [x[itr] for x in volatility_R_sym_std], 'Volatility', 'Volatility timebin '+str(itr+1)+' of '+str(nbrOfTimeBins)+'\nSymmetric condition', os.path.join(report_dir,subj,'Tot_vol_'+str(itr+1)+'of'+str(nbrOfTimeBins)+'_S.png'))
    
    
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

    subj_dir = os.path.join(report_dir,subj)
    report=PDF()
    tot_plots_per_page_1 = ['Tot_ToT_A.png', 'Tot_ToT_S.png', 'Tot_Err_A.png', 'Tot_Err_S.png', 'Tot_vol_3of3_A.png', 'Tot_vol_3of3_S.png', 'Tot_Handsep_A.png', 'Tot_Handsep_S.png']
    tot_plots_per_page_1 = [os.path.join(subj_dir,x) for x in tot_plots_per_page_1]
    report.print_page(tot_plots_per_page_1)
    tot_plots_per_page_2 = ['MaxForces.png', 'TimeOfDay.png', 'Sleep.png', 'PA_table.png']
    tot_plots_per_page_2 = [os.path.join(subj_dir,x) for x in tot_plots_per_page_2]
    report.print_page(tot_plots_per_page_2)
        
    report.output(subj+'_training.pdf', 'F')
    os.rename(subj+'_training.pdf', os.path.join(subj_dir,subj+'_training.pdf'))

