#!/usr/bin/env python
__author__ = 'Horea Christian'


cats = [
	['difficulty', 'easy', 'em100|cell22rand'],
	['difficulty', 'hard', 'em40|cell10rand'],
	['emotion', 'happy', 'HA-cell'],
	['emotion', 'fearful', 'FE-cell'],
	['emotion', 'scrambled', 'cell']
	]

def get_et_data(source=False, make='timecourse', make_categories=cats):
	from os import path
	import sys
	import pandas as pd
	import numpy as np
	import math
	from chr_helpers import get_config_file
	
	config = get_config_file(localpath=path.dirname(path.realpath(__file__))+'/')
	
	#IMPORT VARIABLES
	if not source:
		source = config.get('Source', 'source')
	data_path = config.get('Addresses', source)
	#END IMPORT VARIABLES
	
	if source == 'local':
		from os import listdir
		data_path = path.expanduser(data_path)
		pre_fileslist = listdir(data_path)
		
	print('Loading data from '+data_path)
	if pre_fileslist == []:
		raise InputError('For some reason the list of results files could not be populated.')

	files = [lefile for lefile in pre_fileslist if lefile.endswith('.txt')]
	files = files[3:4]
	
	data_all = pd.DataFrame([]) # empty container frame for concatenating input from multiple files
	for lefile in files:
		print lefile
		data_lefile = pd.DataFrame.from_csv(data_path+lefile, header=42, sep='\t')
		data_lefile = data_lefile.reset_index()
		data_lefile = data_lefile.dropna(axis=1, how='all', thresh=3) #remove non informative (null) columns
				
		#CUTOFF AT 'pulse_start'
		cutoff = data_lefile[(data_lefile['L Raw X [px]'] == '# Message: pulse_start')].index.tolist()
		cutoff = int(cutoff[-1])
		data_lefile = data_lefile[cutoff:]
		data_lefile = data_lefile.reset_index() #make new index
		data_lefile = data_lefile.drop(['index'],1) # drop old index
		data_lefile.index.name = 'measurement'
		data_lefile['Trial'] = data_lefile['Trial'] - data_lefile['Trial'].ix[0] #trial number relative to first remaining trial
		data_lefile['Time'] = (data_lefile['Time'] - data_lefile['Time'].ix[0])/1000 #time relative to first remaining time point; turn time to milliseconds
		#END CUTOFF AT 'pulse_start'
		
		if make_categories:
			new_category_names = set([new_cat[0] for new_cat in cats])
			for new_category_name in new_category_names:
				data_lefile[new_category_name]='' 
			trial_key = data_lefile[(data_lefile['Type'] == 'MSG')][['Trial','L Raw X [px]']].rename(columns={'L Raw X [px]': 'message'}) #crop and rename
			trial_key = np.array(trial_key) #for easier iteration
			for category in cats:
				criterion = category[-1]
				for trial in trial_key:
					trial[1] = trial[1].split(' ')[-1]
					if '-' in criterion:
						if criterion.split('-')[0] in trial[1] and criterion.split('-')[1] not in trial[1]:
							data_lefile.ix[(data_lefile['Trial']==trial[0]), category[0]] = category[1]
					elif '|' in criterion:
						if criterion.split('|')[0] in trial[1] or criterion.split('|')[1] in trial[1]:
							data_lefile.ix[(data_lefile['Trial']==trial[0]), category[0]] = category[1]
					else:
						if criterion in trial[1]:
							data_lefile.ix[(data_lefile['Trial']==trial[0]), category[0]] = category[1]
		
		#~ #MAKE MULTIINDEX
		grouped = data_lefile.reset_index().groupby('Trial')
		data_lefile['measurement'] = grouped.apply(lambda x: pd.Series(np.arange(len(x)), x.index))
		data_lefile.set_index(['Trial', 'measurement'], inplace=True)
		#~ #MAKE MULTIINDEX
		
		if make == 'timecourse':
			data_all = pd.DataFrame([])
			for category in cats:
				group = data_lefile[(data_lefile[category[0]] == category[1])]
				group = group.groupby(level=1).mean()
				group['Time'] = group['Time']-group['Time'].min()
				group['CoI'] = ''
				group['CoI'] = category[1]
				group = group.set_index(['CoI'], append=True, drop=True)
				group = group.reorder_levels(['CoI','measurement'])
				data_all = pd.concat([data_all, group], ignore_index=False)
				#~ data_all.set_index(['CoI', 'mesurement'])
				print np.shape(data_all), data_all.ix[1]
		elif isinstance(make, int):
			data_lefile.set_index(['measurement'], inplace=True)
			print data_lefile.unstack().columns.tolist()
			avg = data_lefile.groupby("Trial")['L Dia X [px]'].agg({0: lambda x: x.head((len(x)+1)//make).mean(), 
                                       1: lambda x: x.tail((len(x)+1)//make).mean()}) 
			result = pd.melt(avg.reset_index(), "Trial", var_name="Measurement", value_name="L Dia X [px]")
			result = result.sort("Trial").set_index(["Trial", "Measurement"])
			print result
		else:
			print 'Please specify the "make" argumant as either "timecourse" or an integer.'
	
		#ADD ID
		#~ data_lefile['ID']=lefile.split('_')[0]
		#~ data_lefile = data_lefile.set_index(['ID'], append=True, drop=True)
		#~ data_lefile = data_lefile.reorder_levels(['ID','Trial','measurement'])
		#END ADD ID

def categories_of_interest(data_frame, scrambling_list):
	# DEFINE CATEGORIES OF INTEREST (COI)
	data_frame['COI']='' 
	data_frame.ix[(data_frame['scrambling'] == 0) & (data_frame['intensity'] == 100), 'COI'] = 'em-easy'
	data_frame.ix[(data_frame['scrambling'] == 0) & (data_frame['intensity'] == 40), 'COI'] = 'em-hard'
	for i in scrambling_list:
		if i != 0: #don't overwrite emotion tags
			data_frame.ix[(data_frame['scrambling'] == i), 'COI'] = 'sc-' + str(i)
			data_frame.ix[(data_frame['scrambling'] == i), 'COI'] = 'sc-' + str(i)
			data_frame.ix[(data_frame['scrambling'] == i), 'COI'] = 'sc-' + str(i)
			data_frame.ix[(data_frame['scrambling'] == i), 'COI'] = 'sc-' + str(i)
			data_frame.ix[(data_frame['scrambling'] == i), 'COI'] = 'sc-' + str(i)
	# END DEFINE CATEGORIES OF INTEREST (COI)
	return data_frame

if __name__ == '__main__':
	get_et_data(make=2)
	#~ show()
