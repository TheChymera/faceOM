#!/usr/bin/env python
__author__ = 'Horea Christian'

def get_et_data(source=False, make='timecourse', pre_cutoff=0, make_categories='', diff=False, savefile='', force_new=False):
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
	regressor_dir = config.get('Data', 'regressor_dir')
	if make == "regressor":
		make = config.getint("Settings", "make")
	if isinstance(make, int) and not pre_cutoff:
		pre_cutoff = config.getint('Settings', 'pre_cutoff')
	#END IMPORT VARIABLES
	
	
	if source == 'local':
		from os import listdir
		data_path = path.expanduser(data_path+eye_tracking)
		pre_fileslist = listdir(data_path)
		regressor_path = path.expanduser(data_path+preprocessed_path+regressor_dir)
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
	
	usually_empty = ["L Mapped Diameter [mm]", "L Validity", "R Validity", " Pupil Confidence"]
	data_all = [] # empty container list for listing per-file dataframes
	for lefile in files:
		print "Processing " + lefile + ":"
		data_lefile = pd.DataFrame.from_csv(data_path+lefile, header=42, sep='\t')
		data_lefile = data_lefile.reset_index()
		data_lefile = data_lefile.dropna(axis=1, how='all', thresh=3) #remove non informative (null) columns
		for field in usually_empty:
			if field in data_lefile.columns.tolist():
				data_lefile = data_lefile.drop(field, 1) #this column contains no useful values and is not in all files, dropna however fails to remove it :/
				
		#CUTOFF AT 'pulse_start'
		cutoff = data_lefile[(data_lefile['L Raw X [px]'] == '# Message: pulse_start')].index.tolist()
		cutoff = int(cutoff[-1])
		data_lefile = data_lefile[cutoff-pre_cutoff:]
		data_lefile = data_lefile.reset_index() #make new index
		data_lefile = data_lefile.drop(['index'],1) # drop old index
		
		if isinstance(make, int):
			data_lefile = data_lefile[(data_lefile["Type"] != "MSG")]
			data_lefile["Pupil"] = ((data_lefile["L Dia Y [px]"] + data_lefile["L Dia X [px]"])/2)**2 # compute Pupil ~area
			data_lefile_single = data_lefile["Pupil"]
			
			if diff == "prebin":
				data_lefile_single = data_lefile_single.diff()
			
			data_lefile_single = downsample(data_lefile_single, sample=make)
			
			if diff == "postbin":
				data_lefile_single = data_lefile_single.diff()
				data_lefile_single = data_lefile_single.ix[1:,1]
				data_lefile_single.to_csv(regressor_path+lefile.split('_')[0]+'_diff_postbin.csv', index=False, header=False, index_label=None)
			
			elif diff == "prebin":
				data_lefile_single = data_lefile_single.ix[:,1]
				data_lefile_single.to_csv(regressor_path+lefile.split('_')[0]+'_diff_prebin.csv', index=False, header=False, index_label=None)
			
			else:
				data_lefile_single = data_lefile_single.ix[:,1]
				data_lefile_single.to_csv(regressor_path+lefile.split('_')[0]+'_new.csv', index=False,  header=False, index_label=None)
			
			continue
		
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
		
		if make == 'timecourse':
			groups_all = []
			for category in make_categories:
				print "Binning category:"+"\""+category[1]+"\""
				group = data_lefile[(data_lefile[category[0]] == category[1])]
				group = group.groupby(level=1).mean() # make per-category means
				group = group.ix[:240] # means for timepoints with missing values will be smaller.
				group['Time'] = group['Time']-group['Time'].ix[0]
				group['CoI'] = ''
				group['CoI'] = category[1]
				group = group.set_index(['CoI'], append=True, drop=True)
				group = group.reorder_levels(['CoI','measurement'])
				group["Pupil"] = ((group["L Dia Y [px]"] + group["L Dia X [px]"])/2)**2 # compute Pupil ~area
				groups_all.append(group)
			data_lefile = pd.concat(groups_all)
		else:
			print 'Please specify the "make" argumant as either "timecourse" or an integer.'
	
		#ADD ID
		data_lefile['ID']=lefile.split('_')[0]
		data_lefile = data_lefile.set_index(['ID'], append=True, drop=True)
		if make == "timecourse":
			data_lefile = data_lefile.reorder_levels(['ID','CoI','measurement'])
		#END ADD ID
		data_all.append(data_lefile)
	if make == "timecourse":
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

