#!/usr/bin/env python
__author__ = 'Horea Christian'


def get_et_data(source=False):
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
	
	data_all = pd.DataFrame([]) # empty container frame for concatenating input from multiple files
	for lefile in ['ET002_face_OM Samples.txt', 'ET004_face_OM Samples.txt']:
		print lefile
		data_lefile = pd.DataFrame.from_csv(data_path+lefile, header=42, sep='\t')
		data_lefile = data_lefile.reset_index()
		data_lefile['ID']=lefile.split('_')[0]
		data_lefile = data_lefile.set_index(['ID'], append=True, drop=True)
		data_lefile = data_lefile.reorder_levels([1,0])
		#REMOVE NON-INFORMATIVE (ALWAYS NULL) COLUMNS
		data_lefile = data_lefile.drop('L Mapped Diameter [mm]', axis=1)
		data_lefile = data_lefile.drop('Aux1', axis=1)
		data_lefile = data_lefile.drop('Frame', axis=1)
		data_lefile = data_lefile.drop('Pupil Confidence', axis=1)
		data_lefile = data_lefile.drop('R Validity', axis=1)
		#END REMOVE NON-INFORMATIVE (ALWAYS NULL) COLUMNS
		print data_lefile.ix[:10]
		#~ print data_lefile[(data_lefile['Type'] == 'MSG')][['Trial','L Raw X [px]']]
		
		
		
		
		
		#~ data_all = pd.concat([data_all, data_lefile], ignore_index=True)
		#~ ID = lefile.split('_')[0]
		#~ multindex = [np.array(ID*len(data_lefile)),np.array(np.arange())]
		#~ data_lefile.reindex(
	

def get_and_filter_results(experiment=False, source=False, remove='', mismeasurement='remove', apply_correct_values=False, make_COI=False):
	import pandas as pd
	from os import path
	import sys
	from chr_helpers import get_config_file

	config = get_config_file(localpath=path.dirname(path.realpath(__file__))+'/')
	

	
	if source == 'server':
		from HTMLParser import HTMLParser
		import urllib
		class ChrParser(HTMLParser):
			def handle_starttag(self, tag, attrs):
				if tag =='a':
					for key, value in attrs:
						if key == 'href' and value.endswith('.csv'):
							pre_fileslist.append(value)
		results_dir = data_path+experiment+'/px'+str(prepixelation)+'/'
		print results_dir
		data_url = urllib.urlopen(results_dir).read()
		parser = ChrParser()
		pre_fileslist = []
		parser.feed(data_url) # pre_fileslist gets populated here
	elif source == 'live':
		from os import listdir
		results_dir = path.dirname(path.dirname(path.realpath(__file__))) + data_path + str(prepixelation) + '/'
		results_dir = path.expanduser(results_dir)
		pre_fileslist = listdir(results_dir)
	elif source == 'local':
		from os import listdir
		results_dir = data_path + experiment + '/px' + str(prepixelation) + '/'
		results_dir = path.expanduser(results_dir)
		pre_fileslist = listdir(results_dir)
		
	print('Loading data from '+results_dir)
		
	if pre_fileslist == []:
		raise InputError('For some reason the list of results files could not be populated.')
	files = [lefile for lefile in pre_fileslist if lefile.endswith('.csv') and not lefile.endswith(ignore_filename+'.csv')]
	
	data_all = pd.DataFrame([]) # empty container frame for concatenating input from multiple files
	for lefile in files:
		data_lefile = pd.DataFrame.from_csv(results_dir+lefile)
		data_lefile['ID'] = path.splitext(lefile)[0]
		scrambling_list = set(data_lefile['scrambling'])
		if apply_correct_values:
			data_lefile=correct_values(data_lefile)	
		if make_COI:
			data_lefile = categories_of_interest(data_lefile, scrambling_list)
		elif mismeasurement == 'fix':
			make_COI == True
			data_lefile = categories_of_interest(data_lefile, scrambling_list)
		if mismeasurement == 'remove':
			data_lefile = data_lefile[data_lefile['RT'] >0] # remove entries with instant RTs here
		elif mismeasurement == 'nan':
			data_lefile.ix[(data_lefile['RT'] <=0), 'RT'] = False # remove entries with incorrect answers here
		elif mismeasurement == 'fix':
			import numpy as np
			for COI in set(data_lefile['COI']):
				data_lefile.ix[(data_lefile['RT'] <=0) & (data_lefile['COI'] == COI), 'RT'] = np.median(data_lefile[data_lefile['COI'] == COI]['RT']) #replace missing values with the median of the repecitive COI
		if 'no-response' in remove:
			data_lefile = data_lefile[data_lefile['keypress'] != 'none'] # remove entries with no answers here
		if 'incorrect' in remove:
			data_lefile = data_lefile[data_lefile['correct answer'] == data_lefile['keypress']] # remove entries with incorrect answers here
		data_all = pd.concat([data_all, data_lefile], ignore_index=True)
	return data_all
	
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
	get_et_data()
	#~ show()
