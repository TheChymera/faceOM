#!/usr/bin/env python
from __future__ import division
__author__ = 'Horea Christian'
from data_functions import get_et_data, downsample, get_rt_data
import numpy as np
import scipy as sp
import pandas as pd
from scipy.stats import sem, pearsonr
import matplotlib.pyplot as plt
from matplotlib import axis
from pylab import figure, show, errorbar, setp, legend
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle
from scipy.stats import ttest_rel, ttest_ind

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
        time_course(make_tight,show=["fix", "easy", "hard", "rt_e", "rt_h"])
    if make == 'discrete_time':
        discrete_time(make_tight,show=show)
    
def corr(source=False, make_tight=True):
    all_timecourses = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', force_new=False)
    timecourse_means = all_timecourses.groupby(level=(1,2)).mean()
    
    pearson = pearsonr(timecourse_means["L Dia X [px]"], timecourse_means["L Dia Y [px]"])
    
    fig = figure(figsize=(3, 3), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    
    ax1=fig.add_subplot(1,1,1)
    ax1.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax1.set_axisbelow(True)
    
    ax1.plot(all_timecourses["L Dia X [px]"][::3], all_timecourses["L Dia Y [px]"][::3],".",markersize=2, color='0.91',zorder=1)
    all_points = Rectangle((0, 0), 1, 1, color="0.9")
    ax1.plot(timecourse_means["L Dia X [px]"], timecourse_means["L Dia Y [px]"],".",markersize=5, alpha=0.7, markerfacecolor='#ffffff', markeredgecolor='g',zorder=3)
    participant_means = Rectangle((0, 0), 1, 1, ec="g", fc="#ffffff")
    A = np.vstack([timecourse_means["L Dia X [px]"], np.ones(len(timecourse_means["L Dia X [px]"]))]).T
    m, c = np.linalg.lstsq(A, timecourse_means["L Dia Y [px]"])[0]
    ax1.plot(np.array(all_timecourses["L Dia X [px]"])[10000:],np.array(all_timecourses["L Dia X [px]"])[10000:]*m+c,color='m', linewidth=0.8,antialiased=True,zorder=2)
    regression = Rectangle((0, 0), 1, 1, color="m")

    
    ax1.set_ylabel('Y-axis Pupil Diameter [px]', fontsize=9)
    ax1.set_xlabel('X-axis Pupil Diameter [px]', fontsize=9)
    ax1.set_ylim(bottom=10) 
    ax1.set_xlim(left=10)
    legend((all_points, participant_means, regression),('Raw','Means', 'Regression'),loc='upper center', bbox_to_anchor=(0.5, 1.038), ncol=3, fancybox=False, shadow=False, prop=FontProperties(size='9'))
    
    return pearson, m, c
    
def time_course(source=False, make_tight=True, compare="difficulty", show=["fix", "easy", "hard", "rt_e", "rt_h"]):
    rt = get_rt_data(make_categories=categories)
    all_timecourses = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', force_new=False)
    all_timecourses["Time"] = all_timecourses["Time"]/1000 #make seconds (from milliseconds)
    #~ all_timecourses.to_csv("/home/chymera/TC_all.csv")
    
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
    
    #~ timecourse_normed.to_csv("/home/chymera/TC_norm.csv")
    
    timecourse_plot = timecourse_normed.groupby(level=0).apply(downsample, sample=4, group='measurement')

    #BEGIN PLOTTING
    fig = figure(figsize=(5, 3), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    
    ax1=fig.add_subplot(1,1,1,axisbg='1')
    ax1.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax1.set_axisbelow(True)
    
    plotted = []
    plotted_names = []
    if "rt_e" in show:
        ax1.axvline(rt[(rt["difficulty"] == "easy")]["RT"].mean(), linewidth=0.3, color='g')
    if "rt_h" in show:
        ax1.axvline(rt[(rt["difficulty"] == "hard")]["RT"].mean(), linewidth=0.3, color='m')
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
    
    return timecourse_normed

def discrete_time(make_tight=True, show=""):
    df = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', force_new=False)
    df["Time"] = df["Time"]/1000 #make seconds (from milliseconds)
   
    discretize = {0:"S01", 1:"S02", 2:"S03", 3:"S04", 4:"S05", 5:"S06", 6:"S07", 7:"S08", 8:"S09", 9:"S10", 10:"S11", 11:"S12", 12:"S13", 13:"S14", 14:"S15", 15:"S16", 16:"S17", 17:"S18", 18:"S19", 19:"S20"}
    
    df = df.groupby(level=[0,1]).apply(downsample, sample=40, group='measurement')
    df.reset_index(inplace=True)

    #fixation has a jitter and building a mean gives smaller time values for the last time points:
    df.ix[(df["CoI"] == "fix"), "Time"] = (df[(df["CoI"] == "easy")]["Time"]+df[(df["CoI"] == "hard")]["Time"])/2 

    #NORM TO BASELINE
    baseline_mean = df[(df["CoI"] == "fix")]["Pupil"].mean() #baseline (fixcross) mean
    df["Pupil"] = df["Pupil"]/baseline_mean
    #END NORM TO BASELINE

    df["dTime"] = df["measurement"].copy()
    df["dTime"] = df["dTime"].apply(lambda x: discretize.get(x,x))
        
    df_means = df.copy()
    df_means = df_means.set_index(['ID',"CoI", "measurement"], append=False, drop=True)
    df_means = df_means.groupby(level=(1,2)).mean()
        
    #BEGIN PLOTTING
    fig = figure(figsize=(5, 3), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    
    ax1=fig.add_subplot(1,1,1,axisbg='1')
    ax1.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax1.set_axisbelow(True)
    ids = sorted(list(set(list(df["dTime"]))))
    pos_ids = np.arange(len(ids))
    
    plotted = []
    plotted_names = []
    if "easy" in show:
        ax1.plot(pos_ids, np.array(df_means.ix["easy"]["Pupil"]), "^-", markeredgecolor="none", linewidth=0.2, color='g')
        easy = Rectangle((0, 0), 1, 1, color="g")
        plotted.append(easy)
        plotted_names.append("Easy Trials")
    if "hard" in show:
        ax1.plot(pos_ids, np.array(df_means.ix["hard"]["Pupil"]), "v-", markeredgecolor="none", linewidth=0.2, color='m')
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
    
    ax1.set_xticks(pos_ids)
    ax1.set_xticklabels(ids,fontsize=9) # add rotation=30 if things get too crowded
    
    ax1.set_ylabel('Pupil Area Ratio', fontsize=11)
    ax1.set_xlabel('Time Series Sextiles [66 ms]', fontsize=11)
    axis.Axis.zoom(ax1.xaxis, -0.6) # sets x margins further apart from the content proportional to its length
    axis.Axis.zoom(ax1.yaxis, -0.4) # sets x margins further apart from the content proportional to its length
    legend((plotted),(plotted_names),loc='upper center', bbox_to_anchor=(0.5, 1.065), ncol=3, fancybox=False, shadow=False, prop=FontProperties(size='5'))
    #END PLOTTING
    
    print ttest_rel(np.array(df[(df["dTime"]=="S6") & (df["CoI"]=="easy")]["Pupil"]),np.array(df[(df["dTime"]=="S6") & (df["CoI"]=="hard")]["Pupil"]))
    
    #~ print ttest_rel(np.array(df_means.ix["easy"]["Pupil"]))
    
    df.to_csv("/home/chymera/dTC.csv")
    return df

if __name__ == '__main__':
    main(make="time_course",show=["fix", "easy", "hard", "rt_e", "rt_h"])
    show()
