#!/usr/bin/env python3
"""
CS 6340, Fall 2021
University of Utah
Maxim Lisnic u1317463
Project : Data Pre-processing functions
"""

import pandas as pd
import re
import nltk
from nltk.stem import WordNetLemmatizer

"""
****************************************************************************************************
Reading functions
****************************************************************************************************
"""

def ReadInput(filename):

    # Open file
    file = open(filename, 'r')
    contents = file.read()
    file.close()

    return contents

def ReadKey(filename):

    # Open file
    file = open(filename, 'r')
    lines = file.read().splitlines()
    file.close()

    data = []

    # Read lines and parse
    for line in lines:
        items = line.split(': ', 1)

        slot = items[0]

        if len(items) == 1:
            continue
        elif items[1] == '---':
            continue
        elif slot == 'TEXT':
            continue
        elif bool(re.match('^[0-9]+\Z', items[1])):
            answer = items[1]
        else:
            answer = items[1].split('"')[1]

        answer = nltk.word_tokenize(answer + ' .')[:-1]
        slot_tags = ['B-' + slot] + ['I-' + slot]*(len(answer)-1)

        entry = {'slot': slot_tags, 'answer': answer}
        data.append(entry)

    return data

def ReadList(filename):
    """
    read and parse the helper lists
    """

    # Init output
    data = []
    
    # Open file
    file = open(filename, 'r')
    lines = file.read().splitlines()
    file.close()

    # Read lines and parse
    for line in lines:
        data.append(line)

    return data

"""
****************************************************************************************************
Helper
****************************************************************************************************
"""

# Adapted from https://www.geeksforgeeks.org/kmp-algorithm-for-pattern-searching/
def KMPSearch(pat, txt):
	M = len(pat)
	N = len(txt)

	starting_indices = []

	lps = [0]*M
	j = 0 # index for pat[]

	computeLPSArray(pat, M, lps)

	i = 0 # index for txt[]
	while i < N:
		if pat[j] == txt[i]:
			i += 1
			j += 1

		if j == M:
			starting_indices.append((i-j))
			j = lps[j-1]

		elif i < N and pat[j] != txt[i]:
			if j != 0:
				j = lps[j-1]
			else:
				i += 1
	
	return starting_indices

def computeLPSArray(pat, M, lps):
	len = 0 

	lps[0] 
	i = 1

	while i < M:
		if pat[i]== pat[len]:
			len += 1
			lps[i] = len
			i += 1
		else:
			if len != 0:
				len = lps[len-1]
			else:
				lps[i] = 0
				i += 1


"""
****************************************************************************************************
Feature building functions
****************************************************************************************************
"""

def BuildInitialData(text, key=None):
    
    # Tokenize text
    sentences = nltk.sent_tokenize(text)
    words = [['PHI-2', 'PHI-1', 'PHI'] + nltk.word_tokenize(sentence) + ['OMEGA', 'OMEGA+1', 'OMEGA+2'] for sentence in sentences]
    words = [word for sentence in words for word in sentence]

    # Match all key tags
    if key is not None:
        bio_tags = ['O'] * len(words)
        for item in key:
            answer_length = len(item['answer'])
            indices = KMPSearch(item['answer'], words)
            if len(indices) == 0:
                continue
            for i in indices:
                bio_tags[i:i+answer_length] = item['slot']

    # Get POS tags
    words = nltk.pos_tag(words)

    # Build a dataframe
    data = pd.DataFrame(
        words,
        columns = ['WORD', 'POS']
    )
    if key is not None:
        data['LABEL'] = bio_tags
    data.loc[data['WORD'] == 'PHI', 'POS'] = 'PHIPOS'
    data.loc[data['WORD'] == 'OMEGA', 'POS'] = 'OMEGAPOS'
    data.loc[data['WORD'] == 'PHI-1', 'POS'] = 'PHI-1POS'
    data.loc[data['WORD'] == 'OMEGA+1', 'POS'] = 'OMEGA+1POS'
    data.loc[data['WORD'] == 'PHI-2', 'POS'] = 'PHI-2POS'
    data.loc[data['WORD'] == 'OMEGA+2', 'POS'] = 'OMEGA+1POS'

    return data

