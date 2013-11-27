#!/usr/bin/env python
from __future__ import division
__author__ = 'Horea Christian'
from data_functions import get_rt_data, downsample
import numpy as np
import scipy as sp
import pandas as pd
from scipy.stats import sem, pearsonr
from matplotlib import axis
import matplotlib.pyplot as plt
from pylab import figure, show, errorbar, setp, legend
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle

categories = [
	['difficulty', 'easy', 'em100|cell22rand'],
	['difficulty', 'hard', 'em40|cell10rand'],
	['emotion', 'happy', 'HA-cell'],
	['emotion', 'fearful', 'FE-cell'],
	['emotion', 'scrambled', 'cell']
	]

def main(make=False, source=False, make_tight=True, compare="difficulty", show="", make_std=True, make_sem=True, ecolor='0.3', elinewidth=2, total="means"):
    data_all = get_rt_data(make_categories=categories)
    data_all["RT"] = data_all["RT"] / 10000 #make seconds
    
    ids = sorted(list(data_all.index.levels[0]))
    pos_ids = np.arange(len(ids))
    fig = figure(figsize=(pos_ids.max()*5, 4), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    ax=fig.add_subplot(1,1,1)
    ax.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax.set_axisbelow(True)
    width = 0.12

    #below this: per-participant graphs
    plot_em_easy = plt.bar(pos_ids-2*width, data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean(), width ,color='m', alpha=0.7, zorder = 1, linewidth=0)
    plot_em_hard = plt.bar(pos_ids-width, data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean(), width ,color='m', alpha=0.4, zorder = 1, linewidth=0)
    plot_sc_easy = plt.bar(pos_ids, data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean(), width ,color="g", alpha=0.7, zorder = 1, linewidth=0)
    plot_sc_hard = plt.bar(pos_ids+width, data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean(), width ,color="g", alpha=0.4, zorder = 1, linewidth=0)
    if make_std:
	errorbar(pos_ids-(width*1.5), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean(), yerr=data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].aggregate(np.std), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids-(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean(), yerr=data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].aggregate(np.std), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids+(width*0.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean(), yerr=data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].aggregate(np.std), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids+(width*1.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean(), yerr=data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].aggregate(np.std), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
    if make_sem:
	errorbar(pos_ids-(width*1.5), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean(), yerr=data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].aggregate(sem), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids-(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean(), yerr=data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].aggregate(sem), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids+(width*0.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean(), yerr=data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].aggregate(sem), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids+(width*1.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean(), yerr=data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].aggregate(sem), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)

    #below this: total graphs
    if total == 'all':
	plt.bar(pos_ids[-1]+1-width, data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), width ,color='m', alpha=0.7, zorder = 1, linewidth=0)
	plt.bar(pos_ids[-1]+1, data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), width ,color='m', alpha=0.4, zorder = 1, linewidth=0)
	plt.bar(pos_ids[-1]+1+width, data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), width ,color='g', alpha=0.7, zorder = 1, linewidth=0)
	plt.bar(pos_ids[-1]+1+2*width, data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), width ,color='g', alpha=0.4, zorder = 1, linewidth=0)
	if make_std:
	    errorbar(pos_ids[-1]+1-(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), yerr=np.std(data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")]['RT']), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), yerr=np.std(data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")]['RT']), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width*1.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), yerr=np.std(data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")]['RT']), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width*2.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), yerr=np.std(data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")]['RT']), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	if make_sem:
	    errorbar(pos_ids[-1]+1-(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), yerr=sem(data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")]['RT']), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), yerr=sem(data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")]['RT']), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width*1.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), yerr=sem(data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")]['RT']), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width*2.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), yerr=sem(data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")]['RT']), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
    elif total == 'means':
	plt.bar(pos_ids[-1]+1-width, data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), width ,color='m', alpha=0.7, zorder = 1, linewidth=0)
	plt.bar(pos_ids[-1]+1, data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), width ,color='m', alpha=0.4, zorder = 1, linewidth=0)
	plt.bar(pos_ids[-1]+1+width, data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), width ,color='g', alpha=0.7, zorder = 1, linewidth=0)
	plt.bar(pos_ids[-1]+1+2*width, data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), width ,color='g', alpha=0.4, zorder = 1, linewidth=0)
	if make_std:
	    errorbar(pos_ids[-1]+1-(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), yerr=np.std(data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean()), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), yerr=np.std(data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean()), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width*1.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), yerr=np.std(data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean()), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width*2.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), yerr=np.std(data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean()), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	if make_sem:
	    errorbar(pos_ids[-1]+1-(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), yerr=sem(data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean()), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width/2), data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), yerr=sem(data_all[(data_all['emotion'] != "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean()), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width*1.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")]['RT'].mean(), yerr=sem(data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "easy")].groupby(level=0)['RT'].mean()), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	    errorbar(pos_ids[-1]+1+(width*2.5), data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")]['RT'].mean(), yerr=sem(data_all[(data_all['emotion'] == "scrambled") & (data_all['difficulty'] == "hard")].groupby(level=0)['RT'].mean()), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)

    width_multiplier = 4
    plt.axvline(pos_ids[-1]+1-width*width_multiplier, color='0.2') #separator - per-person/total
    #~ scrambling_list = [str(i) for i in scrambling_list if i != 0] #format as string for legend
    #~ 
    ids=ids+['  ALL']
    pos_ids = np.arange(len(ids))
    ax.set_ylabel(r'$\mathsf{\overline{RT}}$ [s]', fontsize=11)
    ax.set_xlabel('Participant', fontsize=11)
    ax.set_xticks(pos_ids)
    ax.set_xticklabels(ids,fontsize=9) # add rotation=30 if things get too crowded
    for tick in ax.axes.get_xticklines():
	    tick.set_visible(False)
    ax.set_xlim(0, pos_ids[-1]+width*1) # before scaling to add padding in front of zero
    axis.Axis.zoom(ax.xaxis, -0.8) # sets x margins further apart from the content proportional to its length
    axis.Axis.zoom(ax.yaxis, -0.5) # sets y margins further apart from the content proportional to its length
    ax.set_ylim(bottom=0) # after scaling to disregard padding unerneath zero.
    legend((plot_em_easy, plot_em_hard, plot_sc_easy, plot_sc_hard),('Strong Emotion','Weak Emotion', "Easy Scrambling", "Hard Scrambling"),loc='upper center', bbox_to_anchor=(0.5, 1.065), ncol=4, fancybox=False, shadow=False,prop= FontProperties(size='8'))

    return data_all


if __name__ == '__main__':
    main(show=["fix","easy","hard"])
    show()

