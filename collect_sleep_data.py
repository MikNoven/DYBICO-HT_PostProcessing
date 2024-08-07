#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 10:13:41 2024

@author: gdf724
"""
##############Import necessary libraries###################
import os
import pandas as pd 
import glob
import postproc_helper_HT as pph 

##############Set paths and plot options###################
#Change to where you have your data.
path='/Users/gdf724/Data/ReScale/ReScale2_HomeTraining'
#List all subjects to process.
output_dir='/Users/gdf724/Data/ReScale/ReScale2_HTquestionnaires/'
sub_dir_list = sorted(glob.glob(os.path.join(path,'*/')))
list_of_subjs = [x[-5:-1] for x in sub_dir_list]

for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    HT_days = pph.get_HTfolders(path, subj)
    dates = []
    max_forces_L=[] 
    max_forces_R=[]
    time_of_day=[]
    sleep_times=[]
    sleep_qualities=[]
    pa_bw = []
    pa_ca = []
    pa_sw = []
    pa_wt = []
    pa_ot = []
    pa_wo = []

    for day_itr in range(len(HT_days)): 
        day_path = HT_days[day_itr]
        if os.path.exists(os.path.join(day_path,'SurveyAnswers.txt')):
            dates.append(os.path.basename(day_path)[0:8])
            (sleep_time, sleep_quality, bwalk, cardio, swim, wtrain, ot, what_ot) = pph.get_survey_answers(day_path)
            sleep_times.append(sleep_time)
            sleep_qualities.append(sleep_quality)
            pa_bw.append(bwalk)
            pa_ca.append(cardio)
            pa_sw.append(swim)
            pa_wt.append(wtrain)
            pa_ot.append(ot)
            pa_wo.append(what_ot)
            with open(os.path.join(day_path,'PostProcessing','maxforce.csv')) as mf:
                max_forces_L.append(float(mf.readline())) #Double check the order of the hands.
                max_forces_R.append(float(mf.readline()))
            tmp_timeofday = pph.get_DATAfiles(day_path)[0][-8:-4]
            time_of_day.append(float(tmp_timeofday[0:2])+float(tmp_timeofday[2:])/60) #Defined as hours.
            
    #Save the output for the subject
    data = {'Date':dates,'TimeOfTraining':time_of_day, 
                             'Sleep_hours':sleep_times, 'Sleep_quality':sleep_qualities,
                             'Brisk walk':pa_bw, 'Cardio':pa_ca, 'Swimming':pa_sw, 'Weight training':pa_wt, 
                             'Other':pa_ot, 'WhatOther':pa_wo}
    save_df = pd.DataFrame(data)
    save_df.to_csv(os.path.join(output_dir,subj+'_HT_questionnairedata.csv'),sep=';', index=False)
    