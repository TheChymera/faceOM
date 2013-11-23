#!/usr/bin/env python
__author__ = 'Horea Christian'

def get_et_data(source=False, make='timecourse', make_categories='', savefile='', force_new=False):
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
	eye_tracking = config.get('Data', 'eye_tracking')
	preprocessed_path = config.get('Data', 'df_dir')
	#END IMPORT VARIABLES
	
	
	if source == 'local':
		from os import listdir
		data_path = path.expanduser(data_path+eye_tracking)
		pre_fileslist = listdir(data_path)
		if savefile:
			preprocessed_file = path.expanduser(data_path+preprocessed_path+savefile)
			if path.exists(preprocessed_file) and not force_new:
				data_all = pd.DataFrame.from_csv(preprocessed_file)
				data_all = data_all.set_index(['CoI'],append=True, drop=True)
				data_all = data_all.set_index(['measurement'],append=True, drop=True)
				data_all = data_all.reorder_levels(['ID','CoI','measurement'])
				return data_all
		
	print('Loading data from '+data_path)
	if pre_fileslist == []:
		raise InputError('For some reason the list of results files could not be populated.')

	files = [lefile for lefile in pre_fileslist if lefile.endswith('.txt')]
	
	data_all = [] # empty container list for listing per-file dataframes
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
			new_category_names = set([new_cat[0] for new_cat in make_categories])
			for new_category_name in new_category_names:
				data_lefile[new_category_name]='' 
			trial_key = data_lefile[(data_lefile['Type'] == 'MSG')][['Trial','L Raw X [px]']] #crop
			trial_key = np.array(trial_key) #for easier iteration
			for category in make_categories:
				criterion = category[-1]
				for trial in trial_key:
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
		#~ print data_lefile.xs(320, level=1)
		
		if make == 'timecourse':
			groups_all = []
			for category in make_categories:
				print "Binning category:"+"\""+category[1]+"\""
				group = data_lefile[(data_lefile[category[0]] == category[1])]
				group = group.groupby(level=1).mean() # make per-category means
				#~ if category[1] == 'fix':
					#~ group = group.ix[:160] # because this has a jitter
				#~ else:
				group = group.ix[:240] # means for timepoints with missing values will be smaller.
				group['Time'] = group['Time']-group['Time'].ix[0]
				group['CoI'] = ''
				group['CoI'] = category[1]
				group = group.set_index(['CoI'], append=True, drop=True)
				group = group.reorder_levels(['CoI','measurement'])
				groups_all.append(group)
			data_lefile = pd.concat(groups_all)
		elif isinstance(make, int):
			data_lefile = data_lefile.reset_index()
			avg = data_lefile.groupby("Trial")['L Dia X [px]'].agg({0: lambda x: x.head((len(x)+1)//make).mean(), 
                                       1: lambda x: x.tail((len(x)+1)//make).mean()}) 
			result = pd.melt(avg.reset_index(), "Trial", var_name="measurement", value_name="L Dia X [px]")
			result = result.sort("Trial").set_index(["Trial", "measurement"])
			print result
		else:
			print 'Please specify the "make" argumant as either "timecourse" or an integer.'
	
		#ADD ID
		data_lefile['ID']=lefile.split('_')[0]
		data_lefile = data_lefile.set_index(['ID'], append=True, drop=True)
		data_lefile = data_lefile.reorder_levels(['ID','CoI','measurement'])
		#END ADD ID
		
		data_all.append(data_lefile)
	data_all = pd.concat(data_all)
	data_all.reorder_levels(['ID','CoI','measurement'])
	
	if savefile:
		data_all.to_csv(preprocessed_file)
	
	return data_all

def sequence_check(source=False):
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
	eye_tracking = config.get('Data', 'eye_tracking')
	fmri_logfile = config.get('Data', 'fmri_logfile')
	preprocessed_path = config.get('Data', 'df_dir')
	#END IMPORT VARIABLES
	
	if source == 'local':
		from os import listdir
		eye_tracking = path.expanduser(data_path+eye_tracking)
		fmri_logfile = path.expanduser(data_path+fmri_logfile)
		eye_pre_fileslist = listdir(eye_tracking)
		fmri_pre_fileslist = listdir(fmri_logfile)
	
	et_files = sorted([lefile for lefile in eye_pre_fileslist if lefile.endswith('.txt')])[:9]
	fmri_files = sorted([lefile for lefile in fmri_pre_fileslist if lefile.endswith('OM.log') and not lefile.startswith('KP') and not lefile.startswith('ET_')])[:9]
	files = np.array([[a for a in et_files],[b for b in fmri_files]]).T
	
	for et, fmri in files:
		et_file = pd.DataFrame.from_csv(eye_tracking+et, header=42, sep='\t').reset_index()
		
		# CUTOFF PREVIOUS EXPERIMENTS
		cutoff = et_file[(et_file['L Raw X [px]'] == '# Message: pulse_start')].index.tolist()
		cutoff = int(cutoff[-1])
		et_file = et_file[cutoff:]
		# END CUTOFF PREVIOUS EXPERIMENTS

		et_file = et_file[(et_file['Type']=='MSG')].reset_index()
		et_file = et_file[['L Raw X [px]']].ix[1:].reset_index() #eliminate first row ("pulse_start")
		fmri_file = pd.DataFrame.from_csv(fmri_logfile+fmri, header=3, sep='\t').reset_index()
		fmri_file = fmri_file[(fmri_file['Event Type']=='Picture')].reset_index()
		fmri_file = fmri_file[['Code']]
		seq_file = pd.concat([et_file, fmri_file], axis=1).drop(['index'],1) # drop old index
		seq_file.columns = ['ET', 'fMRI']
		
		seq_file.to_csv(fmri_logfile+"/sequence-check/seq-chk_"+fmri)
		
		#~ for i in np.arange(len(seq_file)):
			#~ if seq_file.ix[i]['fMRI'] not in seq_file.ix[i]['ET']:
				#~ print fmri, i, seq_file.ix[i]['fMRI'], seq_file.ix[i]['ET']

if __name__ == '__main__':
	sequence_check()
	#~ show()
