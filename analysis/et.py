#!/usr/bin/env python
from __future__ import division
__author__ = 'Horea Christian'
from data_functions import get_et_data, downsample
import numpy as np
import scipy as sp
import pandas as pd
from scipy.stats import sem, pearsonr
import matplotlib.pyplot as plt
from pylab import figure, show, errorbar, setp, legend
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle

categories = [
	['difficulty', 'easy', 'em100|cell22rand'],
	['difficulty', 'hard', 'em40|cell10rand'],
	['emotion', 'happy', 'HA-cell'],
	['emotion', 'fearful', 'FE-cell'],
	['emotion', 'scrambled', 'cell'],
    ['fixation', 'fix', 'fix']
	]

def main(make=False, source=False, make_tight=True, compare="difficulty"):
    if make == 'corr':
        corr(make_tight)
    if make == 'tc':
        time_course(make_tight)
    
def corr(source=False, make_tight=True):
    all_timecourses = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', force_new=False)
    timecourse_means = all_timecourses.groupby(level=(1,2)).mean()
    
    pearson = pearsonr(timecourse_means["L Dia X [px]"], timecourse_means["L Dia Y [px]"])
    
    fig = figure(figsize=(3, 3), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    
    ax1=fig.add_subplot(1,1,1)
    ax1.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax1.set_axisbelow(True)
    
    ax1.plot(all_timecourses["L Dia X [px]"], all_timecourses["L Dia Y [px]"],".",markersize=1, color='0.91',zorder=1)
    all_points = Rectangle((0, 0), 1, 1, color="0.9")
    ax1.plot(timecourse_means["L Dia X [px]"], timecourse_means["L Dia Y [px]"],".",markersize=3, alpha=0.7, markerfacecolor='#ffffff', markeredgecolor='g',zorder=3)
    participant_means = Rectangle((0, 0), 1, 1, ec="g", fc="#ffffff")
    A = np.vstack([timecourse_means["L Dia X [px]"], np.ones(len(timecourse_means["L Dia X [px]"]))]).T
    m, c = np.linalg.lstsq(A, timecourse_means["L Dia Y [px]"])[0]
    ax1.plot(np.array(all_timecourses["L Dia X [px]"])[10000:],np.array(all_timecourses["L Dia X [px]"])[10000:]*m+c,color='m', linewidth=0.8,antialiased=True,zorder=2)
    regression = Rectangle((0, 0), 1, 1, color="m")

    
    ax1.set_ylabel('Y-axis Pupil Diameter [px]', fontsize=9)
    ax1.set_xlabel('X-axis Pupil Diameter [px]', fontsize=9)
    ax1.set_ylim(bottom=10) 
    ax1.set_xlim(left=10)
    legend((all_points, participant_means, regression),('Raw','Means', 'Regression'),loc='upper center', bbox_to_anchor=(0.5, 1.065), ncol=3, fancybox=False, shadow=False, prop=FontProperties(size='5'))
    
    return pearson, m, c
    
def time_course(source=False, make_tight=True, compare="difficulty"):
    all_timecourses = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', force_new=False)
    all_timecourses["Pupil"] = ((all_timecourses["L Dia Y [px]"] + all_timecourses["L Dia X [px]"])/2)**2

    timecourse_means = all_timecourses.groupby(level=(1,2)).mean()
    timecourse_meds = all_timecourses.groupby(level=(1,2)).aggregate(np.median)
    timecourse_sems = all_timecourses.groupby(level=(1,2)).aggregate(sem)

    timecourse_means.ix["fix"]["Time"] = (timecourse_means.ix["easy"]["Time"]+timecourse_means.ix["hard"]["Time"])/2
    #NORM TO BASELINE
    baseline_mean = timecourse_means.ix["fix"]["Pupil"].mean() #baseline (fixcross) mean
    normalize = lambda x: (x / baseline_mean) #normalize function
    timecourse_normed = timecourse_means.groupby(level=0).transform(normalize)
    #END NORM TO BASELINE

    timecourse_normed["Time"] = timecourse_means["Time"] # take non-normed time
    timecourse_normed["Time"] = timecourse_normed["Time"]/1000 #make seconds (from milliseconds)
    
    timecourse_plot = timecourse_normed.groupby(level=0).apply(downsample, sample=4, group='measurement')

    #BEGIN PLOTTING
    fig = figure(figsize=(5, 3), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    
    ax1=fig.add_subplot(1,1,1,axisbg='1')
    ax1.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax1.set_axisbelow(True)
    
    if compare == "difficulty":
        #~ ax1.plot(np.array(timecourse_plot.ix["fix"]["Time"]), np.array(timecourse_plot.ix["fix"]["Pupil"]), color="0.8")
        ax1.plot(np.array(timecourse_plot.ix["easy"]["Time"]), np.array(timecourse_plot.ix["easy"]["Pupil"]), color='g')
        ax1.plot(np.array(timecourse_plot.ix["hard"]["Time"]), np.array(timecourse_plot.ix["hard"]["Pupil"]), color='m')
    elif compare == "emotion":
        ax1.plot(np.array(timecourse_normed.ix["happy"]["Time"]), np.array(timecourse_normed.ix["happy"]["Pupil"]), color='g')
        ax1.plot(np.array(timecourse_normed.ix["fearful"]["Time"]), np.array(timecourse_normed.ix["fearful"]["Pupil"]), color='m')
    elif compare == "emotionality":
        ax1.plot(np.array(timecourse_normed.ix["happy"]["Time"]), (np.array(timecourse_normed.ix["happy"]["Pupil"])+np.array(timecourse_normed.ix["fearful"]["Pupil"]))/2, color='g')
        ax1.plot(np.array(timecourse_normed.ix["scrambled"]["Time"]), np.array(timecourse_normed.ix["scrambled"]["Pupil"]), color='m')

    
    #~ ax1.set_ylabel('Pupil Area Ratio', fontsize=11)
    #~ ax1.set_xlabel('Time [s]', fontsize=11)
    
    #BEGIN PLOTTING

if __name__ == '__main__':
    main(make="tc")
    show()
