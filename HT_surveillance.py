#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:00:45 2023
Script for downloading the hometraining data from active participants and 
make sure they're doing alright. 

TODO: 
    Make sure it's possible to download/upload from scripts. Ask Andreas.
@author: gdf724
"""

import os
import glob
import shutil
import datetime
import pysftp
import Configuration.ConfigurationReader as configReader

#/NEXS/Sections/MN/VIP_Projects/ReScale/ReScale2/04_Data/01_DataFiles/00_Raw_Data

def LogOntoERDA(config):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    host = configReader.GetHost(config)
    user = configReader.GetUser(config)
    psw = configReader.GetPsw(config)
    srv = pysftp.Connection(host=host, username=user, password=psw,port= 22, cnopts=cnopts)
    return srv
    

datadir = '/Users/gdf724/Data/ReScale/ReScale2_HomeTraining/'
config = configReader.readConfiguration()
erdadir = configReader.GetRemotepath(config) 

server = LogOntoERDA(config)
HT_list = server.listdir(erdadir)
server.close()

active_subjects = ['y027', 'o029'] #y002 and o001 are special cases and handled accordingly. 
latest_training = [0]*len(active_subjects)


#Fix this after.
for subj_itr in range(len(active_subjects)):
    subject = active_subjects[subj_itr]
    if subject == 'y014':
        erdasub = 'o007'
    elif subject == 'o007':
        erdasub = 'y014'
    else:
        erdasub = subject
    
    sub_HT_list = [x for x in HT_list if len(x)>4 and x[-4:]==erdasub]
    
    #Check for multiple training days and clean up HT list
    last_day = '0'
    del_indices = []
    for itr in range(len(sub_HT_list)):
        tmp = os.path.basename(sub_HT_list[itr])
        datestamp = tmp[:-11]
        if datestamp==last_day:
            del_indices.append(itr-1)
        last_day = datestamp
    
    if last_day != '0':
        latest_training_day = datetime.datetime.strptime(last_day, '%Y%m%d')
        timesincetraining = datetime.datetime.today()-latest_training_day
        latest_training[subj_itr] = timesincetraining.days
    else:
        latest_training[subj_itr] = 'Has not trained!'
    
    for ind in sorted(del_indices, reverse=True):
        del sub_HT_list[ind]
    
    for htday in sub_HT_list:
        day = os.path.basename(htday)
        datestamp = day[:-5]
        #Check if there's a newer version uploaded.
        if not os.path.exists(os.path.join(datadir,subject)):
            os.mkdir(os.path.join(datadir,subject))
        if not os.path.exists(os.path.join(datadir,subject,datestamp+'_'+subject)):
            os.mkdir(os.path.join(datadir,subject,datestamp+'_'+subject))
            os.mkdir(os.path.join(datadir,subject,datestamp+'_'+subject,'Maxforce'))
            server = LogOntoERDA(config)
            server.get_d(remotedir='/'+erdadir+'/'+datestamp+'_'+erdasub, localdir=os.path.join(datadir,subject,datestamp+'_'+subject))
            server.get_d(remotedir='/'+erdadir+'/'+datestamp+'_'+erdasub+'/Maxforce', localdir=os.path.join(datadir,subject,datestamp+'_'+subject,'Maxforce'))
            server.close()

    
print('Active subject: Days since training:')
for subj_itr in range(len(active_subjects)):
    subject = active_subjects[subj_itr]
    print(subject+'                   '+str(latest_training[subj_itr]))