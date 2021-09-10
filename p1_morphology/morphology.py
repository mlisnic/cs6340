#!/usr/bin/env python3
"""
CS 6340, Fall 2021
University of Utah
Maxim Lisnic u1317463
Program 1: Morphology
"""

import sys
from collections import defaultdict

"""
****************************************************************************************************
Reading functions
****************************************************************************************************
"""

def ReadDictionary(filename):
    """
    read and parse the dictionary file, return dictionary file
    """

    # Instantiate a dict
    dictionary = defaultdict(list)

    # Open file
    file = open(filename, 'r')
    lines = file.read().splitlines()
    file.close()

    # Read lines and parse
    for line in lines:
        items = line.split()
        word = items[0]
        pos  = items[1]
        root = items[0] if len(items) == 2 else items[3]
        dictionary[word].append((pos, root))

    return dictionary

def ReadRules(filename):
    """
    read and parse the rules file, return rulebook file
    """

    # Instantiate a rulebook
    rulebook = defaultdict(dict)

    # Open file
    file = open(filename, 'r')
    lines = file.read().splitlines()
    file.close()

    # Read lines and parse
    for line in lines:
        items = line.split()
        id = items[0]
        entry = {
            'affix': items[1],
            'chars_derived': items[2],
            'chars_origin': items[3],
            'pos_origin': items[4],
            'pos_derived': items[6]
        }
        rulebook[id] = entry

    return rulebook

def ReadTest(filename):
    """
    read and parse the test words
    """

    # Open file
    file = open(filename, 'r')
    lines = file.read().splitlines()
    file.close()

    return lines

"""
****************************************************************************************************
Helper functions
****************************************************************************************************
"""

def ReplaceChars(word, affix_type, affix_length, new):

    new = '' if new == '-' else new

    if affix_type == 'PREFIX':
        word = new + word[affix_length:]
    elif affix_type == 'SUFFIX':
        word = word[:-affix_length] + new

    return word

def ApplyRule(word, rule):

    # Check if rule applies
    affix_length = len(rule['chars_derived'])

    if rule['affix'] == 'PREFIX':
        to_try = word[0:affix_length]
    elif rule['affix'] == 'SUFFIX':
        to_try = word[-affix_length:]
    else:
        raise ValueError('Unknown affix type: %s' % rule['affix'])

    if to_try != rule['chars_derived']:
        return (None, None)
    
    # If applies, proceed
    new_word = ReplaceChars(word, rule['affix'], affix_length, rule['chars_origin'])
    new_pos = rule['pos_origin']

    return (new_word, new_pos)
                
def RunMorphologyOnWord(dictionary, rulebook, word, original_word, path_so_far, is_debug=False):

    results = []

    # Check if exists in dictionary
    if word in dictionary:
        entries = dictionary[word]
        for entry in entries:
            pos, root = entry
            result = {
                'WORD': original_word,
                'POS' : pos,
                'ROOT': root,
                'SOURCE': 'dictionary',
                'PATH': path_so_far
            }
            results = results + [result]
        return results
    # Otherwise
    else:
        path = []
        for id, rule in rulebook.items():
            new_word, new_pos = ApplyRule(word, rule)
            if new_word is not None:
                path = path_so_far + [id]
                results = results + (RunMorphologyOnWord(dictionary, rulebook, new_word, original_word, path))

    return results

def CheckConsistency(derivation, rulebook):

    path = derivation['PATH']
    path = list(reversed(path))
    pos = derivation['POS']

    for step in path:
        if rulebook[step]['pos_origin'] != pos:
            return None
        pos = rulebook[step]['pos_derived']

    return pos

def PrintTrace(traces):

    results = []

    for trace in traces:
        strings = []
        for key, value in trace.items():
            strings.append(key + '=' + value)
        strings = '\t'.join(strings)
        results.append(strings)
    
    return '\n'.join(results)

"""
****************************************************************************************************
Worker functions
****************************************************************************************************
"""

def GetTrace(dictionary, rulebook, word):

    results = RunMorphologyOnWord(dictionary, rulebook, word, word, [])

    # Check consistency
    checks = [CheckConsistency(result, rulebook) for result in results]

    # Clean up consistent results
    valid_results = []
    for i, result, check in zip(range(0, len(checks)), results, checks):
        if check is not None:
            new_result = result

            # POS
            new_result['POS'] = check

            # Path
            path = list(reversed(new_result['PATH']))
            path = '-' if len(path) == 0 else ','.join(path)
            new_result['PATH'] = path

            # Source
            source = 'dictionary' if path == '-' else 'morphology'
            new_result['SOURCE'] = source

            # Append
            valid_results += [new_result]

        # Handle not found words
    if len(valid_results) == 0:
        result = {
                'WORD': word,
                'POS' : 'noun',
                'ROOT': word,
                'SOURCE': 'default',
                'PATH': '-'
            }
        return [result] 

    # Sort
    def sort_key(res):
        return res['PATH']+res['POS']
    valid_results = sorted(valid_results, key = sort_key)

    return valid_results

def GetTraces(dictionary, rulebook, test_words):

    for word in test_words:
        trace = GetTrace(dictionary, rulebook, word)
        #print(trace)
        string = PrintTrace(trace)
        print(string)
        print('')

"""
****************************************************************************************************
Main
****************************************************************************************************
"""

def main():

    # Read dictionary
    dictionary = ReadDictionary(sys.argv[1])

    # Read rules
    rulebook = ReadRules(sys.argv[2])

    # Read test
    test_words = ReadTest(sys.argv[3])

    # Run morphology
    GetTraces(dictionary, rulebook, test_words)


if __name__ == "__main__":
    main()