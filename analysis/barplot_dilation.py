#!/usr/bin/env python
from __future__ import division
__author__ = 'Horea Christian'
from data_functions import get_et_data
import numpy as np
import scipy as sp
import pandas as pd
from scipy.stats import sem
import matplotlib.pyplot as plt
from matplotlib import axis
from pylab import figure, show, errorbar, setp, legend
from matplotlib.font_manager import FontProperties

categories_of_interest = [
    ['CoI', 'fix', 'fix'],
    ['CoI', 'emotion-easy', 'em40'],
    ['CoI', 'emotion-hard', 'em100'],
    ['CoI', 'scrambling-easy', 'cell10rand'],
    ['CoI', 'scrambling-hard', 'cell22rand']
    ]

def main(make=False, source=False, make_tight=True, compare="difficulty", show="", make_std=True, make_sem=True, ecolor='0.3', elinewidth=2, total="means", make_scrambled_yn=False, per_participant_error=False):
    data_all = get_et_data(make='timecourse', make_categories=categories_of_interest, savefile='time_series_CoI.csv', baseline="global", force_new=False)
    data_all["Time"] = data_all["Time"]/1000 #make seconds (from milliseconds)
    
    data_all = data_all.reset_index(drop=False)
    data_all = data_all.set_index(["CoI","measurement","ID"], append=True, drop=True)
    data_all = data_all.reset_index(level=0,drop=True)
    
    ids = sorted(list(data_all.index.levels[2]))
    pos_ids = np.arange(len(ids))
    fig = figure(figsize=(pos_ids.max()*5, 4), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    ax=fig.add_subplot(1,1,1)
    ax.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax.set_axisbelow(True)
    width = 0.12

    #below this: per-participant graphs
    fix = plt.bar(pos_ids-3*width, data_all.ix["fix"].groupby(level=(1))['Pupil'].mean(), width ,color='k', alpha=0.25, zorder = 1, linewidth=0)
    plot_em_easy = plt.bar(pos_ids-2*width, data_all.ix["emotion-easy"].groupby(level=(1))['Pupil'].mean(), width ,color='m', alpha=0.7, zorder = 1, linewidth=0)
    plot_em_hard = plt.bar(pos_ids-width, data_all.ix["emotion-hard"].groupby(level=(1))['Pupil'].mean(), width ,color='m', alpha=0.4, zorder = 1, linewidth=0)
    plot_sc_easy = plt.bar(pos_ids, data_all.ix["scrambling-easy"].groupby(level=(1))['Pupil'].mean(), width ,color='g', alpha=0.7, zorder = 1, linewidth=0)
    plot_sc_hard = plt.bar(pos_ids+width, data_all.ix["scrambling-hard"].groupby(level=(1))['Pupil'].mean(), width ,color='g', alpha=0.4, zorder = 1, linewidth=0)
    if per_participant_error:
        if make_std:
            for idx, category in enumerate([category_data[1] for category_data in categories_of_interest]):
                errorbar(pos_ids+(width*(-2.5+1*idx)), data_all.ix[category].groupby(level=(1))['Pupil'].mean(), yerr=data_all.ix[category].groupby(level=1)['Pupil'].aggregate(np.std), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
        if make_sem:
            for idx, category in enumerate([category_data[1] for category_data in categories_of_interest]):
                errorbar(pos_ids+(width*(-2.5+1*idx)), data_all.ix[category].groupby(level=(1))['Pupil'].mean(), yerr=data_all.ix[category].groupby(level=1)['Pupil'].aggregate(sem), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)        
    #below this: total graphs
    plt.bar(pos_ids[-1]+1-width, data_all.ix["fix"]['Pupil'].mean(), width ,color='k', alpha=0.25, zorder = 1, linewidth=0)
    plt.bar(pos_ids[-1]+1, data_all.ix["emotion-easy"]['Pupil'].mean(), width ,color='m', alpha=0.7, zorder = 1, linewidth=0)
    plt.bar(pos_ids[-1]+1+width, data_all.ix["emotion-hard"]['Pupil'].mean(), width ,color='m', alpha=0.4, zorder = 1, linewidth=0)
    plt.bar(pos_ids[-1]+1+2*width, data_all.ix["scrambling-easy"]['Pupil'].mean(), width ,color='g', alpha=0.7, zorder = 1, linewidth=0)
    plt.bar(pos_ids[-1]+1+3*width, data_all.ix["scrambling-hard"]['Pupil'].mean(), width ,color='g', alpha=0.4, zorder = 1, linewidth=0)
    if total == 'all':
        if make_std:
            for idx, category in enumerate([category_data[1] for category_data in categories_of_interest]):
                errorbar(pos_ids[-1]+1+(width*(-0.5+1*idx)), data_all.ix[category]['Pupil'].mean(), yerr=np.std(data_all.ix[category]['Pupil']), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
        if make_sem:
            for idx, category in enumerate([category_data[1] for category_data in categories_of_interest]):
                errorbar(pos_ids[-1]+1+(width*(-0.5+1*idx)), data_all.ix[category]['Pupil'].mean(), yerr=sem(data_all.ix[category]['Pupil']), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
    elif total == 'means':
        if make_std:
            for idx, category in enumerate([category_data[1] for category_data in categories_of_interest]):
                errorbar(pos_ids[-1]+1+(width*(-0.5+1*idx)), data_all.ix[category]['Pupil'].mean(), yerr=np.std(data_all.ix[category].groupby(level=1)['Pupil'].mean()), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
        if make_sem:
            for idx, category in enumerate([category_data[1] for category_data in categories_of_interest]):
                errorbar(pos_ids[-1]+1+(width*(-0.5+1*idx)), data_all.ix[category]['Pupil'].mean(), yerr=sem(data_all.ix[category].groupby(level=1)['Pupil'].mean()), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)

    width_multiplier = 4
    plt.axvline(pos_ids[-1]+1-width*width_multiplier, color='0.2') #separator - per-person/total
    #~ scrambling_list = [str(i) for i in scrambling_list if i != 0] #format as string for legend
    #~ 
    ids=ids+['      ALL']
    pos_ids = np.arange(len(ids))
    ax.set_ylabel(r'$\mathsf{\overline{RT}}$ [s]', fontsize=11)
    ax.set_xlabel('Participant', fontsize=11)
    ax.set_xticks(pos_ids)
    ax.set_xticklabels(ids,fontsize=7.5) # add rotation=30 if things get too crowded
    for tick in ax.axes.get_xticklines():
	    tick.set_visible(False)
    ax.set_xlim(0, pos_ids[-1]+width*1) # before scaling to add padding in front of zero
    axis.Axis.zoom(ax.xaxis, -0.8) # sets x margins further apart from the content proportional to its length
    axis.Axis.zoom(ax.yaxis, -0.5) # sets y margins further apart from the content proportional to its length
    ax.set_ylim(bottom=0) # after scaling to disregard padding unerneath zero.
    legend((fix, plot_em_easy, plot_em_hard, plot_sc_easy, plot_sc_hard),("Fixation",'Strong Emotion','Weak Emotion', "Easy Scrambling", "Hard Scrambling"),loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=5, fancybox=False, shadow=False, prop=FontProperties(size='7'))
    data_all.to_csv("/home/chymera/RT.csv")
    
    return data_all
    
    
if __name__ == '__main__':
    main()
    show()
