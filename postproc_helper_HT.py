# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 15:27:24 2021

@author: dzn332
"""

import numpy as np
import os

#%% drop non-trials 
def drop_non_trials(file):
    # drop all non-trials, i.e. pauses 
    data = file.copy()
    data.drop(data[data['dropindex']==True].index, inplace=True) 
    data.drop("dropindex",1,inplace=True)
    data.index = range(len(data)) 
    
    return data 



#%% sort the data
def sort_data_by_condition(data):
    # list unique conditions & list of conditions 
    import numpy as np
    conditions = data['targetTrial']
    ucon = np.unique(conditions)
    
    # make dummy variables specific for all the included conditions
    import pandas as pd 
    dummies=pd.DataFrame()
    con_matrix = []
    for i in range(len(ucon)):
        d_name = str('d_'+ucon[i])
        dummy=[]
        for j in range(len(conditions)):
            if conditions[j]==ucon[i]:
                dummy.append(1)
            else:
                dummy.append(0)
        dummies[d_name]=dummy
        con_matrix.append(data[dummies[d_name]==1])
        
    return con_matrix 



#%% extract force and target and time data 
def extract_as_arrays(con_data):
    # we find the shortest trial lenght (due to jitter time inconsistencies)
    
    shortest_trial = min([len(con_data['time'][j]) for j in range(len(con_data))])
    
    # we extract the force and find the average trace 
    import numpy as np 
    force_L = np.vstack([np.asarray(con_data['force_L'][j][:shortest_trial]) for j in range(len(con_data))])
    force_R = np.vstack([np.asarray(con_data['force_R'][j][:shortest_trial]) for j in range(len(con_data))])
    
    # jittertime in onset/dur, makes to baseline vary between point 114 and 122. 
    t_L, t_R  = [], []
    for j in range(len(con_data)) : 
        t_L.append([np.asarray(con_data['targets'][j][k][0]) for k in range(shortest_trial)])
        t_R.append([np.asarray(con_data['targets'][j][k][1]) for k in range(shortest_trial)])
    target_L = np.vstack(t_L)
    target_R = np.vstack(t_R)
    
    # get time data 
    time = np.vstack([np.asarray(con_data['time'][j][:shortest_trial]) for j in range(len(con_data))]) 

    #Shortest trial is the index at which the shortest end. 
    return (shortest_trial, force_L, force_R, target_L, target_R, time)
  

#%% rebase force trace to match template time
def rebase_force(t_new,t_new_dur,t_orig,t_orig_dur,force_orig):
    import numpy as np
    #Convert to arrays.
    t_orig=np.asarray(t_orig)
    t_orig = np.asarray([(t_orig[j]-t_orig[0]) for j in range(len(t_orig))])
    force_orig=np.asarray(force_orig)
    force_new=np.zeros(len(t_new))
    
    t_orig_itr = 0
    for n in range(0,len(t_new)):
        tmp_tnew = t_new[n]
        if n > len(t_new)-1 or t_orig_itr > len(t_orig)-1:
            break
        elif n == len(t_new)-1:
            tmp_tnew_ts = t_new_dur-t_new[n]
        else:
            tmp_tnew_ts = t_new[n+1]-t_new[n]
        stop = False
        while not stop: 
            tmp_torig = t_orig[t_orig_itr]
            if t_orig_itr == len(t_orig)-1:
                tmp_torig_ts = t_orig_dur-t_orig[t_orig_itr]
            else:
                tmp_torig_ts = t_orig[t_orig_itr+1]-t_orig[t_orig_itr]
                
            if tmp_tnew > tmp_torig and t_new[n]+tmp_tnew_ts > t_orig[t_orig_itr]+tmp_torig_ts:
                #print('1 '+str(n)+' '+str(((t_orig[t_orig_itr]+tmp_torig_ts-tmp_tnew)/tmp_tnew_ts)))
                force_new[n] = force_new[n]+force_orig[t_orig_itr]*((t_orig[t_orig_itr]+tmp_torig_ts-tmp_tnew)/tmp_tnew_ts)
                t_orig_itr = t_orig_itr + 1
            elif tmp_tnew > tmp_torig and t_new[n]+tmp_tnew_ts < t_orig[t_orig_itr]+tmp_torig_ts:
                #print('2 '+str(n)+' '+str(tmp_tnew_ts/tmp_torig_ts))
                force_new[n] = force_new[n]+force_orig[t_orig_itr]#Leave entire in as it completely fills the element.
                stop = True
            elif tmp_tnew < tmp_torig and t_new[n]+tmp_tnew_ts < t_orig[t_orig_itr]+tmp_torig_ts:
                #print('3 '+str(n)+' '+str((t_new[n]+tmp_tnew_ts-tmp_torig)/tmp_tnew_ts))
                force_new[n] = force_new[n]+force_orig[t_orig_itr]*((t_new[n]+tmp_tnew_ts-tmp_torig)/tmp_tnew_ts)
                stop = True
            elif tmp_tnew < tmp_torig and t_new[n]+tmp_tnew_ts > t_orig[t_orig_itr]+tmp_torig_ts:
                #print('4 '+str(n)+' '+str(tmp_torig_ts/tmp_tnew_ts))
                force_new[n] = force_new[n]+force_orig[t_orig_itr]*(tmp_torig_ts/tmp_tnew_ts)
                t_orig_itr = t_orig_itr + 1
            elif tmp_tnew == tmp_torig and t_new[n]+tmp_tnew_ts == t_orig[t_orig_itr]+tmp_torig_ts:
                #print('5 '+str(n)+' '+str(1))
                force_new[n] = force_new[n]+force_orig[t_orig_itr]
                t_orig_itr = t_orig_itr + 1
                stop = True
            elif tmp_tnew == tmp_torig and t_new[n]+tmp_tnew_ts > t_orig[t_orig_itr]+tmp_torig_ts:
                #print('6 '+str(n)+' '+str(tmp_torig_ts/tmp_tnew_ts))
                force_new[n] = force_new[n]+force_orig[t_orig_itr]*(tmp_torig_ts/tmp_tnew_ts)
                t_orig_itr = t_orig_itr + 1
            elif tmp_tnew == tmp_torig and t_new[n]+tmp_tnew_ts < t_orig[t_orig_itr]+tmp_torig_ts:
                #print('7 '+str(n)+' '+str(tmp_tnew_ts/tmp_torig_ts))
                force_new[n] = force_new[n]+force_orig[t_orig_itr]#Leave entire in as it completely fills the element.
                stop = True
            elif tmp_tnew > tmp_torig and t_new[n]+tmp_tnew_ts == t_orig[t_orig_itr]+tmp_torig_ts:
                #print('8 '+str(n)+' '+str(tmp_tnew_ts/tmp_torig_ts))
                force_new[n] = force_new[n]+force_orig[t_orig_itr]#Leave entire in as it completely fills the element.
                t_orig_itr = t_orig_itr + 1
                stop = True
            elif tmp_tnew < tmp_torig and t_new[n]+tmp_tnew_ts == t_orig[t_orig_itr]+tmp_torig_ts:
                #print('9 '+str(n)+' '+str(tmp_torig_ts/tmp_tnew_ts))
                force_new[n] = force_new[n]+force_orig[t_orig_itr]*(tmp_torig_ts/tmp_tnew_ts)
                t_orig_itr = t_orig_itr + 1
                stop = True
                
            if t_orig_itr > len(t_orig)-1:
                break
        
                
    #Fix the final timestep
    return force_new.tolist()

#%% extract force and target and time data 
def extract_as_arrays_rebase(con_data):
    import numpy as np 
    # we find the shortest trial lenght (due to jitter time inconsistencies and sampling weirdness)
    indx_shortest = 0
    shortest_time = 2.0
    shortest_dur = 0
    for j in range(len(con_data)):
        tmp_ts = con_data['duration'][j]
        if tmp_ts < shortest_time:            
            #print(str(j))
            shortest_time = tmp_ts
            indx_shortest=j
            shortest_dur = con_data['duration'][j]
    
    
    #Create t_new
    t = np.asarray(con_data['time'][indx_shortest])
    time = np.asarray([(t[j]-t[0]) for j in range(len(t))])
    
    forces_L = []
    forces_R = []
    
    for m in range(len(con_data)):
        tmp_ts = (con_data['time'][m][-1]-con_data['time'][m][0])/len(con_data['time'][m])
        if m == indx_shortest:
            forces_L.append(con_data['force_L'][m])
            forces_R.append(con_data['force_R'][m])
        else:
            forces_L.append(rebase_force(time,shortest_dur,con_data['time'][m],con_data['duration'][m],con_data['force_L'][m]))
            forces_R.append(rebase_force(time,shortest_dur,con_data['time'][m],con_data['duration'][m],con_data['force_R'][m]))
    
    # we extract the force and find the average trace 
    force_L = np.vstack(forces_L)
    force_R = np.vstack(forces_R)
    
    target_L = [con_data['targets'][indx_shortest][k][0] for k in range(len(time))]
    target_R = [con_data['targets'][indx_shortest][k][1] for k in range(len(time))]
    
    return (force_L, force_R, target_L, target_R, time)
    

#%% get list of DATA files in log folder
def get_DATAfiles(logdir):
    import os     
    import glob
    DATAfiles = []
    for file in glob.glob(os.path.join(logdir,'PostProcessing','DATA_file*.pkl')):
        DATAfiles.append(file)
    
    return sorted(DATAfiles)



#%% Make a folder for each condition
def make_cond_folder(filepath, con_data):
    import os 
    title = con_data['targetTrial'][0]
    os.chdir(os.path.split(filepath)[0])
    if not os.path.exists(title): os.makedirs(title)

    

#%% save figure 
# def save_fig(filepath,con_data,saveID):
#     import os 
#     title = con_data['targetTrial'][0]
#     os.chdir(os.path.join(os.path.split(filepath)[0]))

#     import matplotlib.pyplot as plt    
#     plt.savefig(saveID+'.png')
    
    # save variables: force, targets, time, before and after averaging 
    # import numpy as np
    # cond_data = np.vstack([force_L, force_R, target_L, target_R, time])
    # np.savetxt(saveID+".npy", cond_data, delimiter=",")
    # os.chdir(os.path.split(filepath)[0])               
    


#%% Get the hometraining folders
def get_HTfolders(datapath,subj):
    import os 
    import glob
    HTfolders = []
    for folder in glob.glob(os.path.join(datapath,subj,'*_'+subj)):
        HTfolders.append(folder)
    
    return sorted(HTfolders)

#%% run loop across list of subjs 
def preproc_loop(list_of_subjs, path):
    import postproc_helper_HT as pph 
    import os 
    
    for i in range(len(list_of_subjs)):
        # Specify log ID
        log = list_of_subjs[i]
        
        # read all output files from folder
        outputfiles = pph.get_outputfiles(os.path.join(path,log))
        
        for k in range(len(outputfiles)):
            datafile = outputfiles[k]   
            filepath = os.path.join(path,log,datafile)
            
            # make directory structure 
            pph.make_PP_folder(filepath)
            
            # save tables.png with info on settings
            settings = pph.print_settings(filepath)
            
            # get maxforce for that subj 
            maxforce = pph.get_maxforce(filepath)
            
            # reshape the data and save as file 
            data_file = pph.reshape_data(filepath)
            
    return (maxforce, settings, data_file, filepath)



#%% get list of output files in log folder
def get_outputfiles(logdir):
    import os 
    os.chdir(logdir)
    
    import glob
    outputfiles = []
    for file in glob.glob("output_file*.pkl"):
        outputfiles.append(file)
    
    if len(outputfiles) == 0:
        for file in glob.glob("correctdata/output_file*.pkl"):
            outputfiles.append(file)
    
    if len(outputfiles)<3 : 
        print('ERROR NOT ENOUGH OUTPUT FILES, CHECK FOLDER')
    elif len(outputfiles)>3 : 
        print('ERROR TOO MANY OUTPUT FILES, CHECK FOLDER')
    
    return outputfiles



#%% Make a folder for post processing data
def make_PP_folder(sesspath):
    import os 
    
    if not os.path.exists(os.path.join(sesspath,'PostProcessing')): os.makedirs(os.path.join(sesspath,'PostProcessing'))
    #PPpath=os.path.join(logpath,'PostProcessing')
    #return PPpath 



#%% print settings out in figure 
def print_settings(filepath):
    import pandas as pd 
    file=pd.read_pickle(filepath) # load file 
    
    settings = file['settings'][0]
    settings_cond = settings.loc[:, ['Baseline_force', 'Left_increase_force', 'Left_decrease_force',
       'Right_increase_force', 'Right_decrease_force', 'Sym_increase_force',
       'Sym_decrease_force', 'Asym_L_increase_R_decrease',
       'Asym_L_decrease_R_increase']]
    settings_ = settings.loc[:, ['no_of_blocks', 'time_between_blocks',
       'trial_repetitions', 'trial_duration', 'jitter_time',
       'baseline_between_trials', 'percent_change_from_baseline',
       'percent_of_maxforce', 'smoothing']]
    
    
    #save figures with information
    import os
    os.chdir(os.path.join(os.path.split(filepath)[0],'PostProcessing'))
    import dataframe_image as dfi # pip install dataframe_image
    df_styled = settings_.style.background_gradient() #adding a gradient based on values in cell
    dfi.export(df_styled,"table_of_settings.png")
    df_styled = settings_cond.style.background_gradient() #adding a gradient based on values in cell
    dfi.export(df_styled,"table_of_conditions.png")
    os.chdir(os.path.split(filepath)[0])
    
    return settings 



#%% print out maxforce from 
def get_maxforce(sess):
    import pandas as pd 
    import os 
    import numpy as np  
    file=pd.read_pickle(os.path.join(sess,'Maxforce','maxforce.pkl')) #% load file 

    # print out maxforce 
    maxforce = file[0]
    
    # save as csv file 
    np.savetxt(os.path.join(sess,'PostProcessing',"maxforce.csv"), np.asarray(maxforce), delimiter=",")

    return maxforce



#%% reshape output file to data file structure 
def reshape_data(filepath): # change output file structure  
    import pandas as pd 
    file=pd.read_pickle(filepath) #% load file 

    # first we rearrange single-entry data per trial 
    trial_no = file['trial'][0] 
    trial_shifts = file['save_trialshift'][0] 
    data = pd.DataFrame()
    targets_, onsets_, durations_, t_, indices = [], [],[],[],[]
    for j in range(len(trial_shifts)): 
        targets_.append(str(trial_shifts[j][1]))
        [_, _, onset, duration, t]=trial_shifts[j] 
        onsets_.append(onset)
        durations_.append(duration)
        t_.append(t)
        
        # we need to seperate the data according to trial, so we group the indices 
        trial_ = trial_shifts[j][0]
        indices_ = [i for i, x in enumerate(trial_no) if x == trial_]
        indices.append(indices_)
    data['targetTrial'] = targets_
    data['onsets']= onsets_
    data['duration'] = durations_
    data['t'] = t_ 
    data['indices'] = indices 
    
    # We mark intermediate data ie pauses, in this new dataframe 
    dropindex = []
    for j in range(len(trial_shifts)): 
        dropindex.append(data['targetTrial'][j][:5] =='Pause')
        if dropindex[j] == False : dropindex[j] = data['duration'][j]==0.5000 
    data['dropindex']=dropindex
    #data.drop(data[data['dropindex']==True].index, inplace=True) 
    #data.drop("dropindex",1,inplace=True)
    #data.index = range(len(data)) 

    # we then use indices calculated previously, to sort arrays in trials
    force_L, force_R, time, fliptime, target_names, targets = [], [], [],[], [],[]
    #test_unique = [] # only to ensure the code was correct 
    for j in range(len(trial_shifts)):
        idx = data.loc[j,'indices']
        force_L.append(file['left_force'][0][min(idx):max(idx)+1])
        force_R.append(file['right_force'][0][min(idx):max(idx)+1])
        time.append(file['time'][0][min(idx):max(idx)+1])
        targets.append(file['target'][0][min(idx):max(idx)+1])
        #fliptime.append(file['fliptime'][0][min(idx):max(idx)+1])
        #target_names.append(file['target_name'][0][min(idx):max(idx)+1])
        #test_unique.append(np.unique(file['target_name'][0][min(idx):max(idx)+1]))
    data['force_L'] = force_L
    data['force_R'] = force_R
    data['time'] = time
    data['targets'] = targets
    #data['fliptime'] = fliptime # about 31 millisecond difference 
    #data['target_names'] = target_names
    
    
    # Save the data file 
    import os
    PPpath = os.path.join(os.path.split(filepath)[0],'PostProcessing')
    logID = os.path.split(filepath)[1][12:-4]
    save_it_as_pkl = os.path.join(PPpath,str("DATA_file_"+logID+".pkl"))
    data.to_pickle(save_it_as_pkl)
    
    return data 
    
    
    
#%% Make GIFs for each run and condition MN
# Call with (path to where you have the postprocessing output, the index of the run, the data sorted by condition, boolean true if you want to overwrite the output)
def makeConditionGIFs(postprocpath, k, con_matrix, overwrite):
    import os
    import postproc_helper_HT as pph
    import matplotlib.pyplot as plt
    import imageio
    import shutil
    
    for c in range(len(con_matrix)):
        con_data = con_matrix[c]
        con_data.index = range(len(con_data))     
        (force_L, force_R, target_L, target_R, time) = pph.extract_as_arrays_rebase(con_data)
    
        plotdir=os.path.join(postprocpath,'Sess_'+str(k+1)+'_'+con_data['targetTrial'][0])
        if os.path.isdir(plotdir) and overwrite:
            shutil.rmtree(plotdir)
        os.makedirs(plotdir)
    
        for x in range(len(con_data)):
            plt.figure(x)
            plt.xlim([0,2])
            plt.ylim([0,1.5])
            plt.xlabel('Seconds')
            plt.ylabel('Maxforce')
            plt.yticks([0.25, 0.5, 0.75, 1.0, 1.25], ['2.5%', '5%', '7.5%', '10%', '12.5%'])
            plt.title(str(x)+' '+con_data['targetTrial'][0])
            plt.plot(time,force_R[x],'r',label="Right force")
            plt.plot(time,target_R, 'r--',label="Right target")
            plt.plot(time,force_L[x], 'b',label="Left force")
            plt.plot(time,target_L, 'b--',label="Left target")   
            plt.legend()
            #plt.show()
            #clock.sleep(1)
            for frame in range(10):
                plt.savefig(os.path.join(plotdir,str(x)+'_'+str(frame)+'.png'))
            plt.clf()
            
        # #Make GIF
        if os.path.isfile(os.path.join(postprocpath,'Sess_'+str(k+1)+'_'+con_data['targetTrial'][0]+'.gif')) and overwrite: 
            os.remove(os.path.join(postprocpath,'Sess_'+str(k+1)+'_'+con_data['targetTrial'][0]+'.gif'))
            
        if not os.path.isfile(os.path.join(postprocpath,'Sess_'+str(k+1)+'_'+con_data['targetTrial'][0]+'.gif')):
            with imageio.get_writer(os.path.join(postprocpath,'Sess_'+str(k+1)+'_'+con_data['targetTrial'][0]+'.gif'), mode='I') as writer:
                for cond in range(len(con_data)):
                    for frame in range(10):
                        imagefile = os.path.join(plotdir,str(cond)+'_'+str(frame)+'.png')
                        if os.path.isfile(imagefile):
                            image = imageio.imread(imagefile)
                            writer.append_data(image)       
        else:
            print("GIF already exists for "+con_data['targetTrial'][0])
#%%Compare force trajectory and target and return integer comparison list.
def compForceTarget(force,target,direction):
    comp = []
    if direction=='gt':
        for itr in range(len(force)):
            if force[itr]>target[itr]:
                comp.append(1)
            else:
                comp.append(0)
    else:
        for itr in range(len(force)):
            if force[itr]<target[itr]:
                comp.append(1)
            else:
                comp.append(0)
    return comp
    
#%%Get RT, ACC and trajectory diff measurements from trial or average-level data MN
#Send in condition-specific data and calculated t from trial, run and subject.
#Get values of RT and ACC as well as impacttime and impact-boolean from each trial.
def get_avg_behaviour_HT(force_L, force_R, target_L, target_R, t, logtransform):
    import numpy as np
    
    force_L = np.array(force_L)
    force_R = np.array(force_R)
    target_L = np.array(target_L)
    target_R = np.array(target_R)
    t = np.array(t)
    
    closeness_thr = 0.05 #The threshold for being close enough to the target for the accuracy to start counting in ACCimpact
                        # and for time on target. 
    der_thr = 0.3 #Threshold of derivative for RT and ReactTime calculation.
    
    tw_ACC = 0.5 #The timewindow for calculating ACC.
    tw_sw = 0.05 #The timewindow for sliding average to compare RTs and ACC
    nbrOfTimebins = 3 #Number of timebins
    
    ts = t[4]-t[3] #The timestep in the data. Need not be perfect. Just do between the third and fourth for now.
    
    indxstep_ACC = int(np.round(tw_ACC/ts))
    indxstep_sw = int(np.round(tw_sw/ts))
    
    ##################ACC from impact###############################    
    impact_L = 0
    ACCimpact_L = 0
    impacttime_L = 0
    impact_R = 0
    ACCimpact_R = 0
    impacttime_R = 0
    
    if logtransform:
        for itr in range(len(force_L)):
            if np.mean(np.log(force_L[itr:itr+indxstep_sw])) < np.mean(np.log(target_L[itr:itr+indxstep_sw]+closeness_thr)) and np.mean(np.log(force_L[itr:itr+indxstep_sw]) > np.log(target_L[itr:itr+indxstep_sw]-closeness_thr)):
                ACCimpact_L = sum(abs(force_L[itr:]-target_L[itr:]))/(t[-1]-t[itr])
                impacttime_L = t[itr]
                impact_L = 1
                break
    
        for itr in range(len(force_R)):
            if np.mean(np.log(force_R[itr:itr+indxstep_sw])) < np.mean(np.log(target_R[itr:itr+indxstep_sw]+closeness_thr)) and np.mean(np.log(force_R[itr:itr+indxstep_sw])) > np.mean(np.log(target_R[itr:itr+indxstep_sw]-closeness_thr)):
                ACCimpact_R = sum(abs(force_R[itr:]-target_R[itr:]))/(t[-1]-t[itr])
                impacttime_R = t[itr]
                impact_R = 1
                break
    else:
        for itr in range(len(force_L)):
            if abs(np.mean(force_L[itr:itr+indxstep_sw])-np.mean(target_L[itr:itr+indxstep_sw])) <= closeness_thr:
                ACCimpact_L = sum(abs(force_L[itr:]-target_L[itr:]))/(t[-1]-t[itr])
                impacttime_L = t[itr]
                impact_L = 1
                break
    
        for itr in range(len(force_R)):
            if abs(np.mean(force_R[itr:itr+indxstep_sw])-np.mean(target_R[itr:itr+indxstep_sw])) <= closeness_thr:
                ACCimpact_R = sum(abs(force_R[itr:]-target_R[itr:]))/(t[-1]-t[itr])
                impacttime_R = t[itr]
                impact_R = 1
                break
            
    
    ##################Reaction time############################
    #Derivative          
    React_L = 0
    indx_react_L = 0
    deriv_L = np.diff(force_L)/np.diff(t)
    while React_L==0:
        if indx_react_L==len(force_L)-1:
            break
        
        if abs(deriv_L[indx_react_L]) > der_thr:
            React_L=t[indx_react_L]
            break
        else: 
            indx_react_L += 1

    React_R = 0
    indx_react_R = 0
    deriv_R = np.diff(force_R)/np.diff(t)
    while React_R==0:
        if indx_react_R==len(force_R)-1:
            break
        
        if abs(deriv_R[indx_react_R]) > der_thr:
            React_R=t[indx_react_R]
            break
        else: 
            indx_react_R += 1   

    ##################Time on target###############################
    time_on_target_L = 0
    time_on_target_R = 0
    
    if logtransform:
        for itr in range(len(force_L)):
            if np.log(force_L[itr]) < np.log(target_L[itr]+closeness_thr) and np.log(force_L[itr]) > np.log(target_L[itr]-closeness_thr):
                time_on_target_L = time_on_target_L+1
        time_on_target_L=time_on_target_L/len(force_L)
            
        
        for itr in range(len(force_R)):
            if np.log(force_R[itr]) < np.log(target_R[itr]+closeness_thr) and np.log(force_R[itr]) > np.log(target_R[itr]-closeness_thr):
                time_on_target_R = time_on_target_R+1
        time_on_target_R=time_on_target_R/len(force_R)
    else:
        for itr in range(len(force_L)):
            if abs(force_L[itr]-target_L[itr]) <= closeness_thr:
                time_on_target_L = time_on_target_L+1
        time_on_target_L=time_on_target_L/len(force_L)
            
        
        for itr in range(len(force_R)):
            if abs(force_R[itr]-target_R[itr]) <= closeness_thr:
                time_on_target_R = time_on_target_R+1
        time_on_target_R=time_on_target_R/len(force_R)        
    
    
    ##################Trajectory diff####################
    diffstart_indx = 0
    diffstop_indx = 0
    for itr in range(len(t)):
        if t[itr] >= 0.25 and diffstart_indx == 0:
            diffstart_indx = itr
        if t[itr] >= 0.75 and diffstop_indx == 0:
            diffstop_indx = itr
    if logtransform:
        force_diff = sum(abs(np.array(np.log(force_R[diffstart_indx:diffstop_indx]))-np.array(np.log(force_L[diffstart_indx:diffstop_indx]))))
    else:
        force_diff = sum(abs(np.array(force_R[diffstart_indx:diffstop_indx])-np.array(force_L[diffstart_indx:diffstop_indx])))
    

    ##################ACC in timewindow#############################
    ACCtw_L = sum(abs(np.array(force_L[-indxstep_ACC:])-np.array(target_L[-indxstep_ACC:])))
    ACCtw_R = sum(abs(np.array(force_R[-indxstep_ACC:])-np.array(target_R[-indxstep_ACC:])))  
    
    #Time binned data
    #Overshoot
    #Undershoot
    #Hand separation
    #Volatility
    timebins = []
    bin_indices = []
    overshoot_L,overshoot_R = [],[]
    undershoot_L,undershoot_R = [],[]
    handsep = []
    volatility_L,volatility_R = [],[]
    
    if logtransform:
        diff_force_L  = abs(np.log(force_L)-np.log(target_L))
        diff_force_R = abs(np.log(force_R)-np.log(target_R))
        tmp_handsep = abs(np.log(force_L)-np.log(force_R))
    else:
        diff_force_L  = abs(force_L-target_L)
        diff_force_R = abs(force_R-target_R)
        tmp_handsep = abs(force_L-force_R)
    
    os_elements_L = compForceTarget(force_L, target_L, 'gt')
    os_elements_R = compForceTarget(force_R, target_R, 'gt')
    us_elements_L = compForceTarget(force_L, target_L, 'lt')
    us_elements_R = compForceTarget(force_R, target_R, 'lt')
    
    tmp_os_L = os_elements_L * diff_force_L
    tmp_os_R = os_elements_R  * diff_force_R
    tmp_us_L = us_elements_L * diff_force_L
    tmp_us_R = us_elements_R * diff_force_R
    
    for itr in range(nbrOfTimebins):
        if itr<nbrOfTimebins-1:
            bin_indices.append(round(len(t)/nbrOfTimebins)*(itr+1))
        else:
            bin_indices.append(len(t)-1)
            
        timebins.append(t[bin_indices[-1]])

        if itr == 0:
            first_indx = 0
        else:
            first_indx = bin_indices[-2]
            
        overshoot_L.append(sum(tmp_os_L[first_indx:bin_indices[-1]]))
        overshoot_R.append(sum(tmp_os_R[first_indx:bin_indices[-1]]))
        undershoot_L.append(sum(tmp_us_L[first_indx:bin_indices[-1]]))
        undershoot_R.append(sum(tmp_us_R[first_indx:bin_indices[-1]]))
        handsep.append(sum(tmp_handsep[first_indx:bin_indices[-1]]))
        volatility_L.append(np.var(diff_force_L[first_indx:bin_indices[-1]]))
        volatility_R.append(np.var(diff_force_R[first_indx:bin_indices[-1]]))
    
    
    
    return React_L, React_R, ACCtw_L, ACCtw_R, ACCimpact_L, \
        ACCimpact_R, impacttime_L, impacttime_R, impact_L, impact_R, \
        time_on_target_L, time_on_target_R, force_diff, timebins, overshoot_L, overshoot_R, undershoot_L, undershoot_R, \
        handsep, volatility_L, volatility_R

#%%Get the success for 150 ms, 200 ms or 250 ms.
def check_success_times(force_L, force_R, target_L, target_R, t):
    
    force_L = np.array(force_L)
    force_R = np.array(force_R)
    target_L = np.array(target_L)
    target_R = np.array(target_R)
    t = np.array(t)
    closeness_thr = 0.05 #The threshold for being close enough to the target for the accuracy to start counting in ACCimpact
                        # and for time on target. 
    
    ##################Trial success#############################
    stability_thresholds=[0.15, 0.2, 0.25, 0.3]
    trial_success_time_L=[]
    trial_success_time_R=[]
    trial_success_time_both=[]
    for stability_threshold in stability_thresholds:
        L_success_indx_start = 0
        R_success_indx_start = 0
        both_success_indx_start = 0
        #Right now it can occur more than once so start with three separate loops
        #Both
        t_tmp=0.0
        for itr in range(len(force_L)):
            tmp_diff_L = abs(force_L[itr]-target_L[itr])
            tmp_diff_R = abs(force_R[itr]-target_R[itr])
            if  tmp_diff_L <= closeness_thr and  tmp_diff_R <= closeness_thr:
                if both_success_indx_start == 0:
                    both_success_indx_start = itr
            else:
                both_success_indx_start = 0
                
            if both_success_indx_start!=0 and t[itr]-t[both_success_indx_start] >= stability_threshold:
                t_tmp=t[itr]
                break
        trial_success_time_both.append(t_tmp)
        
        #Left
        t_tmp=0.0
        for itr in range(len(force_L)):
            if  abs(force_L[itr]-target_L[itr]) <= closeness_thr: 
                if L_success_indx_start == 0:
                    L_success_indx_start = itr  
            else:
                L_success_indx_start = 0
                
            #For now 200 ms cutoff
            if L_success_indx_start!=0 and t[itr]-t[L_success_indx_start] >= stability_threshold:
                t_tmp=t[itr]
                break
        trial_success_time_L.append(t_tmp)
                
        #Right
        t_tmp=0.0
        for itr in range(len(force_R)):
            if  abs(force_R[itr]-target_R[itr]) <= closeness_thr: 
                if R_success_indx_start == 0:
                    R_success_indx_start = itr  
            else:
                R_success_indx_start = 0
                
            if R_success_indx_start!=0 and t[itr]-t[R_success_indx_start] >= stability_threshold:
                t_tmp=t[itr]
                break
        trial_success_time_R.append(t_tmp)
                            
    return stability_thresholds, trial_success_time_L, trial_success_time_R, trial_success_time_both

#%%Get the behavioural parameters from HT data
def get_trial_behaviour_HT(force_L, force_R, target_L, target_R, t, logtransform):
    import numpy as np
    
    force_L = np.array(force_L)
    force_R = np.array(force_R)
    target_L = np.array(target_L)
    target_R = np.array(target_R)
    t = np.array(t)
    
    tw_ACC = 0.5 #The timewindow for calculating ACC.
    tw_sw = 0.05 #The timewindow for sliding average to compare RTs and ACC
    nbrOfTimebins = 3 #Number of timebins
    
    ts = t[4]-t[3] #The timestep in the data. Need not be perfect. Just do between the third and fourth for now.
    
    indxstep_ACC = int(np.round(tw_ACC/ts))
    indxstep_sw = int(np.round(tw_sw/ts))
    
    
    closeness_thr = 0.05 #The threshold for being close enough to the target for the accuracy to start counting in ACCimpact
                        # and for time on target. 
    der_thr = 0.3 #Threshold of derivative for RT and ReactTime calculation.
    

    ##################Reaction time############################
    #Derivative          
    React_L = 0
    indx_react_L = 0
    deriv_L = np.diff(force_L)/np.diff(t)
    while React_L==0:
        if indx_react_L==len(force_L)-1:
            break
        
        if abs(deriv_L[indx_react_L]) > der_thr:
            React_L=t[indx_react_L]
            break
        else: 
            indx_react_L += 1

    React_R = 0
    indx_react_R = 0
    deriv_R = np.diff(force_R)/np.diff(t)
    while React_R==0:
        if indx_react_R==len(force_R)-1:
            break
        
        if abs(deriv_R[indx_react_R]) > der_thr:
            React_R=t[indx_react_R]
            break
        else: 
            indx_react_R += 1   

    ##################Time on target###############################
    time_on_target_L = 0
    time_on_target_R = 0
    
    if logtransform:
        for itr in range(len(force_L)):
            if np.log(force_L[itr]) < np.log(target_L[itr]+closeness_thr) and np.log(force_L[itr]) > np.log(target_L[itr]-closeness_thr):
                time_on_target_L = time_on_target_L+1
        time_on_target_L=time_on_target_L/len(force_L)
            
        
        for itr in range(len(force_R)):
            if np.log(force_R[itr]) < np.log(target_R[itr]+closeness_thr) and np.log(force_R[itr]) > np.log(target_R[itr]-closeness_thr):
                time_on_target_R = time_on_target_R+1
        time_on_target_R=time_on_target_R/len(force_R)
    else:
        for itr in range(len(force_L)):
            if abs(force_L[itr]-target_L[itr]) <= closeness_thr:
                time_on_target_L = time_on_target_L+1
        time_on_target_L=time_on_target_L/len(force_L)
            
        
        for itr in range(len(force_R)):
            if abs(force_R[itr]-target_R[itr]) <= closeness_thr:
                time_on_target_R = time_on_target_R+1
        time_on_target_R=time_on_target_R/len(force_R)        
    
    ##################Trajectory diff####################
    diffstart_indx = 0
    diffstop_indx = 0
    for itr in range(len(t)):
        if t[itr] >= 0.25 and diffstart_indx == 0:
            diffstart_indx = itr
        if t[itr] >= 0.75 and diffstop_indx == 0:
            diffstop_indx = itr
    if logtransform:
        force_diff = sum(abs(np.array(np.log(force_R[diffstart_indx:diffstop_indx]))-np.array(np.log(force_L[diffstart_indx:diffstop_indx]))))
    else:
        force_diff = sum(abs(np.array(force_R[diffstart_indx:diffstop_indx])-np.array(force_L[diffstart_indx:diffstop_indx])))
    ##################ACC from impact###############################    
    
    impact_L = 0
    ACCimpact_L = 0
    impacttime_L = 0
    impact_R = 0
    ACCimpact_R = 0
    impacttime_R = 0
    
    if logtransform:
        for itr in range(len(force_L)):
            if np.mean(np.log(force_L[itr:itr+indxstep_sw])) < np.mean(np.log(target_L[itr:itr+indxstep_sw]+closeness_thr)) and np.mean(np.log(force_L[itr:itr+indxstep_sw])) > np.mean(np.log(target_L[itr:itr+indxstep_sw]-closeness_thr)):
                ACCimpact_L = sum(abs(force_L[itr:]-target_L[itr:]))/(t[-1]-t[itr])
                impacttime_L = t[itr]
                impact_L = 1
                break
    
        for itr in range(len(force_R)):
            if np.mean(np.log(force_R[itr:itr+indxstep_sw])) < np.mean(np.log(target_R[itr:itr+indxstep_sw]+closeness_thr)) and np.mean(np.log(force_R[itr:itr+indxstep_sw])) > np.mean(np.log(target_R[itr:itr+indxstep_sw]-closeness_thr)):
                ACCimpact_R = sum(abs(force_R[itr:]-target_R[itr:]))/(t[-1]-t[itr])
                impacttime_R = t[itr]
                impact_R = 1
                break
    else:
        for itr in range(len(force_L)):
            if abs(np.mean(force_L[itr:itr+indxstep_sw])-np.mean(target_L[itr:itr+indxstep_sw])) <= closeness_thr:
                ACCimpact_L = sum(abs(force_L[itr:]-target_L[itr:]))/(t[-1]-t[itr])
                impacttime_L = t[itr]
                impact_L = 1
                break
    
        for itr in range(len(force_R)):
            if abs(np.mean(force_R[itr:itr+indxstep_sw])-np.mean(target_R[itr:itr+indxstep_sw])) <= closeness_thr:
                ACCimpact_R = sum(abs(force_R[itr:]-target_R[itr:]))/(t[-1]-t[itr])
                impacttime_R = t[itr]
                impact_R = 1
                break
            
    ##################ACC in timewindow#############################
    ACCtw_L = sum(abs(np.array(force_L[-indxstep_ACC:])-np.array(target_L[-indxstep_ACC:])))
    ACCtw_R = sum(abs(np.array(force_R[-indxstep_ACC:])-np.array(target_R[-indxstep_ACC:]))) 
    
    ##################Trial success#############################
    trial_success_time_L=0
    trial_success_time_R=0
    trial_success_time_both=0
    L_success_indx_start = 0
    R_success_indx_start = 0
    both_success_indx_start = 0
    stability_threshold=0.3
    #Right now it can occur more than once so start with three separate loops
    #Both
    for itr in range(len(force_L)):
        tmp_diff_L = abs(force_L[itr]-target_L[itr])
        tmp_diff_R = abs(force_R[itr]-target_R[itr])
        if  tmp_diff_L <= closeness_thr and  tmp_diff_R <= closeness_thr:
            if both_success_indx_start == 0:
                both_success_indx_start = itr
        else:
            both_success_indx_start = 0
            
        if both_success_indx_start!=0 and t[itr]-t[both_success_indx_start] >= stability_threshold:
            trial_success_time_both=t[itr]
            break
    
    #Left
    for itr in range(len(force_L)):
        if  abs(force_L[itr]-target_L[itr]) <= closeness_thr: 
            if L_success_indx_start == 0:
                L_success_indx_start = itr  
        else:
            L_success_indx_start = 0
            
        #For now 200 ms cutoff
        if L_success_indx_start!=0 and t[itr]-t[L_success_indx_start] >= stability_threshold:
            trial_success_time_L=t[itr]
            break

            
    #Right
    for itr in range(len(force_R)):
        if  abs(force_R[itr]-target_R[itr]) <= closeness_thr: 
            if R_success_indx_start == 0:
                R_success_indx_start = itr  
        else:
            R_success_indx_start = 0
            
        if R_success_indx_start!=0 and t[itr]-t[R_success_indx_start] >= stability_threshold:
            trial_success_time_R=t[itr]
            break
                        
    #Time binned data
    #Overshoot
    #Undershoot
    #Hand separation
    #Volatility
    timebins = []
    bin_indices = []
    overshoot_L,overshoot_R = [],[]
    undershoot_L,undershoot_R = [],[]
    handsep = []
    volatility_L,volatility_R = [],[]
    
    if logtransform:
        diff_force_L  = abs(np.log(force_L)-np.log(target_L))
        diff_force_R = abs(np.log(force_R)-np.log(target_R))
        tmp_handsep = abs(np.log(force_L)-np.log(force_R))
    else:
        diff_force_L  = abs(force_L-target_L)
        diff_force_R = abs(force_R-target_R)
        tmp_handsep = abs(force_L-force_R)
    
    os_elements_L = compForceTarget(force_L, target_L, 'gt')
    os_elements_R = compForceTarget(force_R, target_R, 'gt')
    us_elements_L = compForceTarget(force_L, target_L, 'lt')
    us_elements_R = compForceTarget(force_R, target_R, 'lt')
    
    tmp_os_L = os_elements_L * diff_force_L
    tmp_os_R = os_elements_R  * diff_force_R
    tmp_us_L = us_elements_L * diff_force_L
    tmp_us_R = us_elements_R * diff_force_R
        
    for itr in range(nbrOfTimebins):
        if itr<nbrOfTimebins-1:
            bin_indices.append(round(len(t)/nbrOfTimebins)*(itr+1))
        else:
            bin_indices.append(len(t)-1)
            
        timebins.append(t[bin_indices[-1]])

        if itr == 0:
            first_indx = 0
        else:
            first_indx = bin_indices[-2]
            
        overshoot_L.append(sum(tmp_os_L[first_indx:bin_indices[-1]]))
        overshoot_R.append(sum(tmp_os_R[first_indx:bin_indices[-1]]))
        undershoot_L.append(sum(tmp_us_L[first_indx:bin_indices[-1]]))
        undershoot_R.append(sum(tmp_us_R[first_indx:bin_indices[-1]]))
        handsep.append(sum(tmp_handsep[first_indx:bin_indices[-1]]))
        volatility_L.append(np.var(diff_force_L[first_indx:bin_indices[-1]]))
        volatility_R.append(np.var(diff_force_R[first_indx:bin_indices[-1]]))
    
    return React_L, React_R, ACCtw_L, ACCtw_R, ACCimpact_L, \
        ACCimpact_R, impacttime_L, impacttime_R, impact_L, impact_R, \
        time_on_target_L, time_on_target_R, force_diff, trial_success_time_L, trial_success_time_R, \
        trial_success_time_both, timebins, overshoot_L, overshoot_R, undershoot_L, undershoot_R, \
        handsep, volatility_L, volatility_R
        
#%%Get the variance in the last 500ms of each trial. MN
def get_trial_variance_and_error(condition_data):
    import numpy as np
    import postproc_helper_HT as pph
    
    tw_var = 0.5
    ts = condition_data.loc[0]['time'][6] - condition_data.loc[0]['time'][5]
    indxstep_var = int(np.round(tw_var/ts))
    trial_var_L, trial_var_R, target_L, target_R = [], [], [], []
    trial_error_L, trial_error_R = [], []
    for itr in  range(len(condition_data)):
        tmp = condition_data.iloc[itr]
        target_L = [np.asarray(tmp['targets'][k][0]) for k in range(len(tmp['force_L']))]
        target_R = [np.asarray(tmp['targets'][k][1]) for k in range(len(tmp['force_R']))]
        end_indx_L,end_indx_R = pph.get_end_indx(tmp['targetTrial'],np.asarray(target_L),np.asarray(target_R))
        if tmp['targetTrial'] == 'Right_decrease_force' or tmp['targetTrial'] == 'Right_increase_force':
            trial_var_L.append(np.nan)
            trial_error_L.append(np.nan)
        else: 
            trial_var_L.append(np.var(tmp['force_L'][end_indx_L-indxstep_var:end_indx_L]))
            trial_error_L.append(abs(sum(target_L[end_indx_L-indxstep_var:end_indx_L]-np.asarray(tmp['force_L'][end_indx_L-indxstep_var:end_indx_L]))))
        trial_var_R.append(np.var(tmp['force_R'][end_indx_R-indxstep_var:end_indx_R]))
        trial_error_R.append(abs(sum(target_R[end_indx_R-indxstep_var:end_indx_R]-np.asarray(tmp['force_R'][end_indx_R-indxstep_var:end_indx_R]))))
    
    return trial_var_L, trial_var_R, trial_error_L, trial_error_R

#%%Get index of first return to baseline to find RTend depending on condition MN
def get_end_indx(cond,trial_target_L,trial_target_R):
    import numpy as np
    #Fix issue with last target set to 0.01 in some cases in trial case
    trial_target_L[trial_target_L<0.1]=0.5
    trial_target_R[trial_target_R<0.1]=0.5
    #Fix issue with last target set to 0.01 in some cases in average case
    trial_target_L=np.round(trial_target_L,1)
    trial_target_R=np.round(trial_target_R,1)
    indx_L,indx_R = 0,0
    if cond == 'Asym_L_decrease_R_increase':
        indx_L = np.where(trial_target_L==0.5)[0][0]
        indx_R = np.where(trial_target_R==0.5)[0][0]
    elif cond == 'Asym_L_increase_R_decrease':
        indx_L = np.where(trial_target_L==0.5)[0][0]
        indx_R = np.where(trial_target_R==0.5)[0][0]
    elif cond == 'Right_decrease_force':
        indx_R = np.where(trial_target_R==0.5)[0][0]
    elif cond == 'Right_increase_force':
        indx_R = np.where(trial_target_R==0.5)[0][0]
    elif cond == 'Sym_decrease_force':
        indx_L = np.where(trial_target_L==0.5)[0][0]
        indx_R = np.where(trial_target_R==0.5)[0][0]
    elif cond == 'Sym_increase_force':
        indx_L = np.where(trial_target_L==0.5)[0][0]
        indx_R = np.where(trial_target_R==0.5)[0][0]
   
    return indx_L,indx_R

#%%Get targetdirection depending on condition MN 
#Input: String that specifies the condition
#Output: Direction of target (up or down) 
def get_target_directions(cond):
    
    targetdir_L = 0
    targetdir_R = 0
    
    if cond == 'Asym_L_decrease_R_increase':
        targetdir_L = -1
        targetdir_R = 1
    elif cond == 'Asym_L_increase_R_decrease':
        targetdir_L = 1
        targetdir_R = -1
    elif cond == 'Right_decrease_force':
        targetdir_L = 0
        targetdir_R = -1
    elif cond == 'Right_increase_force':
        targetdir_L = 0
        targetdir_R = 1
    elif cond == 'Left_decrease_force': #Not there now but should be?
        targetdir_L = -1
        targetdir_R = 0
    elif cond == 'Left_increase_force': #Not there now but should be?
        targetdir_L = 1
        targetdir_R = 0
    elif cond == 'Sym_decrease_force':
        targetdir_L = -1
        targetdir_R = -1
    elif cond == 'Sym_increase_force':
        targetdir_L = 1
        targetdir_R = 1
        
    return targetdir_L,targetdir_R

#%%Get information from physical activity surveys. 
def get_survey_answers(HT_dir):
    
    def time_answer_reader(line):
        stop = False
        tim = ''
        t_itr=line.find(':')+2
        if t_itr > len(line)-1:
            stop = True
        while not stop:
            if line[t_itr]=='\n':
                return '0'
            elif line[t_itr]==' ' or line[t_itr]=='\\':
                stop = True
            elif line[t_itr]==',':
                tim=tim+'.'
                t_itr=t_itr+1
            else:
                tim=tim+line[t_itr]
                t_itr=t_itr+1
            if t_itr >= len(line)-1:
                stop = True
        return tim
                
                
    with open(os.path.join(HT_dir,'SurveyAnswers.txt'), 'rb') as f:
        lines = f.readlines()
        
    sleep_time = float(time_answer_reader(str(lines[0])))
    if sleep_time > 12:
        sleep_time=sleep_time/10
        sleep_time=str(sleep_time)
    sleep_quality = time_answer_reader(str(lines[1]))    
    bwalk = time_answer_reader(str(lines[2]))
    cardio = time_answer_reader(str(lines[3]))
    swim = time_answer_reader(str(lines[4]))
    wtrain = time_answer_reader(str(lines[5]))
    ot='0'
    what_ot=''
    ot_line=str(lines[6])
    if not ot_line[-1] == ' ':
        ot = time_answer_reader(ot_line)
        stop = False
        str_itr=8
        while not stop:
            if ot_line[str_itr]==' ':
                stop = True
            else:
                what_ot=what_ot+ot_line[str_itr]
                str_itr=str_itr+1
    
    return sleep_time, sleep_quality, bwalk, cardio, swim, wtrain, ot, what_ot





















