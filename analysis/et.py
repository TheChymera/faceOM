#!/usr/bin/env python
from __future__ import division
__author__ = 'Horea Christian'

def main(experiment=False, source=False, prepixelation='not specified', elinewidth=2, ecolor='0.3', make_tight=True, total='means', make_std=False, make_sem=True):
    data_all = get_and_filter_results(experiment, source, prepixelation, mismeasurement='fix', apply_correct_values=True, make_COI=True)
