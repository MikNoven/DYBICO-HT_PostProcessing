#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 10:45:21 2023
Script to make videos of continuous playing the game on 2D-form. 
Will make one video for each session within each day and save it in the report_dir.
@author: gdf724
"""

##############Import libraries###################
import os
import pandas as pd 
import glob
import postproc_helper_HT as pph 
import matplotlib.pyplot as plt
import cv2
import numpy as np

##############Set paths###################
#Change to where you have your data.
path='/Users/gdf724/Data/ReScale/HomeTrainingTest/' 
report_dir='/Users/gdf724/Data/ReScale/HomeTrainingTest/Videos'
#List all subjects to process.
list_of_subjs=['P005']
overwrite = False

##############Plot settings###################
displayWindow = 3 #The time in seconds that is covered in each time frame.
imgResolution = 45 #dpi of saved plots
timeCoarsness = 10 #Reduce the timepoints of plotting. 

#Start with day 1 session 1
for subj in list_of_subjs:
    HT_days = pph.get_HTfolders(path,subj)
    for day_nbr in range(1,len(HT_days)+1):
        day = HT_days[day_nbr-1]
        sessionFiles = sorted(glob.glob(os.path.join(day,'hometraining_output_*.pkl')))
        
        for session in range(1,len(sessionFiles)+1):
            if not os.path.exists(os.path.join(report_dir,subj,'Day_'+str(day_nbr),'Session_'+str(session)+'_video','Session_'+str(session)+'.mp4')) or overwrite:
                data = pd.read_pickle(sessionFiles[session-1])
                
                ##############Plotting###################
                #Needed metadata in title: 
                    #Session
                    #Block (in total)
                    #Condition-specific block
                    #condition
                
                #data column names: 
                    #target_name
                    #target
                    #trial one number for each trial
                    #left_force
                    #right_force
                    #time 
                target_names = data['target_name'][0]
                targets = data['target'][0] #Split into left and right hand targets.
                left_target = [x[0] for x in targets]
                right_target = [x[1] for x in targets]
                left_F = data['left_force'][0]
                right_F = data['right_force'][0]
                time = data['time'][0]
                #Possibly recalculate time to be smooth. Try without and see how bad it is
                
                video_folder = os.path.join(report_dir,subj,'Day_'+str(day_nbr),'Session_'+str(session)+'_video')
                if not os.path.exists(video_folder):
                    os.makedirs(video_folder)
                
                timediff = np.diff(time)
                dt = np.median(timediff)
                indx_window = round(displayWindow/dt)
                
                
                start_indx = 0
                itr=0
                images = []
                while start_indx+indx_window < len(time):
                    tw_indx = [start_indx,start_indx+indx_window]
                    plt.ioff()
                    plt.figure(itr)
                    plt.xlim((time[tw_indx[0]],time[tw_indx[1]]))
                    plt.ylim([0,1.5])
                    plt.plot(time[tw_indx[0]:tw_indx[1]],right_F[tw_indx[0]:tw_indx[1]], 'r', label="Right force")
                    plt.plot(time[tw_indx[0]:tw_indx[1]],right_target[tw_indx[0]:tw_indx[1]], 'r--', label="Right target")
                    plt.plot(time[tw_indx[0]:tw_indx[1]],left_F[tw_indx[0]:tw_indx[1]], 'b', label="Left force")
                    plt.plot(time[tw_indx[0]:tw_indx[1]],left_target[tw_indx[0]:tw_indx[1]], 'b--', label="Left target")
                    plt.xlabel('Seconds')
                    plt.ylabel('Maxforce')
                    plt.yticks([0.25, 0.5, 0.75, 1.0, 1.25], ['2.5%', '5%', '7.5%', '10%', '12.5%'])
                    #plt.show()
                    # save the figure 
                    images.append(os.path.join(video_folder,str(itr)+'.png'))
                    plt.savefig(images[-1],dpi=imgResolution)
                    plt.close()
                    start_indx += timeCoarsness
                    itr += 1
                
                
                ##############Put into video###################
                frame = cv2.imread(os.path.join(images[0]))
                height, width, layers = frame.shape
                #Chande codec
                video = cv2.VideoWriter(os.path.join(video_folder,'Session_'+str(session)+'.mp4'), cv2.VideoWriter_fourcc('M','P','4','V'), 1/(timeCoarsness*dt), (width,height))
                
                for image in images:
                    video.write(cv2.imread(image))
                
                video.release()
