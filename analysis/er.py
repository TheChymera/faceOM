#!/usr/bin/env python
from __future__ import division
__author__ = 'Horea Christian'
from scipy.stats import sem
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.font_manager import FontProperties
from pylab import figure, show, errorbar, setp, legend
from matplotlib import axis
from data_functions import get_rt_data
from itertools import product

categories = [
	['difficulty', 'easy', 'em100|cell22rand'],
	['difficulty', 'hard', 'em40|cell10rand'],
	['emotion', 'happy', 'HA-cell'],
	['emotion', 'fearful', 'FE-cell'],
	['emotion', 'scrambled', 'cell']
	]
	
conditions = [
	[
	['difficulty', 'easy'],
	['difficulty', 'hard']
	],
	[
	['emotion', 'happy'],
	['emotion', 'fearful'],
	['emotion', 'scrambled']
	]
	]

def main(make=False, source=False, make_tight=True, conditions=conditions, show="", make_std=False, make_sem=True, ecolor='0.3', elinewidth=2, total="means", make_scrambled_yn=False, fontscale=1):
    data_all = get_rt_data(make_categories=categories)
    
    ids = sorted(list(data_all.index.levels[0]))
    pos_ids = np.arange(len(ids))
    fig = figure(figsize=(pos_ids.max()*5, 4), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    ax=fig.add_subplot(1,1,1)
    ax.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax.set_axisbelow(True)
    width = 0.12
    
    data_all.reset_index(inplace=True)

    total_errors_columns = ['ID', 'ER'].extend([condition[0][0] for condition in conditions])
    total_errors = pd.DataFrame(columns=total_errors_columns) # empty container frame for concatenating input from multiple files
    
    for le_id in set(data_all['ID']):
	data_for_id = data_all[data_all['ID'] == le_id]
	for C in product(conditions[0], conditions[1]):
	    error_rate = len(data_for_id[(data_for_id[C[0][0]] == C[0][1]) & (data_for_id[C[1][0]] == C[1][1]) & (data_for_id['Type'] == "incorrect")].index)/len(data_for_id[(data_for_id[C[0][0]] == C[0][1]) & (data_for_id[C[1][0]] == C[1][1]) & (data_for_id['Type'] == "hit")].index)
	    
	    row = pd.DataFrame({"ID":[le_id], "ER":[error_rate], C[0][0]:[C[0][1]], C[1][0]:[C[1][1]]})
	    total_errors = total_errors.append(row, ignore_index=True)

    #ADD ID
    total_errors = total_errors.set_index(['ID'], append=True, drop=True)
    total_errors = total_errors.reorder_levels([1,0])
    #END ADD ID
    
    if make_scrambled_yn:
	total_errors["scrambled"]=""
	total_errors.ix[(total_errors["emotion"] == "scrambled"), "scrambled"]= "yes"
	total_errors.ix[(total_errors["emotion"] != "scrambled"), "scrambled"]= "no"

    total_errors_just_plot = total_errors.copy()	# please DO NOT USE THE DATA FROM THIS NEW VARIABLE for anything BUT plotting
    total_errors_just_plot.ix[(total_errors_just_plot['ER'] == 0), 'ER'] = 0.005 # this is a hack to make 0-height bins visible when plotting   
    
    #START DRAWING GRAPHIC ELEMENTS
    #below this: per-participant graphs
    plot_em_easy = plt.bar(pos_ids-2*width, total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "easy")].groupby(level=0)['ER'].mean(), width ,color='m', alpha=0.7, zorder = 1, linewidth=0)
    plot_em_hard = plt.bar(pos_ids-width, total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "hard")].groupby(level=0)['ER'].mean(), width ,color='m', alpha=0.4, zorder = 1, linewidth=0)
    plot_sc_easy = plt.bar(pos_ids, total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "easy")].groupby(level=0)['ER'].mean(), width ,color="g", alpha=0.7, zorder = 1, linewidth=0)
    plot_sc_hard = plt.bar(pos_ids+width, total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "hard")].groupby(level=0)['ER'].mean(), width ,color="g", alpha=0.4, zorder = 1, linewidth=0)

    #below this: total graphs
    plt.bar(pos_ids[-1]+1-width, total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]['ER'].mean(), width ,color='m', alpha=0.7, zorder = 1, linewidth=0)
    plt.bar(pos_ids[-1]+1, total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]['ER'].mean(), width ,color='m', alpha=0.4, zorder = 1, linewidth=0)
    plt.bar(pos_ids[-1]+1+width, total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]['ER'].mean(), width ,color='g', alpha=0.7, zorder = 1, linewidth=0)
    plt.bar(pos_ids[-1]+1+2*width, total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]["ER"].mean(), width ,color='g', alpha=0.4, zorder = 1, linewidth=0)
    if make_std:
	errorbar(pos_ids[-1]+1-(width/2), total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]['ER'].mean(), yerr=np.std(total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]['ER']), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids[-1]+1+(width/2), total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]["ER"].mean(), yerr=np.std(total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]["ER"]), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids[-1]+1+(width*1.5), total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]["ER"].mean(), yerr=np.std(total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]["ER"]), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids[-1]+1+(width*2.5), total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]["ER"].mean(), yerr=np.std(total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]["ER"]), ecolor=str(float(ecolor)+0.25), elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
    if make_sem:
	errorbar(pos_ids[-1]+1-(width/2), total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]["ER"].mean(), yerr=sem(total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]["ER"]), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids[-1]+1+(width/2), total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]["ER"].mean(), yerr=sem(total_errors_just_plot[(total_errors_just_plot['emotion'] != "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]["ER"]), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids[-1]+1+(width*1.5), total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]["ER"].mean(), yerr=sem(total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "easy")]["ER"]), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
	errorbar(pos_ids[-1]+1+(width*2.5), total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]["ER"].mean(), yerr=sem(total_errors_just_plot[(total_errors_just_plot['emotion'] == "scrambled") & (total_errors_just_plot['difficulty'] == "hard")]["ER"]), ecolor=ecolor, elinewidth=elinewidth, capsize=0, linestyle='None', zorder = 2)
  
    width_multiplier = 4
    plt.axvline(pos_ids[-1]+1-width*width_multiplier, color='0.2') #separator - per-person/total

    ids=ids+['   ALL']
    pos_ids = np.arange(len(ids))
    ax.set_ylabel(r'$\mathsf{\Sigma_{wrong} / \Sigma_{all}}$', fontsize=13*fontscale)
    ax.set_xlabel('Participant', fontsize=11*fontscale)
    ax.set_xticks(pos_ids)
    ax.set_xticklabels(ids,fontsize=9*fontscale) # add rotation=30 if things get too crowded
    for tick in ax.axes.get_xticklines():
	    tick.set_visible(False)
    ax.set_xlim(0, pos_ids[-1]+width*1) # before scaling to add padding in front of zero
    axis.Axis.zoom(ax.xaxis, -0.8) # sets x margins further apart from the content proportional to its length
    axis.Axis.zoom(ax.yaxis, -0.5) # sets y margins further apart from the content proportional to its length
    ax.set_ylim(bottom=0) # after scaling to disregard padding unerneath zero.
    legend((plot_em_easy, plot_em_hard, plot_sc_easy, plot_sc_hard),('Strong Emotion','Weak Emotion', "Easy Scrambling", "Hard Scrambling"),loc='upper center', bbox_to_anchor=(0.5, 1.065), ncol=4, fancybox=False, shadow=False,prop= FontProperties(size=str(8*fontscale)))

    return total_errors