def BuildFeatures(data, prefixes, prepositions, suffixes, locations_list):
    """
    function to build the features
    """
    lemmatizer = WordNetLemmatizer()

    # Word attributes ------------------------------

    data['LEMMA'] = (
        data
        .apply(
            lambda x: lemmatizer.lemmatize(x['WORD']),
            axis = 1
         )
    )

    data['ABBR'] = (
        data
        .apply(
            lambda x: x['WORD'].endswith('.')
                      and bool(re.match('^[a-zA-Z.]+\Z', x['WORD']))
                      and bool(re.match('[a-zA-Z]', x['WORD']))
                      and len(x['WORD']) in [2,3,4],
            axis = 1
            )
    )

    data['CAP'] = (
        data
        .apply(
            lambda x: x['WORD'][0].isupper(),
            axis = 1
        )
    )

    data['NUM'] = (
        data
        .apply(
            lambda x: bool(re.match('[0-9]', x['WORD'])),
            axis = 1
        )
    )

    # Adjacent words ------------------------------

    data['NUM+1'] = (
        data
        ['NUM']
        .shift(-1)
    )

    data['NUM-1'] = (
        data
        ['NUM']
        .shift(1)
    )

    data['WORD+1'] = (
        data
        ['LEMMA']
        .shift(-1)
    )

    data['WORD-1'] = (
        data
        ['LEMMA']
        .shift(1)
    )

    data['WORD+2'] = (
        data
        ['LEMMA']
        .shift(-2)
    )

    data['WORD-2'] = (
        data
        ['LEMMA']
        .shift(2)
    )

    data['WORD+3'] = (
        data
        ['LEMMA']
        .shift(-3)
    )

    data['WORD-3'] = (
        data
        ['LEMMA']
        .shift(3)
    )

    data['POS+1'] = (
        data
        ['POS']
        .shift(-1)
    )

    data['POS-1'] = (
        data
        ['POS']
        .shift(1)
    )

    data['POS+2'] = (
        data
        ['POS']
        .shift(-2)
    )

    data['POS-2'] = (
        data
        ['POS']
        .shift(2)
    )

    data['POS+3'] = (
        data
        ['POS']
        .shift(-3)
    )

    data['POS-3'] = (
        data
        ['POS']
        .shift(3)
    )

    # Matching lists ------------------------------

    data['LOC'] = (
        data
        .apply(
            lambda x: x['WORD'].lower() in locations_list,
            axis = 1
        )
    )

    data['PREF'] = (
        data
        .apply(
            lambda x: x['WORD-1'] in prefixes,
            axis = 1
        )
    )

    data['SUFF'] = (
        data
        .apply(
            lambda x: x['WORD+1'] in suffixes,
            axis = 1
        )
    )

    # Globals ------------------------------

    data['LOWERCASE'] = (
        data
        .apply(lambda x: x['WORD'].lower(),
               axis = 1)
    )

    data['GLOBCAP'] = (
        data
        .apply(
            lambda x: bool(re.match('^[a-zA-Z]+\Z', x['WORD']))
                      and not x['WORD'].lower() in prepositions
                      and x['WORD-1'] != 'PHI'
                      and x['CAP'],
            axis = 1
        )
    )
    data['GLOBCAP'] = (
        data
        .groupby(['LOWERCASE'])
        ['GLOBCAP']
        .transform('any')
    )

    data['GLOBPREF'] = (
        data
        .apply(
            lambda x: bool(re.match('^[a-zA-Z]+\Z', x['WORD']))
                      and x['WORD-1'] != 'PHI'
                      and x['WORD-1'] in prefixes,
            axis = 1
        )
    )
    data['GLOBPREF'] = (
        data
        .groupby(['WORD'])
        ['GLOBPREF']
        .transform('any')
    )

    data['GLOBSUFF'] = (
        data
        .apply(
            lambda x: bool(re.match('^[a-zA-Z]+\Z', x['WORD']))
                      and x['WORD+1'] != 'OMEGA'
                      and x['WORD+1'] in suffixes,
            axis = 1
        )
    )
    data['GLOBSUFF'] = (
        data
        .groupby(['WORD'])
        ['GLOBSUFF']
        .transform('any')
    )

    # Clean up ------------------------------

    data = (
        data
        .query('WORD != "PHI" & WORD != "OMEGA"')
        .query('WORD != "PHI-1" & WORD != "OMEGA+1"')
        .query('WORD != "PHI-2" & WORD != "OMEGA+2"')
        .drop(columns = 'LOWERCASE')
        .reset_index(drop = True)
    )

    return data
