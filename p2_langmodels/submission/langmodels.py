#!/usr/bin/env python3
"""
CS 6340, Fall 2021
University of Utah
Maxim Lisnic u1317463
Program 2: Language Models
"""

import argparse
import math
import random

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

def ReadTest(filename):
    """
    read full sentences from test data
    """

    # Instantiate a list
    test_data = []

    # Open file
    file = open(filename, 'r')
    lines = file.read().splitlines()
    file.close()

    # Read lines and parse
    for line in lines:
        test_data.append(line)

    return test_data

"""
****************************************************************************************************
Worker functions
****************************************************************************************************
"""

def GetBigrams(words):
    """
    Given a list of words, group them into two and spit it out
    """
    return [pair for pair in zip(words[:-1], words[1:]) if pair[1] != 'phi']

def GetNgrams(training_data, n):
    """
    Build an n-gram dictionary from training data
    """

    # Pre-pend a phi character
    training_data = [['phi'] + sentence for sentence in training_data]

    # Change all to lowercase and flatten list
    training_data = [word.lower() for sentence in training_data for word in sentence]

    # Group into bigrams, if needed
    if n == 2:
        training_data = GetBigrams(training_data)

    return training_data

def BuildModel(training_data):
    """
    Given a list of ngrams, build out their probabilities
    """

    model = dict()
    ngram_set = set(training_data)

    for ngram in ngram_set:
        freq = training_data.count(ngram)   
        model[ngram] = freq

    return model

def GetProbNgram(ngram, model1, model2, smoothing=False):
    """
    Given an ngram and a uni- and bigram probability models, get probability
    """

    # Handle unigrams
    if type(ngram) is str:
        try:
            freq = model1[ngram]
        except:
            return 'undefined'
        total_freq = sum([model1[key] for key in model1.keys() if key != 'phi'])
        prob = freq / total_freq

    # Handle bigrams
    elif type(ngram) is tuple:

        first_word = ngram[0]

        # Smoothed
        if smoothing:
            try:
                bigram_freq = model2[ngram]
            except:
                bigram_freq = 0
            try:
                prob = (bigram_freq + 1) / (model1[first_word] + len(model1.keys())-1)
            except:
                return 'undefined'
        
        # Not smoothed
        else:
            try:
                prob = model2[ngram] / model1[first_word]
            except:
                return 'undefined'

    return prob

def GetProbSentence(sentence, model1, model2, n, smoothing=False):
    """
    Get log2 probability of a sentence
    """ 

    # Split into words, change to lowercase
    sentence = [word.lower() for word in sentence.split()]

    # Get bigrams if needed
    if n == 2:
        sentence = GetBigrams(['phi'] + sentence)

    result = 0
    for ngram in sentence:
        prob = GetProbNgram(ngram, model1, model2, smoothing)
        if prob == 'undefined':
            return 'undefined'
        result += math.log2(prob)

    return result

"""
****************************************************************************************************
Generator
****************************************************************************************************
"""

def GenWord(first_word, model1, model2):
    """
    Given a word, probabilisticly generate the next one
    """

    # Get all bigrams 
    bigrams = [bigram for bigram in model2.keys() if bigram[0] == first_word]

    # Calculate probabilities
    freqs = [model2[bigram] for bigram in bigrams]
    probs = [freq / sum(freqs) for freq in freqs]

    # Pick bigram
    result = random.choices(
        population = bigrams,
        weights    = probs,
        k          = 1
    )

    return result[0][1]

def GenSentence(first_word, model1, model2):
    """
    Given a word, generate a sentence
    """

    words = [first_word]
    curr_word = first_word.lower()

    while True:

        # Get next word
        try:
            next_word = GenWord(curr_word, model1, model2)
        except:
            break

        # Add and move on
        words.append(next_word)
        curr_word = next_word

        # Check exit conditions
        if next_word in ['.', '?', '!']:
            break
        if len(words) == 11:
            break

    return ' '.join(words)


"""
****************************************************************************************************
Main
****************************************************************************************************
"""

def FormatProb(p):

    if p == 'undefined':
        return p

    return ('%.4f' % p)

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