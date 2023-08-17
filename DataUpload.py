#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 12:40:15 2023
Script for smart upload of ReScale2 data. 
@author: gdf724
"""

import os
import glob
import shutil

datadir = '/Users/gdf724/Data/ReScale/'
erdadir = '/Volumes/io.erda.dk/NEXS/Sections/MN/VIP_Projects/ReScale/ReScale2/04_Data/01_DataFiles/'

#fMRI data
for subj in glob.glob(os.path.join(datadir,'ReScale2_fMRI_behavior','*')):
    if subj.find('.') == -1:
        subject = os.path.basename(subj)
        if not os.path.isdir(os.path.join(erdadir,'00_MRI_Behavioral_Data',subject)):
            os.mkdir(os.path.join(erdadir,'00_MRI_Behavioral_Data',subject))
        for day in glob.glob(os.path.join(subj,'*')):
            tmp = os.path.basename(day)
            if not os.path.isdir(os.path.join(erdadir,'00_MRI_Behavioral_Data',subject,tmp)):
                shutil.copytree(day,os.path.join(erdadir,'00_MRI_Behavioral_Data',subject,tmp))
            
#Adapt
for subj in glob.glob(os.path.join(datadir,'ReScale2_Adapt','*')):
    if subj.find('.') == -1:
        subject = os.path.basename(subj)
        if not os.path.isdir(os.path.join(erdadir,'00_ADAPT_Behavioral_Data',subject)):
            os.mkdir(os.path.join(erdadir,'00_ADAPT_Behavioral_Data',subject))
        for day in glob.glob(os.path.join(subj,'*')):
            tmp = os.path.basename(day)
            if not os.path.isdir(os.path.join(erdadir,'00_ADAPT_Behavioral_Data',subject,tmp)):
                shutil.copytree(day,os.path.join(erdadir,'00_ADAPT_Behavioral_Data',subject,tmp))
            
#Pretests
local_time = os.path.getmtime(os.path.join(datadir,'ReScale2_Pretests','ReScale2_background.xlsx'))
target_time = os.path.getmtime(os.path.join(erdadir,'00_Survey_Data','ReScale2_background.xlsx'))
if target_time < local_time:
    shutil.copyfile(os.path.join(datadir,'ReScale2_Pretests','ReScale2_background.xlsx'),os.path.join(erdadir,'00_Survey_Data','ReScale2_background.xlsx'))
#Reports? 