def get_rt_data(source=False, make_categories=False, no_response="", make_scrambled_yn=False):
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
	rt_dir = config.get('Data', 'rt_dir')
	#END IMPORT VARIABLES
	
	
	if source == 'local':
		from os import listdir
		data_path = path.expanduser(data_path+rt_dir)
		pre_fileslist = listdir(data_path)
		
	print('Loading data from '+data_path)
	if pre_fileslist == []:
		raise InputError('For some reason the list of results files could not be populated.')

	files = [lefile for lefile in pre_fileslist if lefile.endswith('OM.log') and not lefile.startswith("KP") and not lefile.startswith("ET_")]
	
	data_all = [] # empty container list for listing per-file dataframes
	for lefile in files:
		with open(data_path+lefile, 'rb') as source:
			a=0
			for line in source:
				if line == '\r\n':
					a += 1
				else:
					a = 0
				if a == 2:
					break
			df_file = pd.read_csv(source, engine='python', sep="\t")
		if len(set(df_file["Type"])) <= 2:
			continue #skip files which do not contain RT data (identified by having a monotonous "Type")
		df_file = df_file[["Code","RT","Type"]]
		df_file = df_file[(df_file["Code"] != "fixCross")]
		df_file.reset_index(inplace=True)
		
		if isinstance(no_response, int):
			df_file.ix[(df_file["Type"] != "miss"), "RT"] = no_response # remove missed trials with int penalty value
		else:
			df_file = df_file[(df_file["Type"] != "miss")] # remove missed trials
		
		if make_categories:
			new_category_names = set([new_cat[0] for new_cat in make_categories])
			for new_category_name in new_category_names:
				df_file[new_category_name]='' 
			trial_key = df_file[['index','Code']] #crop
			trial_key = np.array(trial_key) #for easier iteration
			for category in make_categories:
				criterion = category[-1]
				for trial in trial_key:
					if '-' in criterion:
						if criterion.split('-')[0] in trial[1] and criterion.split('-')[1] not in trial[1]:
							df_file.ix[(df_file['index']==trial[0]), category[0]] = category[1]
					elif '|' in criterion:
						if criterion.split('|')[0] in trial[1] or criterion.split('|')[1] in trial[1]:
							df_file.ix[(df_file['index']==trial[0]), category[0]] = category[1]
					else:
						if criterion in trial[1]:
							df_file.ix[(df_file['index']==trial[0]), category[0]] = category[1]
		
		if make_scrambled_yn:
		    df_file["scrambled"]=""
		    df_file.ix[(df_file["emotion"] == "scrambled"), "scrambled"]= "yes"
		    df_file.ix[(df_file["emotion"] != "scrambled"), "scrambled"]= "no"				
		
		df_file = df_file.drop(['index'],1) # drop old index
		#ADD ID
		df_file['ID']=lefile.split('-')[0]
		df_file = df_file.set_index(['ID'], append=True, drop=True)
		df_file = df_file.reorder_levels([1,0])
		#END ADD ID
		data_all.append(df_file)
	data_all = pd.concat(data_all)
	data_all["RT"] = data_all["RT"] / 10000 #make seconds
	return data_all
		
def downsample(x, sample, group=''):
	x = x.reset_index()
	if group:
		x = x.groupby(x[group].div(sample)).mean()
		del x[group]
	else:
		x = x.groupby(x.index/sample).mean()
	return x
