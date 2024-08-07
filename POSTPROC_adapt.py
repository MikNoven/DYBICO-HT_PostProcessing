#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 15:03:23 2023
Script for post-processing of the adaptation data.
@author: gdf724
"""

##############Import necessary libraries###################
import os
import pandas as pd 
import glob
import postproc_helper_HT as pph 


##############Set paths and plot options###################
path='/Users/gdf724/Data/ReScale/ReScale2_Adapt/'
report_dir='/Users/gdf724/Data/ReScale/ReScale2_reports/fMRI/'
background_path = '/Users/gdf724/Data/ReScale/ReScale2_Pretests/ReScale2_background.xlsx'
#list_of_subjs = ['y005']
sub_dir_list = sorted(glob.glob(os.path.join(path,'*/')))
list_of_subjs = [x[-5:-1] for x in sub_dir_list]
#Do you want to make videos and a pdf report?
makeVideos = False 
makeReport = True
#Do you want to f average trajectory plots for each run and condition?
overwrite = False
logtransform = True #Whether to logtransform data
make_stats_file = True


for i in range(len(list_of_subjs)):
    subj = list_of_subjs[i]
    adapt_days = pph.get_HTfolders(path,subj)
    