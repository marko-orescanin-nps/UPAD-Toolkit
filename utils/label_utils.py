import itertools


def generate_combinations(classes: list) -> list:
    '''
    Description: Used to calculate LABEL_COMBINATIONS in src/constants.py

    :classes: list of Classes (A, B, C, D, ...)

    :returns: all combinations of supplied classes
    '''
    result = []
    for L in range(len(classes) + 1):
        for subset in itertools.combinations(classes, L):
            result.append(subset)
    return result