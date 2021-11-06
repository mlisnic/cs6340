#!/usr/bin/env python3
"""
CS 6340, Fall 2021
University of Utah
Maxim Lisnic u1317463
Project
"""

import argparse
import pandas as pd
import pycrfsuite
from data_processing import *

"""
****************************************************************************************************
Modeling functions
****************************************************************************************************
"""

def TrainModel(data):

    # Split the data
    X_train = [sent.loc[:, sent.columns != 'LABEL'].to_dict('records') for sent in data]
    y_train = [sent['LABEL'] for sent in data]

    # Initiate the trainer
    trainer = pycrfsuite.Trainer(verbose=True)
    for xseq, yseq in zip(X_train, y_train):
        trainer.append(xseq, yseq)

    # Set parameters
    trainer.set_params({
        'c1': 1.0,  
        'c2': 1e-3,  
        'max_iterations': 300, 
        'feature.possible_transitions': True
    })

    # Train
    trainer.train('model.crfsuite')

"""
****************************************************************************************************
Main
****************************************************************************************************
"""

def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('doclist')
    parser.add_argument('keylist')
    args = vars(parser.parse_args())

    # Read input data lists
    all_docs = ReadList(args['doclist'])
    all_keys = ReadList(args['keylist'])
    
    # Read helpers
    prefixes       = ReadList('./lists/prefixes.txt')
    prepositions   = ReadList('./lists/prepositions.txt')
    suffixes       = ReadList('./lists/suffixes.txt')
    locations      = pd.read_csv('./lists/locations.csv')
    locations_list = list(locations['country']) + list(locations['capital'])
    locations_list = [x.lower() for x in locations_list]

    # Build up the dataset
    data = []
    for f_doc, f_key in zip(all_docs, all_keys):
        text = ReadInput(f_doc)
        key = ReadKey(f_key)
        x = BuildInitialData(text, key)
        x['DOC'] = f_doc.split('/')[-1]
        data.append(x)
    data = [BuildFeatures(sent, prefixes, prepositions, suffixes, locations_list) for sent in data]

    # Train the model
    TrainModel(data)

if __name__ == "__main__":
    main()