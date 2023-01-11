# DYBICO-HT_PostProcessing
Post-processing for home training DYBICO data to characterize progress and present it to the researcher. 

This software will output a training report for the entire training period (thus far) containing:
- Plot of max force for each hand and day
- Plot of the time of day that training started
- Plot of sleep time and quality
- Table of physical activity for each day
as well as performance measures averaged for each day. 

It will also produce training reports for each training day with performance measures between sessions, within sessions, and within blocks.

## Paradigm time naming conventions
The training paradigm for each individual is divided into training days. Each training day consists of three sessions, separated by a self-paced pause. Within each session, there are 3 blocks of 20 trials of each condition.  

## Performance measurements
The following measures are of interest for characterizing learning progress:
- Time on target (within 0.5% of max force to the target, not having to be continuous)
- Error at the final 500 ms of the trial 
- Reaction time (only relevant for at least block-averaged data)
- Hand separation from 0.25s to 0.75s Right minus Left

Other factors that are relevant for performance are:
- Hand (L/R)
- Condition (A/S)
- Force step size (2.5-10% of max force)
- Force direction (I/D)
- (Time between training days)

## Background measures of importance
The following background measures can be of importance for daily performance or to check on device stability. 
- Max force (L/R)
- Time and quality of sleep
- Physical activity
- Time of day of training
