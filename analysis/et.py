#!/usr/bin/env python
from __future__ import division
__author__ = 'Horea Christian'
from data_functions import get_et_data
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from pylab import figure, show, errorbar, setp, legend

categories = [
	['difficulty', 'easy', 'em100|cell22rand'],
	['difficulty', 'hard', 'em40|cell10rand'],
	['emotion', 'happy', 'HA-cell'],
	['emotion', 'fearful', 'FE-cell'],
	['emotion', 'scrambled', 'cell'],
    ['fixation', 'fix', 'fix']
	]

def main(source=False, make_tight=True):
    timecourse = get_et_data(make='timecourse', make_categories=categories, savefile='time_series.csv', force_new=True)
    #~ print timecourse.index.tolist()


    timecourse_means = timecourse.groupby(level=(1,2)).mean()
    
    timecourse_fix_mean = (timecourse_means.ix["fix"]["L Dia Y [px]"].mean()+timecourse_means.ix["fix"]["L Dia Y [px]"].mean())/2
    #~ normalize = lambda x: (x / timecourse_fix_mean)
    
    #~ timecourse_means = timecourse_means.groupby(level=0).transform(normalize)
    #~ timecourse_means = timecourse.groupby(level=(1,2)).aggregate(np.median)
    timecourse_sems = timecourse.groupby(level=(1,2)).aggregate(stats.sem)
    
    #~ print timecourse_sems.ix['easy'].ix[:10] 
    
    fig = figure(figsize=(4, 3), dpi=300,facecolor='#eeeeee', tight_layout=make_tight)
    ax1=fig.add_subplot(2,2,1)
    ax2=fig.add_subplot(2,2,2)
    ax3=fig.add_subplot(2,2,3)
    ax4=fig.add_subplot(2,2,4)
    ax1.yaxis.grid(True, linestyle='-', which='major', color='#dddddd',alpha=0.6, zorder = 0)
    ax1.set_axisbelow(True)
    
    #~ plt.plot(np.array(timecourse_means.ix["easy"]["Time"])/1000, np.array(timecourse_means.ix["easy"]["L Dia X [px]"]), color='m')
    #~ plt.plot(np.array(timecourse_means.ix["easy"]["Time"])/1000, np.array(timecourse_means.ix["easy"]["L Dia Y [px]"]), color='g')
    ax1.plot(np.array(timecourse_means.ix["easy"]["Time"])/1000, (np.array(timecourse_means.ix["easy"]["L Dia Y [px]"])+np.array(timecourse_means.ix["easy"]["L Dia X [px]"]))/timecourse_fix_mean/2, color='g')
    ax1.plot(np.array(timecourse_means.ix["hard"]["Time"])/1000, (np.array(timecourse_means.ix["hard"]["L Dia Y [px]"])+np.array(timecourse_means.ix["hard"]["L Dia X [px]"]))/timecourse_fix_mean/2, color='m')
    ax2.plot(np.array(timecourse_means.ix["happy"]["Time"])/1000, (np.array(timecourse_means.ix["happy"]["L Dia Y [px]"])+np.array(timecourse_means.ix["happy"]["L Dia X [px]"]))/timecourse_fix_mean/2, color='g')
    ax2.plot(np.array(timecourse_means.ix["fearful"]["Time"])/1000, (np.array(timecourse_means.ix["fearful"]["L Dia Y [px]"])+np.array(timecourse_means.ix["fearful"]["L Dia X [px]"]))/timecourse_fix_mean/2, color='m')
    ax3.plot(np.array(timecourse_means.ix["scrambled"]["Time"])/1000, (np.array(timecourse_means.ix["scrambled"]["L Dia Y [px]"])+np.array(timecourse_means.ix["scrambled"]["L Dia X [px]"]))/timecourse_fix_mean/2, color='m')
    ax3.plot((np.array(timecourse_means.ix["happy"]["Time"])+np.array(timecourse_means.ix["happy"]["Time"]))/2000, (np.array(timecourse_means.ix["happy"]["L Dia Y [px]"])+np.array(timecourse_means.ix["happy"]["L Dia X [px]"])+np.array(timecourse_means.ix["fearful"]["L Dia Y [px]"])+np.array(timecourse_means.ix["fearful"]["L Dia X [px]"]))/timecourse_fix_mean/4, color='g')

if __name__ == '__main__':
    main()
    show()
