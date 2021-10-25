#!/usr/bin/env python3
"""
CS 6340, Fall 2021
University of Utah
Maxim Lisnic u1317463
Program 3: Named Entitiy Recognition
"""

import argparse
import pandas as pd

"""
****************************************************************************************************
Reading functions
****************************************************************************************************
"""

def ReadTrain(filename):
    """
    read and parse the training data file
    """

    # Instantiate a list
    training_data = []

    # Open file
    file = open(filename, 'r')
    lines = file.read().splitlines()
    file.close()

    # Read lines and parse
    for line in lines:
        items = line.split()
        training_data.append(items)

    return training_data

"""
****************************************************************************************************
Main
****************************************************************************************************
"""

def main():

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('train')
    parser.add_argument('-test', required = False)
    parser.add_argument('-gen', required = False)
    args = vars(parser.parse_args())

    # Read training data
    training_data = ReadTrain(args['train'])

    # Get ngrams
    ngrams1 = GetNgrams(training_data, 1)
    ngrams2 = GetNgrams(training_data, 2)
        
    # Build models
    model1 = BuildModel(ngrams1)
    model2 = BuildModel(ngrams2)

    #--------------------------------------------------
    # Testing
    #--------------------------------------------------

    if args['test'] is not None:

        # Read test data
        test_data = ReadTest(args['test'])

        # Get test probs
        for sentence in test_data:
            prob_a = GetProbSentence(sentence, model1, model2, n = 1, smoothing = False)
            prob_b = GetProbSentence(sentence, model1, model2, n = 2, smoothing = False)
            prob_c = GetProbSentence(sentence, model1, model2, n = 2, smoothing = True)

            print('S = %s' % sentence)
            print('')
            print('Unsmoothed Unigrams, logprob(S) = %s' % FormatProb(prob_a))
            print('Unsmoothed Bigrams, logprob(S) = %s' % FormatProb(prob_b))
            print('Smoothed Bigrams, logprob(S) = %s' % FormatProb(prob_c))
            print('')

    #--------------------------------------------------
    # Generating
    #--------------------------------------------------

    elif args['gen'] is not None:

        # Read seeds
        seeds = ReadTest(args['gen'])

        # Generate
        for seed in seeds:
            print('Seed = %s' % seed)
            print('')
            for i in range(1,11):
                sentence = GenSentence(seed, model1, model2)
                print('Sentence %d: %s' % (i, sentence))
            print('')



if __name__ == "__main__":
    main()