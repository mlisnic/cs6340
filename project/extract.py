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
import sys
import numpy as np
from data_processing import *

"""
****************************************************************************************************
Modeling functions
****************************************************************************************************
"""

def Predict(data):

    # Read in the model
    tagger = pycrfsuite.Tagger()
    tagger.open('model.crfsuite')

    # Predict
    yhat = [tagger.tag(sent.to_dict('records')) for sent in data]

    return yhat

def ExtractSlot(slot, pred, sent):

    mask = [bool(re.match('[BI]-'+slot, tag)) for tag in pred]
    tags = np.array(pred)[mask]
    words = np.array([word['WORD'] for word in sent.to_dict('records')])[mask]

    seen = []
    results = []
    for tag, word in zip(tags,words):
        if tag[0] == 'B':
            results.append(' '.join(seen))
            seen = []
            seen.append(word)
        else:
            seen.append(word)
    results.append(' '.join(seen))
    results = list(set([item for item in results if item != '']))

    return results

def ExtractAnswers(data, yhat):

    answers = []

    for sent, pred in zip(data, yhat):

        phrases = []
        for slot in ['ACQUIRED', 'ACQBUS', 'ACQLOC', 'DLRAMT', 'PURCHASER', 'SELLER', 'STATUS']:
            phrases.append(ExtractSlot(slot, pred, sent))
        
        doc_answer = {
            'TEXT': sent['DOC'][0],
            'ACQUIRED': phrases[0],
            'ACQBUS': phrases[1],
            'ACQLOC': phrases[2],
            'DLRAMT': phrases[3],
            'PURCHASER': phrases[4],
            'SELLER': phrases[5],
            'STATUS': phrases[6],
        }
        answers.append(doc_answer)

    return answers

"""
****************************************************************************************************
Main
****************************************************************************************************
"""

def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('doclist')
    args = vars(parser.parse_args())

    # Read input data lists
    all_docs = ReadList(args['doclist'])
    
    # Read helpers
    prefixes       = ReadList('./lists/prefixes.txt')
    prepositions   = ReadList('./lists/prepositions.txt')
    suffixes       = ReadList('./lists/suffixes.txt')
    locations      = pd.read_csv('./lists/locations.csv')
    locations_list = list(locations['country']) + list(locations['capital'])
    locations_list = [x.lower() for x in locations_list]

    # Build up the dataset
    data = []
    for f_doc in all_docs:
        text = ReadInput(f_doc)
        x = BuildInitialData(text)
        x['DOC'] = f_doc.split('/')[-1]
        data.append(x)
    data = [BuildFeatures(sent, prefixes, prepositions, suffixes, locations_list) for sent in data]

    # Predict labels
    yhat = Predict(data)

    # Extract slots
    answers = ExtractAnswers(data, yhat)

    # Export
    original_stdout = sys.stdout

    with open(args['doclist'] +  '.templates', 'w') as f:
        sys.stdout = f 
        for answer in answers:
            for key,value in answer.items():
                if len(value) == 0:
                    print('%s: ---' % key)
                elif key == 'TEXT':
                    print('%s: %s' % (key, value))
                else:
                    for item in value:
                        print('%s: \"%s\"' % (key, item))
            print('')
        sys.stdout = original_stdout

if __name__ == "__main__":
    main()