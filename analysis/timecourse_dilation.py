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

categories = [
	['difficulty', 'easy', 'em100|cell22rand'],
	['difficulty', 'hard', 'em40|cell10rand'],
	['emotion', 'happy', 'HA-cell'],
	['emotion', 'fearful', 'FE-cell'],
	['emotion', 'scrambled', 'cell'],
    ['fixation', 'fix', 'fix']
	]

def corr(source=False, make_tight=True, force_new=False):
    all_timecourses = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', force_new=force_new)
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

    ax1.tick_params(axis='both', labelsize=8)
    ax1.set_ylabel('Y-axis Pupil Diameter [px]', fontsize=9)
    ax1.set_xlabel('X-axis Pupil Diameter [px]', fontsize=9)
    ax1.set_ylim(bottom=10) 
    ax1.set_xlim(left=10)
    legend((all_points, participant_means, regression),('Raw','Per-(Time, Condition) Particiant Means', 'Regression'),loc='upper center', bbox_to_anchor=(0.5, 1.038), ncol=3, fancybox=False, shadow=False, prop=FontProperties(size='7'))
    
    return [list(pearson), m, c]
    
def time_course(source=False, make_tight=True, make_sem=True, show=["emotion", "scrambled", "rt_em", "rt_sc"], sample_by=4, fontscale=1, force_new=False):
    rt = get_rt_data(make_categories=categories)
    all_timecourses = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', baseline="participant", force_new=force_new)
    all_timecourses["Time"] = all_timecourses["Time"]/1000 #make seconds (from milliseconds)
    all_timecourses.to_csv("/home/chymera/TC_all.csv")

    all_timecourses = all_timecourses.reset_index(drop=False)
    all_timecourses = all_timecourses.set_index(["CoI","measurement"], append=True, drop=True)
    all_timecourses = all_timecourses.reset_index(level=0,drop=True)
    
    #downsamples the timecourse:
    timecourse_plot = all_timecourses.groupby(level=0).apply(downsample, sample=sample_by, group='measurement')
    
    #BEGI SEMS
    SEM_timecourse_normed = all_timecourses.groupby(level=(0,1)).aggregate(sem)
    SEM_timecourse_plot = SEM_timecourse_normed.groupby(level=0).apply(downsample, sample=sample_by, group='measurement')
    ###END SEMS

    timecourse_plot = timecourse_plot.reset_index(level=1)
    SEM_timecourse_plot = SEM_timecourse_plot.reset_index(level=1)

    #BEGIN PLOTTING
    fig = figure(figsize=(5, 3), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    
    ax1=fig.add_subplot(1,1,1,axisbg='1')
    ax1.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax1.set_axisbelow(True)
    
    plotted = []
    plotted_names = []

    if "fix" in show:
        if make_sem:
            ax1.fill_between(np.array(timecourse_plot.ix["fix"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["fix"]["Pupil"]+SEM_timecourse_plot.ix["fix"]["Pupil"]/2), np.array(timecourse_plot.ix["fix"]["Pupil"]-SEM_timecourse_plot.ix["fix"]["Pupil"]/2), facecolor="0.8", edgecolor="none", alpha=0.2, zorder=0)
        ax1.plot(np.array(timecourse_plot.ix["fix"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["fix"]["Pupil"]), color="0.8",zorder=2)
        fix = Rectangle((0, 0), 1, 1, color="0.8")
        plotted.append(fix)
        plotted_names.append("Fixation")
    if "easy" in show:
        if make_sem:
            ax1.fill_between(np.array(timecourse_plot.ix["easy"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["easy"]["Pupil"]+SEM_timecourse_plot.ix["easy"]["Pupil"]/2), np.array(timecourse_plot.ix["easy"]["Pupil"]-SEM_timecourse_plot.ix["easy"]["Pupil"]/2), facecolor="g", edgecolor="none", alpha=0.1, zorder=0)
        ax1.plot(np.array(timecourse_plot.ix["easy"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["easy"]["Pupil"]), color='g',zorder=2)
        easy = Rectangle((0, 0), 1, 1, color="g")
        plotted.append(easy)
        plotted_names.append("Easy Trials")
    if "hard" in show:
        if make_sem:
            ax1.fill_between(np.array(timecourse_plot.ix["hard"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["hard"]["Pupil"]+SEM_timecourse_plot.ix["hard"]["Pupil"]/2), np.array(timecourse_plot.ix["hard"]["Pupil"]-SEM_timecourse_plot.ix["hard"]["Pupil"]/2), facecolor="m", edgecolor="none", alpha=0.1, zorder=0)
        ax1.plot(np.array(timecourse_plot.ix["hard"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["hard"]["Pupil"]), color='m',zorder=2)
        hard = Rectangle((0, 0), 1, 1, color="m")
        plotted.append(hard)
        plotted_names.append("Hard Trials")
    if "happy" in show:
        if make_sem:
            ax1.fill_between(np.array(timecourse_plot.ix["happy"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["happy"]["Pupil"]+SEM_timecourse_plot.ix["happy"]["Pupil"]/2), np.array(timecourse_plot.ix["happy"]["Pupil"]-SEM_timecourse_plot.ix["happy"]["Pupil"]/2), facecolor="g", edgecolor="none", alpha=0.1, zorder=0)
        ax1.plot(np.array(timecourse_plot.ix["happy"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["happy"]["Pupil"]), color='g',zorder=2)
        happy = Rectangle((0, 0), 1, 1, color="g")
        plotted.append(happy)
        plotted_names.append("'Happy' Trials")
    if "fearful" in show: 
        if make_sem:
            ax1.fill_between(np.array(timecourse_plot.ix["fearful"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["fearful"]["Pupil"]+SEM_timecourse_plot.ix["fearful"]["Pupil"]/2), np.array(timecourse_plot.ix["fearful"]["Pupil"]-SEM_timecourse_plot.ix["fearful"]["Pupil"]/2), facecolor="m", edgecolor="none", alpha=0.1, zorder=0)
        ax1.plot(np.array(timecourse_plot.ix["fearful"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["fearful"]["Pupil"]), color='m',zorder=2)
        fearful = Rectangle((0, 0), 1, 1, color="m")
        plotted.append(fearful)
        plotted_names.append("'Fearful' Trials")
    if "emotion" in show:
        tc = (np.array(timecourse_plot.ix["fearful"]["measurement"])/(60/sample_by)+np.array(timecourse_plot.ix["happy"]["measurement"])/(60/sample_by))/2
        v = (np.array(timecourse_plot.ix["fearful"]["Pupil"])+np.array(timecourse_plot.ix["happy"]["Pupil"]))/2
        if make_sem:
            se = (np.array(SEM_timecourse_plot.ix["fearful"]["Pupil"])+np.array(SEM_timecourse_plot.ix["happy"]["Pupil"]))/4
            ax1.fill_between(tc, v+se, v-se, facecolor="g", edgecolor="none", alpha=0.1, zorder=0)
        ax1.plot(tc, v, color='g',zorder=2)
        emotion = Rectangle((0, 0), 1, 1, color="g")
        plotted.append(emotion)
        plotted_names.append("Emotion Trials")
    if "scrambled" in show:
        if make_sem:
            ax1.fill_between(np.array(timecourse_plot.ix["scrambled"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["scrambled"]["Pupil"]+SEM_timecourse_plot.ix["scrambled"]["Pupil"]/2), np.array(timecourse_plot.ix["scrambled"]["Pupil"]-SEM_timecourse_plot.ix["scrambled"]["Pupil"]/2), facecolor="m", edgecolor="none", alpha=0.1, zorder=0)
        ax1.plot(np.array(timecourse_plot.ix["scrambled"]["measurement"])/(60/sample_by), np.array(timecourse_plot.ix["scrambled"]["Pupil"]), color='m',zorder=2)
        scrambled = Rectangle((0, 0), 1, 1, color="m")
        plotted.append(scrambled)
        plotted_names.append("Scrambled Trials")
    if "all" in show:
        all_tc = (np.array(timecourse_plot.ix["easy"]["measurement"])/(60/sample_by)+np.array(timecourse_plot.ix["hard"]["measurement"])/(60/sample_by))/2
        all_v = (np.array(timecourse_plot.ix["easy"]["Pupil"])+np.array(timecourse_plot.ix["hard"]["Pupil"]))/2
        if make_sem:
            all_se = (np.array(SEM_timecourse_plot.ix["easy"]["Pupil"])+np.array(SEM_timecourse_plot.ix["hard"]["Pupil"]))/4
            ax1.fill_between(all_tc, all_v+all_se, all_v-all_se, facecolor="g", edgecolor="none", alpha=0.1, zorder=0)
        ax1.plot(all_tc, all_v, color='g',zorder=2)
        ALL = Rectangle((0, 0), 1, 1, color="g")
        plotted.append(ALL)
        plotted_names.append("All Trials")

    if "rt_e" in show:
        ax1.axvline(rt[(rt["difficulty"] == "easy")]["RT"].mean(), linewidth=0.3, color='g', zorder=1)
    if "rt_h" in show:
        ax1.axvline(rt[(rt["difficulty"] == "hard")]["RT"].mean(), linewidth=0.3, color='m', zorder=1)
    if "rt_ha" in show:
        ax1.axvline(rt[(rt["emotion"] == "happy")]["RT"].mean(), linewidth=0.3, color='g', zorder=1)
    if "rt_fe" in show:
        ax1.axvline(rt[(rt["emotion"] == "fearful")]["RT"].mean(), linewidth=0.3, color='m', zorder=1)
    if "rt_em" in show:
        ax1.axvline(rt[(rt["emotion"] != "scrambled")]["RT"].mean(), linewidth=0.3, color='g', zorder=1)
    if "rt_sc" in show:
        ax1.axvline(rt[(rt["emotion"] == "scrambled")]["RT"].mean(), linewidth=0.3, color='m', zorder=1)
    if "rt_all" in show:
        ax1.axvline(rt[(rt["difficulty"] == "easy") | (rt["difficulty"] == "hard")]["RT"].mean(), linewidth=0.3, color='g', zorder=1)

    ax1.tick_params(axis='both', labelsize=8*fontscale)
    ax1.set_ylabel('Pupil Area Ratio', fontsize=11*fontscale)
    ax1.set_xlabel('Time [s]', fontsize=11*fontscale)
    legend((plotted),(plotted_names),loc='upper center', bbox_to_anchor=(0.5, 1.06), ncol=3, fancybox=False, shadow=False, prop=FontProperties(size=str(9*fontscale)))
    #END PLOTTING
    
    return all_timecourses

def discrete_time(make_tight=True, show="", sample_size=40, fontscale=1):
    df = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', baseline="participant", force_new=False)
    df["Time"] = df["Time"]/1000 #make seconds (from milliseconds)
   
    discretize = {0:"S01", 1:"S02", 2:"S03", 3:"S04", 4:"S05", 5:"S06", 6:"S07", 7:"S08", 8:"S09", 9:"S10", 10:"S11", 11:"S12", 12:"S13", 13:"S14", 14:"S15", 15:"S16", 16:"S17", 17:"S18", 18:"S19", 19:"S20"}
    
    df = df.groupby(level=[0,1]).apply(downsample, sample=sample_size+1, group='measurement')
    df.reset_index(inplace=True)

    #fixation has a jitter and building a mean gives smaller time values for the last time points:
    df.ix[(df["CoI"] == "fix"), "Time"] = (df[(df["CoI"] == "easy")]["Time"]+df[(df["CoI"] == "hard")]["Time"])/2 

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
        ax1.plot(pos_ids, np.array(df_means.ix["happy"]["Pupil"]), "^-", markeredgecolor="none", linewidth=0.2, color='g')
        happy = Rectangle((0, 0), 1, 1, color="g")
        plotted.append(happy)
        plotted_names.append("Happy Trials")
    if "fearful" in show: 
        ax1.plot(pos_ids, np.array(df_means.ix["fearful"]["Pupil"]), "v-", markeredgecolor="none", linewidth=0.2, color='m')
        fearful = Rectangle((0, 0), 1, 1, color="m")
        plotted.append(fearful)
        plotted_names.append("Fearful Trials")
    if "emotion" in show:
        ax1.plot(pos_ids, (np.array(df_means.ix["happy"]["Pupil"])+np.array(df_means.ix["fearful"]["Pupil"]))/2, "^-", markeredgecolor="none", linewidth=0.2, color='g')
        emotion = Rectangle((0, 0), 1, 1, color="g")
        plotted.append(emotion)
        plotted_names.append("Emotion Trials")
    if "scrambled" in show:
        ax1.plot(pos_ids, np.array(df_means.ix["scrambled"]["Pupil"]), "v-", markeredgecolor="none", linewidth=0.2, color='m')
        scrambled = Rectangle((0, 0), 1, 1, color="m")
        plotted.append(scrambled)
        plotted_names.append("Scrambled Trials")
    
    ax1.set_xticks(pos_ids)
    ax1.set_xticklabels(ids,fontsize=9*fontscale) # add rotation=30 if things get too crowded
    
    ax1.set_ylabel('Pupil Area Ratio', fontsize=11*fontscale)
    ax1.set_xlabel('Time Series Sextiles [66 ms]', fontsize=11*fontscale)
    axis.Axis.zoom(ax1.xaxis, -0.6) # sets x margins further apart from the content proportional to its length
    axis.Axis.zoom(ax1.yaxis, -0.4) # sets x margins further apart from the content proportional to its length
    legend((plotted),(plotted_names),loc='upper center', bbox_to_anchor=(0.5, 1.06), ncol=3, fancybox=False, shadow=False, prop=FontProperties(size=str(5*fontscale)))
    #END PLOTTING
    
    return df
