#!/usr/bin/env python
from __future__ import division
__author__ = 'Horea Christian'
from data_functions import get_et_data
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
    #~ print timecourse.index.tolist()

    timecourse_means = all_timecourses.groupby(level=(1,2)).mean()
    timecourse_meds = all_timecourses.groupby(level=(1,2)).aggregate(np.median)
    timecourse_sems = all_timecourses.groupby(level=(1,2)).aggregate(sem)
    
    keys=["mean", "med", "sem"]
    timecourses = pd.concat([timecourse_means,timecourse_meds,timecourse_sems], keys=keys)
    timecourses_normed=timecourses.copy()
    timecourses.to_csv("/home/chymera/tc.csv")
    baseline_mean = (timecourses.ix["mean"].ix["fix"]["L Dia Y [px]"].mean()+timecourses.ix["mean"].ix["fix"]["L Dia Y [px]"].mean())/2 #baseline (fixcross) mean
    f = lambda x: (x/2)
    timecourses_normed.ix["mean"] = timecourses.ix["mean"].groupby(level=0).transform(f)
    print timecourses_normed.ix["mean"]
    #~ print timecourses.ix["mean"].groupby(level=0).transform(f)

    #~ print timecourses_normed.ix["mean"].ix["fix"]["Time"]
    for key in keys:
        timecourses.ix[key].ix["fix"]["Time"] = (timecourses.ix[key].ix["easy"]["Time"]+timecourses.ix[key].ix["hard"]["Time"])/2
        #~ print timecourses_normed.ix[key].ix["fix"]["Time"]
        #~ print timecourses.ix[key]["Time"]
        #~ print timecourses.ix[key]["Time"]
        
        #NORM TO BASELINE
        baseline_mean = (timecourses.ix[key].ix["fix"]["L Dia Y [px]"].mean()+timecourses.ix[key].ix["fix"]["L Dia Y [px]"].mean())/2 #baseline (fixcross) mean
        normalize = lambda x: (x / baseline_mean) #normalize function
        #~ print timecourses.ix[key].groupby(level=0).transform(normalize)
        timecourses_normed.ix[key]=timecourses.ix[key].groupby(level=0).transform(normalize)
        #END NORM TO BASELINE
        #~ print timecourses_normed.ix[key]["Time"]
        #~ print timecourses.ix[key]["Time"]
   
        #~ print timecourses.ix[key]["Time"]
        timecourses_normed.ix[key]["Time"] = timecourses.ix[key]["Time"] # take non-normed time
        #~ print timecourses_normed.ix[key]["Time"]
        #~ print timecourses.ix[key]["Time"]
        timecourses_normed.ix[key]["Time"] = timecourses_normed.ix[key]["Time"]/1000 #make seconds (from milliseconds)
        timecourses_normed.ix[key]["Pupil"] = (timecourses_normed.ix[key]["L Dia Y [px]"] + timecourses_normed.ix[key]["L Dia X [px]"])/2
        
        timecourses_normed.ix[key] = timecourses_normed.ix[key].groupby(level=0).apply(downsample)
        
    #~ print timecourses.ix["mean"].ix["fix"]["Time"]
    
    #~ raise
    #~ timecourse_means.ix["fix"]["Time"] = (timecourse_means.ix["easy"]["Time"]+timecourse_means.ix["hard"]["Time"])/2
    #~ #NORM TO BASELINE
    #~ baseline_mean = (timecourse_means.ix["fix"]["L Dia Y [px]"].mean()+timecourse_means.ix["fix"]["L Dia Y [px]"].mean())/2 #baseline (fixcross) mean
    #~ normalize = lambda x: (x / baseline_mean) #normalize function
    #~ timecourse_normed = timecourse_means.groupby(level=0).transform(normalize)
    #~ #END NORM TO BASELINE
#~ 
    #~ timecourse_normed["Time"] = timecourse_means["Time"] # take non-normed time
    #~ timecourse_normed["Time"] = timecourse_normed["Time"]/1000 #make seconds (from milliseconds)
    #~ timecourse_normed["Pupil"] = (timecourse_normed["L Dia Y [px]"] + timecourse_normed["L Dia X [px]"])/2
    #~ 
    
    #~ print np.array(timecourse_normed.ix["easy"]["Time"])
    
    #~ timecourse_resampled = timecourse_normed.groupby(level=0).resample(rule='0.1S', how=np.mean)
    #~ timecourse_resampled = timecourse_normed.set_index(pd.DatetimeIndex(timecourse_normed['Time']))
    #~ timecourse_resampled = timecourse_normed.to_datetime(timecourse_normed['Time'],unit='S')
    #~ print timecourse_resampled.ix[:5]
    #~ print timecourse_resampled.ix["hard"].ix[:5]
    
    #~ timecourse_normed = timecourse_normed.groupby(level=0).apply(downsample)
    
    #BEGIN PLOTTING
    fig = figure(figsize=(6, 3), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    
    ax1=fig.add_subplot(1,1,1)
    ax1.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax1.set_axisbelow(True)
    
    if compare == "difficulty":
        ax1.plot(np.array(timecourses_normed.ix["mean"].ix["fix"]["Time"]), np.array(timecourses_normed.ix["mean"].ix["fix"]["Pupil"]), color="0.8")
        ax1.plot(np.array(timecourses_normed.ix["mean"].ix["easy"]["Time"]), np.array(timecourses_normed.ix["mean"].ix["easy"]["Pupil"]), color='g')
        ax1.plot(np.array(timecourses_normed.ix["mean"].ix["hard"]["Time"]), np.array(timecourses_normed.ix["mean"].ix["hard"]["Pupil"]), color='m')
        #~ ax1.fill_between(np.array(timecourse_normed.ix["hard"]["Time"]), np.array(timecourse_normed.ix["hard"]["Pupil"])+sem/2, y-sem/2, alpha=0.5)
    elif compare == "emotion":
        ax1.plot(np.array(timecourse_normed.ix["happy"]["Time"]), np.array(timecourse_normed.ix["happy"]["Pupil"]), color='g')
        ax1.plot(np.array(timecourse_normed.ix["fearful"]["Time"]), np.array(timecourse_normed.ix["fearful"]["Pupil"]), color='m')
    elif compare == "emotionality":
        ax1.plot(np.array(timecourse_normed.ix["happy"]["Time"]), (np.array(timecourse_normed.ix["happy"]["Pupil"])+np.array(timecourse_normed.ix["fearful"]["Pupil"]))/2, color='g')
        ax1.plot(np.array(timecourse_normed.ix["scrambled"]["Time"]), np.array(timecourse_normed.ix["scrambled"]["Pupil"]), color='m')

    
    ax1.set_ylabel(r'Pupil ratio: $\mathsf{\frac{X+Y}{\bar{X}_{fix}+\bar{Y}_{fix}}}$', fontsize=11)
    ax1.set_xlabel('Time [s]', fontsize=11)
    
    #BEGIN PLOTTING

def downsample(x):
    x = x.reset_index()
    x = x.groupby(x['measurement'].div(4)).mean()
    del x['measurement']
    return x

if __name__ == '__main__':
    main(make="tc")
    show()
