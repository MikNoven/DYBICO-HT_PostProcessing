#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 09:35:05 2023

@author: gdf724
"""
import os
import pandas as pd 
import postproc_helper_HT as pph
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np


path='/Users/gdf724/Data/ReScale/HomeTrainingTest/'
list_of_subjs=['P001', 'P002', 'P003']
report_dir='/Users/gdf724/Data/ReScale/HomeTrainingTest/Reports'

for subj in list_of_subjs:
    HT_days = pph.get_HTfolders(path, subj)
    sleep_times=[]
    sleep_qualities=[]
    physical_activity_matrix=[]
    pa_rows = ['Training day %d' % x for x in range(1,len(HT_days)+1)]
    pa_columns = ('Brisk walk', 'Cardio', 'Swimming', 'Weight training', 'Other')
    
    for day_itr in range(len(HT_days)): #Check if it's not already done and if overwrite is false
        day_save_folder = os.path.join(report_dir,subj,'Day_'+str(day_itr+1))
        day_path = HT_days[day_itr]
        (sleep_time, sleep_quality, bwalk, cardio, swim, wtrain, ot, what_ot) = pph.get_survey_answers(day_path)
        sleep_times.append(sleep_time)
        sleep_qualities.append(sleep_quality)
        physical_activity_matrix.append([str(day_itr+1), bwalk, cardio, swim, wtrain, ot])

    plt.ioff()
    PA_df = pd.DataFrame(data=physical_activity_matrix, columns=['TrainingDay', 'Walk/h', 'Cardio/h', 'Swimming/h', 'Weight Training/h', 'Other/h'])
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

        