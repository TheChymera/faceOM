#!/usr/bin/env python
__author__ = 'Horea Christian'


def get_and_filter_results(experiment=False, source=False, prepixelation='not specified', remove='', mismeasurement='remove', apply_correct_values=False, make_COI=False):
	import pandas as pd
	from os import path
	import sys
	from chr_helpers import get_config_file

	config = get_config_file(localpath=path.dirname(path.realpath(__file__))+'/')
	
	if isinstance(prepixelation, (int, long)):
		print prepixelation
	
	#IMPORT VARIABLES
	if prepixelation == 'not specified': #is not triggers if the value is defined as 0 .
		prepixelation = config.getint('Data', 'prepixelation')
	if not experiment:
		experiment = config.get('Data', 'experiment')
	if not source:
		source = config.get('Source', 'source')
	data_path = config.get('Addresses', source)
	ignore_filename = config.get('Data', 'ignore_filename')
	#END IMPORT VARIABLES
	
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

def correct_values(data):
	data.ix[(data['scrambling'] != 0), 'intensity'] = 100
	return data
	
if __name__ == '__main__':
	main()
	show()
