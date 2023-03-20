#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 11:44:36 2023
Script for actually generating the pdf report.
@author: gdf724
"""
import os
from fpdf import FPDF, HTMLMixin
from datetime import datetime
import glob

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


#Whole training period 
report_dir='/Users/gdf724/Data/ReScale/HomeTrainingTest/Reports'
subj=os.listdir(report_dir)
for line in subj:
    print(line[0])
    if line[0]=='.':
        subj.remove(line)
    elif line[-2:]=='df' or line[-2:]=='sv':
        subj.remove(line)

for subject in subj:
    if subject == 'P005':
        report=PDF()
        subj_dir = os.path.join(report_dir,subject)
        tot_plots_per_page_1 = ['Tot_ToT_A.png', 'Tot_ToT_S.png', 'Tot_Err_A.png', 'Tot_Err_S.png', 'Tot_Succ_A.png', 'Tot_Succ_S.png', 'Tot_Handsep_A.png', 'Tot_Handsep_S.png']
        tot_plots_per_page_1 = [os.path.join(subj_dir,x) for x in tot_plots_per_page_1]
        report.print_page(tot_plots_per_page_1)
        tot_plots_per_page_2 = ['MaxForces.png', 'TimeOfDay.png', 'Sleep.png', 'PA_table.png']
        tot_plots_per_page_2 = [os.path.join(subj_dir,x) for x in tot_plots_per_page_2]
        report.print_page(tot_plots_per_page_2)
            
        report.output(subject+'_training.pdf', 'F')
        os.rename(subject+'_training.pdf', os.path.join(subj_dir,subject+'_training.pdf'))
        
        
        