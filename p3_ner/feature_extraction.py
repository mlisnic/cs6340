#!/usr/bin/env python3
"""
CS 6340, Fall 2021
University of Utah
Maxim Lisnic u1317463
Program 3: Named Entitiy Recognition
"""

import argparse
import pandas as pd
import re

"""
****************************************************************************************************
Reading functions
****************************************************************************************************
"""

def ReadInput(filename):
    """
    read and parse the input file
    """

    # Instantiate the lists
    label = []
    word = []
    pos = []

    label.append('')
    pos.append('PHIPOS')
    word.append('PHI')

    # Open file
    file = open(filename, 'r')
    lines = file.read().splitlines()
    file.close()

    # Read lines and parse
    for line in lines:

        items = line.split()

        if len(items) == 0:
            label.append('')
            pos.append('OMEGAPOS')
            word.append('OMEGA')
            label.append('')
            pos.append('PHIPOS')
            word.append('PHI')
        else:
            label.append(items[0])
            pos.append(items[1])
            word.append(items[2])

    # End
    label.append('')
    pos.append('OMEGAPOS')
    word.append('OMEGA')

    # Create df
    data = pd.DataFrame(
        {
            'LABEL': label,
            'POS'  : pos,
            'WORD' : word
        }
    )

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
Features
****************************************************************************************************
"""

def BuildFeatures(data, prefixes, prepositions, suffixes, locations_list):
    """
    function to build the features
    """

    # Word attributes ------------------------------

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

    # Adjacent words ------------------------------

    data['WORD+1'] = (
        data
        ['WORD']
        .shift(-1)
    )

    data['WORD-1'] = (
        data
        ['WORD']
        .shift(1)
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
        .drop(columns = 'LOWERCASE')
        .reset_index(drop = True)
    )

    # Convert bools to 1/0
    data = data * 1

    # Reorder
    columns = data.columns.tolist()[1:]
    columns = ['LABEL'] + sorted(columns)
    data = data[columns]

    return data

"""
****************************************************************************************************
Main
****************************************************************************************************
"""

def GetName(filepath):
    """
    convert input filepath to output
    """

    filename = (filepath.split('/')[-1]).split('.')[0]

    return './' + filename + '_ft.csv'

def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('train')
    parser.add_argument('test')
    args = vars(parser.parse_args())

    # Read input data
    training_data = ReadInput(args['train'])
    testing_data  = ReadInput(args['test'])

    # Read helpers
    prefixes       = ReadList('./official-data/lists/prefixes.txt')
    prepositions   = ReadList('./official-data/lists/prepositions.txt')
    suffixes       = ReadList('./official-data/lists/suffixes.txt')
    locations      = pd.read_csv('./official-data/lists/locations.csv')
    locations_list = list(locations['country']) + list(locations['capital'])
    locations_list = [x.lower() for x in locations_list]

    # Build features
    training_data_ft = BuildFeatures(training_data, prefixes, prepositions, suffixes, locations_list)
    testing_data_ft  = BuildFeatures(testing_data, prefixes, prepositions, suffixes, locations_list)

    # Save
    training_data_ft.to_csv(GetName(args['train']), index = False)
    testing_data_ft.to_csv(GetName(args['test']), index = False)

if __name__ == "__main__":
    main()