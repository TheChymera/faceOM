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

def main(make=False, source=False, make_tight=True, compare="difficulty", show=""):
    if make == 'corr':
        corr(make_tight)
    if make == 'time_course':
        time_course(make_tight,show=show)
    
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
    
def time_course(source=False, make_tight=True, compare="difficulty", show="fix, easy, hard"):
    all_timecourses = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', force_new=False)
    all_timecourses["Time"] = all_timecourses["Time"]/1000 #make seconds (from milliseconds)
    all_timecourses.to_csv("/home/chymera/TC_all.csv")
    
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
    
    timecourse_normed.to_csv("/home/chymera/TC_norm.csv")
    
    timecourse_plot = timecourse_normed.groupby(level=0).apply(downsample, sample=4, group='measurement')

    #BEGIN PLOTTING
    fig = figure(figsize=(5, 3), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    
    ax1=fig.add_subplot(1,1,1,axisbg='1')
    ax1.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax1.set_axisbelow(True)
    
    plotted = []
    plotted_names = []
    if "fix" in show:
        ax1.plot(np.array(timecourse_plot.ix["fix"]["Time"]), np.array(timecourse_plot.ix["fix"]["Pupil"]), color="0.8")
        fix = Rectangle((0, 0), 1, 1, color="0.8")
        plotted.append(fix)
        plotted_names.append("Fixation")
    if "easy" in show:
        ax1.plot(np.array(timecourse_plot.ix["easy"]["Time"]), np.array(timecourse_plot.ix["easy"]["Pupil"]), color='g')
        easy = Rectangle((0, 0), 1, 1, color="g")
        plotted.append(easy)
        plotted_names.append("Easy Trials")
    if "hard" in show:
        ax1.plot(np.array(timecourse_plot.ix["hard"]["Time"]), np.array(timecourse_plot.ix["hard"]["Pupil"]), color='m')
        hard = Rectangle((0, 0), 1, 1, color="m")
        plotted.append(hard)
        plotted_names.append("Hard Trials")
    if "happy" in show:
        happy = ax1.plot(np.array(timecourse_normed.ix["happy"]["Time"]), np.array(timecourse_normed.ix["happy"]["Pupil"]), color='g')
    if "fearful" in show: 
        fearful = ax1.plot(np.array(timecourse_normed.ix["fearful"]["Time"]), np.array(timecourse_normed.ix["fearful"]["Pupil"]), color='m')
    if "emotion" in show:
        emotion = ax1.plot(np.array(timecourse_normed.ix["happy"]["Time"]), (np.array(timecourse_normed.ix["happy"]["Pupil"])+np.array(timecourse_normed.ix["fearful"]["Pupil"]))/2, color='g')
    if "scrambled" in show:
        scrambled = ax1.plot(np.array(timecourse_normed.ix["scrambled"]["Time"]), np.array(timecourse_normed.ix["scrambled"]["Pupil"]), color='m')
    
    ax1.set_ylabel('Pupil Area Ratio', fontsize=11)
    ax1.set_xlabel('Time [s]', fontsize=11)
    legend((plotted),(plotted_names),loc='upper center', bbox_to_anchor=(0.5, 1.065), ncol=3, fancybox=False, shadow=False, prop=FontProperties(size='5'))
    
    #END PLOTTING

if __name__ == '__main__':
    main(make="time_course", show=["fix","easy","hard"])
    show()
